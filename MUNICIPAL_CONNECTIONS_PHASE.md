# Connected properties — local 2.8.0-dev.1

24 October 2026. The user authorized all five proposed steps: connected parcel view, unresolved site investigation, geographically varied building checks, navigation/source comparison, and preparation of a bounded static online release. Publication is a separate step. Public 2.5.1 and clean public Git history remain unchanged.

## What changed

The municipal explorer now keeps cadastral parcels, municipal buildings/parts/sites, documented property/subalterno identities and candidate civics in the same white IT/EN workspace. Selecting a parcel shows separate counts and paginated lists for each grain. Property records retain full member keys, attested scope, certificate dates, original floor/interior observations and candidate civic evidence. Selecting a civic opens embedded Street View with upper-left resize, minimize, restore and close.

A navigation trail records actual clicks. It is explicitly not a verified legal access chain. Municipal/site/parcel overlaps do not allocate a subalterno to a building, floor, entrance or apartment polygon. When a record has multiple candidate cartographic parcels, the user chooses explicitly; no largest/nearest candidate is silently assigned. Up to 100 parcel alternatives are shown with truncation indicated; each result section is paginated at 50. Original cadastral dossiers remain available via Full dossier and return to the municipal explorer.

Selected records highlight on the coordinated map. Compare source displays a table of object grain, source/class, date, geometry, identity and reported use, with an orange reference overlay when geometry exists. Property records without geometry remain without geometry. No source disagreement is labelled a completed cadastral change. All 82,434 source parcel outlines remain available at city overview scale, alongside optional volumetric count cells and North/South controls. Street-detail layers remain bounded. In 2D, large parcel overviews draw the original simplified outlines as one display path for responsiveness; clicking that overview zooms to street detail, where individual source parcels can be selected. Source records/geometries are not merged or rewritten.

## Complete unmatched building/part investigation

The investigation reads the acquired September 2026 municipal data and preserves every source key. The correct join remains ID_UINS → site CLASSID, never exported row ID.

| Class | Unmatched references | Source objects | Share |
|---|---:|---:|---:|
| Main buildings | 24 | 42,048 | 0.057% |
| Minor buildings | 605 | 57,695 | 1.049% |
| Volumetric parts | 633 | 128,273 | 0.493% |

**All 1,262 unmatched references contain ID_UINS = 0.** All were checked against acquired site polygons using positive intersection >0.1 m² in EPSG32632. No positive-overlap candidate was found for any of these 1,262 objects. No replacement key was assigned and no source record was altered. This establishes a source-key/coverage limit, not proof that a site does not exist or that a source is erroneous. Cause of zero/coverage remains unknown. Impact is medium for navigating these source site relationships; confidence is high in the reproducible counts, not in any unknown legal access.

Circulation remains outside this targeted building/part investigation: 34,029 pedestrian and 21,213 vehicle source site references were already unmatched in 2.7. Do not present 1,262 as the total across all municipal classes. Total across classes stays 56,504.

The Source investigation view supports browsing all 1,262 findings and filtering by class. `output/municipal/investigation.sqlite` and JSON are separate ignored read models. Reproduce with `py -X utf8 scripts/build_municipal_investigation.py`. Sources are opened read-only. Inspectable executed companion: `output/research/municipal-connections-quality.ipynb`.

## Fifty geographically varied building cases

Ten municipal main buildings per coordinate stratum (North/South/West/East/Centre), with purposive source-use/interior-ring selections followed by deterministic farthest-point coverage. These are source-link checks, not site visits, new documentary validation, a random sample or a citywide accuracy estimate.

The cohort includes 7 cases with interior geometry rings, 20 with multiple parcel-level candidate civics, 25 with multiple parcel overlaps and 24 whose source use differs from the exact residential/unknown strings. Uses include industrial, commercial/industrial, railway, public-service, hospital, school and residential entries. Multilabel source use does not establish the use of each property. Interior rings suggest open geometry and do not prove courtyard entrances. Case cards retain original use, parcel keys, number of candidate volumetric parts, property scope/evidence counts and candidate civic counts. Parcel properties are never allocated to the chosen building from shared parcel membership alone.

