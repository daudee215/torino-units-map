"""Read-only, bounded city catalogue API; geometry is loaded by viewport."""
from contextlib import closing
from pathlib import Path
from urllib.parse import urlparse,parse_qs,unquote
import json,math,re,sqlite3
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'output/city/catalog.sqlite'
def get_city(url):
 parsed=urlparse(url)
 if not parsed.path.startswith('/api/city'):return None
 if not DB.exists():return 503,dict(error='City catalogue has not been built')
 args=parse_qs(parsed.query);get=lambda k,d='':args.get(k,[d])[0]
 with closing(sqlite3.connect(DB.as_uri()+'?mode=ro',uri=True,timeout=10)) as db:
  if parsed.path=='/api/city':
   s=json.loads(db.execute("SELECT value FROM metadata WHERE key='summary'").fetchone()[0]);s['boundary']=json.loads((ROOT/'output/city/boundary.geojson').read_text(encoding='utf-8'));return 200,s
  if parsed.path=='/api/city/features':
   try:
    bounds=list(map(float,get('bbox').split(',')))
    if len(bounds)!=4 or not all(math.isfinite(x) for x in bounds):raise ValueError()
    x0,y0,x1,y1=bounds
    if not (7<x0<x1<8 and 44<y0<y1<46):raise ValueError()
   except ValueError:return 400,dict(error='Invalid bounding box')
   kind=get('kind','parcel')
   if kind not in {'parcel','building','entrance'}:return 400,dict(error='Invalid layer')
   # Broad extents use the municipality boundary, never a city-sized feature payload.
   if (x1-x0)*(y1-y0)>.0002:return 200,dict(type='FeatureCollection',features=[],zoom_required=True,truncated=False)
   rows=db.execute('SELECT e.id,e.kind,e.fp,e.title,e.geo FROM entities e JOIN spatial s ON e.n=s.n WHERE e.kind=? AND s.x0<=? AND s.x1>=? AND s.y0<=? AND s.y1>=? ORDER BY e.n LIMIT 1501',(kind,x1,x0,y1,y0)).fetchall()
   return 200,dict(type='FeatureCollection',truncated=len(rows)>1500,zoom_required=False,features=[dict(type='Feature',id=r[0],geometry=json.loads(r[4]),properties=dict(id=r[0],kind=r[1],fp=r[2],title=r[3])) for r in rows[:1500]])
  if parsed.path=='/api/city/search':
   kind=get('kind','property')
   if kind not in {'property','parcel','entrance','building'}:return 400,dict(error='Invalid search kind')
   q=get('q')[:180];fp=get('parcel')
   try:offset=max(0,min(1000000,int(get('offset','0'))))
   except ValueError:return 400,dict(error='Invalid offset')
   if fp and not re.fullmatch(r'\d+/[0-9A-Za-z]+',fp):return 400,dict(error='Invalid parcel')
   terms=re.findall(r'\w+',q,flags=re.UNICODE)
   where='kind=?';params=[kind]
   if terms:where+=' AND search MATCH ?';params.append(' AND '.join('"'+t+'"*' for t in terms))
   if fp:
    where+=' AND id IN (SELECT id FROM memberships WHERE fp=?)';params.append(fp)
   total=db.execute('SELECT count(*) FROM search WHERE '+where,params).fetchone()[0]
   rows=db.execute('SELECT id,kind,title,words FROM search WHERE '+where+' ORDER BY rowid LIMIT 50 OFFSET ?',params+[offset]).fetchall()
   return 200,dict(total=total,offset=offset,limit=50,records=[dict(id=r[0],kind=r[1],title=r[2],description=r[3][:220]) for r in rows])
  if parsed.path.startswith('/api/city/record/'):
   rid=unquote(parsed.path.split('/record/',1)[1])
   if len(rid)>250:return 400,dict(error='Invalid record')
   row=db.execute('SELECT detail FROM properties WHERE id=?',(rid,)).fetchone()
   if row:return 200,dict(record=json.loads(row[0]))
   row=db.execute('SELECT detail,geo,fp FROM entities WHERE id=?',(rid,)).fetchone()
   if not row:return 404,dict(error='Unknown city record')
   r=json.loads(row[0]);r['geometry']=json.loads(row[1])
   if row[2]:r['property_record_count']=db.execute('SELECT count(*) FROM memberships WHERE fp=?',(row[2],)).fetchone()[0]
   return 200,dict(record=r)
 return 404,dict(error='Unknown city endpoint')
