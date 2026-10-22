"""Torino study area: parcels + buildings + entrances + census households -> unit estimates and web layers.

Usage: python -I analysis.py <tiles_dir> <civici_csv> <edifici_shp> <sezioni_shp> <out_dir>
"""
import json
import re
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from lxml import etree
from shapely.geometry import Polygon, box

tiles_dir, civ_csv, edif_shp, sez_shp, out = map(Path, sys.argv[1:6])
out.mkdir(parents=True, exist_ok=True)
NS = {"gml": "http://www.opengis.net/gml/3.2", "CP": "http://mapserver.gis.umn.edu/mapserver"}
AOI_LL = (7.640, 45.070, 7.668, 45.086)
log = {}


def ring(pl):
    v = pl.split()
    return [(float(v[i + 1]), float(v[i])) for i in range(0, len(v), 2)]  # EPSG:6706 is lat,lon


# --- 1. parcels -------------------------------------------------------------
rows = []
for f in sorted(tiles_dir.glob("tile_*.gml")):
    for feat in etree.parse(str(f)).iterfind(".//CP:CadastralParcel", NS):
        ref = feat.findtext("CP:NATIONALCADASTRALREFERENCE", namespaces=NS)
        for poly in feat.iterfind(".//gml:Polygon", NS):
            ext = ring(poly.findtext("gml:exterior//gml:posList", namespaces=NS))
            holes = [ring(h.text) for h in poly.iterfind("gml:interior//gml:posList", NS)]
            rows.append({"ref": ref, "geometry": Polygon(ext, holes)})
raw = gpd.GeoDataFrame(rows, crs="EPSG:6706")
log["parcel_records_raw"] = len(raw)
raw["wkb"] = raw.geometry.to_wkb()
raw = raw.drop_duplicates(["ref", "wkb"]).drop(columns="wkb")
parcels = raw.dissolve(by="ref", as_index=False)
p = parcels["ref"].str.extract(
    r"^(?P<comune>[A-Z]\d{3})_(?P<foglio>\d{4})(?P<allegato>.)(?P<sviluppo>.)\.(?P<particella>.+)$")
parcels = pd.concat([parcels, p], axis=1).to_crs(32632)
parcels["foglio"] = parcels["foglio"].astype(int)
bad = ~parcels.is_valid
parcels.loc[bad, "geometry"] = parcels.loc[bad].buffer(0)
parcels["area_m2"] = parcels.area.round(1)
parcels["tipo"] = np.where(parcels["particella"].str.fullmatch(r"\d+"), "lotto",
                           parcels["particella"].str.extract(r"^([A-Z]+)")[0].str.lower())
log.update(parcels=len(parcels), invalid_fixed=int(bad.sum()),
           lotti=int((parcels.tipo == "lotto").sum()))
aoi = gpd.GeoSeries([box(*AOI_LL)], crs=4326).to_crs(32632).iloc[0]
lots = parcels[parcels.tipo == "lotto"].copy()

# --- 2. buildings (Carta Tecnica, EPSG:3003) -----------------------------------
aoi3003 = gpd.GeoSeries([aoi], crs=32632).to_crs(3003).iloc[0]
bld = gpd.read_file(edif_shp, bbox=aoi3003.bounds, encoding="cp1252").to_crs(32632)
# EPSG:3003 -> 32632 via the default Helmert leaves a systematic offset against the cadastre.
# Grid search on 1,500 footprints (min. building area on road parcels: 3.8% -> 0.95%) gives dx=-1.1, dy=+1.0 m.
# Civic numbers are already in the cadastral frame and are not shifted.
BLD_SHIFT = (-1.1, 1.0)
bld["geometry"] = bld.translate(*BLD_SHIFT)
log["building_shift_m"] = BLD_SHIFT
bld = bld[bld.intersects(aoi)].copy()
bld["geometry"] = bld.buffer(0)
bld = bld[~bld.is_empty]


def levels(s):
    """Above-ground levels from NUM_PIANI. '5+1' -> 6, '5+s' -> 5.5, '3/2' -> 2.5. Assumed legend."""
    if s is None or not str(s).strip() or str(s).strip() == "?":
        return np.nan
    s = str(s).strip().lower()
    if "/" in s:
        a = [float(x) for x in s.split("/") if x.isdigit()]
        return float(np.mean(a)) if a else np.nan
    m = re.match(r"^(\d+)(?:\+(\d+|s))?$", s)
    if not m:
        return np.nan
    return int(m[1]) + (0.5 if m[2] == "s" else int(m[2] or 0))