Existing dated documentary observations (including Cavour 9) are retained and shown separately on their parcel. No new current/legal entrance has been verified. No apartment completeness, owner/tenant or energy/company claim has been added.

## Static release candidate prepared locally

`municipal-data-client.js` supports the same source searches, viewport layers, exact site-key candidates, evidence filters, source contexts, graphs, connected properties/civics and investigation through a read-only API locally or bounded gzip static shards. Existing city/pilot static models are reused. Search quality postings avoid downloading the full catalogue for a filter. Static source records are hash-sharded, search uses token-prefix postings, geometry is spatially tiled, large polygons stay in separate broad-layer shards, and links are bidirectional with their original methods/metrics. The client does not call a local API in static mode.

Prepare municipal shards: `py -X utf8 scripts/prepare_municipal_publication.py`. Check every shard: `py -X utf8 scripts/check_municipal_publication.py`. Stage the complete candidate: `py -X utf8 scripts/prepare_connected_release.py`.

Ignored candidate folder: `output/release-2.8.0-rc.1/`. It combines the reviewed base publication allowlist and the new validated municipal shards; a manifest records every path, size and SHA256. It is approximately 688 MB, below the enforced 900 MiB package budget; individual compressed source shards are below 25 MiB. Exact final size/count are in `output/qa/connected-release.json`. No raw PDFs/GPKGs/downloads, SQLite databases, local review events, QA outputs or unresolved-licence ARPA geometry are copied. Source property/address records are not private company measurements. New static evidence is rebuilt from source-only dossier records, never workflow notes.

Local development preview: http://127.0.0.1:8765/?release=2.8.0-dev.1 . Static candidate preview: http://127.0.0.1:8765/output/release-2.8.0-rc.1/?staticCity=1 . The flag disables the API even on localhost; the candidate's meta flag enables the municipal explorer. On GitHub Pages the hostname selects static data automatically. The original city component stays source version 2.5.1; the municipal raw catalogue stays source build 2.7.0-dev.1; the connected runtime is 2.8.0-dev.1 and package is 2.8.0-rc.1. These are component/provenance versions, not claims of a new online deployment.

Future publication still needs explicit user authorization, municipal attribution/return-copy wording review and clean public history. Do not push the primary development branch. No new push, remote write or deployment occurred in this phase.

## Verification and limits

Passed actual-source connected-property checks across every cohort parcel/section, exhaustive zero-key finding reconciliation, pagination/domain/ambiguity checks, the 1282/94 fixture (14 source property records, property /39 to civic 116066 candidate), existing municipal geometry/key/model checks, every municipal static shard's hash/privacy/schema/count checks, existing city/pilot static publication checks, real static adapters without a local API, JS syntax and Python compile. The static municipal adapter test records its request/byte totals in QA; these are local file reads, not a network speed claim. A 738-source-record parcel also passes a final-page check (offset 700, 38 records).

Chrome verified the local and static parcel → property 1282/94/39 → civic 116066 route, embedded Street View, upper-left keyboard resize (410 to 420 px with right/bottom fixed), minimize/restore/close, source comparison, full-dossier return, source-investigation class filter, 3D, IT/EN and 390 px layout (scroll width 390, map width 375). Switching 2D/3D preserves the selected connection section. No captured application errors. Browser checks and final screenshots are recorded in `output/qa/connected-properties-browser.json`. Large overview loading and old-dossier transitions can briefly pause on this device; no network latency benchmark is claimed. Tests are samples of UI and deterministic source checks, not proof of all source geometries, current occupancy, legal access or exhaustive apartment coverage. Basemap/Street View imagery still depends on third-party connectivity. Static spatial context scans are bounded and may report truncation; very broad context geometries may require zoom/narrowing. Simplified 3D continues to use reported source heights on a flat plane, not terrain or LoD2/2.5 roof surfaces.

## Next decisions

Use the static candidate to review usability and performance, then request publication explicitly if desired. Further property refinement needs source documents or authoritative identifiers connecting specific subalterni to entrances. More overlap metrics or 3D detail alone cannot establish that relationship. Preserve source observations, candidate interpretations and unknowns separately.
