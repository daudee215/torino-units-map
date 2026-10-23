"""Export a bounded, source-only static city atlas for GitHub Pages.

Local catalogues contain only source facts; nevertheless every exported record is
recursively checked. No workflow ledger, notes, raw downloads or SQLite is copied.
"""
from collections import defaultdict
from pathlib import Path
import gzip,hashlib,json,math,re,sqlite3,unicodedata
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/city'
FORBIDDEN={'review','review_events','note','review_note','owner','tenant','concessionario','codice_fiscale','raw_pdf','credentials','workflow','saved_at'}
def clean(value):
 if isinstance(value,dict):
  assert not FORBIDDEN.intersection(value),FORBIDDEN.intersection(value)
  for x in value.values():clean(x)
 elif isinstance(value,list):
  for x in value:clean(x)
def tokens(text):
 text=''.join(c for c in unicodedata.normalize('NFD',text.lower()) if not unicodedata.combining(c))
 return re.findall(r'[^\W_]+',text,flags=re.UNICODE)
def encode(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
def prepare():
 OUT.mkdir(exist_ok=True)
 # Reject unexpected prior artifacts rather than copying an arbitrary directory.
 assert not OUT.is_symlink()
 db=sqlite3.connect((ROOT/'output/city/catalog.sqlite').as_uri()+'?mode=ro',uri=True)
 manifest=[]
 def write(name,value):
  clean(value);raw=encode(value);data=gzip.compress(raw,compresslevel=9,mtime=0) if name.endswith('.gz') else raw
  target=OUT/name;target.parent.mkdir(exist_ok=True,parents=True);target.write_bytes(data)
  assert len(data)<25*1024**2,'Unexpected oversized static shard'
  manifest.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 summary=json.loads(db.execute("SELECT value FROM metadata WHERE key='summary'").fetchone()[0]);summary.update(version='2.5.1',local_only=False,public_source_only=True)
 summary['boundary']=json.loads((ROOT/'output/city/boundary.geojson').read_text(encoding='utf-8'))
 records=defaultdict(dict);briefs=defaultdict(list);postings=defaultdict(lambda:defaultdict(list));members=defaultdict(dict);ranges={};count=0
 def add(rid,kind,title,description,detail):
  nonlocal count
  count+=1;clean(detail)
  bucket=hashlib.sha256(rid.encode()).hexdigest()[:3];records[bucket][rid]=detail
  briefs[(count-1)//1000].append(dict(n=count,id=rid,kind=kind,title=title,description=description[:220]))
  if kind not in ranges:ranges[kind]=[count,count]
  else:ranges[kind][1]=count
  for term in set(tokens(title+' '+description)):
   prefix=term[:2];postings[prefix][term].append(count)
  return count
 print('Preparing source record shards and search postings…',flush=True)
 for rid,kind,title,raw,geo in db.execute('SELECT id,kind,title,detail,geo FROM entities ORDER BY n'):
  r=json.loads(raw);r['geometry']=json.loads(geo)
  if kind=='parcel':r['property_record_count']=db.execute('SELECT count(*) FROM memberships WHERE fp=?',(r['fp'],)).fetchone()[0]
  add(rid,kind,title,title+' '+str(r.get('fp') or ''),r)
 for rid,title,raw in db.execute('SELECT id,title,detail FROM properties ORDER BY rowid'):
  r=json.loads(raw);description=r['address']+' '+title+' '+' '.join('/'.join(m) for m in r['members'])
  numeric_id=add(rid,'property',title,description,r)
  for fp in r['parcels']:
   if re.fullmatch(r'\d+/[0-9A-Za-z]+',fp):members[fp.split('/')[0]].setdefault(fp,[]).append(numeric_id)
 for bucket,rows in records.items():write('records/'+bucket+'.json.gz',rows)
 del records
 for block,rows in briefs.items():write('briefs/'+str(block)+'.json.gz',rows)
 del briefs
 for prefix,words in postings.items():write('search/'+prefix.encode().hex()+'.json.gz',words)
 del postings
 for sheet,rows in members.items():write('members/'+sheet+'.json.gz',rows)
 del members
 print('Preparing spatial tiles…',flush=True)
 # Whole geometries retain source topology. A feature crossing cells appears in
 # each intersected tile and is deduplicated by its full source id in the client.
 step=.005;bounds=summary['bounds'];tile_count=0
 for x in range(math.floor(bounds[0]/step),math.ceil(bounds[2]/step)):
  for y in range(math.floor(bounds[1]/step),math.ceil(bounds[3]/step)):
   rows=db.execute('SELECT e.id,e.kind,e.fp,e.title,e.geo,s.x0,s.y0,s.x1,s.y1 FROM entities e JOIN spatial s ON e.n=s.n WHERE s.x0<=? AND s.x1>=? AND s.y0<=? AND s.y1>=?',((x+1)*step,x*step,(y+1)*step,y*step)).fetchall()
   if not rows:continue
   features=[dict(type='Feature',id=r[0],geometry=json.loads(r[4]),properties=dict(id=r[0],kind=r[1],fp=r[2],title=r[3],bbox=list(r[5:9]))) for r in rows]
   write(f'tiles/{x}_{y}.json.gz',features);tile_count+=1
 db.close()
 print('Preparing the source-only pilot workbench…',flush=True)
 with sqlite3.connect((ROOT/'output/property-workspace/catalog.sqlite').as_uri()+'?mode=ro',uri=True) as pilot:
  buckets=defaultdict(dict);brief_rows=[];contexts=defaultdict(dict)
  for rid,brief,detail,search in pilot.execute('SELECT id,brief,detail,search FROM records'):
   buckets[hashlib.sha256(rid.encode()).hexdigest()[:2]][rid]=json.loads(detail)
   brief_rows.append(dict(json.loads(brief),search=search))
  for bucket,rows in buckets.items():write('workbench/records/'+bucket+'.json.gz',rows)
  write('workbench/search.json.gz',brief_rows)
  for fp,detail in pilot.execute('SELECT parcel,detail FROM parcels'):contexts[fp.split('/')[0]][fp]=json.loads(detail)
  for sheet,rows in contexts.items():write('workbench/parcels/'+sheet+'.json.gz',rows)
  psummary=json.loads(pilot.execute("SELECT value FROM metadata WHERE key='summary'").fetchone()[0]);psummary.update(version='2.5.1',local_only=False,public_source_only=True)
  write('workbench/summary.json.gz',psummary)
 summary['static']=dict(record_count=count,ranges=ranges,brief_size=1000,tile_step=step,tile_count=tile_count,record_hash_prefix=3,search_prefixes=sorted(bytes.fromhex(p['path'].split('/')[1].split('.')[0]).decode() for p in manifest if p['path'].startswith('search/')),search_normalization='lowercase, NFD accents removed, Unicode alphanumeric token prefixes',gzip=True)
 from prepare_city_overview import overview
 overview(write,summary)
 write('summary.json',summary)
 size=sum(r['bytes'] for r in manifest);assert size<650*1024**2,'City publication exceeds reviewed 650 MiB city budget'
 (OUT/'manifest.json').write_bytes(encode(dict(version='2.5.1',public_source_only=True,bytes=size,records=count,files=manifest)))
 allowed={r['path'] for r in manifest}|{'manifest.json'}
 actual={p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()}
 assert actual==allowed,'Unexpected or stale city publication files'
 print(f'City publication: {count:,} source records, {len(manifest):,} shards, {size/1024**2:.1f} MiB; no local workflow data.',flush=True)
if __name__=='__main__':prepare()
