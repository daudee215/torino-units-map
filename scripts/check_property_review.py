"""Check grain, temporal claims and graph evidence on the actual local review."""
import json
from collections import Counter
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from build_property_review import validate_identity_event
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    s=read(ROOT/'output/property-review/summary.json')
    assert s['local_only'] and s['quality_denominator']==24706 and sum(s['quality_counts'].values())==24706
    assert s['accuracy'] is None and s['precision'] is None and s['recall'] is None and s['independent_current_truth_pairs']==0
    assert len(s['cohort'])==30 and len({c['parcel'] for c in s['cohort']})==30 and s['source_discovery_completed']==30
    assert all(not c['search_hits_are_evidence'] and c['current_access_truth']=='unknown' and c['manual_site_review']=='pending' for c in s['cohort'])
    audit=read(ROOT/'output/property-review/inventory-audit.json')
    assert len(audit)==len({r['key'] for r in audit})==178
    assert dict(Counter(r['status'] for r in audit))==s['inventory_audit_counts']
    assert all(r['apartment_count'] is None and r['current_identity_status']=='unknown' and r['split_or_merger']=='not_established' for r in audit)
    assert all(r['query_status']=='queried' and r['query_outcome']!='not_queried' for r in audit)
    assert all(not r['exact_query_match'] for r in audit)
    def check(path):
        d=read(path);assert d['local_only'] and d['access_graph']['surveyed_route'] is False
        nodes={n['id'] for n in d['access_graph']['nodes']}
        assert len(nodes)==len(d['access_graph']['nodes'])
        for edge in d['access_graph']['edges']:
            assert edge['source_node'] in nodes and edge['target_node'] in nodes and not edge['current_confirmed']
            if edge['status']=='documented_historical_access':assert edge['source_document']['page']>0
        assert all(not f['current_confirmed'] and not f['independent_current_ground_truth'] for f in d['evidence_quality'].values())
        for events in list(d['property_history'].values())+list(d['documentary_key_history'].values()):
            for e in events:
                if e.get('planned_year'):assert e['date'] is None and not e['completed_change']
                if e['kind']=='document_observation':assert not e['completed_change']
        for event in d['identity_change_relations']:validate_identity_event(event)
    paths=list((ROOT/'output/property-review/parcels').glob('*/*.json'))
    with ThreadPoolExecutor(max_workers=12) as pool:list(pool.map(check,paths))
    digione=read(ROOT/'output/property-review/parcels/1175/643.json')
    assert digione['identity_questions'][0]['status']=='relationship_unknown'
    beaumont=read(ROOT/'output/property-review/parcels/1221/149.json')
    events=beaumont['documentary_key_history']['L219//1221/149/2']
    assert any(e.get('planned_year')==2028 and e['date'] is None for e in events)
    assert any(e.get('planned_year')==2027 and e['date'] is None and e['pending_cadastral_update'] for e in events)
    # Guard against treating a certificate renewal/address similarity as a legal change.
    invalid=dict(kind='renumbering',before_members=[['L219','','1175','643','113']],after_members=[['L219','','1175','643','114']],manually_page_inspected=False,source='https://example.invalid',page=1,sha256='0'*64,claims_it='x',claims_en='x')
    try:validate_identity_event(invalid)
    except AssertionError:pass
    else:raise AssertionError('Unsupported identity change accepted')
    print(f'Property review verified: {len(paths)} parcel dossiers, 178 distinct keys, 30 researched cases; source dates, missing ground truth, graph references and change-evidence gates preserved.')
if __name__=='__main__':main()
