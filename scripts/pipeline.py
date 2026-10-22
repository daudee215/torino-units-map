"""Torino pilot: entrances (civici) -> cadastral parcels (foglio/particella) -> unit/POD template.

Usage: python -I pipeline.py <civici_csv> <parcels_gml> <out_dir>
"""
import re
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from lxml import etree
from shapely.geometry import Polygon

civ_csv, gml_path, out_dir = map(Path, sys.argv[1:4])
out_dir.mkdir(parents=True, exist_ok=True)

NS = {"gml": "http://www.opengis.net/gml/3.2", "CP": "http://mapserver.gis.umn.edu/mapserver"}
STREET = "VIA FELICE CORDERO DI PAMPARATO"

# --- parcels -----------------------------------------------------------------
rows = []
tree = etree.parse(str(gml_path))
for f in tree.iterfind(".//CP:CadastralParcel", NS):
    ref = f.findtext("CP:NATIONALCADASTRALREFERENCE", namespaces=NS)
    rings = f.findall(".//gml:Polygon", NS)
    for poly in rings:
        ext = poly.findtext("gml:exterior//gml:posList", namespaces=NS).split()
        # EPSG:6706 axis order is lat, lon
        coords = [(float(ext[i + 1]), float(ext[i])) for i in range(0, len(ext), 2)]
        holes = []
        for h in poly.iterfind("gml:interior//gml:posList", NS):
            v = h.text.split()
            holes.append([(float(v[i + 1]), float(v[i])) for i in range(0, len(v), 2)])
        rows.append({"ref": ref, "geometry": Polygon(coords, holes)})

parcels = gpd.GeoDataFrame(rows, crs="EPSG:6706").dissolve(by="ref", as_index=False)
# L219_122200.1 -> comune L219, foglio 1222, allegato 0, sviluppo 0, particella 1
m = parcels["ref"].str.extract(r"^(?P<comune>[A-Z]\d{3})_(?P<foglio>\d{4})(?P<allegato>.)(?P<sviluppo>.)\.(?P<particella>.+)$")
parcels = pd.concat([parcels, m], axis=1)
parcels["foglio"] = parcels["foglio"].astype(int)
parcels = parcels.to_crs(32632)
parcels["area_m2"] = parcels.area.round(1)
parcels["valid"] = parcels.is_valid
parcels.loc[~parcels.valid, "geometry"] = parcels.loc[~parcels.valid].buffer(0)

# --- entrances ---------------------------------------------------------------
civ = pd.read_csv(civ_csv, sep=";", decimal=",", dtype={"CIVICO": str, "CAP": str})
civ = gpd.GeoDataFrame(civ, geometry=gpd.points_from_xy(civ.COORDINATA_X, civ.COORDINATA_Y), crs=32632)
# clip to the WFS request bbox (road parcels extend far beyond it)
req = gpd.GeoSeries.from_xy([7.6507, 7.6574], [45.0757, 45.0808], crs=4326).to_crs(32632)
civ = civ.cx[req.x.min():req.x.max(), req.y.min():req.y.max()].copy()
# match only to real lots: road/water parcels have non-numeric particella (STRADA..., ACQUA...)
lots = parcels[parcels["particella"].str.fullmatch(r"\d+")]

def split_civico(s):
    m = re.match(r"^(\d+)\s*(bis|ter|quater)?\s*(?:/([A-Z]))?\s*(?:scala\s+(\w+))?\s*(.*)$", s.strip())
    if not m:
        return pd.Series([None, None, None, None, s])
    return pd.Series([int(m[1]), m[2], m[3], m[4], m[5] or None])

civ[["num", "bis", "lettera", "scala", "altro"]] = civ["CIVICO"].apply(split_civico)

# point-in-polygon; entrances sit on the street-side boundary, so fall back to nearest parcel within 15 m
j = gpd.sjoin(civ, lots[["ref", "foglio", "particella", "area_m2", "geometry"]], how="left", predicate="within")
j = j[~j.index.duplicated()]
miss = j["ref"].isna()
if miss.any():
    near = gpd.sjoin_nearest(
        civ.loc[miss], lots[["ref", "foglio", "particella", "area_m2", "geometry"]],
        how="left", max_distance=25, distance_col="dist_m",
    )
    near = near[~near.index.duplicated()]
    for c in ["ref", "foglio", "particella", "area_m2", "dist_m"]:
        j.loc[miss, c] = near[c]
j["match"] = "within"
j.loc[miss, "match"] = "nearest<=25m"
j.loc[j["ref"].isna(), "match"] = "none"
j = j.drop(columns=["index_right"], errors="ignore")
j["dist_m"] = j.get("dist_m", pd.Series(0, index=j.index)).fillna(0).round(1)

# --- outputs -----------------------------------------------------------------
gpkg = out_dir / "torino_cordero_pilot.gpkg"
parcels.to_file(gpkg, layer="particelle", driver="GPKG")
j.to_file(gpkg, layer="ingressi_civici", driver="GPKG")

street = j[j["VIA"] == STREET].sort_values(["num", "lettera"], na_position="first")
cols = ["COD_CIVICO", "VIA", "CIVICO", "num", "lettera", "scala", "foglio", "particella", "ref", "area_m2", "match", "dist_m"]
street[cols].to_csv(out_dir / "cordero_ingressi_particelle.csv", index=False)

# unit template: one row per entrance, to be expanded with SISTER visure (subalterni) and POD
tmpl = street[["COD_CIVICO", "VIA", "CIVICO", "foglio", "particella"]].copy()
for c in ["subalterno", "categoria", "interno", "piano", "consistenza", "pod", "fonte_sub", "fonte_pod"]:
    tmpl[c] = ""
tmpl.to_csv(out_dir / "unita_template.csv", index=False)

# per-parcel summary of entrances
summ = (
    j[j["ref"].notna()]
    .groupby(["foglio", "particella"])
    .agg(n_ingressi=("COD_CIVICO", "size"), civici=("CIVICO", lambda s: ", ".join(sorted(set(s)))),
         vie=("VIA", lambda s: "; ".join(sorted(set(s)))))
    .reset_index()
)
summ.to_csv(out_dir / "particelle_con_ingressi.csv", index=False)

print("parcels", len(parcels), "| invalid fixed", int((~parcels.valid).sum()))
print("entrances in bbox", len(j), "| match:", j["match"].value_counts().to_dict())
print(street[cols].to_string(index=False))
