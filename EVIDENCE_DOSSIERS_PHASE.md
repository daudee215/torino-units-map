# Documentary evidence and city-first viewing — local 2.9.0-dev.2

24 October 2026. The user authorized the next local phase: difficult public-document property cases, clearer evidence labels and reduced loading pauses, including slower-connection checks. Public 2.5.1 is unchanged. No push, deployment or external message is authorized or performed. Frozen local 2.8.0-rc.1 remains unchanged; the new local candidate is 2.9.0-rc.1.

## Property evidence cases

The new **Property evidence cases** panel contains 13 deliberately selected cases: 11 property/complex subjects and two Catasto Terreni controls. Twelve have page-checked documentary observations; one is an unresolved certificate-address discrepancy. This is not a random sample, apartment census, legal-access validation or proof of current occupancy. All current-access flags remain false.

| Case | Reported reference / scope | Supported observation and limit |
|---|---|---|
| Digione 3, 2022 | 1175/643/113 | Former porter premises and associated cellar. Address-only access support. |
| Digione 3, 2023 | 1175/643/114 | Document describes access from the vehicle entrance hall and a shared courtyard facility. Remains distinct from subalterno 113; no merger or succession inferred. |
| Buon Pastore, 2019 | Multi-parcel complex, including 1180/229, 232, 235, 255, 259, 448 | Central court and access from different streets. Page 7 reports linked portions and updates pending in 2019; no unique subalterno allocation inferred. |
| Francia 73, 2022 | 1223/9/2 | Former school, not an individual apartment or apartment area. No individual entrance proved. |
| Fabrizi 55, 2022 | 1173/331/2 | Ground-floor premises with external services in a residential building. Address does not establish a particular door. |
| Regina Margherita 220, 2023 | CT 1179/415 | Land control: not an apartment or urban subalterno. No CF property match created. |
| Beaumont 22, 2023 | 1221/149/2 | Former porter premises; source explicitly reports a cadastral update still to be made. No completed change inferred. |
| Borsellino 16, 2023 | CT 1222/476 part | Land/right-of-way description, not a surveyed route or apartment entrance. No CF property match created. |
| Racconigi market, 2023 | 31 subalterni on 1224/562 plus 1224/546/42 | Collective market/parking scope; not 32 apartments or 32 separate entrances. |
| Cavour 9, 2026 | 1281/107/7 | Two openings on a communal courtyard, reached through the vehicle passage. Date and section limits preserved. |
| San Francesco da Paola 38/G, 2026 | 1306/93/45, C/1, T-S1 | New technical-sheet review: primary street entry and secondary courtyard route through Via Mazzini 20. No current access verified. |
| Repubblica 31 market, 2023 | 1217/163 subalterni 3, 5, 6, 7 | Documentary complex scope explicitly excludes electrical-cabin subalterno 4 from the described transfer. No current procedure outcome inferred. |
| Via Roma address discrepancy | 1282/94/40 | Public certificate record says VIA ROMA 266; other civic candidates at the parcel are 360/366. The address is not silently changed. No acquired document resolves the entrance. |

The original nine municipal observations were rechecked on cited pages; Cavour 9 was retained and rechecked. New San Francesco sheet pages 3 and 4 were rendered and visually inspected; the source describes the two routes and gives the exact reported identity. Repubblica's explicit inclusion/exclusion is on page 25 of the acquired 2023 disposal plan. Cases retain year-only date precision where only the document year is established. Source-page links, file SHA256, scope, unknowns and next required evidence are recorded in `data/property-evidence/cases.json`. Raw PDFs/page images stay ignored.

New technical sheet: https://bandi.comune.torino.it/sites/default/files/allegati/avvisi/2026/4534/2_2026_assoc_confisc_allegato_1_scheda_tecnico_patrimoniale_s_francesco_paola_38_g.pdf . Municipal plan: https://risorse.comune.torino.it/bilancio/pdf/2023/DEL-685-2023-All_6-29545_2023_06.pdf . Other source links are in each case.

