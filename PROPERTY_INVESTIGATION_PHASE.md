> Historical local development record. Publication of its reviewed source-only features was authorized on 25 October 2026 as 2.15.0. See RELEASES.md and SOURCE_ATTRIBUTION.md. Raw/local-only references below are development paths, not shipped artifacts.

# Whole-Torino property investigation — local 2.15.0-dev.1

25 October 2026. Implements the five authorized next steps after 2.14: complete parcel-property filtering, an entrance workbench, an explanatory investigation queue, broader documentary research and readable source dossier exports. Everything remains local. Public 2.13.0 and its clean public-history checkout remain unchanged; no new publication is authorized.

## Use

Open http://127.0.0.1:8765/?release=2.15.0-dev.1 . Select a parcel, then **Investigate / Indaga**. Its four views are Properties, Entrances, To investigate and Export. Sources & tools contains **Property investigation queue** and **Source updates**.

- Search covers the complete acquired parcel set, not the currently displayed 25 rows. Exact subalterno, reported floor, source scope, entrance status and selected-document filters combine with the search. Matching a member retains the whole source group.
- Entrances combines source civic points with reported-address candidates. Points with associated properties appear first. Off-parcel address candidates have a distinct label. Show candidates filters the whole property set; dated alternative observations remain visible. Street View previews a civic without replacing the selected parcel, including mobile Map → Details return and language switching.
- The read-only citywide queue explains what evidence is missing. Its categories overlap; they are neither an accuracy score nor established errors. Each item opens its exact source identity and any acquired candidate parcels. A source without geometry is retained without choosing a nearby parcel.
- Dossier downloads cover an individual property/group or the filtered parcel set, in standalone HTML and allowlisted JSON. They include original source links, dates, literal keys, unknown sections, certificate observations and municipal inventory provenance. HTML supports browser printing/save-PDF; no PDF was generated or print-dialog output tested in this phase.
- Added exact-link support for `municipal-key:` inventory-only IDs, preserving their distinct source identity.

## Full-source audit

The read model profiles all **226,951 source identities/groups**. **220,132** have at least one acquired cartographic parcel candidate, with every original membership preserved across **82,434 parcel dossiers**. The remaining **6,819** are retained in the investigation queue and existing source catalogue; no cartographic assignment was invented. The largest acquired parcel set, 1387/1, contains **738 source objects**, not 738 verified apartments.

| Investigation prompt | Source identities/groups |
| --- | ---: |
| No acquired entrance candidate | 98,397 |
| Address candidates without shared cartographic candidate | 70,578 |
| Group/whole-building scope to distinguish | 4,913 |
| Incomplete reported cadastral identity | 1,742 |
| Multiple candidates or conflicting address observations | 137 |

Counts overlap and cannot be summed as a number of errors. All current-access-confirmed fields remain false. Multiple observation dates do not establish a cadastral change. Documentary key candidates do not establish section equivalence. No apartment geometry, owner, tenant, POD, consumption or company data was added.

`data/property-investigation/` contains 256 compressed parcel buckets, bounded 100-record queue pages, a summary and a SHA256/byte manifest: **2,017 listed files, 21,797,347 bytes**. Data loads only when investigation is opened; bounded in-memory caches retain 12 resource promises and 20 parcel filter states. Global source search remains the existing catalogue; the new full-set filtering operates inside an explicitly selected parcel. No backend write or source identity mutation is introduced.

## Five additional documentary subjects

These extend the four 2.14 subjects to **nine selected sources** across north/south/east/west/centre. This is a purposive documentary sample, not representative building coverage or a new citywide plan dataset.

