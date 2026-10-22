"""Package reviewed public energy sources; raw PDFs stay outside served deliverables.
The certificate transcription intentionally excludes certifier names/contact details.
"""
import json
from pathlib import Path
import geopandas as gpd
from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[1]
data = ROOT / "data"
solar = {}
for name in ["south", "east", "west", "flat"]:
    raw = json.loads((ROOT / f"_raw/pvgis/{name}.json").read_text(encoding="utf-8"))
    d = raw["data"]
    solar[name] = dict(url=raw["url"], inputs=d["inputs"], totals=d["outputs"]["totals"]["fixed"], monthly=d["outputs"]["monthly"]["fixed"])
(data / "solar.json").write_text(json.dumps(dict(provider="European Commission JRC PVGIS 5.3", retrieved="2026-10-22", scenarios=solar), separators=(",", ":")), encoding="utf-8")
gse = gpd.read_file(ROOT / "_raw/gse/areas2025.geojson")
gse.geometry = gse.intersection(box(7.640, 45.070, 7.668, 45.086))
gse = gse[["COD_AC", "RAG_SOC", "TXT1", "COD_CONSEG", "geometry"]]
gse.to_file(data / "grid_areas.geojson", driver="GeoJSON")
certificates = [
    dict(id="2026-208400-0131", parcel="1175/434", municipality="L219", subalterni=["75"], scope="unit", use="residential",
         address="VIA CORDERO DI PAMPARATO FELICE 17", floor="1", heated_area_m2=53.47, construction_year=1935,
         energy_class="E", epgl_nren_kwh_m2_year=167.27, heating_need_kwh_m2_year=98.08,
         standard_electricity_kwh_year=None, standard_gas_sm3_year=143.74, standard_district_heat_kwh_year=10348.75,
         declared_building_units=35, valid_until="2036-10-20", submitted="2026-10-20", status="Inviato"),
    dict(id="2025-200471-0025", parcel="1175/434", municipality="L219", subalterni=["8", "9"], scope="unit_multi_subalterno", use="non_residential",
         address="VIA CORDERO DI PAMPARATO FELICE 17", floor="0", heated_area_m2=120, construction_year=1939,
         energy_class="D", epgl_nren_kwh_m2_year=480.97, heating_need_kwh_m2_year=345.01,
         standard_electricity_kwh_year=2206.42, standard_gas_sm3_year=5383.07, standard_district_heat_kwh_year=None,
         declared_building_units=1, valid_until="2035-11-19", submitted="2025-11-19", status="Inviato")
]
for c in certificates:
    c.update(source="https://energia-energiapt.piemontetu.it/fra-ept/ape", retrieved="2026-10-22",
             location_method="cadastral_parcel_and_address", declared_coordinates=[7.716667, 45.116667],
             coordinate_status="rejected_outside_study_area", source_pages=[1, 2, 3], attestation_object="unit", pod=None)
(data / "ape_units.json").write_text(json.dumps(dict(
    coverage="Two inspected certificates for a single address; not a complete San Donato inventory.",
    search_result_records=15, inspected_records=2, certificates=certificates,
    limitations=["Public consultation copies have no legal value.", "APE energy is standardized modelled energy, not billed consumption.",
                 "A multi-subalterno certificate total belongs to the attested property; never duplicate it per identifier.",
                 "Declared building-unit counts differ across certificates and are not a verified building inventory.",
                 "APE coordinates were rejected; no apartment polygon or precise interior position is known."]
), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("Prepared PVGIS scenarios, four GSE areas and two reviewed APE records.")