bld["livelli"] = bld["NUM_PIANI"].map(levels)
bld["impronta_m2"] = bld.area.round(1)
bld["residenziale"] = bld["CAT_USO"].fillna("").str.startswith("residenziale")
# residential GFA; generica only (balconies, external lifts etc. are also polygons in this layer)
bld["sul_res_m2"] = np.where(bld.residenziale & (bld.DESCRIZ == "generica"),
                             bld.impronta_m2 * bld.livelli.fillna(1), 0.0)
bld["bld_id"] = bld["CIT_AR"].astype(str)
log["buildings"] = len(bld)
log["buildings_residential"] = int(bld.residenziale.sum())
log["levels_unparsed"] = int(bld.livelli.isna().sum())

# alignment check: share of building footprint area falling inside some cadastral lot
inter = gpd.overlay(bld[["bld_id", "geometry"]], lots[["ref", "geometry"]], how="intersection", keep_geom_type=True)
inter["a"] = inter.area
log["bld_area_in_lots_pct"] = round(100 * inter["a"].sum() / bld.area.sum(), 1)
best = inter.sort_values("a", ascending=False).drop_duplicates("bld_id")
best = best.merge(bld[["bld_id", "impronta_m2"]], on="bld_id")
best["quota_in_lotto"] = (best["a"] / best["impronta_m2"]).round(2)
bld = bld.merge(best[["bld_id", "ref", "quota_in_lotto"]], on="bld_id", how="left")
bld = bld.merge(lots[["ref", "foglio", "particella"]], on="ref", how="left")

# --- 3. census sections: dasymetric allocation of households by residential GFA ----
sez = gpd.read_file(sez_shp).to_crs(32632)
sez = sez[sez.intersects(aoi)].copy()
sez["SEZCENS"] = sez["SEZCENS"].astype(int)
cent = bld.copy()
cent["geometry"] = bld.representative_point()
cent = gpd.sjoin(cent, sez[["SEZCENS", "NFAMIGL", "NRESID", "geometry"]], how="left", predicate="within")
bld["SEZCENS"] = cent["SEZCENS"].values
sec = bld.groupby("SEZCENS").agg(sul_res=("sul_res_m2", "sum"), n_res=("residenziale", "sum")).reset_index()
sec = sec.merge(sez[["SEZCENS", "NFAMIGL", "NRESID"]], on="SEZCENS", how="right")
sec["NFAMIGL"] = sec["NFAMIGL"].fillna(0)
sec["sul_per_famiglia"] = sec["sul_res"] / sec["NFAMIGL"].replace(0, np.nan)
ok = sec[(sec.NFAMIGL > 0) & (sec.sul_res > 0)]
log["sections"] = len(sec)
log["sections_with_households_and_gfa"] = len(ok)
log["households_total"] = int(sec.NFAMIGL.sum())
log["households_without_res_gfa"] = int(sec.loc[(sec.NFAMIGL > 0) & ~(sec.sul_res > 0), "NFAMIGL"].sum())
q = ok["sul_per_famiglia"].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(1)
log["gfa_per_household_m2_quantiles"] = q.to_dict()
log["gfa_vs_households_corr"] = round(float(np.corrcoef(ok.sul_res, ok.NFAMIGL)[0, 1]), 3)

# sections where m2-per-household is implausible: households sit in buildings coded non-residential,
# institutions, or the floor count is wrong. Allocation there is unreliable.
sec["affidabilita"] = np.where(sec.sul_per_famiglia.between(40, 250), "normale", "bassa")
log["sections_low_confidence"] = int(((sec.affidabilita == "bassa") & (sec.NFAMIGL > 0)).sum())
bld = bld.merge(sec[["SEZCENS", "sul_res", "NFAMIGL", "affidabilita"]], on="SEZCENS", how="left")
bld["famiglie_stimate"] = np.where(bld.sul_res > 0, bld.NFAMIGL * bld.sul_res_m2 / bld.sul_res, 0.0).round(1)
bld = bld.drop(columns=["sul_res", "NFAMIGL"])

