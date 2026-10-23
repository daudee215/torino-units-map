"""Grain and provenance checks on actual local investigation outputs."""
from collections import Counter
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    summary=load(ROOT/'output/investigation/summary.json')
    assert summary['local_only'] is True
    sample=summary['sample']
    assert len(sample)==30 and len({c['building_id'] for c in sample})==30 and len({c['parcel'] for c in sample})==30
    assert set(Counter(c['stratum'] for c in sample).values())=={5}
    assert all(c['documentary_entrance_validation']=='pending' and c['manual_site_review']=='pending' for c in sample)
    entrances=load(ROOT/'data/ingressi.json')['p'];ids={str(x) for x in entrances['COD_CIVICO']}
    buildings=load(ROOT/'data/edifici.json')['p'];building_ids={str(x) for x in buildings['bld_id']}
    additional=0
    for path in (ROOT/'output/investigation/parcels').glob('*/*.json'):
        data=load(path);graph=load(ROOT/'data/registry/parcels'/(data['parcel']+'.json'))
        assert data['shared_access_context']['current_courtyard_status']=='unknown'
        if data['shared_access_context']['courtyard_status']=='historically_reported':assert any(d['courtyard_support'] for d in data['documents'])
        property_ids={p['id'] for p in graph['properties']}
        assert set(data['property_evidence'])==property_ids
        for pid,e in data['property_evidence'].items():
            assert not e['legal_entrance_confirmation'] and e['physical_unit_location']=='unknown'
            assert e['source_lineages'].count('SIPEE')==1 and e['independent_source_count'] is None
            excluded={l['target'].split(':',1)[1] for l in graph['links'] if l['kind']=='property_entrance' and l['source']==pid}
            for c in e.get('additional_entrance_candidates',[]):
                additional+=1
                assert c['status']=='candidate' and c['entrance_id'] in ids and c['entrance_id'] not in excluded
                assert c['property_parcel']==data['parcel'] and c['parcel_distance_m']<=25
        for eid,e in data['entrances'].items():
            assert eid in ids
            for route in e.get('routes',[]):
                assert route['status']=='candidate' and route['unknown']
                assert route['internal_access']['table']=='v_acc_int_civico_tp_str'
                for b in route['building_candidates']:
                    assert b['building_id'] in building_ids and b['status']=='candidate' and b['distance_m']<=3
        for d in data['documents']:
            assert d['current_validity']=='unknown' and not d['legal_confirmation'] and not d['raw_document_published']
            assert d['page']>0 and len(d['sha256'])==64
            assert not {'concessionario','owner','codice_fiscale'} & set(d)
    docs=load(ROOT/'output/investigation/document-observations.json')
    digione=[d for d in docs if d['parcels']==['1175/643']]
    assert {d['members'][0][4] for d in digione}=={'113','114'} and len(digione)==2
    market=next(d for d in docs if d['id']=='torino-2023-racconigi-market')
    assert len(market['members'])==32 and market['area_reported_m2'] is None
    assert market['object_scope']=='multi_property_market_concession'
    inventory=load(ROOT/'output/investigation/municipal-inventory.json')
    assert inventory['local_only'] and inventory['counts']['torino_rows']==4439
    assert inventory['counts']['pilot_rows']==228 and inventory['counts']['pilot_parcels']==65
    assert inventory['excluded_pages']==list(range(52,467))
    records=inventory['torino_records'];assert len({r['id'] for r in records})==len(records)
    assert all(r['page']<=51 and r['address_scope']=='asset_group_primary_address' and r['current_validity']=='unknown' and not r['legal_confirmation'] for r in records)
    anchors={'437':(None,4.5,None),'32301':(None,None,11361.0),'633':(None,None,4575.0),'972':(18.0,None,None),'994':(None,None,12550.0)}
    for code,expected in anchors.items():
        row=next(r for r in records if r['municipal_cadastral_row_code']==code)
        assert tuple(row['numeric_consistency'][k] for k in ['consistency_m2','consistency_rooms','consistency_m3'])==expected
    print('Municipal inventory verified: 228 pilot references; partial repeated layouts excluded; area, rooms and volume remain distinct.')
    print(f'Investigation verified: 30 distinct cases, six strata; {additional} additional candidate records; routes remain unconfirmed; 113/114 and grouped/land evidence preserved.')


if __name__=='__main__':main()
