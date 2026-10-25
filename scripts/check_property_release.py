"""Inspect all new static source-only inputs, without raw acquisitions or databases."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,re
from check_city_publication import clean
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def check():
 counts={};identities=set();queue=set();issues=Counter();parcels=0
 for folder in ['refinement','property-investigation']:
  base=ROOT/'data'/folder;m=read(base/'manifest.json')
  assert m['public_source_only'] and not m['local_only'] and m['reviewed_for_publication']
  assert m['publication_version']=='2.15.0'
  paths=set()
  for f in m['files']:
   name=f['path'];assert name not in paths;paths.add(name)
   suffix=name.removeprefix('data/'+folder+'/');assert suffix!=name
   pattern=r'(?:summary|documents)\.json|(?:parcels|addresses)/[0-9a-f]{2}\.json\.gz' if folder=='refinement' else r'summary\.json|parcels/[0-9a-f]{2}\.json\.gz|queue/(?:incomplete_identity|multiple_or_changed|address_only|no_entrance|group_scope)/\d+\.json\.gz'
   assert re.fullmatch(pattern,suffix),name
   p=ROOT/name;assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink()
   raw=p.read_bytes();assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256'],name
   obj=read(p);clean(obj)
   if folder=='property-investigation' and suffix.startswith('parcels/'):
    for pid,parcel in obj.items():
     parcels+=1;assert hashlib.sha256(pid.encode()).hexdigest()[:2]==p.name[:2]
     assert len({r['id'] for r in parcel['properties']})==len(parcel['properties'])
     for r in parcel['properties']:
      identities.add(r['id']);assert not r['current_access_confirmed'] and 'geometry' not in r
      assert r['certificate_count']==len(r['observations'])
   elif folder=='property-investigation' and suffix.startswith('queue/'):
    reason=suffix.split('/')[1];assert obj['offset']==int(p.name.split('.')[0])*100
    issues[reason]+=len(obj['records'])
    for r in obj['records']:queue.add(r['id']);assert reason in r['issues'] and not r['current_access_confirmed']
   elif folder=='refinement' and suffix.startswith(('parcels/','addresses/')):
    for r in obj.values():assert not r['current_access_confirmed']
  assert paths|{'data/'+folder+'/manifest.json'}=={p.relative_to(ROOT).as_posix() for p in base.rglob('*') if p.is_file()}
  assert sum(f['bytes'] for f in m['files'])==m['bytes'];counts[folder]=len(paths)
 s=read(ROOT/'data/property-investigation/summary.json');assert len(identities)==220132 and len(identities|queue)==s['source_identities']==226951
 assert parcels==s['cartographic_parcels']==82434 and dict(issues)==s['issue_counts']
 docs=read(ROOT/'data/refinement/documents.json');assert len(docs['cases'])==9
 assert all(not c['current_access_confirmed'] and not c['section_confirmed'] and c['source_url'].startswith('https:') for c in docs['cases'])
 largest=s['largest_parcel'];p=read(ROOT/'data/property-investigation/parcels'/(hashlib.sha256(largest['id'].encode()).hexdigest()[:2]+'.json.gz'))[largest['id']];assert len(p['properties'])==738
 print(json.dumps(dict(public_source_only=True,parcels=parcels,mapped_identities=len(identities),retained_source_identities=len(identities|queue),documents=9,files=counts)))
if __name__=='__main__':check()