| Subject | Dated source facts and limits |
| --- | --- |
| Via Bologna 175/G, north | Official 2014 municipal HTML page, last updated 1 December 2014. Workshop 1145/98/2 and courtyard 1145/98/4. Also reports 1145/97 without a subalterno; none invented. Describes civic 175 and vehicle passage 175/G as distinct courtyard routes. |
| Mongreno 79, east | 2022 procedure PDF, identities pages 1–2, access description page 1. Apartment/attic 1204/98/37 and garage 1204/98/68, not two apartments. Stair C/interior 7, internal attic stair and separate landing door are reported observations. |
| Castelgomberto 75, south | 2023 procedure PDF, identity page 2 and access page 5. Non-residential 1387/35/173; cadastral update stated in progress. Stair B in municipal toponymy versus A in deeds/condominium rules; neither chosen as current truth. |
| Corso Francia 275/B, west | 2023 procedure PDF, page 1. Only northern unit 1227/464/2, not both units in the building. Pedestrian gate 275B differs from reported cadastral address 275. |
| Via Po 18/C-D, centre | 2025 procedure PDF, identity page 2/access page 1. 1280/85/21, arcade access and secondary courtyard exit. Distinct from previously acquired Via Po 18/I, subalterno 6. |

All sources use municipal originals with dated retrieval receipts and SHA256 hashes. Procedure year is not presented as an exact document issue date. Chrome extension inspected official sources; bounded downloads and extracted texts were checked against rendered PDF pages. HTML links have no fabricated PDF page fragment. Unproductive Vandalino/Luserna searches are retained as bounded search outcomes, not evidence of absent documents.

Raw originals stay under `_raw/investigation-20261025/`; acquisition receipts and extracted text are under `output/investigation-v215/`. `scripts/curate_investigation_documents.py` reproduces factual curation from those hash-checked originals and rebuilds the refinement manifest. Source context remains the 2.14 ANNCSU/ISTAT/DTM data; no more recent terrain, LoD2 roofs or current legal entrance confirmation was found or claimed.

## Reproduction and verification

1. `py -X utf8 scripts/curate_investigation_documents.py`
2. `py -X utf8 scripts/build_property_investigation.py`
3. `py -X utf8 scripts/check_property_investigation.py`
4. `py -X utf8 scripts/check_refinement_context.py`
5. `node scripts/check-property-investigation.cjs`
6. `node scripts/check-refinement-evidence.cjs`

The full check compares every generated property membership and member list against read-only SQLite catalogues, checks observation/inventory counts, confirms every source identity survives in a parcel or queue, verifies duplicate consistency, queue counts and all manifest hashes. Results: `output/qa/property-investigation-checks.json` and `output/qa/refinement-context-checks.json`. Rebuilding unchanged sources is deterministic apart from build timestamps.

Additional checks passed for saved references, source comparison, static city and municipal adapters without API fallback, bilingual evidence labels, and syntax of all changed runtime modules. Actual 738-record fixture tests cover a record at index 700, exact subalterno/floor including floor zero, unsplit grouped identities, off-parcel candidates, dated inventory and certificate provenance, unsafe URL rejection and HTML escaping/export exclusions.

Chrome verification covered static-only and normal local/API modes; full-set search and exact filters at 1387/1; a negative floor filter; entrance 7786 → 32 source candidates; preview keeping parcel 1387/1; minimize/restore/close and upper-left keyboard resizing; queue pagination 1–100 → 101–137; nine-source catalogue and Bologna HTML links; a saved `municipal-key:` URL; HTML/JSON downloads inspected on disk; readable HTML opened in Chrome; 1440px desktop and 390px mobile IT/EN without horizontal page overflow. Mobile preview survives language switching and returns to the same parcel workbench. No captured application errors in the checked workflows. Nearby Street View imagery can show a different civic label; it is not an entrance verification.

QA screenshots and downloaded artifact copies: `output/qa/investigation-v215/`. No raw plans, receipts, QA, local notes/reviews or databases are publication inputs.

## Publication boundary / continuation

New runtime: `property-investigation-model.js`, `property-investigation.js`, `property-investigation.css`; connected parcel tasks and municipal inspector integrate it. Runtime/phase filenames were added to the future top-level file list only. **Neither `data/property-investigation/` nor modified `data/refinement/` has been approved for publication or added to the public data allowlist.** A future release needs explicit user publication authorization, source/licence review, complete reviewed data dependencies and a fresh clean-history release build. Do not push this root checkout or run historical pinned release preparation blindly.

Clean public worktree remains at `008df7319ba0731d3ea1ee0a17db93c35a1d0cc7` (2.13.0), with no local changes. No push or Pages deployment was performed. Shutdown remains cancelled.
