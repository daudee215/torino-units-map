"""Attach reviewed, source-only address evidence to bounded static parcel files.

No raw archives, local decisions, notes or database files are published.
Run after rebuilding registry parcels. Requires the inspected local crosswalk.
"""
import json
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def select(value, fields):
    return {k:value[k] for k in fields if k in value}


def prepare(version='2.1.0'):
    source=json.loads((ROOT/'output/addresses/evidence.json').read_text(encoding='utf-8'))
    metadata=select(source,['anncsu_file','municipal_revision_advertised','built'])
    metadata['local_only']=False
    metadata['attribution']=[
        dict(provider='Città di Torino',licence='CC BY 4.0',
             source='https://www.geoportale.piemonte.it/geonetwork/srv/api/records/c_l219:8987bd22-fea8-44e0-a900-7a6400032b30'),
        dict(provider='ANNCSU — Istat / Agenzia delle Entrate',licence='CC BY 4.0',
             source='https://www.anncsu.gov.it/it/consultazione-dellarchivio/open-data/',
             licence_statement='https://www.anncsu.gov.it/it/consultazione-dellarchivio/ricerca-strade-e-numeri-civici/'),
        dict(provider='Regione Piemonte — BDTRE 2026',licence='CC BY 4.0',source=source['bdtre']['source'])]
    metadata['bdtre']=select(source['bdtre'],['edition','data_cutoff','inspected','package_sha256','tables','licence','source','limitations'])
    count=0
    for path in sorted((ROOT/'data/registry/parcels').glob('*/*.json')):
        parcel=json.loads(path.read_text(encoding='utf-8'))
        assert all('review' not in link for link in parcel['links'])
        ids={str(e['COD_CIVICO']) for e in parcel['entrances']}
        entrances={}
        for eid in ids:
            original=source['entrances'][eid]
            record=select(original,['municipal','status','flags','anncsu_match_method','inherited_parcel_method'])
            record['anncsu_candidates']=[select(c,['street_id','access_id','municipal_street_code','municipal_access_code','street','civic','suffix']) for c in original['anncsu_candidates']]
            record['bdtre_candidates']=[select(c,['id','table','tp_str_nom','civico_num','civico_sub','data_acq','data_agg','data_fin','modo_prod','coordinates_32632','access_type','distance_m','match_method','status']) for c in original.get('bdtre_candidates',[])]
            entrances[eid]=record
        parcel['address_evidence']={**metadata,'entrances':entrances}
        path.write_text(json.dumps(parcel,ensure_ascii=False,separators=(',',':'),sort_keys=True),encoding='utf-8')
        count+=1
    print(f'Reviewed static address evidence attached to {count} source-only parcel files.')
    path=ROOT/'data/registry/summary.json'
    summary=json.loads(path.read_text(encoding='utf-8'));summary['version']=version
    path.write_text(json.dumps(summary,ensure_ascii=False,separators=(',',':'),sort_keys=True),encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--version',default='2.1.0')
    prepare(parser.parse_args().version)
