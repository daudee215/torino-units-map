# Municipal explorer — local 2.7.0-dev.1

Completed 24 October 2026. The user authorized implementing the broader municipal sources. This phase is local only. Public 2.5.1 and its clean release checkout remain unchanged; no push or deployment occurred.

## Source scope and identity

September 2026 Città di Torino DBGT downloads, announced 19 October, provide 434,085 records across eleven classes:

| Source class | Records |
|---|---:|
| Sites / complexes | 36,622 |
| Main buildings | 42,048 |
| Minor buildings | 57,695 |
| Volumetric parts | 128,273 |
| Canopies / shelters | 27,874 |
| Pedestrian circulation | 50,673 |
| Vehicle circulation | 23,527 |
| Street elements | 25,440 |
| Building archive grid | 3,746 |
| Census sections | 6,916 |
| Commercial records | 31,271 |

These are source objects of different grain, not apartments. The existing 226,951 property/source identities, 82,434 cadastral references, 63,402 regional footprints, 119,108 civics and pilot ledgers are preserved. No company/energy phase was added.

Download page: http://geoportale.comune.torino.it/web/cartografia/cartografia-scarico . Licence: http://geoportale.comune.torino.it/web/cartografia/licenze-duso . Raw ZIPs, hashes and profiles remain local under ignored `_raw/municipal-dbgt-202609/` and `output/research/municipal-dbgt-202609/`. The municipal licence page includes attribution and return-copy wording to review before any future publication; no communication was sent.

## Corrected source join — important for future work

`ID_UINS` refers to site **CLASSID**, not the exported site row ID. Preserve both keys. The initial research compared row IDs provisionally; those mismatch counts are superseded. Example: volume CIT_AR 1 references key 7651, which resolves to site row 7316 (CLASSID 7651); their geometries intersect. Site row 7651 instead has CLASSID 2577 and is approximately 6.87 km away. Never join these columns by coincident row numbers.

All 36,622 CLASSIDs are unique. Current unmatched references: main building 24, minor 605, volume 633, pedestrian 34,029, vehicle 21,213; total 56,504. Most unresolved references are circulation rows, not buildings. The interface exposes actual site row/key and intersection diagnostics. Tests assert the correct key on every source-ID graph edge and this concrete regression fixture.

## Implemented interface and graph

White ArcGIS-style local explorer, complete IT/EN controls, whole-municipality/North/South views, eleven source categories plus original civic/property search, source attributes, evidence filters, 2D and simplified 3D. Existing cadastral dossiers remain reachable and return to the municipal explorer. Civic selection opens shared embedded Street View with upper-left resize, minimize, restore and close.

Search is 50 records/page. Viewport layers are capped at 2,000 features each; large views use source-volume count grids and require zoom for details. Context intersections are paginated with a bounded 1,000 bounding-box candidate scan explicitly reported. Source grids count volumes, not apartments. Comparison overlays preserve competing references.

Graph edges: 245,712 declared ID_UINS references; 128,272 volume/main-or-minor footprint overlaps; 675,478 parcel overlaps; 126,054 regional footprint comparisons. Total 1,175,516. Positive polygon overlap threshold is 0.1 square metres in EPSG32632. Geometry fractions/IoU are geometry measures, not accuracy scores or proof of legal equivalence, ownership, parcel change or access. All competing matches remain candidates.

Archive grids locate archive context, not individual permits. Census geometry labelled 2021 does not establish the year of demographic attributes. Commercial rows do not establish current premises, apartment inventories or ownership. Source attributes are whitelisted; contact/proprietor fields are not exported.

## Height evidence and model limits

105,674 volumes have positive source height; 98,078 meet default extrusion rules. Rules require valid geometry, finite positive reported height below 300 m, positive comparable eaves/ground elevations, height agreement within 0.05 m and source portion `al suolo`. There are 1,727 height/elevation disagreements and 6,724 non-ground portions. Unknown/excluded and non-ground portions stay flat; disagreements require an explicit opt-in and amber display. Integer floors: 53,488; unknown: 7,848; not applicable: 57,695; compound descriptions: 9,242. Values such as `5+1` remain original text, never apartment counts.

This is relative extrusion on a flat reference plane. No terrain, detailed roof faces, apartment floors, independent height survey or LoD2/2.5 model is claimed. The roof-element download inspected is canopy-only.

## Reproduction and verification

`py -X utf8 scripts/build_municipal_explorer.py` builds ignored `output/municipal/catalog.sqlite` and summary from read-only acquired inputs and existing catalogue. Cached CRS transformers; fresh corrected canonical build completed in 217.8 seconds. The one-time repair script is retained for audit, but is not required by the canonical build. A pre-correction ignored database is retained locally and must not be delivered.

`py -X utf8 scripts/serve_registry.py` serves local read-only municipal APIs on 8766. `py -m http.server 8765 --bind 127.0.0.1` serves the UI. Preview: http://127.0.0.1:8765/?release=2.7.0-dev.1 . After the requested laptop shutdown these services must be restarted.

Passed: corrected municipal checks on the fresh canonical build, source/class/geometry/graph/key/API bounds/privacy/model checks, existing city-catalogue checks, static-city fallback and identity-evidence checks, JS syntax and Python compile. QA: `output/qa/municipal-explorer-checks.json`.

Chrome extension checks: all-city overview, source-height 3D, height disagreement filtering, cadastral overlay, source context, corrected key 7651 to site row 7316, original property 1282/94/39 dossier round trip, separate civic staircase addresses, embedded Street View upper-left keyboard resize (410 to 420 px with right/bottom fixed), minimize/restore/close, IT/EN and 390 px DOM layout without horizontal overflow. Browser checks are samples, not validation of every source relationship or current legal entrance. Final screenshot and browser checklist are in `output/qa/`.

## Next work and publication boundary

Next useful work is source-specific interpretation of unmatched references and targeted documented property/access cases, followed by a reviewed bounded static municipal export if publication is authorized. Do not imply exhaustive property or apartment coverage. Current legal entrances remain unverified. No new publication is authorized. Runtime JS/CSS were added to the future publication allowlist only to avoid missing assets; raw archives, municipal SQLite/read models, local reviews and unresolved-licence geometry remain excluded. Never push the primary development history; use clean public history and the reviewed allowlist for any separately authorized release.
