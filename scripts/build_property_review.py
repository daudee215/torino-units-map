"""Local, inspectable assessment of cohort evidence, unmatched keys and access chains."""
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import csv,json
import re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/property-review'

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def key(m):return '/'.join(m)
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),encoding='utf-8');temp.replace(path)
def rows_csv(path,rows,fields):
    with path.open('w',encoding='utf-8-sig',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
        for r in rows:
            values={f:r.get(f) for f in fields}
            for f,v in values.items():
                if isinstance(v,(list,dict)):v=json.dumps(v,ensure_ascii=False)
                if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')):v="'"+v
                values[f]=v
            writer.writerow(values)

def validate_identity_event(event):
    assert event['kind'] in {'subdivision','merger','renumbering'}
    before,after=event['before_members'],event['after_members']
    assert before and after and not set(map(tuple,before)) & set(map(tuple,after))
    assert all(len(m)==5 and m[0]=='L219' and all(str(v).isdigit() for v in m[2:]) for m in before+after)
    assert len(set(map(tuple,before)))==len(before) and len(set(map(tuple,after)))==len(after)
    if event['kind']=='subdivision':assert len(before)==1 and len(after)>1
    if event['kind']=='merger':assert len(before)>1 and len(after)==1
    if event['kind']=='renumbering':assert len(before)==len(after)==1
    assert event['manually_page_inspected'] is True and event['source'].startswith('https://') and event['page']>0
    assert len(event['sha256'])==64 and event['claims_it'] and event['claims_en']
    if event.get('effective_date'):datetime.strptime(event['effective_date'],'%Y-%m-%d')
    return event

def build():
    OUT.mkdir(exist_ok=True)
    summary=load(ROOT/'output/investigation/summary.json');sample={c['parcel']:c for c in summary['sample']}
    inventory=load(ROOT/'output/investigation/municipal-inventory.json')
    searches={r['parcel']:r for r in load(ROOT/'output/qa/property-document-searches.json')}
    extra=load(OUT/'document-observations.json');extra_by=defaultdict(list)
    event_path=OUT/'identity-events.json'
    identity_events=[validate_identity_event(e) for e in load(event_path)] if event_path.exists() else []
    for d in extra:extra_by[d['parcel']].append(d)
    inventory_rows=defaultdict(list)
    for fp,rs in inventory['pilot_records'].items():
        for r in rs:inventory_rows[fp].append(r)
    paths=sorted((ROOT/'data/registry/parcels').glob('*/*.json'))
    with ThreadPoolExecutor(max_workers=12) as pool:graphs=list(pool.map(load,paths))
    relevant=[g for g in graphs if g['properties'] or inventory_rows[g['parcel']] or g['parcel'] in sample]
    with ThreadPoolExecutor(max_workers=12) as pool:
        investigations=dict(pool.map(lambda g:(g['parcel'],load(ROOT/'output/investigation/parcels'/(g['parcel']+'.json'))),relevant))
    audit=[];cases=[];outputs=[];quality_by_id=defaultdict(set);event_ids=set();graph_count=0
    baseline_missing=set()
    for g in graphs:
        fp=g['parcel'];inv=inventory_rows[fp]
        if not g['properties'] and not inv and fp not in sample:continue
        investigation=investigations[fp]
        props=g['properties'];members={tuple(m):p['id'] for p in props for m in p['members']}
        triples=defaultdict(list)
        for m,pid in members.items():triples[(m[0],*m[2:])].append((m,pid))
        all_documents=investigation['documents']+extra_by[fp]
        query_path=ROOT/'_raw/ape/inventory'/('parcel-'+fp.replace('/','-')+'.json')
        if not query_path.exists():query_path=ROOT/'_raw/ape/review-phase'/query_path.name
        query=load(query_path) if query_path.exists() else None
        query_members={}
        if query and query['status'] in {'queried','possible_truncation'}:
            for record in query.get('records',[]):
                for cat in record.get('catasto') or []:
                    if cat.get('codiceComuneCatastale')!='L219':continue
                    m=tuple(str(cat.get(f) or '').strip() for f in ['codiceComuneCatastale','sezione','foglio','particella','subalterno'])
                    query_members[m]=record.get('uid')
        grouped=defaultdict(list)
        for r in inv:
            if r['identity_status']=='reported_key' and tuple(r['member']) not in members:grouped[tuple(r['member'])].append(r)
        parcel_audit=[]
        for m,rs in grouped.items():
            baseline_missing.add(m)
            document_ids=[d['id'] for d in all_documents if d.get('cadastre')!='CT' and m in map(tuple,d.get('members',[]))]
            aliases=triples.get((m[0],*m[2:]),[])
            if m in query_members:status='query_match_not_in_register'
            elif aliases:status='section_difference_requires_review'
            elif document_ids:status='additional_documented_reference'
            else:status='additional_reported_reference'
            row=dict(key=key(m),member=list(m),parcel=fp,status=status,source_rows=[r['id'] for r in rs],
                source_pages=sorted({r['page'] for r in rs}),asset_groups=sorted({r['asset_group_code'] for r in rs}),
                asset_primary_addresses=sorted({r['asset_primary_address'] for r in rs}),
                asset_descriptions=sorted({r['asset_description'] for r in rs}),source=rs[0]['source'],
                address_scope='asset_group_primary_address',document_ids=document_ids,
                section_alternatives=[dict(member=list(a),property_id=pid) for a,pid in aliases],
                query_status=query['status'] if query else 'not_queried',query_retrieved=query.get('retrieved') if query else None,
                query_returned_records=query.get('returned_records') if query else None,exact_query_match=m in query_members,
                current_identity_status='unknown',apartment_count=None,split_or_merger='not_established',
                next_evidence='current cadastral identity and a dated exact-key-to-entrance document')
            row['query_outcome']='not_queried' if not query else 'request_error' if query['status']=='error' else 'empty_response' if query.get('returned_records')==0 else 'exact_key_returned' if m in query_members else 'records_returned_without_exact_key'
            parcel_audit.append(row);audit.append(row)
        # Explicit nodes and edge evidence. Missing courtyard/staircase geometry is never fabricated.
        nodes={};edges=[]
        def node(id,kind,label,**rest):nodes.setdefault(id,dict(id=id,kind=kind,label=label,**rest));return id
        def edge(a,b,status,evidence,source=None):edges.append(dict(source_node=a,target_node=b,status=status,evidence=evidence,source_document=source,current_confirmed=False))
        for e in g['entrances']:
            eid=str(e['COD_CIVICO']);entry=node('entrance:'+eid,'civic_entrance',e['indirizzo'],entrance_id=eid)
            for route in investigation['entrances'].get(eid,{}).get('routes',[]):
                a=route['internal_access'];internal=node('internal:'+str(a['id']),'source_internal_access',str(a['id']),coordinates_32632=a['coordinates_32632'])
                edge(entry,internal,'candidate','BDTRE full-address correspondence; physical route unknown')
                for b in route['building_candidates']:
                    bid=node('building:'+b['building_id'],'building',b['building_id'])
                    edge(internal,bid,'candidate','Internal point / footprint proximity; not a staircase or served-property proof')
        facets={};histories={}
        for p in props:
            pid=node(p['id'],'property',key(p['members'][0]),members=p['members'])
            documents=[d for d in all_documents if d.get('cadastre')!='CT' and set(map(tuple,p['members'])) & set(map(tuple,d.get('members',[])))]
            historical=[d for d in documents if d.get('access_support')=='historical_access_description' or d.get('status')=='documented_historical_access']
            evidence=investigation['property_evidence'][pid]
            if historical:status='documented_historical_access'
            elif 'cadastral_section_alias_requires_review' in p['flags'] or any('conflict' in f for f in p['flags']):status='conflicting'
            elif documents:status='documented_address_only'
            elif evidence['entrance_candidates'] or evidence.get('additional_entrance_candidates'):status='candidate'
            else:status='unknown'
            quality_by_id[pid].add(status)
            facets[pid]=dict(status=status,document_ids=[d['id'] for d in documents],historical_access_documents=[d['id'] for d in historical],
                current_confirmed=False,physical_position='unknown',independent_current_ground_truth=False)
            # Only relationships active in the existing local investigation are used as candidates.
            active_count=evidence['entrance_candidates']
            source_links=[l for l in g['links'] if l['kind']=='property_entrance' and l['source']==pid]
            # Review-aware active edge IDs are computed below from the local ledger.
            active_links=[l for l in source_links if active_relationship(l)]
            assert len(active_links)==active_count
            for l in active_links:
                eid=l['target'].split(':',1)[1];target=node('entrance:'+eid,'civic_entrance',eid,entrance_id=eid)
                edge(target,pid,'candidate','Source-derived address proposal; operational review is not legal confirmation')
            for c in evidence.get('additional_entrance_candidates',[]):
                eid=c['entrance_id'];target=node('entrance:'+eid,'civic_entrance',c['address'],entrance_id=eid)
                edge(target,pid,'candidate','Exact full civic/address plus declared parcel within 25 m')
            for d in historical:
                hall=node('document-access:'+d['id'],'historical_passage','Vehicle entrance hall / androne carraio',geometry=None)
                edge(hall,pid,'documented_historical_access','Dated document explicitly reports this access to this cadastral key',dict(url=d['source'],page=d['page'],id=d['id']))
            events=[]
            for c in g['certificates']:
                if c['id'] not in p['certificates']:continue
                if c.get('submitted'):events.append(dict(kind='certificate_submission',date=c['submitted'],id=c['id'],meaning='certificate event; not creation or subdivision of a property',source=c.get('source')))
                if c.get('expires'):events.append(dict(kind='certificate_expiry',date=c['expires'],id=c['id'],meaning='certificate validity endpoint; not termination of the property',source=c.get('source')))
            for d in documents:
                date=d.get('observed_source_year') or str(d.get('document_year') or '') or None
                events.append(dict(kind='document_observation',date=date,source_label=d.get('source_label') or date,
                    id=d['id'],source=d['source'],page=d['page'],claims_it=d['claims_it'],claims_en=d['claims_en'],
                    pending_cadastral_update=d.get('cadastral_update_pending',False),planned_year=d.get('planned_year'),completed_change=False))
            for r in inv:
                if tuple(r['member']) in map(tuple,p['members']):events.append(dict(kind='inventory_observation',date='2023-04',id=r['id'],source=r['source'],page=r['page'],meaning='municipal asset reference; current validity unknown'))
            histories[pid]=sorted(events,key=lambda e:(e['date'] or '9999',e['kind'],e['id']))
            event_ids.update((pid,e['kind'],e['id']) for e in events)
        case=None
        if fp in sample:
            search=searches.get(fp);supporting=[d['id'] for d in all_documents]
            case=dict(sample[fp],research_status='source_discovery_completed' if search else 'source_discovery_pending',
                query=search['query'] if search else None,search_date=search.get('retrieved') if search else None,
                discovery_links=search['links'] if search else [],search_hits_are_evidence=False,
                inspected_document_ids=supporting,inventory_reference_count=len(inv),
                findings='dated_document_observations' if supporting else 'no_exact_key_access_document_acquired',
                documentary_entrance_validation='historical_evidence_only' if any(f['status']=='documented_historical_access' for f in facets.values()) else 'unresolved',
                current_access_truth='unknown',manual_site_review='pending',next_action='obtain dated exact-key access evidence and establish present validity')
            cases.append(case)
        data=dict(version='2.3.0-dev.1',local_only=True,parcel=fp,case=case,inventory_audit=parcel_audit,
            evidence_quality=facets,property_history=histories,additional_documents=extra_by[fp],
            access_graph=dict(nodes=list(nodes.values()),edges=edges,missing_steps=['courtyard/passage alignment','staircase identity','physical unit location'],
                surveyed_route=False),
            identity_change_relations=[e for e in identity_events if any('/'.join(m[2:4])==fp for m in e['before_members']+e['after_members'])],identity_change_warning='No subdivision, merger or renumbering is established by address similarity or certificate dates.')
        reference_history=defaultdict(list)
        for d in all_documents:
            if d.get('cadastre')=='CT':continue
            for m in d.get('members',[]):
                if '/'.join(m[2:4])!=fp or tuple(m) in members:continue
                reference_history[key(m)].append(dict(kind='document_observation',date=d.get('observed_source_year') or str(d.get('document_year') or '') or None,
                    source_label=d.get('source_label') or str(d.get('document_year') or ''),id=d['id'],source=d['source'],page=d['page'],
                    claims_it=d['claims_it'],claims_en=d['claims_en'],pending_cadastral_update=d.get('cadastral_update_pending',False),
                    planned_year=d.get('planned_year'),completed_change=False))
        data['documentary_key_history']=dict(reference_history)
        if fp=='1175/643':data['identity_questions']=[dict(members=[['L219','','1175','643','113'],['L219','','1175','643','114']],status='relationship_unknown',reason='Separate source references; no document establishes a renumbering or merger.')]
        outputs.append(data);graph_count+=bool(edges)
    assert len(baseline_missing)==178 and len(cases)==30 and len(searches)==30
    with ThreadPoolExecutor(max_workers=12) as pool:list(pool.map(lambda d:write(OUT/'parcels'/(d['parcel']+'.json'),d),outputs))
    precedence=['conflicting','documented_historical_access','documented_address_only','candidate','unknown']
    quality=Counter(next(k for k in precedence if k in values) for values in quality_by_id.values())
    quality={k:quality[k] for k in ['documented_historical_access','documented_address_only','candidate','conflicting','unknown']}
    assert len(quality_by_id)==load(ROOT/'data/registry/summary.json')['counts']['properties']
    result=dict(version='2.3.0-dev.1',local_only=True,built=datetime.now(timezone.utc).isoformat(),
        quality_counts=quality,quality_denominator=sum(quality.values()),unit='property/group identities in the acquired register',
        inventory_audit_counts=dict(Counter(r['status'] for r in audit)),inventory_audit_total=len(audit),cohort=cases,
        inventory_audit=audit,
        cohort_size=30,source_discovery_completed=len(searches),additional_inspected_observations=len(extra),
        historical_events=len(event_ids),parcels_with_access_graph=graph_count,confirmed_subdivisions_mergers=len(identity_events),
        independent_current_truth_pairs=0,accuracy=None,precision=None,recall=None,
        accuracy_reason='No independently confirmed current property-to-entrance ground truth; the purposive sample cannot establish district-wide accuracy.',
        additional_queries=sum(1 for _ in (ROOT/'_raw/ape/review-phase').glob('parcel-*.json')),
        additional_query_errors=sum(load(p)['status']=='error' for p in (ROOT/'_raw/ape/review-phase').glob('parcel-*.json')))
    write(OUT/'summary.json',result);write(OUT/'inventory-audit.json',audit)
    rows_csv(OUT/'inventory-audit.csv',audit,['key','parcel','status','source_pages','asset_primary_addresses','query_status','exact_query_match','document_ids','current_identity_status','next_evidence'])
    rows_csv(OUT/'cohort-review.csv',cases,['parcel','building_id','stratum','research_status','inspected_document_ids','inventory_reference_count','findings','documentary_entrance_validation','current_access_truth','next_action'])
    print(json.dumps({k:v for k,v in result.items() if k not in {'cohort','inventory_audit'}},ensure_ascii=False))

REVIEWS={}
def active_relationship(link):
    review=REVIEWS.get(link['id'],{})
    today=datetime.now(timezone.utc).astimezone(__import__('zoneinfo').ZoneInfo('Europe/Rome')).date().isoformat()
    return review.get('decision')!='rejected' and (not review.get('valid_from') or review['valid_from']<=today) and (not review.get('valid_to') or review['valid_to']>today)

if __name__=='__main__':
    import sqlite3
    with sqlite3.connect(ROOT/'output/registry/properties.sqlite') as db:
        for rid,decision,start,end in db.execute('SELECT relationship_id,decision,valid_from,valid_to FROM review_events ORDER BY id'):
            REVIEWS[rid]=dict(decision=decision,valid_from=start,valid_to=end)
    build()
