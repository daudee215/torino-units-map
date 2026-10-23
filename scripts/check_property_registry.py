"""High-value integrity and grain checks for the actual built registry."""
import json
from pathlib import Path
import sqlite3
from build_property_registry import text,floor_key,numeric

ROOT=Path(__file__).resolve().parents[1]


def main():
    assert text(0)=='0' and numeric(0)==0 and numeric(None) is None
    assert floor_key(-1)!=floor_key(1) and floor_key(0)==floor_key('0')==floor_key('0.0')
    summary=json.loads((ROOT/'data/registry/summary.json').read_text(encoding='utf-8'))
    db=sqlite3.connect(ROOT/'output/registry/properties.sqlite')
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
    certs={r[0]:json.loads(r[1]) for r in db.execute("SELECT id,attributes FROM entities WHERE kind='certificate'")}
    properties={r[0]:json.loads(r[1]) for r in db.execute("SELECT id,attributes FROM entities WHERE kind='property'")}
    assert len(certs)==summary['counts']['certificates']
    assert len(properties)==summary['counts']['properties']
    bulk_ids=set()
    for cid,c in certs.items():
        assert c['property_id'] in properties
        assert cid in properties[c['property_id']]['certificates']
        for observation in c.get('interior_observations',[]):
            assert observation['source_field']=='interno' and observation['source_record_id']
            assert observation['normalized'] is not None or observation['raw'] is None or isinstance(observation['raw'],str)
        if c['eligible_on_date']:
            assert c['active'] and c['submitted']<=summary['as_of']<=c['expires']
        for alias in c.get('source_aliases',[]):
            assert alias['id'] not in bulk_ids and alias['id'] not in certs, 'Bulk record duplicated after reconciliation'
            bulk_ids.add(alias['id'])
            year,_,progress=c['public_code'].split('-')
            key=year+progress+str(c['internal_certifier_id'])
            assert bytes.fromhex(alias['id'].split(':',1)[1]).decode('ascii').endswith(key), 'Different certificates merged on attributes alone'
            assert alias['submitted']==c['submitted']
            assert set(map(tuple,alias['members'])) & set(map(tuple,c['members']))
    grouped=certs['sipee:2025-200471-0025']
    for p in properties.values():
        values={o['normalized'] for o in p.get('interior_observations',[]) if o['normalized']}
        assert set(p.get('reported_interiors',[]))==values
        assert ('conflicting_reported_interiors' in p['flags'])==(len(values)>1)
    assert {m[4] for m in grouped['members']}=={'8','9'}
    assert grouped['standard_electricity_kwh_year']==2206.42
    assert len([c for c in certs.values() if c.get('standard_electricity_kwh_year')==2206.42])==1
    assert certs['sipee:2026-208400-0131']['standard_electricity_kwh_year'] is None
    # Every graph target remains a real loaded GIS entity, not a generated apartment polygon.
    for kind,source_kind,target_kind in db.execute('''SELECT DISTINCT r.kind,s.kind,t.kind FROM relationships r
        JOIN entities s ON s.id=r.source JOIN entities t ON t.id=r.target'''):
        assert source_kind=='property'
        assert target_kind=={'declared_parcel':'parcel','property_entrance':'entrance','property_building':'building','property_alias':'property'}[kind]
    sample=json.loads((ROOT/'data/roof_evidence.json').read_text(encoding='utf-8'))
    assert sample['audit']['sample_features']==152
    assert sample['audit']['has_roof_planes'] is False
    assert sample['audit']['original_coordinates_have_z'] is False
    assert not db.execute("SELECT name FROM sqlite_master WHERE name IN ('meters','readings')").fetchall(), 'Private measurements must not share the public registry'
    print(f"Registry verified: {len(properties):,} property/group identities, {len(certs):,} certificates, {len(bulk_ids):,} reconciled bulk IDs; FK, grain, missing-energy and roof-evidence checks passed.")
    db.close()


if __name__=='__main__':main()
