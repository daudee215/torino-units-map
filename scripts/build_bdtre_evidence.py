"""Inspect acquired BDTRE Torino and attach conservative access candidates locally.

No join on metadata oid/uuid: the acquired tables repeat those values.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from shapely import from_wkb
from pyproj import Transformer
from build_address_evidence import address_key,street_aliases

ROOT=Path(__file__).resolve().parents[1]


def geometry(blob):
    assert blob[:2]==b'GP'
    envelope=(blob[3]>>1)&7
    return from_wkb(blob[8+{0:0,1:32,2:48,3:48,4:64}[envelope]:])


def build():
    path=next((ROOT/'_raw/bdtre').glob('*.gpkg'))
    db=sqlite3.connect(path);db.row_factory=sqlite3.Row
    target=ROOT/'output/addresses/evidence.json'
    evidence=json.loads(target.read_text(encoding='utf-8'))
    tables={};indexes={}
    for table in ['v_acc_pc_civico_tp_str','v_acc_int_civico_tp_str','v_edifc','v_un_vol']:
        tables[table]=dict(rows=db.execute(f'SELECT count(*) FROM {table}').fetchone()[0],
            distinct_uuid=db.execute(f'SELECT count(DISTINCT uuid) FROM {table}').fetchone()[0],
            distinct_oid=db.execute(f'SELECT count(DISTINCT oid) FROM {table}').fetchone()[0])
        if 'civico' not in table:continue
        index=defaultdict(list)
        for row in db.execute('SELECT * FROM '+table):
            row=dict(row);g=geometry(row.pop('geometria'))
            if g.geom_type!='Point':continue
            if not row['tp_str_nom'] or not row['civico_num']:continue
            record={k:row[k] for k in ['id','tp_str_nom','civico_num','civico_sub','data_acq','data_agg','data_fin','modo_prod']}
            record.update(table=table,coordinates_32632=[g.x,g.y],access_type=row.get('acc_pc_ty'))
            index[address_key(row['tp_str_nom'],row['civico_num']+(row['civico_sub'] or ''))].append(record)
        names={record['tp_str_nom'] for records in index.values() for record in records}
        aliases=street_aliases({e['municipal']['street'] for e in evidence['entrances'].values() if e['municipal']},names)
        indexes[table]=(index,aliases)
    transform=Transformer.from_crs(4326,32632,always_xy=True)
    counts=Counter()
    for entrance in evidence['entrances'].values():
        municipal=entrance['municipal'];entrance['bdtre_candidates']=[]
        if not municipal:continue
        xy=transform.transform(*municipal['coordinates']);key=address_key(municipal['street'],municipal['civic'])
        for table,(index,aliases) in indexes.items():
            candidates=index[key];method='exact_normalized_street_civic_and_within_20m'
            if not candidates and municipal['street'] in aliases:
                candidates=index[address_key(aliases[municipal['street']],municipal['civic'])]
                method='unique_full_street_words_reordered_exact_civic_and_within_20m'
            for record in candidates:
                x,y=record['coordinates_32632'];distance=((xy[0]-x)**2+(xy[1]-y)**2)**0.5
                if distance<=20:
                    entrance['bdtre_candidates'].append(dict(record,distance_m=round(distance,2),
                        match_method=method,status='candidate'))
        counts['entrances_with_access_candidates']+=bool(entrance['bdtre_candidates'])
        for table in indexes:
            counts[table]+=sum(c['table']==table for c in entrance['bdtre_candidates'])
    evidence['bdtre']=dict(edition='2026',data_cutoff='2026-03-31',inspected=datetime.now(timezone.utc).isoformat(),
        package_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),tables=tables,counts=dict(counts),licence='CC BY 4.0',
        source='https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:da9b12ba-866a-4f0f-8704-5b7b753e4f15',
        limitations=['Table id is scoped to this package and table; oid/uuid are repeated metadata values.',
                    'Access candidates do not establish an apartment entrance or building relationship.',
                    '20m is a search threshold, not positional accuracy.',
                    'Internal-access points are not apartment polygons or apartment counts.'])
    target.write_text(json.dumps(evidence,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps(evidence['bdtre'],ensure_ascii=False))


if __name__=='__main__':build()
