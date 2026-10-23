"""City source-grain, spatial bounds, identifiers and read-only API checks."""
from contextlib import closing
import json,sqlite3
from urllib.parse import quote
from city_api import DB,get_city

def main():
 with closing(sqlite3.connect(DB)) as db:
  assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  s=json.loads(db.execute("SELECT value FROM metadata WHERE key='summary'").fetchone()[0])
  assert s['municipality']=='L219' and s['istat']=='001272' and not s['apartment_census']
  assert int(s['cadastre']['numberReturned'])-s['quality']['repeated_parcel_reference_features']==s['counts']['parcel']
  assert s['counts']['property_source_identities']==s['counts']['ape_identities']+s['counts']['municipal_only_identities']
  db.execute("ATTACH DATABASE 'output/property-workspace/catalog.sqlite' AS pilot")
  assert not db.execute('SELECT count(*) FROM pilot.records r LEFT JOIN properties p ON r.id=p.id WHERE p.id IS NULL').fetchone()[0]
  assert s['counts']['parcel']>80000 and s['counts']['building']>60000 and s['counts']['entrance']>100000
  assert db.execute('SELECT count(*) FROM entities').fetchone()[0]==db.execute('SELECT count(*) FROM spatial').fetchone()[0]
  assert not db.execute('SELECT count(*) FROM memberships m LEFT JOIN properties p ON p.id=m.id WHERE p.id IS NULL').fetchone()[0]
  for (raw,) in db.execute("SELECT detail FROM entities WHERE kind='parcel'"):
   p=json.loads(raw);assert p['reference'].startswith('L219_') and p['allegato'] is not None and p['sviluppo'] is not None
  for (raw,) in db.execute('SELECT detail FROM properties'):
   p=json.loads(raw);assert any(m[0]=='L219' for m in p['members']) and not p['current_entrance_confirmed']
   assert len({c['id'] for c in p['certificates']})==len(p['certificates'])
   assert set(p['parcels'])=={m[2]+'/'+m[3] for m in p['members'] if m[0]=='L219'}
   if not p['certificates']:assert p['address_scope']=='municipal asset group'
  rid=db.execute('SELECT id FROM properties LIMIT 1').fetchone()[0]
 assert get_city('/api/city')[0]==200
 status,res=get_city('/api/city/search?kind=property');assert status==200 and len(res['records'])<=50 and res['total']==s['counts']['property_source_identities']
 assert get_city('/api/city/search?kind=property&offset=bad')[0]==400
 assert get_city('/api/city/search?kind=invalid')[0]==400
 assert get_city('/api/city/search?parcel=bad')[0]==400
 assert get_city('/api/city/record/'+quote(rid,safe=''))[0]==200
 assert get_city('/api/city/record/not-present')[0]==404
 for bad in ['nan,45,7.7,45.1','7.7,45.1,7.6,45','0,0,1,1']:
  assert get_city('/api/city/features?bbox='+bad)[0]==400
 status,res=get_city('/api/city/features?bbox=7.58,45.01,7.77,45.14');assert status==200 and not res['features'] and res['zoom_required']
 for kind in ['parcel','building','entrance']:
  status,res=get_city('/api/city/features?kind='+kind+'&bbox=7.68,45.06,7.69,45.07');assert status==200 and 0<len(res['features'])<=1500
 for q in ['" OR 1=1 --','*','1175/643','VIA ROMA']:
  status,res=get_city('/api/city/search?kind=property&q='+quote(q));assert status==200 and len(res['records'])<=50
 print('City catalogue verified:',json.dumps(s['counts']),'; spatial viewport caps, exact source grain and read-only endpoints passed.')
if __name__=='__main__':main()