# --- 4. entrances -> lot -> building ------------------------------------------
civ = pd.read_csv(civ_csv, sep=";", decimal=",", dtype={"CIVICO": str, "CAP": str})
civ = gpd.GeoDataFrame(civ, geometry=gpd.points_from_xy(civ.COORDINATA_X, civ.COORDINATA_Y), crs=32632)
civ = civ[civ.within(aoi)].copy()
civ["indirizzo"] = civ["VIA"].str.title() + " " + civ["CIVICO"]
j = gpd.sjoin(civ, lots[["ref", "geometry"]], how="left", predicate="within")
j = j[~j.index.duplicated()].drop(columns="index_right")
j["match_lotto"] = np.where(j.ref.notna(), "dentro", None)
miss = j.ref.isna()
near = gpd.sjoin_nearest(civ.loc[miss], lots[["ref", "geometry"]], how="left", max_distance=25, distance_col="d")
near = near[~near.index.duplicated()]
j.loc[miss, "ref"] = near["ref"]
j.loc[miss & j.ref.notna(), "match_lotto"] = "vicino<=25m"
j["match_lotto"] = j["match_lotto"].fillna("nessuno")
j = j.merge(lots[["ref", "foglio", "particella"]], on="ref", how="left")
j = gpd.GeoDataFrame(j, geometry="geometry", crs=32632)

# nearest residential-or-any main building, preferring buildings on the same lot
res_b = bld[bld.DESCRIZ == "generica"][["bld_id", "ref", "geometry"]].rename(columns={"ref": "ref_b"})
nb = gpd.sjoin_nearest(j[["COD_CIVICO", "ref", "geometry"]], res_b, how="left", max_distance=30, distance_col="d_bld")
nb["same_lot"] = nb.ref == nb.ref_b
nb = nb.sort_values(["COD_CIVICO", "same_lot", "d_bld"], ascending=[True, False, True]).drop_duplicates("COD_CIVICO")
# second pass: if nearest building isn't on the same lot, look for any building on the same lot within 30 m
alt = j[["COD_CIVICO", "ref", "geometry"]].merge(res_b, left_on="ref", right_on="ref_b", suffixes=("", "_b"))
alt["d_bld"] = alt.geometry.distance(gpd.GeoSeries(alt["geometry_b"], crs=32632))
alt = alt[alt.d_bld <= 30].sort_values("d_bld").drop_duplicates("COD_CIVICO")
nb = nb.set_index("COD_CIVICO")
alt = alt.set_index("COD_CIVICO")
use_alt = alt.index[~nb.loc[alt.index, "same_lot"].astype(bool)]
nb.loc[use_alt, "bld_id"] = alt.loc[use_alt, "bld_id"]
nb.loc[use_alt, "d_bld"] = alt.loc[use_alt, "d_bld"]
j = j.merge(nb[["bld_id", "d_bld"]], left_on="COD_CIVICO", right_index=True, how="left")
j["d_bld"] = j["d_bld"].round(1)

n_ingr_bld = j.groupby("bld_id").size().rename("n_ingressi")
bld = bld.merge(n_ingr_bld, left_on="bld_id", right_index=True, how="left")
bld["n_ingressi"] = bld["n_ingressi"].fillna(0).astype(int)
j = j.merge(bld[["bld_id", "famiglie_stimate", "n_ingressi", "livelli", "CAT_USO"]], on="bld_id", how="left")
j["famiglie_per_ingresso"] = (j.famiglie_stimate / j.n_ingressi.replace(0, np.nan)).round(1)
log["entrances"] = len(j)
log["entrance_lot_match"] = j.match_lotto.value_counts().to_dict()
log["entrances_with_building"] = int(j.bld_id.notna().sum())

