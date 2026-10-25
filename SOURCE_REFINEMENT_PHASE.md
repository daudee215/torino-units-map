> Historical local development record. Publication of its reviewed source-only features was authorized on 25 October 2026 as 2.15.0. See RELEASES.md and SOURCE_ATTRIBUTION.md. Raw/local-only references below are development paths, not shipped artifacts.

# Source refinement and efficiency — local 2.14.0-dev.1

Completed 25 October 2026 (Europe/Berlin); source acquisitions and initial profiling on 24 October. The user authorized all five next steps and then requested resumption. Public 2.13.0 / commit 008df7319ba0731d3ea1ee0a17db93c35a1d0cc7 and its clean public checkout remain unchanged. No new publication or shutdown is authorized.

## Delivered scope

1. **Performance measurement and selective rendering.** Added opt-in, local-only diagnostics (`diagnostics`) with navigation/resource timing, named operation durations, supported long-task counters and optional Chromium heap estimate. No telemetry is sent; no record IDs, addresses or source URLs are logged. `diagnosticsCold` forces dataset-fetch reloads in the static clients; this is not a full browser-cache reset. A base-layer identity cache avoids clear/addData when selection-only changes reuse the same data and Leaflet layer. Enablement, data or map-layer changes still repaint; selection/comparison overlays remain independent. The cache resets on map teardown. Existing source caches, gzip shards, zoom gating and stale-response tokens remain.
2. **One parcel workspace.** Connections / Sources & context / Documents task buttons retain parcel and source-grain boundaries. Context and documentary payloads load on demand and are bounded, memoized static reads. Old documentary observations and four additional sheets are available in Documents; an empty legacy-case message is suppressed when that pane has other evidence. Sticky task navigation and scrolling bring the requested task into view on mobile. `Sources & tools → Source updates` lists the new context and opens each selected documentary parcel directly on Documents.
3. **Address reconciliation audit.** Reacquired official municipal CSV and ANNCSU regional ZIP into an immutable new raw folder. Their bytes match previously acquired files; no newer source vintage is claimed. A whole-source crosswalk preserves full street/access identifiers, civic letters and numeric separators. Only complete normalized street/civic syntax and unambiguous full street-word reorderings are used. `12/A` can match `12A`; `12/1` never becomes `121`. No fuzzy, civic-only, nearest-door or property-assignment rule is added. Civic context shows the original national identifiers and candidate status.
4. **Documentary enrichment.** Four technical-property sheets acquired and original identity/access pages rendered and visually reviewed: Cigna/Cervino (north), Plava 75 (south), Po 18/I (centre), Rossana 24 (west). Dated factual summaries preserve each subject's scope and original page links. They do not create new official catalogue identities or accept current entrances. Cigna includes seven reported subalterni and a common asset; Plava reports cadastral updating in progress; Po 18/I records commercial property 1280/85/6 and distinct arcade/cellar routes; Rossana distinguishes premises subalterno 18 from courtyard portions 15/16/17. No raw PDFs, plans, owner/tenant names or contract records are included in the read model. Procedure year is labelled separately from an unknown document issue date.
5. **ISTAT and terrain assessment/integration as context.** Audited the actual current Torino 2023 workbook and its dictionary against 2021 section geometry. Parcel/section intersections expose section-level dwelling/household counts, with explicit unknowns and multiple sections retained. No counts are allocated to parcels, buildings or apartments. Acquired a whole-Torino 5m ICE DTM mosaic in four WCS tiles, respecting the 2048-pixel service limit; sampled each parcel's representative point. Display is approximate, dated terrain context. Vertical-reference compatibility with municipal building elevations is not established, so the existing flat-plane 3D extrusions are unchanged. No LoD2/2.5 or current doorway elevation is claimed.

## Actual source findings

| Finding / grain | Evidence | Implication and handling |
| --- | --- | --- |
| Municipal civic source rows | 119,145 unique IDs; 37 outside the municipality boundary | The existing 119,108 mapped civics remain unchanged. The larger source count is not new map coverage. |
| ANNCSU Torino source rows | 109,700; filename INDIR_PIEM_20260915.csv; 0 duplicate access IDs; 0 coordinate-bearing rows | Municipal coordinates remain the spatial source. Address agreement alone is not shared/legal access. |
| Crosswalk statuses over municipal CSV IDs | 90,448 unique candidates; 28,697 no acquired candidate | Source agreement, not an accuracy score. Unmatched addresses stay unresolved; none is replaced. |
| Three refreshes | Municipal CSV, ANNCSU ZIP and ISTAT ZIP byte-identical to earlier acquisitions | Retrieval time is not source freshness. No claim of a newer edition. |
| Census section statistics / geometry | 4,314 unique data rows, 148 columns; 6,916 geometric sections; 0 data rows without geometry; 2,602 geometries without a statistics row | High interpretation risk if missing rows become zeros. The UI preserves unknown separately from observed zero. |
| Parcel/section intersections | 71,350 parcels intersect one section; 11,081 multiple; 3 none | No first-section-only assignment or weighted household/apartment allocation. Small positive slivers remain explicit. |
| Terrain samples | 82,434 valid samples; EPSG:32632, 5m grid, nodata -99; values about 201.9–673.58m | A representative-point terrain cell is not a doorway, roof or reconciled building ground elevation. |

