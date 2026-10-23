"""Acquire the municipal BDTRE 2026 package advertised by the official grid.

Raw download and extraction remain ignored. Does not alter application geometry.
"""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
import requests

ROOT=Path(__file__).resolve().parents[1]
URL='https://www.datigeo-piem-download.it/static/regp01/BDTRE2026_VECTOR/BDTRE_DATABASE_GEOTOPOGRAFICO_2026-LIMI_COMUNI_10_GAIMSDWL-001272-EPSG32632-GPKG.zip'


def main():
    folder=ROOT/'_raw/bdtre';folder.mkdir(parents=True,exist_ok=True)
    target=folder/'torino-2026.zip'
    if not target.exists():
        temporary=target.with_suffix('.partial')
        with requests.get(URL,stream=True,timeout=(15,90)) as response:
            response.raise_for_status()
            with temporary.open('wb') as stream:
                total=0
                for chunk in response.iter_content(4*1024**2):
                    total+=len(chunk)
                    if total>2*1024**3:raise ValueError('Package exceeds 2 GiB acquisition bound')
                    stream.write(chunk)
        temporary.replace(target)
        (folder/'source.json').write_text(json.dumps(dict(url=URL,retrieved=datetime.now(timezone.utc).isoformat(),
            sha256=hashlib.sha256(target.read_bytes()).hexdigest(),licence='CC BY 4.0',
            catalogue='https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:da9b12ba-866a-4f0f-8704-5b7b753e4f15')),encoding='utf-8')
    with zipfile.ZipFile(target) as archive:
        for name in archive.namelist():
            # Only known data/document types; flatten names to prevent path traversal.
            if Path(name).suffix.lower() not in {'.gpkg','.txt'}:continue
            destination=folder/Path(name).name
            if not destination.exists():
                with archive.open(name) as source,destination.open('wb') as output:shutil.copyfileobj(source,output)
    print('BDTRE Torino package available locally; application geometry unchanged.')


if __name__=='__main__':main()
