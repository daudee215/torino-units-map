"""Join official 2021 geography to 2023 census data and allocate within complete sections.

Run from repository root: py scripts/enrich_public_data.py
Raw sources are cached in _raw; no legacy SEZCENS identifier join is used.
Only sections >=99.5% inside the study rectangle receive a building allocation.
Allocated dwelling counts are continuous estimates, never synthetic apartment identities.
"""
import io
import json
import zipfile
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

import geopandas as gpd
import openpyxl
from shapely.geometry import Polygon, MultiPolygon, box

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = ROOT / "_raw"
BOUNDS = (7.640, 45.070, 7.668, 45.086)


def read(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def decode(g, meta):
    def ring(encoded):
        x = y = 0
        out = []
        for i in range(0, len(encoded), 2):
            x += encoded[i]
            y += encoded[i + 1]
            out.append((meta["lon0"] + x / meta["q"], meta["lat0"] + y / meta["q"]))
        return out
    polygons = [Polygon(ring(p[0]), [ring(r) for r in p[1:]]) for p in g]
    return MultiPolygon(polygons)


def main():
    meta, bld = read("meta"), read("edifici")
    z = zipfile.ZipFile(RAW / "istat/Comuni_2023.zip")
    book = openpyxl.load_workbook(io.BytesIO(z.read("Comuni_2023/Torino_2023_sezioni.xlsx")), read_only=True, data_only=True)
    values = iter(book[book.sheetnames[0]].values)
    columns = next(values)
    records = [dict(zip(columns, r)) for r in values]
    census = {int(r["SEZ21_ID"]): r for r in records}
    assert len(census) == len(records), "Duplicate census identifiers"
    geometry_file = RAW / "istat/R01_21.zip"
    geo = gpd.read_file(f"/vsizip/{geometry_file.as_posix()}/SHP/R01_21_WGS84.shp", where="PRO_COM = 1272")
    aoi = gpd.GeoSeries([box(*BOUNDS)], crs=4326).to_crs(geo.crs).iloc[0]
    sections = geo[geo.intersects(aoi)].copy()
    sections["coverage"] = sections.intersection(aoi).area / sections.area
    buildings = gpd.GeoDataFrame(
        [{k: v[i] for k, v in bld["p"].items()} for i in range(bld["n"])],
        geometry=[decode(g, meta) for g in bld["g"]], crs=4326,
    ).to_crs(geo.crs)
    anchors = buildings.copy()
    anchors.geometry = buildings.representative_point()
    joined = gpd.sjoin(anchors, sections[["SEZ21_ID", "coverage", "geometry"]], how="left", predicate="within")
    assert len(joined) == len(buildings), "Ambiguous building-to-section join"
    totals = joined.groupby("SEZ21_ID").sul_res_m2.sum()
    out = {}
    status = Counter()
    for _, r in joined.iterrows():
        sid = None if r.SEZ21_ID != r.SEZ21_ID else int(r.SEZ21_ID)
        c = census.get(sid)
        gfa = float(r.sul_res_m2 or 0)
        reason = "non_residential" if gfa <= 0 else "missing_census"
        unit = hh = occupied = vacant = None
        if gfa > 0 and c:
            if r.coverage < .995:
                reason = "partial_section"
            elif all(isinstance(c.get(k), (float, int)) and c[k] >= 0 for k in ["A2", "A3", "A8", "PF1"]):
                reason = "allocated_2023"
                weight = gfa / totals.loc[sid]
                unit, hh = c["A8"] * weight, c["PF1"] * weight
                occupied, vacant = c["A2"] * weight, c["A3"] * weight
        status[reason] += 1
        out[str(r.bld_id)] = dict(section_id=sid, status=reason, dwellings=unit, households=hh,
                                  occupied=occupied, vacant_or_nonresident=vacant)
    # Preserve exact counts per fully covered section (before any display rounding).
    for sid, group in joined.groupby("SEZ21_ID"):
        values = [out[str(v)] for v in group.bld_id]
        allocated = [v for v in values if v["status"] == "allocated_2023"]
        if allocated:
            assert abs(sum(v["dwellings"] for v in allocated) - census[int(sid)]["A8"]) < 1e-6
    features = []
    for _, r in sections.to_crs(4326).iterrows():
        sid = int(r.SEZ21_ID)
        c = census.get(sid, {})
        props = dict(section_id=str(sid), coverage=round(r.coverage, 5), population_2021=int(r.POP21),
                     households_2021=int(r.FAM21), dwellings_2021=int(r.ABI21))
        props.update({k: c.get(k) for k in ["P1", "PF1", "A2", "A3", "A5", "A8"]})
        features.append(dict(type="Feature", properties=props, geometry=r.geometry.__geo_interface__))
    timestamp = datetime.now(timezone.utc).isoformat()
    result = dict(retrieved_at=timestamp, municipality="001272", bounds=BOUNDS,
                  source="https://www.istat.it/notizia/dati-per-sezioni-di-censimento/",
                  data_url="https://esploradati.istat.it/databrowser/DWL/PERMPOP/SUBCOM/Comuni_2023.zip",
                  geometry_url="https://www.istat.it/storage/cartografia/basi_territoriali/2021/R01_21.zip",
                  reference_year=2023, geometry_year=2021, buildings=out,
                  audit=dict(sections=len(sections), full_sections=int((sections.coverage >= .995).sum()),
                             sections_with_2023=sum(int(v) in census for v in sections.SEZ21_ID),
                             buildings=len(out), allocation_status=dict(status),
                             city_totals={k:sum(r.get(k) or 0 for r in records if isinstance(r.get(k), (float,int))) for k in ["P1","PF1","A2","A3","A8"]}),
                  limitations=["Residential gross floor area is a proxy for dwelling allocation, not a unit survey.",
                               "Boundary sections are not allocated; missing values are not zero.",
                               "Original building use and floor counts may be incomplete or outdated.",
                               "2023 census counts use 2021 section geography; building locations use representative points."])
    (DATA / "census2023.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (DATA / "census2023.geojson").write_text(json.dumps(dict(type="FeatureCollection", features=features), separators=(",", ":")), encoding="utf-8")
    print(json.dumps(result["audit"], indent=2))


if __name__ == "__main__":
    main()
