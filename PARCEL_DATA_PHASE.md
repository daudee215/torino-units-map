**Publication authorization — 23 October 2026:** the user requested publishing the whole-Torino version to the existing GitHub repository and Pages site. Prepare release `2.5.0` from clean public history. Include the reviewed source-only static city tiles/search/record shards and pilot workbench; exclude raw archives, SQLite databases, local workflow/notes and unresolved-licence ARPA geometry. Public review remains disabled. Later development returns to local-only.

**Whole-Torino local expansion — 23 October 2026:** read [WHOLE_TORINO_PHASE.md](WHOLE_TORINO_PHASE.md). Local `2.5.0-dev.1` adds actual citywide AdE parcel geometry (82,434 distinct cartographic references), 63,402 BDTRE footprints, 119,108 municipal civic points and 226,951 property/source identities with bounded map/search loading. Existing pilot identities and ledgers remain preserved. These are source records, not verified apartments or legal entrance links. No new publication is authorized.

**Latest local phase — 23 October 2026:** read [PROPERTY_WORKSPACE_PHASE.md](PROPERTY_WORKSPACE_PHASE.md). Local `2.4.0-dev.1` adds the white property workspace, 178 searchable municipal-only references, 38 shared-key comparisons (31 APE records / 41 comparison rows), and two explicitly unresolved section cases. Case notes/status remain separate from source facts. Source/API and Chrome IT/EN/mobile/Street View/navigation checks passed. Published 2.2.0 is unchanged; no new push is authorized.

# Current phase — refined parcel and property evidence

**Latest local phase — 23 October 2026:** the user authorized all five property-review steps. Read `PROPERTY_REVIEW_PHASE.md`. Local `2.3.0-dev.1` adds a 30-case source investigation, the full 178-key audit (171 inventory-only, 5 document-supported, 2 section differences), 32 additional query snapshots, explicit candidate/historical access chains, deduplicated source timelines and evidence-quality counts. All current access/site truth remains unverified; no accuracy score or completed cadastral changes are inferred. Checks and Chrome IT/EN/mobile/access-chain Street View verification passed. Published 2.2.0 remains unchanged; no new push is authorized.


**Publication authorization — 23 October 2026:** the user requested publishing the current property-investigation version as 2.2.0 to the existing GitHub repository and Pages site. This supersedes earlier local-only statements for this release. Publish source-only static investigation dossiers, the reviewed municipal inventory pilot references and historical factual summaries, with attribution. Rebuild without reading local review events. Raw evidence, local reviews and unresolved-licence geometry remain excluded from both the artifact and new public history. Later development returns to local-only. Deployment verification is recorded in `RELEASES.md`.


**Latest local work — 23 October 2026:** read `PROPERTY_VALIDATION_PHASE.md`. Local `2.2.0-dev.1` completes 1,150 targeted parcel queries (0 remaining errors), yielding 24,706 property/group identities and 27,137 certificates. Adds local municipal inventory evidence (228 pilot references on 65 parcels), historical document observations, spatial access alternatives, a priority queue and 30-case review cohort. Documentary entrance/site validation remains pending. Checks and Chrome IT/EN/phone/Street View verification passed. Published 2.1.0 is unchanged; no new push is authorized.


**Publication update — 23 October 2026:** the user authorized the current parcel-focused release on the existing GitHub Pages site. Earlier local-only statements below describe development history. Release `2.0.0` excludes the ARPA geometry sample with unresolved rights, raw acquisitions and all local review records. The public register is read-only. Further development remains local until separately authorized.

Updated 23 October 2026 (Europe/Berlin). Local version `2.0.0-dev.4`.

The user pivoted away from energy work and selected **property/subalterno identity and entrance links** as the first priority. This supersedes the active energy phase in `PUBLIC_ENERGY_PHASE.md`; that document now describes historical work. Keep all v2 changes local. Do not push or publish.

## Immediate outcome

The main map action opens the Property register. Energy navigation and prominent energy actions have been removed; existing calculations/data remain preserved for later use. White ArcGIS-style surfaces, IT/EN controls and embedded resizable Street View remain.

The register now contains a parcel identity dossier:

- A search within the selected parcel for full cadastral keys, subalterni, reported addresses, civic suffixes and floors.
- Filters for incomplete identity, absence of an active entrance proposal, several entrance candidates, accepted review links, grouped/whole-building objects and conflicting cadastral sections.
- A civic-entrance table preserving official lettered addresses and civic IDs. Each entrance lists distinct proposed property identities and identities accepted in review, with actions to filter the property list or open Street View.
- Accepted/rejected review decisions remain local. Rejected links and links outside their supplied validity dates are excluded from active entrance counts, while their evidence remains visible in the review cards. Unknown dates stay unknown; date limits are evaluated using the current Europe/Rome date, with valid-until exclusive.
- Grouped cadastral members remain one property entity. Filtering never splits their certificates, area or energy, generates apartment polygons, or rewrites the sources.

No new authoritative property identities or confirmed entrances were acquired by this UI change. The underlying registry remains the 22 October source snapshot: 25,400 certificate entities and 23,501 property/group identities, with evidence on 3,101 parcels. These are not a complete apartment census, and unresolved duplicate/section identities remain.

## Next acquisition and refinement priorities

1. Work parcel by parcel on exact municipality + cadastral section + sheet + parcel + subalterno keys. Preserve source spellings and conflicting sections; test equivalence instead of deleting discrepancies.
2. Improve source coverage for the 26 street queries that reached the observed 500-record cap. Use verified public cadastral query capabilities for targeted parcel acquisition, preserving requests, retrieval dates and cap flags. Do not claim completeness from an empty response or from one capped query.
3. Resolve address aliases, civic letters and source-date changes using official civic evidence. Address agreement creates a proposal; proximity alone does not confirm a property's actual access. Multiple entrances may be legitimate and must remain representable.
4. Prioritize incomplete identities, competing entrance links and section aliases for source-backed review. Identify what additional evidence each decision needs. Review acceptance is an operational decision, not legal cadastral verification.
5. Add floor, area, use and construction attributes only with provenance and their actual grain. A whole-building value must not be silently copied to each apartment. Physical apartment interiors remain unknown unless an actual source supplies them.

## Validation

`node scripts/check-identity-evidence.cjs` covers cadastral-key search, exact entrance linkage, grouped members, rejected-link retention and exclusive review-date validity. Continue running `py scripts/check_property_registry.py` for source identities and grouped-certificate semantics. Browser QA must cover IT/EN, filters, entrance drill-down, Street View and phone layout. Raw acquisitions, local review records and QA artifacts remain excluded from publication.

Verified in Chrome on 23 October: full-key search selected subalterno 75; entrance 40966 filtered 13 of 27 identities; grouped filtering kept subalterni 8+9 together; IT/EN changed the dossier labels; civic 17/C opened its embedded Street View. The 390 px layout had equal scroll/client widths. No application errors were captured. Static/review services returned HTTP 200. QA screenshot: `output/qa/v2-parcel-identity.png`; temporary viewport overrides were cleared. No review decisions were changed during these checks. No push or deployment was performed.
