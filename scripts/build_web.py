"""Compact web layers: delta-encoded integer coordinates (1e-6 deg), columnar properties, one file per layer.

Usage: python -I build_web.py <gpkg> <out_dir>
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np

gpkg, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
Q = 1e6
LON0, LAT0 = 7.64, 45.07  # origin inside the study area keeps numbers short


def enc_ring(coords):
    a = np.round((np.asarray(coords)[:, :2] - [LON0, LAT0]) * Q).astype(np.int64)
    if len(a) > 1 and (a[0] == a[-1]).all():
        a = a[:-1]  # Leaflet closes rings itself
    d = np.vstack([a[:1], np.diff(a, axis=0)])
    return d.ravel().tolist()


def enc_geom(g):
    if g.geom_type == "Point":
        x, y = enc_ring([(g.x, g.y)])
        return [x, y]
    polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
    return [[enc_ring(p.exterior.coords)] + [enc_ring(r.coords) for r in p.interiors] for p in polys]


def clean(v):
    if v is None:
        return None
    if isinstance(v, (float, np.floating)):
        if np.isnan(v):
            return None
        return int(v) if float(v).is_integer() else round(float(v), 1)
    if isinstance(v, (np.integer,)):
        return int(v)
    return v


def layer(name, gdf, cols, simplify=None):
    g = gdf.to_crs(32632)
    if simplify:
        g["geometry"] = g.simplify(simplify, preserve_topology=True)
    g = g[~g.is_empty].to_crs(4326)
    data = {
        "n": len(g),
        "p": {c: [clean(v) for v in g[c].tolist()] for c in cols},
        "g": [enc_geom(geom) for geom in g.geometry],
    }
    s = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    (out / f"{name}.json").write_text(s, encoding="utf-8")
    return len(s)


lots = gpd.read_file(gpkg, layer="lotti_sintesi")
parcels = gpd.read_file(gpkg, layer="particelle")
bld = gpd.read_file(gpkg, layer="edifici")
ent = gpd.read_file(gpkg, layer="ingressi_civici")
sez = gpd.read_file(gpkg, layer="sezioni_censimento")

sizes = {
    "lotti": layer("lotti", lots, ["ref", "foglio", "particella", "foglio_particella", "area_m2", "n_edifici", "n_ingressi",
                                    "livelli_max", "sul_res_m2", "famiglie_stimate", "uso_prevalente", "epoca", "affidabilita"]),
    "strade": layer("strade", parcels[parcels.tipo != "lotto"], ["ref", "tipo"]),
    "edifici": layer("edifici", bld[bld.DESCRIZ == "generica"],
                     ["bld_id", "CAT_USO", "NUM_PIANI", "livelli", "ALT_EDIFIC", "EPOCA_COST", "VAL_STORIC", "impronta_m2",
                      "sul_res_m2", "famiglie_stimate", "n_ingressi", "foglio", "particella", "SEZCENS", "affidabilita"]),
    "ingressi": layer("ingressi", ent.assign(fp=ent.foglio.astype("Int64").astype(str) + "/" + ent.particella.astype(str)),
                      ["COD_CIVICO", "VIA", "CIVICO", "indirizzo", "CAP", "CIRCOSCRIZIONE", "fp", "match_lotto",
                       "bld_id", "famiglie_per_ingresso"]),
    "sezioni": layer("sezioni", sez, ["SEZCENS", "NRESID", "NFAMIGL", "sul_res", "affidabilita"], 0.5),
}
ok = sez[(sez.NFAMIGL > 0) & (sez.sul_res > 0)]
meta = {"lon0": LON0, "lat0": LAT0, "q": Q,
        "sul_per_famiglia_mediana": round(float(ok.sul_per_famiglia.median()), 1)}
(out / "meta.json").write_text(json.dumps(meta))
for k, v in sizes.items():
    print(f"{k:9s} {v/1e6:6.2f} MB")
print(f"total     {sum(sizes.values())/1e6:6.2f} MB")
