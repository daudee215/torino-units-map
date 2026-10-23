"""Actual catalogue, join grain, bounded search and isolated workflow persistence checks."""
from contextlib import closing
from pathlib import Path
import hashlib,json,sqlite3,tempfile
from urllib.parse import quote
import workspace_api
ROOT=Path(__file__).resolve().parents[1]
def main():
    database=ROOT/'output/property-workspace/catalog.sqlite'
    before=hashlib.sha256(database.read_bytes()).hexdigest()
    with closing(sqlite3.connect(database)) as db:
        metadata=json.loads(db.execute("SELECT value FROM metadata WHERE key='summary'").fetchone()[0])
        assert metadata['records']==24884 and metadata['ape_identities']==24706 and metadata['municipal_only_key_records']==178
        rows=[json.loads(r[0]) for r in db.execute("SELECT detail FROM records WHERE kind='municipal_reported_key'")]
        assert len({r['id'] for r in rows})==len({tuple(r['members'][0]) for r in rows})==178
        assert all(not r['certificates'] and r['floor'] is None and r['heated_area_m2'] is None and r['residential'] is None and not r['connections'] and not r['current_entrance_confirmed'] for r in rows)
        assert all(r['address_scope']=='asset_group_primary_address' and any(e['kind']=='inventory_observation' for e in r['history']) for r in rows)
        assert not db.execute('SELECT count(*) FROM record_parcels p LEFT JOIN records r ON p.id=r.id WHERE r.id IS NULL').fetchone()[0]
    comparisons=json.loads((ROOT/'output/property-workspace/source-comparisons.json').read_text(encoding='utf-8'))
    assert len(comparisons)==len({(c['property_id'],c['municipal_row_id']) for c in comparisons})==41
    assert len({c['key'] for c in comparisons})==38 and len({c['property_id'] for c in comparisons})==31
    assert all(c['area_difference_m2'] is None and c['area_comparison']=='different_measurement_definitions' and c['municipal_floor'] is None and c['municipal_unit_use'] is None and not c['apartment_access_confirmation'] for c in comparisons)
    for source,expected in [('all',24884),('municipal',178),('shared_key',31),('section_case',2),('ape',24706)]:
        status,data=workspace_api.get_workspace('/api/property-workspace/search?source='+source)
        assert status==200 and data['total']==expected and len(data['records'])<=50
    status,first=workspace_api.get_workspace('/api/property-workspace/search?q=1175%2F643%2F113')
    assert status==200 and first['total']==1 and first['records'][0]['kind']=='municipal_reported_key'
    status,second=workspace_api.get_workspace('/api/property-workspace/search?source=all&offset=50')
    assert status==200 and second['offset']==50
    status,injected=workspace_api.get_workspace('/api/property-workspace/search?q=%25%27%20OR%201%3D1')
    assert status==200 and injected['total']==0
    assert workspace_api.get_workspace('/api/property-workspace/search?parcel=..%2F..')[0]==400
    assert workspace_api.get_workspace('/api/property-workspace/record/not-a-record')[0]==404
    _,cases=workspace_api.get_workspace('/api/property-workspace/search?source=section_case')
    assert len(cases['records'])==2
    for row in cases['records']:
        _,data=workspace_api.get_workspace('/api/property-workspace/record/'+quote(row['id'],safe=''))
        r=data['record'];assert r['members'][0][1]=='' and r['audit']['section_alternatives'][0]['member'][1]=='='
        assert not metadata['section_review']['status']=='resolved'
    # Workflow writes go to a disposable ledger; source records and actual user notes are untouched.
    original=workspace_api.CASES
    try:
        with tempfile.TemporaryDirectory() as temp:
            workspace_api.CASES=Path(temp)/'cases.sqlite'
            rid=first['records'][0]['id']
            workspace_api.save_case(dict(record_id=rid,status='needs_document',note='Evidence check'))
            assert workspace_api.case_for(rid)['note']=='Evidence check'
            workspace_api.save_case(dict(record_id=rid,status='in_progress',note='Second event'))
            with closing(sqlite3.connect(workspace_api.CASES)) as db:assert db.execute('SELECT count(*) FROM case_events').fetchone()[0]==2
            assert workspace_api.case_for(rid)['status']=='in_progress'
            try:workspace_api.save_case(dict(record_id=rid,status='legally_verified',note=''))
            except ValueError:pass
            else:raise AssertionError('Workflow incorrectly accepted legal verification')
    finally:workspace_api.CASES=original
    assert hashlib.sha256(database.read_bytes()).hexdigest()==before
    print('Property workspace verified: 24,884 source records, 178 separate municipal keys, 38 shared keys /31 records /41 source comparisons; bounded search, section preservation and append-only workflow isolation passed.')
if __name__=='__main__':main()