# --- 5. parcel summary ---------------------------------------------------------
pb = bld[bld.ref.notna()].groupby("ref").agg(
    n_edifici=("bld_id", "size"),
    livelli_max=("livelli", "max"),
    sul_res_m2=("sul_res_m2", "sum"),
    famiglie_stimate=("famiglie_stimate", "sum"),
    uso_prevalente=("CAT_USO", lambda s: s.mode().iat[0] if len(s.mode()) else None),
    epoca=("EPOCA_COST", lambda s: s.mode().iat[0] if len(s.mode()) else None),
    affidabilita=("affidabilita", lambda s: "bassa" if (s == "bassa").any() else "normale"),
)
pi = j[j.ref.notna()].groupby("ref").agg(
    n_ingressi=("COD_CIVICO", "size"),
    civici=("indirizzo", lambda s: "; ".join(sorted(set(s)))),
)
lots = lots.merge(pb, left_on="ref", right_index=True, how="left").merge(pi, left_on="ref", right_index=True, how="left")
lots["n_ingressi"] = lots["n_ingressi"].fillna(0).astype(int)
lots["n_edifici"] = lots["n_edifici"].fillna(0).astype(int)
lots["famiglie_stimate"] = lots["famiglie_stimate"].fillna(0).round(0)
lots["sul_res_m2"] = lots["sul_res_m2"].fillna(0).round(0)
lots["foglio_particella"] = lots["foglio"].astype(str) + "/" + lots["particella"]
log["lots_with_entrances"] = int((lots.n_ingressi > 0).sum())
log["lots_with_res_buildings"] = int((lots.sul_res_m2 > 0).sum())
log["est_households_on_lots"] = int(lots.famiglie_stimate.sum())

# --- 6. write ------------------------------------------------------------------
gpkg = out / "torino_sandonato.gpkg"
for name, g in [("particelle", parcels), ("lotti_sintesi", lots), ("edifici", bld),
                ("ingressi_civici", j), ("sezioni_censimento", sez.merge(sec[["SEZCENS", "sul_res", "sul_per_famiglia", "affidabilita"]], on="SEZCENS"))]:
    g.to_file(gpkg, layer=name, driver="GPKG")

lots.drop(columns="geometry").sort_values(["foglio", "particella"]).to_csv(out / "lotti_sintesi.csv", index=False)
j.drop(columns="geometry").sort_values(["VIA", "CIVICO"]).to_csv(out / "ingressi_civici.csv", index=False)

# template for SISTER visure: one row per lot with residential buildings, priority by estimated households
tpl = lots[lots.sul_res_m2 > 0][["foglio", "particella", "civici", "n_ingressi", "famiglie_stimate", "affidabilita"]]
tpl = tpl.sort_values("famiglie_stimate", ascending=False)
tpl.to_csv(out / "visure_da_richiedere.csv", index=False)

# web layers, EPSG:4326, rounded
def gj(g, cols, nd=6, simplify=None):
    g = g[cols + ["geometry"]].to_crs(4326).copy()
    if simplify:
        g["geometry"] = g.simplify(simplify, preserve_topology=True)
    d = json.loads(g.to_json(drop_id=True))
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], nd), round(c[1], nd)]
    for ft in d["features"]:
        ft["geometry"]["coordinates"] = rnd(ft["geometry"]["coordinates"])
        ft["properties"] = {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in ft["properties"].items()}
    return d

web = {
    "lotti": gj(lots, ["foglio_particella", "area_m2", "n_edifici", "n_ingressi", "civici", "livelli_max",
                       "sul_res_m2", "famiglie_stimate", "uso_prevalente", "epoca", "affidabilita"]),
    "strade": gj(parcels[parcels.tipo != "lotto"], ["ref", "tipo"]),
    "edifici": gj(bld[bld.DESCRIZ == "generica"], ["bld_id", "CAT_USO", "NUM_PIANI", "livelli", "ALT_EDIFIC",
                                                   "EPOCA_COST", "impronta_m2", "sul_res_m2", "famiglie_stimate",
                                                   "n_ingressi", "foglio", "particella", "SEZCENS", "affidabilita"]),
    "ingressi": gj(j, ["COD_CIVICO", "indirizzo", "foglio", "particella", "match_lotto", "bld_id",
                       "famiglie_per_ingresso", "livelli"]),
    "sezioni": gj(sez.merge(sec[["SEZCENS", "sul_res"]], on="SEZCENS"),
                  ["SEZCENS", "NRESID", "NFAMIGL", "sul_res"], simplify=0.5),
    "_meta": {"sul_per_famiglia_mediana": float(q.loc[0.5])},
}
(out / "web_layers.json").write_text(json.dumps(web, separators=(",", ":"), ensure_ascii=False))
(out / "log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False, default=str))
print(json.dumps(log, indent=1, ensure_ascii=False, default=str))
