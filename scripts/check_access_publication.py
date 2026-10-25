"""Validate the complete reviewed 2.16 static access/navigation dataset."""
from pathlib import Path
from collections import Counter
import gzip,json,hashlib,re
from check_city_publication import clean
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def check():
 base=ROOT/'data/access-resolution';m=read(base/'manifest.json');s=read(base/'summary.json')
 assert m['publication_version']=='2.16.0' and m['public_source_only'] and m['reviewed_for_publication'] and not m['local_only']
 assert s['public_source_only'] and not s['local_only'] and s['source_identity_changes']==0 and not s['current_access_confirmed']
 seen=set();counts=Counter();unlocated=set();civicids=set();methods=Counter()
 for f in m['files']:
  name=f['path'];assert name not in seen;seen.add(name)
  suffix=name.removeprefix('data/access-resolution/');assert suffix!=name
  assert re.fullmatch(r'(?:summary|document-routes)\.json|unmapped-index\.json\.gz|(?:civics|parcels|unmapped)/[0-9a-f]{2}\.json\.gz',suffix),name
  p=ROOT/name;assert not p.is_symlink() and p.resolve().is_relative_to(base.resolve());raw=p.read_bytes()
  assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256'],name
  obj=read(p);clean(obj)
  if suffix.startswith('civics/'):
   for rid,r in obj.items():
    assert rid not in civicids;civicids.add(rid);assert not r['current_access_confirmed'] and 'geometry' not in r
    assert len(r['coordinates'])==2 and 7<r['coordinates'][0]<8 and 44<r['coordinates'][1]<46
    assert r['reported_roles']==sorted({a['role'] for a in r['access_observations']})
    for a in r['access_observations']:
     assert not a['current_access_confirmed'] and 0<=a['distance_m']<=20
     assert a['role'] in ['external_direct','vehicle_access','internal_access_record','unknown']
     assert 'xy' not in a and 'geometry' not in a and 'coordinates' not in a
    for related in r['related_parcels']:
     assert not related['current_access_confirmed'] and related['id'].startswith('cadastre:')
     assert set(related['methods'])<={'property_address','bdtre_point'} and related['property_source_count']>=len(related['property_examples'])
    counts['civics']+=1
  elif suffix.startswith('parcels/'):counts['parcels']+=len(obj)
  elif suffix.startswith('unmapped/'):
   for rid,r in obj.items():
    assert rid not in unlocated;unlocated.add(rid);assert r['original_memberships_unchanged'] and not r['current_access_confirmed']
    counts[r['reason']]+=1
    for candidate in r['reference_hypotheses']:
     for method in candidate['methods']:methods[method['method']]+=1
 assert counts['civics']==s['civics']==119108 and counts['parcels']==s['parcels']==82434 and len(unlocated)==6819
 assert all(counts[k]==v for k,v in s['reasons'].items())
 index=read(base/'unmapped-index.json.gz');assert {r['id'] for r in index}==unlocated and len(index)==6819
 assert len(read(base/'document-routes.json')['cases'])==22
 assert seen|{'data/access-resolution/manifest.json'}=={p.relative_to(ROOT).as_posix() for p in base.rglob('*') if p.is_file()}
 assert m['bytes']==sum(f['bytes'] for f in m['files'])
 print(json.dumps(dict(public_source_only=True,counts=dict(counts),unlocated=len(unlocated),hypothesis_links=dict(methods),files=len(seen),verified_current_access=0)))
if __name__=='__main__':check()
