"""Validate actual address evidence, coordinates, provenance and candidate grain."""
import json
from pathlib import Path
from build_address_evidence import address_key,street_signature
from build_property_registry import interior

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'output/addresses/evidence.json').read_text(encoding='utf-8'))
assert data['local_only']
assert data['counts']['duplicated_municipal_ids']==0
assert data['counts']['duplicated_anncsu_access_ids']==0
assert len(data['entrances'])==data['counts']['pilot_rows']
assert interior('-')['normalized'] is None
assert interior('0')['raw']=='0' and interior('0')['normalized'] is None
assert interior('6')['normalized']=='6' and interior('A')['normalized']=='A'
assert interior('//')['normalized'] is None
assert interior('scala A')['kind']=='descriptor'
assert interior('10139')['kind']=='needs_review'
assert address_key('VIA TEST','17/C')!=address_key('VIA TEST','17')
assert address_key('VIA TEST','17 scala A')!=address_key('VIA TEST','17/A')
for eid,entrance in data['entrances'].items():
    municipal=entrance['municipal']
    if not municipal:continue
    assert 6<municipal['coordinates'][0]<9 and 44<municipal['coordinates'][1]<47
    assert 0<=municipal['displacement_m']<1, 'Unexpected change against inherited municipal coordinates'
    key=address_key(municipal['street'],municipal['civic'])
    candidates=entrance['anncsu_candidates']
    if entrance['status'] in {'unique_address_candidate','unique_street_order_candidate'}:assert len(candidates)==1
    for c in candidates:
        assert key[1]==address_key(c['street'],c['civic']+c['suffix'])[1]
        assert key[0]==address_key(c['street'],c['civic']+c['suffix'])[0] or (entrance['anncsu_match_method'].startswith('unique_full_street_words') and street_signature(municipal['street'])==street_signature(c['street']))
        assert c['street_id'] and c['access_id']
    for c in entrance.get('bdtre_candidates',[]):
        assert c['status']=='candidate' and c['distance_m']<=20
        assert key[1]==address_key(c['tp_str_nom'],c['civico_num']+(c['civico_sub'] or ''))[1]
        assert key[0]==address_key(c['tp_str_nom'],'')[0] or (c['match_method'].startswith('unique_full_street_words') and street_signature(municipal['street'])==street_signature(c['tp_str_nom']))
assert data['bdtre']['tables']['v_edifc']['distinct_uuid']==1, 'Recheck metadata key findings'
print('Address checks passed: coordinate decoding, suffix isolation, source keys, exact address candidates, BDTRE distances and interior placeholders.')
