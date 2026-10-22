"""Build a reviewed public Pages artifact, never the entire workspace."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dist"
FILES = [
    "index.html", "styles.css", "workspace.css", "app.js", "workspace.js",
    "energy-model.js", ".nojekyll", "robots.txt", "sitemap.xml",
    "README.md", "HANDOFF.md", "DATA_REVIEW.md", "V2_ROADMAP.md", "RELEASES.md",
    "vendor/leaflet.js", "vendor/turf.min.js", "vendor/jszip.min.js",
    "vendor/maplibre-gl.js", "vendor/maplibre-gl.css",
    "data/meta.json", "data/lotti.json", "data/edifici.json", "data/ingressi.json",
    "data/sezioni.json", "data/strade.json", "data/census2023.json",
    "data/census2023.geojson", "data/ape_units.json", "data/demand_benchmark.json",
    "data/grid_areas.geojson", "data/solar.json",
    "data/download/torino_sandonato_dati.zip", "data/download/torino_sandonato_energy.zip",
]


def build():
    assert DEST.resolve() == ROOT.resolve() / "dist", "Unexpected publication directory"
    if DEST.exists():
        if DEST.is_symlink():
            raise ValueError("Publication directory must not be a symlink")
        shutil.rmtree(DEST)
    DEST.mkdir()
    manifest = []
    for relative in FILES:
        source = ROOT / relative
        assert source.is_file() and not source.is_symlink(), relative
        assert source.resolve().is_relative_to(ROOT.resolve()), relative
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        manifest.append({"path": relative, "bytes": target.stat().st_size,
                         "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    (DEST / "publication-manifest.json").write_text(
        json.dumps({"version": "1.0.0", "files": manifest}, indent=2) + "\n", encoding="utf-8")
    print(f"Public artifact: {len(FILES)} reviewed files, {sum(f['bytes'] for f in manifest):,} bytes")


if __name__ == "__main__":
    build()
