"""Reproduce the authorized Pages artifact from hash-pinned public inputs only."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]

def inputs():
 m=json.loads((ROOT/'release-files.json').read_text(encoding='utf8'))
 assert m['version']=='2.13.0' and m['publication_authorized'] and m['public_source_only']
 assert len({r['path'] for r in m['files']})==len(m['files'])
 assert sum(r['bytes'] for r in m['files'])==m['bytes']<900*1024**2
 def verify(r):
  name=r['path'];p=ROOT/name
  assert not Path(name).is_absolute() and '..' not in Path(name).parts
  assert not set(Path(name).parts)&{'_raw','output','.git','dist','__pycache__','node_modules'}
  assert not name.endswith(('.pdf','.sqlite','.db','.gpkg','.pyc','.env'))
  assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(ROOT.resolve())
  raw=p.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'],name
  return r
 with ThreadPoolExecutor(max_workers=12) as pool:list(pool.map(verify,m['files']))
 return m

def build():
 m=inputs();dest=ROOT/'dist'
 assert dest.resolve()==ROOT.resolve()/'dist' and not dest.is_symlink()
 if dest.exists():shutil.rmtree(dest)
 dest.mkdir()
 def copy(r):
  p=dest/r['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r['path'],p)
 with ThreadPoolExecutor(max_workers=12) as pool:list(pool.map(copy,m['files']))
 (dest/'publication-manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
 print(f"Public 2.13.0: {len(m['files']):,} reviewed files / {m['bytes']:,} bytes",flush=True)

if __name__=='__main__':build()
