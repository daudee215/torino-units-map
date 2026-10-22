"""Tile the AdE INSPIRE WFS (it returns nothing for large bboxes) and save one GML per tile.

Usage: python -I fetch_parcels.py <out_dir> <lat0> <lon0> <lat1> <lon1> [dlat] [dlon]
"""
import sys
import time
import urllib.request
from pathlib import Path

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
lat0, lon0, lat1, lon1 = map(float, sys.argv[2:6])
dlat = float(sys.argv[6]) if len(sys.argv) > 6 else 0.004
dlon = float(sys.argv[7]) if len(sys.argv) > 7 else 0.007

BASE = ("https://wfs.cartografia.agenziaentrate.gov.it/inspire/wfs/owfs01.php"
        "?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=CP:CadastralParcel&BBOX=")

i = 0
lat = lat0
while lat < lat1 - 1e-9:
    lon = lon0
    while lon < lon1 - 1e-9:
        bb = ",".join(f"{v:.5f}".rstrip("0").rstrip(".") for v in (lat, lon, min(lat + dlat, lat1), min(lon + dlon, lon1)))  # server rejects some trailing zeros
        f = out / f"tile_{i:03d}.gml"
        if not f.exists() or f.stat().st_size < 2000:
            for attempt in range(3):
                try:
                    data = urllib.request.urlopen(BASE + bb, timeout=180).read()
                    break
                except Exception as e:  # noqa: BLE001
                    print("retry", bb, e)
                    time.sleep(5)
            f.write_bytes(data)
        n = f.read_bytes().count(b"<CP:CadastralParcel ")
        print(i, bb, n, flush=True)
        if n == 0:
            print("  WARNING empty tile", bb)
        i += 1
        lon += dlon
    lat += dlat
