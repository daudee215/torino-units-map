"""Build a local-only, reproducible address crosswalk; never infer unit access.

Run with --download to refresh the observed official downloads. Raw files and
the crosswalk stay ignored until redistribution terms and matches are reviewed.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import unicodedata
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1]
CIVIC_URL = 'http://geoportale.comune.torino.it/geodati/civici_WGS84_EPSG4326_csv.csv'
ANN_URL = 'https://anncsu.open.agenziaentrate.gov.it/age-inspire/opendata/anncsu/getds.php?INDIR_PIEM'


def norm(value):
    return re.sub(r'[^A-Z0-9]', '', unicodedata.normalize('NFKD', str(value or '')).upper())


def address_key(street, civic):
    # Retain all letter/scala/bis components. No fuzzy aliases or proximity.
    return norm(street), norm(civic)


def street_signature(street):
    # Only complete word reordering; no abbreviation expansion or partial names.
    words=re.findall(r'[A-Z0-9]+',unicodedata.normalize('NFKD',street).upper())
    return tuple(sorted(words))


def street_aliases(municipal_names, source_names):
    left,right=defaultdict(set),defaultdict(set)
    for name in municipal_names:left[street_signature(name)].add(name)
    for name in source_names:right[street_signature(name)].add(name)
    return {next(iter(names)):next(iter(right[key])) for key,names in left.items()
            if len(names)==1 and len(right[key])==1}


def distance(a, b):
    from math import radians, sin, cos, asin, sqrt
    x1,y1,x2,y2=map(radians,[*a,*b])
    return 12742000*asin(min(1,sqrt(sin((y2-y1)/2)**2+cos(y1)*cos(y2)*sin((x2-x1)/2)**2)))


def build(download=False):
    civic_path=ROOT/'_raw/civics/civici_WGS84_EPSG4326_csv.csv'
    ann_path=ROOT/'_raw/anncsu/INDIR_PIEM_download.zip'
    for path,url in [(civic_path,CIVIC_URL),(ann_path,ANN_URL)]:
        if download or not path.exists():
            response=requests.get(url,timeout=(15,90));response.raise_for_status()
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(response.content)
            path.with_suffix(path.suffix+'.source.json').write_text(json.dumps(dict(url=url,retrieved=datetime.now(timezone.utc).isoformat())),encoding='utf-8')
    civic_rows=list(csv.DictReader(io.StringIO(civic_path.read_text(encoding='utf-8-sig')),delimiter=';'))
    by_id=defaultdict(list)
    for row in civic_rows:
        by_id[row['COD_CIVICO']].append(row)
    with zipfile.ZipFile(ann_path) as archive:
        names=[n for n in archive.namelist() if n.endswith('.csv')]
        assert len(names)==1
        with archive.open(names[0]) as stream:
            ann_rows=[r for r in csv.DictReader(io.TextIOWrapper(stream,encoding='utf-8-sig'),delimiter=';') if r['CODICE_COMUNE']=='L219' and r['CODICE_ISTAT']=='001272']
    national=defaultdict(list)
    for row in ann_rows:
        if any(row[k] for k in ['SPECIFICITA','METRICO','PROGRESSIVO_SNC']):
            continue  # Special numbering needs a separately verified rule.
        national[address_key(row['ODONIMO'],row['CIVICO']+row['ESPONENTE'])].append(dict(
            street_id=row['PROGRESSIVO_NAZIONALE'],access_id=row['PROGRESSIVO_ACCESSO'],
            municipal_street_code=row['CODICE_COMUNALE'],municipal_access_code=row['CODICE_COMUNALE_ACCESSO'],
            street=row['ODONIMO'],civic=row['CIVICO'],suffix=row['ESPONENTE']))
    aliases=street_aliases({r['VIA'] for r in civic_rows},{r['ODONIMO'] for r in ann_rows})
    def lookup(row):
        candidates=national[address_key(row['VIA'],row['CIVICO'])]
        method='exact_normalized_street_civic'
        if not candidates and row['VIA'] in aliases:
            candidates=national[address_key(aliases[row['VIA']],row['CIVICO'])]
            method='unique_full_street_words_reordered_and_exact_civic'
        return candidates,method
    layer=json.loads((ROOT/'data/ingressi.json').read_text(encoding='utf-8'))
    meta=json.loads((ROOT/'data/meta.json').read_text(encoding='utf-8'))
    rows=[{k:v[i] for k,v in layer['p'].items()} for i in range(layer['n'])]
    results={};counts=Counter()
    city_counts=Counter()
    for row in civic_rows:
        candidates,method=lookup(row);n=len(candidates)
        city_counts[('unique_address_candidate' if method=='exact_normalized_street_civic' else 'unique_street_order_candidate') if n==1 else 'ambiguous_address' if n else 'no_exact_address']+=1
    for i,e in enumerate(rows):
        eid=str(e['COD_CIVICO']);matches=by_id[eid];flags=[];municipal=None
        if len(matches)==1:
            row=matches[0]
            xy=[float(row[k].replace(',','.')) for k in ['COORDINATA_X','COORDINATA_Y']]
            assert 6<xy[0]<9 and 44<xy[1]<47
            municipal=dict(street=row['VIA'],civic=row['CIVICO'],coordinates=xy,
                           cap=row['CAP'],district=row['CIRCOSCRIZIONE'])
            if address_key(e['VIA'],e['CIVICO'])!=address_key(row['VIA'],row['CIVICO']):flags.append('municipal_address_changed')
            # Compact coordinates use the project's origin and quantization.
            point=layer['g'][i]
            old=[meta['lon0']+point[0]/meta['q'],meta['lat0']+point[1]/meta['q']]
            if isinstance(old,list) and len(old)==2 and isinstance(old[0],(int,float)):
                municipal['displacement_m']=round(distance(old,xy),2)
                if municipal['displacement_m']>5:flags.append('municipal_position_changed_over_5m')
            candidates,method=lookup(row)
        else:
            flags.append('municipal_id_missing' if not matches else 'municipal_id_duplicated')
            candidates=[]
            method=None
        status=('unique_address_candidate' if method=='exact_normalized_street_civic' else 'unique_street_order_candidate') if len(candidates)==1 else 'ambiguous_address' if candidates else 'no_exact_address'
        counts[status]+=1
        for flag in flags:counts[flag]+=1
        results[eid]=dict(municipal=municipal,anncsu_candidates=candidates,status=status,flags=flags,
                          anncsu_match_method=method,
                          inherited_parcel_method=e['match_lotto'])
    source_meta=[]
    for path,url,licence in [(civic_path,CIVIC_URL,'CC BY 4.0 (catalogue)'),(ann_path,ANN_URL,'Open data; redistribution terms pending metadata review')]:
        sidecar=path.with_suffix(path.suffix+'.source.json')
        acquisition=json.loads(sidecar.read_text(encoding='utf-8')) if sidecar.exists() else {}
        source_meta.append(dict(url=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),licence=licence,
                                retrieved=acquisition.get('retrieved'),retrieval_date_known=bool(acquisition)))
    result=dict(built=datetime.now(timezone.utc).isoformat(),local_only=True,
        sources=source_meta,anncsu_file=names[0],municipal_revision_advertised='2026-09-30',
        counts=dict(municipal_rows=len(civic_rows),anncsu_torino_rows=len(ann_rows),pilot_rows=len(rows),
                    duplicated_municipal_ids=sum(len(v)>1 for v in by_id.values()),
                    duplicated_anncsu_access_ids=sum(v>1 for v in Counter(r['PROGRESSIVO_ACCESSO'] for r in ann_rows).values()),
                    **counts),city_crosswalk_counts=dict(city_counts),entrances=results,
        limitations=['Exact normalized address agreement is a candidate, not a confirmed shared access.',
                      'ANNCSU Torino coordinates are absent in this snapshot.',
                      'No parcel or building assignments were replaced.',
                      'No inference of apartment interiors or legal cadastral verification.'])
    target=ROOT/'output/addresses/evidence.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps(result['counts']));print(json.dumps(city_counts))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--download',action='store_true')
    build(parser.parse_args().download)
