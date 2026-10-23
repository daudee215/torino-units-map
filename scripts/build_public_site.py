"""Build a reviewed public Pages artifact, never the entire workspace."""
import hashlib
import json
from pathlib import Path
import shutil
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dist"
FILES = [
    "index.html", "styles.css", "workspace.css", "app.js", "workspace.js",
    "energy-model.js", "registry-workspace.js", "registry.css", "identity-evidence.js", "parcel-identity.js",
    "public-energy-model.js", "public-energy-workspace.js", "public-energy.css", ".nojekyll", "robots.txt", "sitemap.xml",
    "README.md", "HANDOFF.md", "DATA_REVIEW.md", "V2_ROADMAP.md", "RELEASES.md",
    "PARCEL_DATA_PHASE.md", "V2_PROGRESS.md", "PUBLIC_ENERGY_PHASE.md", "ADDRESS_REFINEMENT_PHASE.md",
    "vendor/leaflet.js", "vendor/turf.min.js", "vendor/jszip.min.js",
    "vendor/maplibre-gl.js", "vendor/maplibre-gl.css",
    "data/meta.json", "data/lotti.json", "data/edifici.json", "data/ingressi.json",
    "data/sezioni.json", "data/strade.json", "data/census2023.json",
    "data/census2023.geojson", "data/ape_units.json", "data/demand_benchmark.json",
    "data/grid_areas.geojson", "data/solar.json",
    "data/roof_evidence.json", "data/public_demand_profiles.json", "data/solar_weather_2023.json", "data/torino_energy_context.json",
    "data/registry/summary.json", "data/download/torino_property_registry_v2.zip",
    "data/download/torino_sandonato_dati.zip", "data/download/torino_sandonato_energy.zip",
]


def publication_files():
    # A bounded source read model, not the local database or acquisition caches.
    parcels = sorted((ROOT / "data/registry/parcels").glob("*/*.json"))
    summary = json.loads((ROOT / "data/registry/summary.json").read_text(encoding="utf-8"))
    assert len(parcels) == summary["counts"]["parcels"], "Incomplete parcel read model"
    def check(path):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert all("review" not in link for link in data["links"]), "Local review data in static source model"
        addresses=data.get('address_evidence')
        assert addresses and addresses['local_only'] is False, 'Missing reviewed static address evidence'
        assert set(addresses['entrances'])=={str(e['COD_CIVICO']) for e in data['entrances']}
        assert len(addresses['attribution'])==3
    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(check, parcels))
    print(f"Validated {len(parcels)} source-only parcel files", flush=True)
    return FILES + [p.relative_to(ROOT).as_posix() for p in parcels]


def build():
    assert DEST.resolve() == ROOT.resolve() / "dist", "Unexpected publication directory"
    if DEST.exists():
        if DEST.is_symlink():
            raise ValueError("Publication directory must not be a symlink")
        shutil.rmtree(DEST)
    DEST.mkdir()
    manifest = []
    files = publication_files()
    def copy(relative):
        source = ROOT / relative
        assert source.is_file() and not source.is_symlink(), relative
        assert source.resolve().is_relative_to(ROOT.resolve()), relative
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return {"path": relative, "bytes": target.stat().st_size,
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    with ThreadPoolExecutor(max_workers=16) as pool:
        manifest = list(pool.map(copy, files))
    (DEST / "publication-manifest.json").write_text(
        json.dumps({"version": "2.1.0", "files": manifest}, indent=2) + "\n", encoding="utf-8")
    print(f"Public artifact: {len(files)} reviewed files, {sum(f['bytes'] for f in manifest):,} bytes")


if __name__ == "__main__":
    build()
