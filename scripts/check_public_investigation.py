"""Validate the bounded source-only investigation release, without local files."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

FORBIDDEN={'review','review_events','note','review_note','owner','tenant','concessionario','codice_fiscale','file','raw_pdf','credentials'}
INVENTORY_FIELDS=set('asset_group_code municipality asset_primary_address asset_description municipal_cadastral_row_code sheet parcel subalterno consistency_m2 consistency_rooms consistency_m3 page row_y id member inherited_group_fields group_field_conflicts scope address_scope identity_status current_validity legal_confirmation field_units numeric_consistency in_pilot source edition'.split())

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def clean(value):
    if isinstance(value,dict):
        assert not FORBIDDEN.intersection(value), FORBIDDEN.intersection(value)
        for child in value.values():clean(child)
    elif isinstance(value,list):
        for child in value:clean(child)

def check(root):
    summary=read(root/'data/investigation/summary.json');clean(summary)
    assert summary['public_source_only'] and not summary['local_only'] and summary['version']=='2.2.0'
    assert len(summary['sample'])==30 and set(Counter(c['stratum'] for c in summary['sample']).values())=={5}
    assert len({c['parcel'] for c in summary['sample']})==30
    assert all(c['documentary_entrance_validation']=='pending' and c['manual_site_review']=='pending' for c in summary['sample'])
    paths=sorted((root/'data/investigation/parcels').glob('*/*.json'))
    expected={p.relative_to(root/'data/registry/parcels').as_posix() for p in (root/'data/registry/parcels').glob('*/*.json')}
    assert {p.relative_to(root/'data/investigation/parcels').as_posix() for p in paths}==expected
    def inspect(path):
        data=read(path);clean(data)
        assert data['public_source_only'] and not data['local_only'] and data['version']=='2.2.0'
        assert path.relative_to(root/'data/investigation/parcels').with_suffix('').as_posix()==data['parcel']
        assert data['shared_access_context']['current_courtyard_status']=='unknown'
        assert all(not e['legal_entrance_confirmation'] and e['physical_unit_location']=='unknown' for e in data['property_evidence'].values())
        for d in data['documents']:
            assert d['current_validity']=='unknown' and not d['raw_document_published'] and not d['legal_confirmation']
        for r in data['municipal_inventory']:
            assert set(r)==INVENTORY_FIELDS and r['in_pilot'] and r['address_scope']=='asset_group_primary_address'
            assert r['current_validity']=='unknown' and not r['legal_confirmation'] and r['page']<=51
        return len(data['municipal_inventory'])
    with ThreadPoolExecutor(max_workers=16) as pool:inventory_count=sum(pool.map(inspect,paths))
    assert inventory_count==228
    print(f'Public investigation verified: {len(paths)} source-only dossiers; {inventory_count} municipal references; 30 pending review cases; no local review fields.')
    return paths

if __name__=='__main__':check(Path(__file__).resolve().parents[1])
