"""Produce an inspectable GIS package from the reviewed pilot sources.
APE geometries are explicitly labelled entrance proxies, never flat polygons.
"""
import json
import zipfile
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from enrich_public_data import decode

root = Path(__file__).resolve().parents[1]
data = root / "data"
out = root / "output/gis"
out.mkdir(parents=True, exist_ok=True)
meta = json.loads((data / "meta.json").read_text())
census = json.loads((data / "census2023.json").read_text())
ape = json.loads((data / "ape_units.json").read_text())


def layer(name):
    d = json.loads((data / f"{name}.json").read_text(encoding="utf-8"))
    rows = [{k: v[i] for k, v in d["p"].items()} for i in range(d["n"])]
    if name == "ingressi":
        geoms = [Point(meta["lon0"] + g[0] / meta["q"], meta["lat0"] + g[1] / meta["q"]) for g in d["g"]]
    else:
        geoms = [decode(g, meta) for g in d["g"]]
    return gpd.GeoDataFrame(rows, geometry=geoms, crs=4326)


buildings, lots, entrances = layer("edifici"), layer("lotti"), layer("ingressi")
for key in ["dwellings", "households", "status", "section_id"]:
    buildings[f"census2023_{key}"] = buildings.bld_id.map(lambda b: census["buildings"].get(str(b), {}).get(key))
buildings["parcel_key"] = buildings.apply(lambda r: None if pd.isna(r.foglio) else f"{int(r.foglio)}/{r.particella}", axis=1)
for idx, lot in lots.iterrows():
    b = buildings[(buildings.parcel_key == lot.foglio_particella) & (buildings.sul_res_m2 > 0)]
    complete = len(b) > 0 and (b.census2023_status == "allocated_2023").all()
    lots.loc[idx, "dwellings_2023_estimate"] = b.census2023_dwellings.sum() if complete else None
    lots.loc[idx, "households_2023_estimate"] = b.census2023_households.sum() if complete else None
    lots.loc[idx, "census2023_status"] = "allocated_2023" if complete else "incomplete_coverage" if len(b) else "non_residential"
grid = gpd.read_file(data / "grid_areas.geojson")
grid_matches = gpd.sjoin(entrances, grid[["COD_AC", "geometry"]], how="left", predicate="intersects")
codes = grid_matches.groupby("COD_CIVICO").COD_AC.apply(lambda x: ";".join(sorted(set(x.dropna()))))
entrances["grid_area_2025_indicative"] = entrances.COD_CIVICO.map(codes)
points = []
for certificate in ape["certificates"]:
    candidates = entrances[(entrances.fp == certificate["parcel"]) & (entrances.CIVICO.astype(str) == "17") & entrances.VIA.str.contains("CORDERO", case=False, na=False)]
    assert len(candidates) == 1, "Do not guess an APE entrance when ambiguous"
    row = {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in certificate.items()}
    row.update(unit_key=f"L219/{certificate['parcel']}/" + "+".join(certificate["subalterni"]),
               entrance_id=str(candidates.iloc[0].COD_CIVICO), location_scope="entrance_proxy_not_apartment_geometry",
               energy_kind="APE_standard_use_not_metered", geometry=candidates.geometry.iloc[0])
    points.append(row)
properties = gpd.GeoDataFrame(points, crs=4326)
gpkg = out / "torino_sandonato_energy.gpkg"
gpkg.unlink(missing_ok=True)
frames = {"parcels": lots, "buildings": buildings, "entrances": entrances,
          "census2021_geometry_2023_counts": gpd.read_file(data / "census2023.geojson"),
          "gse_grid_areas_2025": grid, "ape_entrance_proxies": properties}
for name, frame in frames.items():
    frame.to_crs(32632).to_file(gpkg, layer=name, driver="GPKG")
    frame.drop(columns="geometry").to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
package = data / "download/torino_sandonato_energy.zip"
with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.write(gpkg, gpkg.name)
    for name in frames:
        z.write(out / f"{name}.csv", f"{name}.csv")
    for name in ["ape_units.json", "demand_benchmark.json", "solar.json"]:
        z.write(data / name, name)
    z.write(root / "DATA_REVIEW.md", "DATA_REVIEW.md")
    z.writestr("README.txt", "San Donato / Campidoglio pilot. GeoPackage EPSG:32632.\n"
               "Apartment interior geometry and PODs are not available. APE point geometry is an entrance proxy only.\n"
               "Multi-subalterno APE totals are not duplicated per identifier. Census allocations and energy scenarios are not measurements.\n"
               "Read DATA_REVIEW.md for dates, source links, attribution and material limitations.\n")
print(f"Built {package.name}: {package.stat().st_size / 1e6:.2f} MB; six GIS layers and six CSV tables.")