Two reviewed street-label aliases link the San Francesco observations to municipal civic candidates: document SAN FRANCESCO DA PAOLA 38/G → municipal S. FRANCESCO DA PAOLA 38/G (civic 98478); document VIA MAZZINI 20 → municipal VIA GIUSEPPE MAZZINI 20 (civic 68681). Civic letters are matched exactly: 38/H, 38/I, 20/A, 20/C and 20/F are not substituted. Alias matching is a candidate join, not a legal-access verification. Two additional reviewed aliases retain exact civics for Beaumont 22 → Claudio Beaumont 22 and Moris 9 → Giuseppe Moris 9. Buon Pastore title addresses (18 / Moris 9) and page-7 cadastral addresses (26 / Regina Margherita 153 bis) stay separate by role and page. The Mazzini point has no acquired parcel candidate; the document describes a route through a vehicle passage, so no artificial point-in-parcel match is forced.

Documentary identity observations remain separate from the 226,951 city source identities. Candidates are linked by reported municipality/sheet/parcel/subalterno, with unreported section and group scope explicitly unverified. A group containing a matching member is not equated to the whole documented subject. Land controls create no CF property matches. No apartment polygons, interior-door coordinates, new LoD2 roofs, company measurements or energy calculations are created.

## Evidence shown beside assertions

Four bilingual labels: **Reported by source**, **Described in document**, **Geometric candidate**, **Unknown**. They describe assertion provenance, not a ranked confidence/accuracy score. A source ID_UINS → CLASSID reference is declared in the source; overlap/IoU/point-in-parcel remains geometric candidature. Certificate address observations and spatial corroboration are shown separately. Unknown means not established in acquired evidence, not absent.

A collapsible legend explains the labels. Document pages, dates, source scope and current-access unknowns remain visible. Case cards appear in relevant parcel context without being assigned to every property on that parcel; property cards require a reported-key candidate, and civic cards cite only observations linked to that candidate civic. Street View can be opened for either documented route while keeping the case dossier visible. Case view and route selection survive IT/EN and 2D/3D switching. Street View remains nearby imagery, not proof of the unit entrance.

## Loading changes and measured limits

The city overview no longer decompresses/parses and draws all 82,434 vector outlines on the main thread. `data/parcel-overview/` contains 142 transparent 512-pixel PNG tiles displayed as 256-pixel Web Mercator tiles at native zooms 10–14. Each zoom retains coverage of all 82,434 source identities; no source records/geometries are merged or rewritten. Original selectable parcel geometry still loads at street detail. Clicking the overview zooms in. Source-count labels explicitly refer to the catalogue, not the count visible in a North/South viewport. The old cadastral dossier map uses the same tiled display.

All zoom levels together total 2,358,529 PNG bytes. The whole-city zoom-12 overlay is 178,275 bytes versus 6,072,264 bytes of previous overview gzip shards: 97.06% less overlay payload at this zoom/extent. This is not a 97% whole-application speed improvement. Tile registration was checked against 52 source vertices using an independent EPSG:3857 projection. Manifest hashes, dimensions, transparency, source geometry digest and coverage counts are checked.

The default Whole Torino page now starts without loading the hidden pilot's GIS/statistical/legacy source data. About 4,332,550 source bytes are deferred until a pilot tab is requested. Pilot data/definitions and earlier energy work are preserved. Loading is memoized to avoid duplicate initialisation. Chrome verified first on-demand Pilot map loading with saved 1175/434 (two buildings/eight entrances) and return to Whole Torino. Explicit view=pilot startup is checked separately.

Chrome's local cold-cache test used simulated 2 Mbps download and 150 ms latency. The observed nine parcel tiles transferred 179,963 bytes including HTTP overhead in a 2,127 ms map-tile phase. CDP capture covers the map-loading phase, not full navigation or paint; no complete page-speed or real mobile/production network claim follows. Basemap/Street View depend on external services. Network/cache emulation is reset after testing. QA files: `output/qa/property-evidence-slow-local.json` and `property-evidence-payload-comparison.json`. Final static candidate loading checks are recorded separately.

## Reproduce and verify

- Build cases: `py -X utf8 scripts/build_property_evidence_cases.py` (reads acquired PDFs/city source catalogue only).
- Build overview: `py -X utf8 scripts/build_parcel_overview_tiles.py` (about 12 seconds locally; source geometry untouched).
- Source/scope/tile checks: `py -X utf8 scripts/check_property_evidence_phase.py`.
- Real bilingual UI module checks: `node scripts/check-evidence-labels.cjs`.
- Static city/municipal and identity checks remain in their existing scripts.
- Prepare independent local static candidate: `py -X utf8 scripts/prepare_evidence_release.py`.

