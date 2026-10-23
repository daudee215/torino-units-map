"""Retrieve the official Torino municipal parcel ZIP from the regional bulk archive.
The region is 1.5 GB; HTTP ranges download only the 450 MB Torino province entry.
Raw archives stay ignored. No guessing municipal filenames or extracting paths.
"""
import io,json,struct,zipfile,zlib,hashlib
from datetime import datetime,timezone
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
URL='https://wfs.cartografia.agenziaentrate.gov.it/inspire/wfs/GetDataset.php?dataset=PIEMONTE.zip'
class Remote(io.RawIOBase):
 def __init__(self):
  r=requests.get(URL,headers={'Range':'bytes=0-0'},timeout=45);r.raise_for_status()
  assert r.status_code==206
  self.size=int(r.headers['Content-Range'].split('/')[-1]);self.pos=0;self.modified=r.headers.get('Last-Modified')
 def seekable(self):return True
 def seek(self,n,whence=0):self.pos=n if whence==0 else self.pos+n if whence==1 else self.size+n;return self.pos
 def tell(self):return self.pos
 def read(self,n=-1):
  n=self.size-self.pos if n<0 else min(n,self.size-self.pos)
  if n<=0:return b''
  r=requests.get(URL,headers={'Range':f'bytes={self.pos}-{self.pos+n-1}'},timeout=90);r.raise_for_status();assert r.status_code==206
  assert len(r.content)==n
  self.pos+=n;return r.content

def main():
 folder=ROOT/'_raw/city-parcels';folder.mkdir(exist_ok=True)
 province=folder/'TO.zip'
 if not province.exists():
  remote=Remote();archive=zipfile.ZipFile(remote);entry=archive.getinfo('TO.zip')
  remote.seek(entry.header_offset);header=remote.read(30);name_len,extra_len=struct.unpack('<HH',header[26:30]);start=entry.header_offset+30+name_len+extra_len
  response=requests.get(URL,headers={'Range':f'bytes={start}-{start+entry.compress_size-1}'},stream=True,timeout=(15,90));response.raise_for_status();assert response.status_code==206
  decoder=zlib.decompressobj(-15);crc=0;size=0
  with province.with_suffix('.partial').open('wb') as out:
   for chunk in response.iter_content(4*1024**2):
    block=decoder.decompress(chunk);out.write(block);crc=zlib.crc32(block,crc);size+=len(block)
    print(f'Province archive: {size//1024**2} MiB',flush=True)
   block=decoder.flush();out.write(block);crc=zlib.crc32(block,crc);size+=len(block)
  assert size==entry.file_size and crc==entry.CRC
  province.with_suffix('.partial').replace(province)
  (folder/'source.json').write_text(json.dumps(dict(url=URL,province_entry='TO.zip',retrieved=datetime.now(timezone.utc).isoformat(),regional_modified=remote.modified,license='CC BY 4.0',attribution='Agenzia delle Entrate',documentation='https://www.agenziaentrate.gov.it/portale/download-massivo-cartografia-catastale')),encoding='utf-8')
 with zipfile.ZipFile(province) as archive:
  names=archive.namelist();(folder/'province-entries.json').write_text(json.dumps(names),encoding='utf-8')
  selected=[n for n in names if Path(n).stem.upper()=='L219_TORINO' and n.lower().endswith('.zip')]
  print('Torino candidate entries:',selected,flush=True)
  if len(selected)!=1:
   print('Inspect province-entries.json before selecting an entry');return
  target=folder/'L219.zip';target.write_bytes(archive.read(selected[0]))
 with zipfile.ZipFile(target) as archive:
  for name in archive.namelist():
   if Path(name).suffix.lower()=='.gml':
    data=archive.read(name);(folder/Path(name).name).write_bytes(data);print(name,len(data),hashlib.sha256(data).hexdigest(),flush=True)
if __name__=='__main__':main()
