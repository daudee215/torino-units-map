"""Separate, local citywide source catalogue. Never rewrites the reviewed pilot.

Cartographic references, APE identities, asset-group inventory observations and
spatial/address candidates retain their distinct grain and provenance.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import csv, hashlib, json, re, sqlite3
from lxml import etree
from shapely.geometry import Polygon, Point, mapping
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree
from pyproj import Transformer
from build_bdtre_evidence import geometry
from build_address_evidence import address_key
from build_property_registry import ident, member, numeric, interior

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/city'
NS={'gml':'http://www.opengis.net/gml/3.2','CP':'http://mapserver.gis.umn.edu/mapserver'}
APE_SOURCE='https://www.dati.gov.it/view-dataset/dataset_id/dettaglio-attestato-di-prestazione-energetica-ape-sezione-dati-generali'
BDTRE_SOURCE='https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:da9b12ba-866a-4f0f-8704-5b7b753e4f15'
CIVIC_SOURCE='http://geoportale.comune.torino.it/geodati/civici_WGS84_EPSG4326_csv.csv'
def j(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def load(p):return json.loads(p.read_text(encoding='utf-8'))

def add_pilot_extension(db,parcel_by_fp,address_index):
 """Retain pilot-only historical/live identities without collapsing source aliases.

 Only source facts are read. Workflow, notes and relationship decisions are not
 copied into the city catalogue. Existing city records link to the pilot dossier.
 """
 existing={r[0] for r in db.execute('SELECT id FROM properties')};added=0
 pilot=sqlite3.connect((ROOT/'output/property-workspace/catalog.sqlite').as_uri()+'?mode=ro',uri=True)
 for rid,raw in pilot.execute("SELECT id,detail FROM records WHERE kind='ape_identity'"):
  if rid in existing:continue
  original=json.loads(raw);certs=[]
  for c in original['certificates']:
   cert=dict(id=c['id'],source_record_id=c.get('source_record_id'),submitted=c.get('submitted'),expires=c.get('expires'),active_source_flag=c.get('active'),status=c.get('status'),address=c.get('address'),civic=c.get('civic'),floor=c.get('floor'),heated_area_m2=c.get('heated_area_m2'),interiors=[],object_scope=c.get('object_scope'),source_url=c.get('source') or APE_SOURCE)
   cert['address_candidates']=address_index.get(address_key(cert['address'],cert['civic']),[]);certs.append(cert)
  certs.sort(key=lambda c:(c['submitted'] or '',c['id']),reverse=True)
  p={k:original[k] for k in ['id','members','scope','identity_complete','title','address']}
  p.update(kind='property',source_scope='pilot_live_source_extension',certificates=certs,municipal_refs=original['municipal_refs'],current_entrance_confirmed=False,parcels=sorted({m[2]+'/'+m[3] for m in original['members'] if m[0]=='L219'}),pilot_record_available=True,address_scope='attested object',address_candidates=certs[0]['address_candidates'] if certs else [],cartographic_candidates={fp:parcel_by_fp.get(fp,[]) for fp in {m[2]+'/'+m[3] for m in original['members'] if m[0]=='L219'}})
  db.execute('INSERT INTO properties VALUES(?,?,?)',(rid,p['title'],j(p)))
  db.executemany('INSERT INTO memberships VALUES(?,?)',[(rid,fp) for fp in p['parcels']])
  db.execute('INSERT INTO search VALUES(?,?,?,?)',(rid,'property',p['title'],p['address']+' '+p['title']+' '+' '.join('/'.join(m) for m in p['members'])))
  added+=1
 pilot.close();return added

def build():
 OUT.mkdir(exist_ok=True)
 target=OUT/'catalog.sqlite';temp=OUT/'catalog.build.sqlite'
 db=sqlite3.connect(temp)
 db.executescript('DROP TABLE IF EXISTS entities; DROP TABLE IF EXISTS spatial; DROP TABLE IF EXISTS properties; DROP TABLE IF EXISTS memberships; DROP TABLE IF EXISTS metadata; DROP TABLE IF EXISTS search; CREATE TABLE entities(n INTEGER PRIMARY KEY,id TEXT UNIQUE,kind TEXT,fp TEXT,title TEXT,detail TEXT,geo TEXT); CREATE VIRTUAL TABLE spatial USING rtree(n,x0,x1,y0,y1); CREATE TABLE properties(id TEXT PRIMARY KEY,title TEXT,detail TEXT); CREATE TABLE memberships(id TEXT,fp TEXT,PRIMARY KEY(id,fp)); CREATE INDEX membership_fp ON memberships(fp,id); CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT); CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,kind UNINDEXED,title,words,tokenize="unicode61 remove_diacritics 2");')
 counts=Counter();quality=Counter();parcel_shapes=[];parcel_rows=[];parcel_by_fp=defaultdict(list)
 to_m=Transformer.from_crs(4326,32632,always_xy=True).transform
 to_ll=Transformer.from_crs(32632,4326,always_xy=True).transform
 def entity(r,g):
  bounds=g.bounds;rid=r['id'];r['geometry']=None
  row=db.execute('INSERT INTO entities(id,kind,fp,title,detail,geo) VALUES(?,?,?,?,?,?)',(rid,r['kind'],r.get('fp'),r['title'],j(r),j(mapping(g)))).lastrowid
  db.execute('INSERT INTO spatial VALUES(?,?,?,?,?)',(row,bounds[0],bounds[2],bounds[1],bounds[3]))
  db.execute('INSERT INTO search VALUES(?,?,?,?)',(rid,r['kind'],r['title'],r['title']+' '+str(r.get('fp') or '')))
  counts[r['kind']]+=1
 print('Reading municipal boundary and BDTRE buildings…',flush=True)
 source_path=next((ROOT/'_raw/bdtre').glob('*.gpkg'))
 source=sqlite3.connect(source_path);source.row_factory=sqlite3.Row
 boundary=unary_union([geometry(r[0]) for r in source.execute("SELECT geometria FROM v_limi_comuni_piem WHERE comune_ist='001272' AND comune_bel='L219'")])
 assert boundary.is_valid and 120e6<boundary.area<140e6
 boundary_ll=transform(to_ll,boundary)
 (OUT/'boundary.geojson').write_text(j(mapping(boundary_ll)),encoding='utf-8')
 parcel_path=next((ROOT/'_raw/city-parcels').glob('*_ple.gml'))
 root_meta={};cartographic={}
 for event,e in etree.iterparse(str(parcel_path),events=('start','end'),tag=['{http://www.opengis.net/wfs/2.0}FeatureCollection','{'+NS['CP']+'}CadastralParcel']):
  if e.tag.endswith('FeatureCollection') and event=='start':root_meta=dict(e.attrib);continue
  if event!='end' or not e.tag.endswith('CadastralParcel'):continue
  ref=e.findtext('CP:NATIONALCADASTRALREFERENCE',namespaces=NS)
  m=re.fullmatch(r'L219_(\d{4})(.)(.)\.(.+)',ref or '')
  if not m:quality['unparsed_cartographic_reference']+=1;continue
  pieces=[]
  for p in e.findall('.//gml:Polygon',NS):
   def ring(text):
    values=list(map(float,text.split()));return list(zip(values[1::2],values[0::2]))
   ext=p.findtext('gml:exterior//gml:posList',namespaces=NS)
   holes=[ring(x.text) for x in p.findall('gml:interior//gml:posList',NS)]
   pieces.append(Polygon(ring(ext),holes))
  g=unary_union(pieces)
  if not g.is_valid:quality['invalid_parcel_geometry']+=1
  fp=str(int(m[1]))+'/'+m[4]
  r=dict(id='cadastre:'+ref,kind='parcel',title=fp,fp=fp,reference=ref,sheet=str(int(m[1])),parcel=m[4],allegato=m[2],sviluppo=m[3],source='Agenzia delle Entrate',source_url=load(ROOT/'_raw/city-parcels/source.json')['documentation'],source_timestamp=root_meta.get('timeStamp'),geometry_valid=g.is_valid,matching='sheet/parcel cartographic candidate; section correspondence unverified')
  if ref in cartographic:
   quality['repeated_parcel_reference_features']+=1
   previous,shape=cartographic[ref];cartographic[ref]=(previous,unary_union([shape,g]))
  else:cartographic[ref]=(r,g)
  e.clear()
  while e.getprevious() is not None:del e.getparent()[0]
 for r,g in cartographic.values():
  entity(r,g);parcel_shapes.append(transform(to_m,g));parcel_rows.append(r);parcel_by_fp[r['fp']].append(r['id'])
 del cartographic
 print('Parcel references:',counts['parcel'],flush=True)
 tree=STRtree(parcel_shapes)
 def spatial_candidates(g):
  # Preserve all intersections; never pick an arbitrary first parcel.
  ids=[int(i) for i in tree.query(g,predicate='intersects')]
  return [parcel_rows[i]['id'] for i in ids if parcel_rows[i]['parcel'].isdigit()]
 for row in source.execute('SELECT * FROM v_edifc'):
  r=dict(row);g=geometry(r['geometria'])
  if g.is_empty or not boundary.intersects(g):quality['building_outside_boundary']+=1;continue
  ll=transform(to_ll,g.simplify(.25,preserve_topology=True))
  entity(dict(id='bdtre:2026:v_edifc:'+str(r['id']),kind='building',title=r['edifc_nome'] or 'BDTRE '+str(r['id']),source_url=BDTRE_SOURCE,package_table_id=r['id'],use=r['edifc_uso'],source_updated=r['data_agg'],source_acquired=r['data_acq'],geometry_valid=g.is_valid,parcel_candidates=spatial_candidates(g.representative_point()),parcel_match_method='building representative point intersects parcel; candidate only',height_m=None,lod='2D footprint; no roof model'),ll)
 source.close()
 address_index=defaultdict(list)
 civic_path=ROOT/'_raw/civics/civici_WGS84_EPSG4326_csv.csv'
 with civic_path.open(encoding='utf-8-sig',newline='') as stream:
  seen=set()
  for r in csv.DictReader(stream,delimiter=';'):
   rid='civic:'+r['COD_CIVICO']
   if rid in seen:quality['duplicate_civic_id_rows']+=1;continue
   seen.add(rid)
   try:x,y=[float(r[k].replace(',','.')) for k in ['COORDINATA_X','COORDINATA_Y']]
   except ValueError:quality['invalid_civic_coordinates']+=1;continue
   point=Point(x,y);projected=transform(to_m,point)
   if not boundary.covers(projected):quality['civic_outside_boundary']+=1;continue
   candidates=spatial_candidates(projected)
   record=dict(id=rid,kind='entrance',title=r['VIA']+' '+r['CIVICO'],street=r['VIA'],civic=r['CIVICO'],district=r['CIRCOSCRIZIONE'],source_url=CIVIC_SOURCE,coordinates=[x,y],parcel_candidates=candidates,parcel_match_method='point intersects parcel; candidate only',current_property_access_confirmed=False)
   entity(record,point);address_index[address_key(r['VIA'],r['CIVICO'])].append(dict(id=rid,address=record['title'],coordinates=[x,y]))
 print('Buildings / civics:',counts['building'],counts['entrance'],flush=True)
 grouped=defaultdict(list);bulk_path=ROOT/'_raw/ape/bulk/general.csv'
 with bulk_path.open(encoding='cp1252',errors='replace',newline='') as stream:
  for r in csv.DictReader(stream,delimiter=';'):
   if (r.get('codice_comune_catastale') or '').strip().upper()=='L219':
    r={k:(v or '') for k,v in r.items() if k is not None};grouped[r['id_certificato']].append(r);counts['ape_source_rows']+=1
 properties={};exact_members=defaultdict(set)
 for cid,rows in grouped.items():
  r=rows[0];members=sorted({tuple(member(x['codice_comune_catastale'],x['sezione'],x['foglio'],x['particella'],x['subalterno'])) for x in rows})
  obj=r.get('oggetto_ape') or '';scope='whole_building' if 'Intero' in obj else 'group' if 'Gruppo' in obj else 'cadastral_property'
  known=bool(members and all(m[0] and m[2] and m[3] and m[4].isdigit() for m in members))
  pid=ident('property:',[scope,members if known else 'bulk:'+cid])
  p=properties.setdefault(pid,dict(id=pid,kind='property',members=members,scope=scope,certificates=[],municipal_refs=[],identity_complete=known,current_entrance_confirmed=False))
  cert=dict(id='bulk:'+cid,source_record_id=cid,submitted=r['data_invio_file'],expires=r['data_scadenza'],active_source_flag=r['flg_attivo'],address=r['desc_indirizzo'],civic=r['num_civico'],floor=r['piano'] or None,heated_area_m2=numeric(r['sup_riscaldata']),interiors=sorted({x['interno'] for x in rows if x['interno']}),object_scope=r['oggetto_ape'],source_url=APE_SOURCE)
  cert['address_candidates']=address_index.get(address_key(cert['address'],cert['civic']),[])
  p['certificates'].append(cert)
  for m in members:exact_members[m].add(pid)
 counts['ape_certificate_ids']=len(grouped);counts['ape_identities']=len(properties)
 del grouped
 inventory=load(ROOT/'output/investigation/municipal-inventory.json')
 for r in inventory['torino_records']:
  if r['identity_status']!='reported_key':quality['municipal_incomplete_rows']+=1;continue
  m=tuple(r['member']);ids=exact_members.get(m)
  if not ids:
   pid='municipal-key:'+hashlib.sha256('/'.join(m).encode()).hexdigest()[:24]
   properties.setdefault(pid,dict(id=pid,kind='property',members=[m],scope='reported_cadastral_reference',certificates=[],municipal_refs=[],identity_complete=True,current_entrance_confirmed=False));ids=[pid]
  for pid in ids:properties[pid]['municipal_refs'].append(r)
 pilot=sqlite3.connect((ROOT/'output/property-workspace/catalog.sqlite').as_uri()+'?mode=ro',uri=True)
 pilot_ids={r[0] for r in pilot.execute('SELECT id FROM records')};pilot.close()
 for p in properties.values():
  p['certificates'].sort(key=lambda c:(c['submitted'] or '',c['id']),reverse=True)
  preferred=p['certificates'][0] if p['certificates'] else None
  p['address']=(' '.join([preferred['address'] or '',preferred['civic'] or '']).strip() if preferred else p['municipal_refs'][0]['asset_primary_address'])
  p['address_candidates']=preferred['address_candidates'] if preferred else []
  p['title']=' + '.join('/'.join(m[2:]) for m in p['members'])
  p['parcels']=sorted({m[2]+'/'+m[3] for m in p['members']})
  p['pilot_record_available']=p['id'] in pilot_ids
  p['cartographic_candidates']={fp:parcel_by_fp.get(fp,[]) for fp in p['parcels']}
  p['address_scope']='attested object' if preferred else 'municipal asset group'
  quality['properties_with_address_candidates']+=bool(p['address_candidates'])
  quality['properties_with_unique_address_candidate']+=len(p['address_candidates'])==1
  quality['properties_with_cartographic_candidates']+=any(p['cartographic_candidates'].values())
  counts['municipal_only_identities']+=not bool(p['certificates'])
  db.execute('INSERT INTO properties VALUES(?,?,?)',(p['id'],p['title'],j(p)))
  db.executemany('INSERT INTO memberships VALUES(?,?)',[(p['id'],fp) for fp in p['parcels']])
  db.execute('INSERT INTO search VALUES(?,?,?,?)',(p['id'],'property',p['title'],p['address']+' '+p['title']+' '+' '.join('/'.join(m) for m in p['members'])))
 counts['bulk_ape_identities']=counts['ape_identities']
 counts['pilot_additional_ape_identities']=add_pilot_extension(db,parcel_by_fp,address_index)
 counts['ape_identities']+=counts['pilot_additional_ape_identities']
 counts['property_source_identities']=db.execute('SELECT count(*) FROM properties').fetchone()[0]
 summary=dict(version='2.5.0-dev.1',local_only=True,built=datetime.now(timezone.utc).isoformat(),municipality='L219',istat='001272',counts=dict(counts),quality=dict(quality),boundary_area_km2=round(boundary.area/1e6,3),bounds=list(boundary_ll.bounds),cadastre=root_meta,parcel_source=load(ROOT/'_raw/city-parcels/source.json'),ape_source=load(ROOT/'_raw/ape/bulk/general-source.json'),bdtre_source=BDTRE_SOURCE,civic_source=CIVIC_SOURCE,apartment_census=False,current_entrance_truth='unknown',pilot_preserved=True,limitations=['Source editions differ. Municipal boundary is BDTRE 2026; parcels are the September 2026 bulk snapshot.','Municipal asset inventory is April 2023, asset-group addresses are not unit entrances.','APE records do not cover all properties; certificate scope and renewals remain distinct.','Address/geometry links are candidates; cadastral section aliases are not merged.','City catalogue does not replace or duplicate the pilot relationship-review ledger.'])
 dates=db.execute("select min(json_extract(j.value,'$.submitted')),max(json_extract(j.value,'$.submitted')) from properties,json_each(properties.detail,'$.certificates') j").fetchone()
 summary['ape_submission_range']=list(dates)
 summary['limitations'].append('Regional bulk APE certificate count excludes pilot live-source certificates. Pilot-only identities supplement the city catalogue; overlapping source aliases remain in the pilot dossier.')
 summary['quality']['properties_with_address_candidates']=db.execute("select count(*) from properties where json_array_length(detail,'$.address_candidates')>0").fetchone()[0]
 summary['quality']['properties_with_unique_address_candidate']=db.execute("select count(*) from properties where json_array_length(detail,'$.address_candidates')=1").fetchone()[0]
 summary['quality']['properties_with_cartographic_candidates']=db.execute("select count(distinct p.id) from properties p,json_each(p.detail,'$.cartographic_candidates') a where json_array_length(a.value)>0").fetchone()[0]
 summary['quality']['incomplete_property_identities']=db.execute("select count(*) from properties where json_extract(detail,'$.identity_complete')=0").fetchone()[0]
 summary['quality']['pilot_identity_links']=db.execute("select count(*) from properties where json_extract(detail,'$.pilot_record_available')=1").fetchone()[0]
 db.execute('INSERT INTO metadata VALUES(?,?)',('summary',j(summary)));db.commit()
 assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 db.close();temp.replace(target)
 (OUT/'summary.json').write_text(j(summary),encoding='utf-8');print(j(summary),flush=True)
if __name__=='__main__':build()