Publication validation for the prepared new source assets is data-only and does not require raw PDFs or local SQLite in a future clean public build. Raw files, case images, QA output, local reviews, databases and unresolved-licence geometry are excluded. The candidate is prepared locally from the frozen source-only 2.8 artifact plus declared current runtime/documents and reviewed new data. It does not mutate the 2.8 candidate or public history.

Development preview: http://127.0.0.1:8765/?release=2.9.0-dev.1 . Static preview: http://127.0.0.1:8765/output/release-2.9.0-rc.1/?staticCity=1 . Final verification records and screenshot are under `output/qa/`.

## Remaining uncertainty

These dossiers establish what dated documents and public source records report. They do not establish present accessibility, occupancy, legal cadastral equivalence or apartment completeness. Stronger current links need an authoritative complete-key/entrance document or an authorised current-site check. Publication requires a separate user instruction and the clean public-history workflow. 

## City-first refinement (user follow-up, 24 October)

The user requested removing Pilot navigation, using the pilot's simple click interaction across Whole Torino, clearer entrances and a calmer interface. This supersedes the earlier dev.1 explicit pilot-startup behavior. Every initial URL now opens the municipal atlas, including saved view=pilot and lotto links. The original pilot code, source records and previous energy work are preserved as baseline material, with no Pilot tabs or city-to-pilot action in the current interface.

Whole-city source coverage was already acquired: 82,434 cartographic parcel references, 63,402 regional footprints, 119,108 municipal civic points, 226,951 property/source identities, plus the municipal classes. Those source counts are not individual apartment or verified entrance counts. The interaction is citywide; deeper document investigations remain uneven, and energy allocations or San Donato-only measurements are not copied into other neighbourhoods.

The main 2D map defaults to parcels and municipal main buildings, with circulation, volumetric parts and contextual layers optional. Overview volume clusters are hidden by default. Civic features are requested only from zoom 18 and within a bounded detail extent. Seven-pixel blue markers have white outlines, address tooltips and priority above polygon layers; marker clicks open Street View directly. The 3D view enables source-height volumes and prioritises civic hit selection. Search no longer starts with 50 arbitrary volume rows; an empty query explains how to navigate. Volume filters appear only for volume searches.

Search and detail panes can be hidden; detail selection opens the dossier automatically. Sources, evidence cases, investigations and full dossiers sit under Sources & tools. Connected parcels have direct Buildings / Properties / Entrances buttons. IT/EN controls and white ArcGIS-style layout are retained. Street View retains upper-left resizing, minimise/restore/close. Google can show nearby imagery at a different house number: the window explicitly asks users to check civic and imagery date.

Chrome verified the new 1440px desktop map, exact Mazzini 20 search, a direct map-marker click to Mazzini 20/C (civic:68683), and embedded imagery. Keyboard upper-left resizing changed width 410 to 420px with right/bottom fixed, and minimise/restore/close worked. Further final browser checks are recorded in output/qa/property-evidence-browser.json. No current legal access is asserted.

### Final city-first verification

Chrome additionally verified northern civic:54271 (Strada del Francese 97 int. 53) and southern civic:8043 (Strada Castello di Mirafiori 352 int. 4), with bounded parcels/buildings/civics and embedded nearby imagery. The San Francesco 1306/93 dossier exposes all five acquired civic candidates and 14 property-source records without equating those counts with apartment completeness. The Entrances / Street View action and the full dossier round-trip worked. Both document route previews preserve the case panel; IT/EN, 2D/3D, 390px layout and closed-panel state were checked. No captured application errors. Temporary viewport and network overrides are reset.

Screenshots: output/qa/whole-torino-v2.9-overview.png and whole-torino-v2.9-street-view.png. Browser record: output/qa/property-evidence-browser.json. These QA images/logs remain local and excluded from publication. Source/adapter/evidence/identity checks pass. The prepared source-only candidate is validated separately by scripts/check_evidence_release.py; its QA JSON records actual hashes and bytes. The original phase's 2 Mbps /150ms timing remains a measured local tile-phase result only, not a final static or whole-app timing claim.