The missing-statistics and unverified-elevation issues have high confidence as source-profile observations, but do not establish missing housing or wrong building heights. No accuracy percentage or legal decision is inferred.

## Research/access limits

The historical building-project catalogue is documented for 1780–1928 and uses historical street-name rules. An exact Cibrario/20 search previously returned no results; partial Cibrario and Po/18 outcomes were not verifiable after browser timeouts. These are recorded in `output/refinement/historical-query-audit.json`; no absence of projects is inferred and no project facts were acquired from those attempts. The four alternative municipal property sheets provide the bounded geographically varied documentary sample. EdificaTO is not treated as an open bulk plan feed.

Source discovery/inspection used the Chrome extension; bulk official files were acquired through reproducible bounded downloads. Cigna's advertised index.php download link failed, while its canonical official file path returned the verified PDF. The successful actual URL and SHA256 are retained. PDF summaries are based on reviewed pages, not search snippets alone.

## Performance evidence and limits

QA files under `output/qa/refinement-performance-*` contain baseline, optimized, forced-dataset-reload, normal-cache, mobile and final diagnostic snapshots. The controlled desktop runs used 1440x900; mobile used 390x844. Earlier before/after render snapshots used the native wider viewport and are single-run diagnostics, not controlled speed benchmarks.

In the 1440px normal-cache workflow, the captured search was 77.6ms and source-property selection 10.5ms; selection-only painting was 0.2ms, with 46 unchanged layer operations skipped across the captured sequence. Mobile source-property selection was 11.4ms and selection painting 0.4ms, with 26 skipped operations. These observations are local, cache/device/task dependent, include the instrumented code path, and are not a general speedup or network SLA. Initial map/decompression work can still create long tasks. Resource Timing bytes can omit cache/cross-origin transfers and are not the full 691MB publication. Heap values are optional Chromium estimates, not application-only retained memory. Workers and persistent caching were not added without stronger profiling evidence.

## Verification

- Full derived-read-model check covers all 82,434 parcel records and 119,145 civic records, keys/buckets, no confirmed access, section-grain/null/zero semantics, bounded candidates, terrain limits and the 514-file SHA256/size manifest (7,261,284 bytes). The manifest is explicitly local-only and not reviewed for publication.
- Actual-shard UI module checks cover civic 116066 → national access ID 30083353, multiple sections with missing and zero values at Plava, source terrain values/limits, grouped documentary scopes and IT/EN labels. Rendering cache tests exercise unchanged data, layer recreation and enablement changes.
- Reference, comparison, city-static, municipal-static and bilingual evidence checks pass; syntax checks pass for changed runtime files. Static-adapter regression tests use no local API.
- Chrome verified static-only source context, candidate identifiers and original page links; all four documentary subjects were opened during verification. Normal local preview has no diagnostic panel. Mobile task views fit 390px with no horizontal overflow, preserve IT/EN and retain embedded Street View. Temporary viewport overrides reset. No captured application errors in the verified final flows.
- QA screenshots: `output/qa/refinement-v2.14-*`. Executed companion notebook: `output/refinement/source-quality-audit.ipynb`. Reproducible acquisition/profiling/check scripts are under `scripts/`. Raw acquisitions remain `_raw/refinement-20261024/`; neither raw files nor QA are publication inputs.

## Continuation / publication boundary

Preview: http://127.0.0.1:8765/?release=2.14.0-dev.1

Open **Sources & tools → Source updates**, then a parcel document. Or select any parcel/civic and use the three parcel-task buttons.

New runtime dependencies: `atlas-performance.js`, `atlas-render-cache.js`, `refinement-evidence.js`; modified city/municipal static clients, connected view, evidence cases and municipal explorer. The new `data/refinement/` read model must receive a separate source/licence/publication review and explicit allowlist before any future release; it is deliberately not added to the current public data build. Future publication must include all runtime dependencies and the reviewed derived shards, and rebuild release hashes from clean public history. Do not run the pinned 2.9 or 2.13 release preparation blindly against this version. No new push or Pages deployment was performed. Public 2.13.0 stays live.
