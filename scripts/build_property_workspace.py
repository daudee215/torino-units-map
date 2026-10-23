"""Build a local searchable record catalogue, preserving source identities and grain."""
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,re,sqlite3
from build_address_evidence import street_signature
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/property-workspace'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def key(m):return '/'.join(m)
def j(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))

def build():
    OUT.mkdir(exist_ok=True)
    inventory=load(ROOT/'output/investigation/municipal-inventory.json')
    by_key=defaultdict(list)
    for rows in inventory['pilot_records'].values():
        for r in rows:
            if r['identity_status']=='reported_key':by_key[tuple(r['member'])].append(r)
    audit={r['key']:r for r in load(ROOT/'output/property-review/inventory-audit.json')}
    review_summary=load(ROOT/'output/property-review/summary.json')
    paths=sorted((ROOT/'data/registry/parcels').glob('*/*.json'))
    with ThreadPoolExecutor(max_workers=12) as pool:graphs=list(pool.map(load,paths))
    relevant=[g for g in graphs if g['properties'] or g['parcel'] in inventory['pilot_records']]
    def read_review(g):
        path=ROOT/'output/property-review/parcels'/(g['parcel']+'.json')
        return g['parcel'],load(path) if path.exists() else None
    with ThreadPoolExecutor(max_workers=12) as pool:reviews=dict(pool.map(read_review,relevant))
    with ThreadPoolExecutor(max_workers=12) as pool:
        investigations=dict(pool.map(lambda g:(g['parcel'],load(ROOT/'output/investigation/parcels'/(g['parcel']+'.json'))),relevant))
    records={};record_parcels=defaultdict(set);matched_keys=set();comparisons=[]
    def comparison(p,r):
        source_address=' '.join(str(p.get(k) or '') for k in ['address','civic']).strip()
        address_agreement=street_signature(source_address)==street_signature(r['asset_primary_address'])
        return dict(key=key(r['member']),property_id=p['id'],municipal_row_id=r['id'],
            municipal_source=r['source'],page=r['page'],source_year='2023-04',
            ape_reported_address=source_address,municipal_primary_address=r['asset_primary_address'],
            address_scope='asset_group_primary_address',full_address_words_agree=address_agreement,
            apartment_access_confirmation=False,ape_floor=p.get('floor'),municipal_floor=None,
            ape_heated_area_m2=p.get('heated_area_m2'),ape_area_scope=p['scope'],
            municipal_m2=r['numeric_consistency']['consistency_m2'],municipal_rooms=r['numeric_consistency']['consistency_rooms'],municipal_m3=r['numeric_consistency']['consistency_m3'],
            area_comparison='different_measurement_definitions',area_difference_m2=None,
            municipal_asset_description=r['asset_description'],municipal_unit_use=None,
            ape_residential=p.get('residential'),same_unit_use_established=False)
    for g in relevant:
        fp=g['parcel'];review=reviews.get(fp);prop_ids={p['id'] for p in g['properties']}
        for p in g['properties']:
            refs=[r for m in p['members'] for r in by_key.get(tuple(m),[])]
            for r in refs:matched_keys.add(tuple(r['member']))
            compare=[comparison(p,r) for r in refs]
            comparisons.extend(compare)
            record_parcels[p['id']].add(fp)
            if p['id'] in records:continue  # Cross-parcel groups are one source identity.
            certs=[c for c in g['certificates'] if c['id'] in p['certificates']]
            facet=review['evidence_quality'].get(p['id']) if review else None
            linked=[l for l in g['links'] if l['source']==p['id'] and l['kind'] in {'property_entrance','property_building','property_alias'}]
            inv_evidence=investigations[fp]['property_evidence'].get(p['id'],{})
            record=dict(id=p['id'],kind='ape_identity',members=p['members'],title=' + '.join('/'.join(m[2:]) for m in p['members']),
                address=' '.join(str(p.get(k) or '') for k in ['address','civic']).strip(),address_scope='attested_object_reported_address',
                parcel=fp,scope=p['scope'],identity_complete=p['identity_complete'],flags=p['flags'],
                municipal_refs=refs,source_comparisons=compare,certificates=certs,
                floor=p.get('floor'),heated_area_m2=p.get('heated_area_m2'),residential=p.get('residential'),
                interiors=p.get('reported_interiors',[]),quality=facet['status'] if facet else 'unknown',
                historical_access_document_ids=facet.get('historical_access_documents',[]) if facet else [],
                history=review['property_history'].get(p['id'],[]) if review else [],
                connections=linked,additional_entrance_candidates=inv_evidence.get('additional_entrance_candidates',[]),
                case=review.get('case') if review else None,current_entrance_confirmed=False,
                origin='shared_key' if refs else 'ape',source_property_id=p['id'])
            records[p['id']]=record
        # Property geometry / entry context is retained separately from assignments.
        for m,rs in by_key.items():
            if '/'.join(m[2:4])!=fp or m in matched_keys:continue
            rid='municipal-key:'+hashlib.sha256(key(m).encode()).hexdigest()[:24]
            record_parcels[rid].add(fp)
            if rid in records:continue
            report=audit[key(m)]
            records[rid]=dict(id=rid,kind='municipal_reported_key',members=[list(m)],title='/'.join(m[2:]),
                address=rs[0]['asset_primary_address'],address_scope='asset_group_primary_address',parcel=fp,
                scope='reported_cadastral_reference',identity_complete=True,flags=['current_identity_unverified'],
                municipal_refs=rs,source_comparisons=[],certificates=[],floor=None,heated_area_m2=None,residential=None,interiors=[],
                quality='reported_key_unverified',history=(review['documentary_key_history'].get(key(m),[]) if review else [])+[
                    dict(kind='inventory_observation',date='2023-04',id=r['id'],source=r['source'],page=r['page']) for r in rs],
                historical_access_document_ids=[],
                connections=[],additional_entrance_candidates=[],case=review.get('case') if review else None,
                current_entrance_confirmed=False,origin='section_case' if report['section_alternatives'] else 'municipal_only',
                source_property_id=None,audit=report)
    # Full-key matches are deterministic; different sections and groups are never collapsed.
    assert len(matched_keys)==38
    assert len(records)==24706+178 and sum(r['kind']=='municipal_reported_key' for r in records.values())==178
    contexts={g['parcel']:dict(parcel=g['parcel'],buildings=g['buildings'],entrances=g['entrances']) for g in graphs}
    comparisons=list({(c['property_id'],c['municipal_row_id']):c for c in comparisons}.values())
    database=OUT/'catalog.sqlite';temp=OUT/'catalog-building.sqlite'
    if temp.exists():temp.unlink()
    with sqlite3.connect(temp) as db:
        db.executescript('CREATE TABLE records(id TEXT PRIMARY KEY, parcel TEXT, origin TEXT, kind TEXT, search TEXT, brief TEXT, detail TEXT); CREATE TABLE record_parcels(id TEXT,parcel TEXT,PRIMARY KEY(id,parcel)); CREATE TABLE parcels(parcel TEXT PRIMARY KEY,detail TEXT); CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT); CREATE INDEX record_origin ON records(origin); CREATE INDEX record_parcel_lookup ON record_parcels(parcel,id);')
        for rid,r in records.items():
            r['parcels']=sorted(record_parcels[rid])
            brief={k:r[k] for k in ['id','title','address','parcel','parcels','origin','kind','quality','scope']}
            brief['member_count']=len(r['members']);brief['first_key']='/'.join(r['members'][0][2:])
            brief['certificate_count']=len(r['certificates']);brief['municipal_reference_count']=len(r['municipal_refs'])
            hay=' '.join([r['title'],r['address'],*map(key,r['members']),*r['parcels']]).casefold()
            db.execute('INSERT INTO records VALUES(?,?,?,?,?,?,?)',(rid,r['parcel'],r['origin'],r['kind'],hay,j(brief),j(r)))
            db.executemany('INSERT INTO record_parcels VALUES(?,?)',[(rid,fp) for fp in r['parcels']])
        db.executemany('INSERT INTO parcels VALUES(?,?)',[(fp,j(c)) for fp,c in contexts.items()])
        meta=dict(version='2.4.0-dev.1',local_only=True,built=datetime.now(timezone.utc).isoformat(),records=len(records),
            ape_identities=24706,municipal_only_key_records=178,matched_municipal_keys=38,
            matched_record_ids=sum(r['origin']=='shared_key' for r in records.values()),section_cases=2,
            comparisons=len(comparisons),counts_by_origin=dict(Counter(r['origin'] for r in records.values())),
            record_count_is_not_property_count=True,section_review=dict(status='unresolved',
                manual='https://servizi.regione.piemonte.it/media/960/download',page=37,
                citizen_manual='https://servizi.regione.piemonte.it/media/508/download',citizen_page=6,
                finding='Official manuals define the section field and optional search parameter, but no equivalence of = and blank was established. Records remain separate.'),
            cohort=review_summary['cohort'])
        db.execute('INSERT INTO metadata VALUES(?,?)',('summary',j(meta)))
    db.close()
    temp.replace(database)
    (OUT/'summary.json').write_text(j(meta),encoding='utf-8')
    (OUT/'source-comparisons.json').write_text(j(comparisons),encoding='utf-8')
    print(j({k:v for k,v in meta.items() if k not in {'cohort','section_review'}}))

if __name__=='__main__':build()
