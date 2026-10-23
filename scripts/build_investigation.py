"""Build local evidence facets, spatial alternatives and a stratified review cohort.

Proximity is never promoted to an accepted property relationship. The 30 cases
are a reproducible validation worklist, not a ground-truth accuracy sample.
"""
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sqlite3
import argparse
from build_property_registry import TODAY
from build_address_evidence import street_signature,norm
from pyproj import Transformer
from shapely.geometry import Polygon,MultiPolygon,Point
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/investigation'


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def shapes(name):
    data=load(ROOT/f'data/{name}.json');meta=load(ROOT/'data/meta.json')
    project=Transformer.from_crs(4326,32632,always_xy=True)
    def ring(values):
        x=y=0;points=[]
        for i in range(0,len(values),2):
            x+=values[i];y+=values[i+1]
            points.append(project.transform(meta['lon0']+x/meta['q'],meta['lat0']+y/meta['q']))
        return points
    attrs=[{k:v[i] for k,v in data['p'].items()} for i in range(data['n'])]
    geometry=[]
    for feature in data['g']:
        polygons=[Polygon(ring(p[0]),[ring(r) for r in p[1:]]) for p in feature]
        g=MultiPolygon(polygons)
        if not g.is_valid:g=g.buffer(0)
        geometry.append(g)
    return attrs,geometry


