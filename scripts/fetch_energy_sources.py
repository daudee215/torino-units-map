"""Cache official public files used by the pilot. No credentials or company data.
Run from any directory: py scripts/fetch_energy_sources.py
APE PDFs were retrieved through the official SIPEE citizen interface in Chrome;
they must be reviewed individually rather than fabricated or blindly counted.
"""
import json
from pathlib import Path
import requests

root = Path(__file__).resolve().parents[1]
sources = {
    "istat/R01_21.zip": "https://www.istat.it/storage/cartografia/basi_territoriali/2021/R01_21.zip",
    "istat/Comuni_2023.zip": "https://esploradati.istat.it/databrowser/DWL/PERMPOP/SUBCOM/Comuni_2023.zip",
    "arera/Dati_regione_2025.zip": "https://www.arera.it/fileadmin/allegati/dati/monitoraggioretail/Dati_regione_2025.zip",
}
for path, url in sources.items():
    target = root / "_raw" / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        r = requests.get(url, timeout=180)
        r.raise_for_status()
        target.write_bytes(r.content)
    print(path, target.stat().st_size)
for name, angle, aspect in [("south", 30, 0), ("east", 30, -90), ("west", 30, 90), ("flat", 0, 0)]:
    target = root / f"_raw/pvgis/{name}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        continue
    params = dict(lat=45.078, lon=7.654, peakpower=1, loss=14, angle=angle, aspect=aspect,
                  raddatabase="PVGIS-SARAH3", outputformat="json")
    r = requests.get("https://re.jrc.ec.europa.eu/api/v5_3/PVcalc", params=params, timeout=90)
    r.raise_for_status()
    target.write_text(json.dumps(dict(url=r.url, data=r.json())), encoding="utf-8")
layer = "https://services-eu1.arcgis.com/sawHMGY9o8rHlY2j/arcgis/rest/services/AC_Comuni_2025/FeatureServer/0"
target = root / "_raw/gse/areas2025.geojson"
target.parent.mkdir(parents=True, exist_ok=True)
if not target.exists():
    r = requests.get(layer + "/query", params=dict(f="geojson", where="1=1", geometry="7.640,45.070,7.668,45.086",
                     geometryType="esriGeometryEnvelope", inSR=4326, outSR=4326, spatialRel="esriSpatialRelIntersects",
                     outFields="*", returnGeometry="true"), timeout=60)
    r.raise_for_status()
    result = r.json()
    if "error" in result or "features" not in result or result.get("exceededTransferLimit"):
        raise RuntimeError("Incomplete or failed GSE query")
    target.write_text(json.dumps(result), encoding="utf-8")