def build(public=False):
    destination=ROOT/'data/investigation' if public else OUT
    destination.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    addresses=load(ROOT/'output/addresses/evidence.json')
    la,lg=shapes('lotti');ba,bg=shapes('edifici')
    by_building={str(b['bld_id']):geometry for b,geometry in zip(ba,bg)}
    by_lot={a['foglio_particella']:geometry for a,geometry in zip(la,lg)}
    lt,bt=STRtree(lg),STRtree(bg)
    project=Transformer.from_crs(4326,32632,always_xy=True)
    spatial={};counts=Counter()
    address_lookup=defaultdict(list)
    for eid,a in addresses['entrances'].items():
        if not a['municipal']:continue
        point=Point(project.transform(*a['municipal']['coordinates']))
        address_lookup[(street_signature(a['municipal']['street']),norm(a['municipal']['civic']))].append(eid)
        parcel_candidates=[]
        for i in lt.query(point,predicate='dwithin',distance=25):
            distance=lg[i].distance(point)
            parcel_candidates.append(dict(parcel=la[i]['foglio_particella'],distance_m=round(distance,3),
                method='covers_point' if lg[i].covers(point) else 'within_25m_search',status='candidate'))
        parcel_candidates.sort(key=lambda x:(x['distance_m'],x['parcel']))
        containing=[c for c in parcel_candidates if c['method']=='covers_point']
        routes=[]
        external=[c for c in a.get('bdtre_candidates',[]) if c['table']=='v_acc_pc_civico_tp_str']
        internal=[c for c in a.get('bdtre_candidates',[]) if c['table']=='v_acc_int_civico_tp_str']
        for access in internal:
            p=Point(access['coordinates_32632']);buildings=[]
            for i in bt.query(p,predicate='dwithin',distance=3):
                buildings.append(dict(building_id=str(ba[i]['bld_id']),distance_m=round(bg[i].distance(p),3),
                    method='covers_internal_point' if bg[i].covers(p) else 'within_3m_search',status='candidate'))
            buildings.sort(key=lambda x:(x['distance_m'],x['building_id']))
            routes.append(dict(internal_access=dict(table=access['table'],id=access['id'],
                date=access['data_agg'],coordinates_32632=access['coordinates_32632']),
                external_access_candidates=[dict(table=c['table'],id=c['id']) for c in external],
                building_candidates=buildings,status='candidate',
                evidence=['same full source address (possibly reordered words)','internal access point compared with inherited GIS footprints'],
                unknown=['physical route between access points','which cadastral property is served']))
        flags=[]
        if len(containing)>1:flags.append('multiple_covering_parcels')
        if not containing:flags.append('no_covering_parcel')
        if len({b['building_id'] for r in routes for b in r['building_candidates']})>1:flags.append('multiple_route_buildings')
        spatial[eid]=dict(parcel_candidates=parcel_candidates,routes=routes,flags=flags)
        for flag in flags:counts[flag]+=1
        counts['entrances_with_internal_routes']+=bool(routes)
        counts['entrances_with_route_building_candidates']+=any(r['building_candidates'] for r in routes)
    paths=sorted((ROOT/'data/registry/parcels').glob('*/*.json'))
    with ThreadPoolExecutor(max_workers=8) as pool:graphs=list(pool.map(load,paths))
    documents_path=ROOT/'output/investigation/document-observations.json'
    documents=load(documents_path) if documents_path.exists() else []
    inventory_path=ROOT/'output/investigation/municipal-inventory.json'
    inventory=load(inventory_path) if inventory_path.exists() else dict(pilot_records={},counts={})
    reviews={}
    database=ROOT/'output/registry/properties.sqlite'
    if not public and database.exists():
        with sqlite3.connect(database) as db:
            for rid,decision,start,end in db.execute('SELECT relationship_id,decision,valid_from,valid_to FROM review_events ORDER BY id'):
                reviews[rid]=dict(decision=decision,valid_from=start,valid_to=end)
    def active(link):
        review=reviews.get(link['id'],{})
        if review.get('decision')=='rejected':return False
        if review.get('valid_from') and review['valid_from']>TODAY:return False
        if review.get('valid_to') and review['valid_to']<=TODAY:return False
        return True
    by_document=defaultdict(list)
    for d in documents:
        for fp in d.get('parcels',[]):by_document[fp].append(d)
    dossiers=[];building_cases=[]
    for g in graphs:
        fp=g['parcel'];property_evidence={};score=0;reasons=Counter()
        for p in g['properties']:
            source_links=[l for l in g['links'] if l['source']==p['id'] and l['kind']=='property_entrance']
            links=[l for l in source_links if active(l)]
            civic=str(p.get('civic') or '').strip();street=str(p.get('address') or '').strip()
            if civic:street=re.sub(r'\s+'+re.escape(civic)+r'$', '',street,flags=re.I)
            additional=[]
            excluded={l['target'].split(':',1)[1] for l in source_links}
            if civic:
                for eid in address_lookup.get((street_signature(street),norm(civic)),[]):
                    if eid in excluded:continue  # Never revive rejected/out-of-validity proposals.
                    support=[c for c in spatial[eid]['parcel_candidates'] if c['parcel']==fp]
                    if not support:continue
                    a=addresses['entrances'][eid]['municipal']
                    additional.append(dict(entrance_id=eid,address=a['street']+' '+a['civic'],
                        parcel_distance_m=support[0]['distance_m'],status='candidate',
                        method='full_street_words_and_civic_with_declared_parcel_within_25m',
                        property_parcel=fp,inherited_parcel_assignment_unchanged=True))
            issues=[]
            if not p['identity_complete']:issues.append('missing_identity')
            if not links:issues.append('no_entrance_candidate')
            if len(links)>1:issues.append('multiple_entrance_candidates')
            if 'cadastral_section_alias_requires_review' in p['flags']:issues.append('section_conflict')
            if p['scope']!='cadastral_property' or len(p['members'])>1:issues.append('grouped_object')
            reasons.update(issues)
            certificates=[c for c in g['certificates'] if c['id'] in p['certificates']]
            support=[d['id'] for d in by_document[fp] if d.get('cadastre')!='CT' and set(map(tuple,p['members'])) & set(map(tuple,d['members']))]
            inventory_support=[r['id'] for r in inventory['pilot_records'].get(fp,[]) if r['identity_status']=='reported_key' and tuple(r['member']) in set(map(tuple,p['members']))]
            property_evidence[p['id']]=dict(identity_basis='source_reported' if p['identity_complete'] else 'incomplete_source_identity',
                address_basis='address_candidate' if links else 'unknown',entrance_candidates=len(links),
                original_entrance_proposals=len(source_links),
                additional_entrance_candidates=additional,
                inspected_certificate_ids=[c['id'] for c in certificates if c.get('inspected_pdf')],
                source_lineages=['SIPEE']+(['municipal_property_documents'] if support else [])+(['municipal_inventory_2023'] if inventory_support else []),document_ids=support,
                municipal_inventory_ids=inventory_support,
                independent_source_count=None,
                issues=issues,physical_unit_location='unknown',legal_entrance_confirmation=False,
                next_evidence_needed=['dated document tying the exact cadastral key to an entrance',
                                      'confirm current validity and any split/merger'])
            counts['properties_with_additional_entrance_candidates']+=bool(additional)
        score=reasons['missing_identity']*20+reasons['no_entrance_candidate']*15+reasons['multiple_entrance_candidates']*8+reasons['section_conflict']*6
        streets={e['VIA'] for e in g['entrances']}
        # Words such as "int." and "bis" alone do not make a civic lettered.
        lettered=any(re.search(r'\d\s*/?\s*[A-Z]\b|\bSCALA\s+[A-Z]\b|\bINT\.?\s+\d*\s*/?\s*[A-Z]\b',str(e['CIVICO']).upper()) for e in g['entrances'])
        tags=[]
        if len(g['buildings'])==1 and len(g['entrances'])==1:tags.append('simple')
        if len(g['buildings'])==1 and len(g['entrances'])>1:tags.append('multiple_entrances')
        if len(g['buildings'])>1:tags.append('shared_parcel')
        if lettered:tags.append('lettered_civics')
        if len(streets)>1:tags.append('multiple_streets')
        if reasons['no_entrance_candidate'] or reasons['section_conflict']:tags.append('identity_ambiguity')
        dossier=dict(parcel=fp,priority_score=score,reasons=dict(reasons),property_evidence=property_evidence,
            entrances={str(e['COD_CIVICO']):spatial.get(str(e['COD_CIVICO']),{}) for e in g['entrances']},
            shared_access_context=dict(multiple_buildings_same_parcel=len(g['buildings'])>1,
                building_ids=[str(b['bld_id']) for b in g['buildings']],
                courtyard_status='historically_reported' if any(d['courtyard_support'] for d in by_document[fp]) else 'unknown',
                current_courtyard_status='unknown',
                warning='Shared parcel does not establish shared access or a courtyard; historical documents do not establish current arrangements.'),
            documents=by_document[fp],municipal_inventory=inventory['pilot_records'].get(fp,[]),sample_case=None)
        dossiers.append(dossier)
        for b in g['buildings']:
            building_cases.append(dict(building_id=str(b['bld_id']),parcel=fp,tags=tags,score=score,
                property_identities=len(g['properties']),entrances=len(g['entrances']),
                streets=sorted(streets),address=g['entrances'][0]['indirizzo'] if g['entrances'] else None,
                source_document_count=len(by_document[fp]),
                geometry_checks=dict(valid_footprint=bool(by_building[str(b['bld_id'])].is_valid),
                    footprint_fraction_on_inherited_parcel=round(by_building[str(b['bld_id'])].intersection(by_lot[fp]).area/max(0.01,by_building[str(b['bld_id'])].area),4))))
    # Five cases in each stratum; distinct parcel and building across the cohort.
    selected=[];used=set()
    for stratum in ['simple','multiple_entrances','shared_parcel','lettered_civics','multiple_streets','identity_ambiguity']:
        choices=sorted([b for b in building_cases if stratum in b['tags'] and b['property_identities']],
                       key=lambda b:(-bool(b['source_document_count']),b['parcel']!='1175/434',-b['score'],b['parcel'],b['building_id']))
        taken=0
        for b in choices:
            if b['parcel'] in used:continue
            selected.append(dict(b,stratum=stratum,validation_status='automated_checks_only',
                documentary_entrance_validation='pending',manual_site_review='pending'))
            used.add(b['parcel']);taken+=1
            if taken==5:break
    assert len(selected)==30 and len({c['building_id'] for c in selected})==30
    by_case={c['parcel']:c for c in selected}
    for d in dossiers:
        d['sample_case']=by_case.get(d['parcel'])
    attribution=[dict(provider='Città di Torino - www.comune.torino.it',licence='CC BY 4.0',
        licence_statement='https://www.comune.torino.it/note-legali',reviewed='2026-10-23',
        changes='Selected property references and factual summaries; PDF tables extracted and linked to source pages.'),
        dict(provider='Regione Piemonte — BDTRE 2026',licence='CC BY 4.0',source=addresses['bdtre']['source']),
        dict(provider='Città di Torino — municipal GIS',licence='CC BY 4.0',
             source='https://www.geoportale.piemonte.it/geonetwork/srv/api/records/c_l219:8987bd22-fea8-44e0-a900-7a6400032b30')]
    def write(d):
        if public:
            d.update(local_only=False,public_source_only=True,version='2.2.0',attribution=attribution)
            # Curated factual summaries only; never include raw PDF locations.
            d['documents']=[{k:v for k,v in doc.items() if k!='file'} for doc in d['documents']]
        path=destination/'parcels'/(d['parcel']+'.json');path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_suffix('.tmp')
        temporary.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8');temporary.replace(path)
    with ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(write,dossiers))
    queue=sorted([dict(parcel=d['parcel'],score=d['priority_score'],reasons=d['reasons']) for d in dossiers if d['priority_score']],key=lambda d:(-d['score'],d['parcel']))
    summary=dict(built=datetime.now(timezone.utc).isoformat(),local_only=not public,spatial_counts=dict(counts),
        municipal_inventory=inventory['counts'],
        sample=selected,queue=queue,document_observations=len(documents),
        documents_in_pilot=sum(bool(by_document[g['parcel']]) for g in graphs),
        limitations=['Candidate routes are not surveyed paths or confirmed property access.',
                      'The sample is purposive, not random or statistically representative.',
                      'No precision/recall estimate is possible without independently confirmed entrance truth.',
                      'Courtyard geometries are not generated.'])
    if public:
        summary.update(public_source_only=True,version='2.2.0',attribution=attribution,
            document_observations=len({d['id'] for dossier in dossiers for d in dossier['documents']}),
            publication_scope='Source-only pilot read models; no local reviews, raw documents or city-wide inventory rows.')
    (destination/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps(dict(spatial_counts=dict(counts),sample_cases=len(selected),queue_parcels=len(queue))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--public',action='store_true')
    build(public=parser.parse_args().public)
