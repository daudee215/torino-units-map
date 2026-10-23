**Published and verified — 23 October 2026:** whole-Torino release **2.5.0** is live at https://daudee215.github.io/torino-units-map/ . Runtime commit `418e59a1250af0f56ae55bcadfae59902ba208d0`; successful build/deploy: https://github.com/daudee215/torino-units-map/actions/runs/39995396107 . Citywide geometry/search and the read-only 24,884-record pilot workbench are online. Raw archives, local databases/reviews and excluded ARPA geometry are not published. Source counts are not verified apartment counts; legal entrances remain unverified. Further development returns to local-only until separately authorized.

**Publication authorization — 23 October 2026:** the user requested publishing the whole-Torino version to the existing GitHub repository and Pages site. Prepare release `2.5.0` from clean public history. Include the reviewed source-only static city tiles/search/record shards and pilot workbench; exclude raw archives, SQLite databases, local workflow/notes and unresolved-licence ARPA geometry. Public review remains disabled. Later development returns to local-only.

# Whole Torino — local 2.5.0-dev.1

23 October 2026. The user authorized expanding the prototype to the whole Torino municipality. This authorizes local acquisition and implementation, not a new GitHub publication. Published 2.2.0 and the reviewed pilot remain preserved.

## Actual acquired coverage

- Municipality: Torino, cadastral code L219, ISTAT 001272. Official BDTRE boundary is a union of two valid parts, approximately 130.006 km². It is not the metropolitan city.
- AdE bulk cadastral snapshot: 22 September 2026, 82,443 feature rows, consolidated by their full national cartographic reference into **82,434 distinct references**. Nine repeated references were dissolved only within the exact same reference. Allegato and sviluppo remain part of the identity. Roads/water and nonnumeric parcel labels are retained, so this is not a count of private building lots.
- **63,402 BDTRE 2026 building footprints**, intersecting the municipal boundary. Geometry remains 2D; no LoD2/2.5 or height is invented.
- **119,108 municipal civic points** inside/on the BDTRE boundary. Thirty-seven outside-boundary points are excluded from this map and counted in QA. The raw city address source remains preserved. Civic points include lettered/other numbering, not just residential front doors.
- Regional APE bulk: **224,759 source certificate identifiers**, **218,958 source property/group identities**, selected by explicit L219 municipality code. This table's observed submissions span 31 July 2016 to 31 July 2026 and its records carry the source active flag. It is not an all-time certificate census.
- **4,454 additional APE identities from existing pilot live-source evidence** supplement the city bulk. All **24,884 prior pilot record IDs** have a city entry/link. The city does not replace the richer pilot dossier for overlapping identities.
- Total: **226,951 source identities** = 223,412 APE identities/groups across these sources + 3,539 additional inventory references. This is not a unique-property or apartment count. Source-group/certificate overlaps remain explicit; no unsupported cross-source merge is made.
- The full existing April 2023 Torino municipal inventory is used. Incomplete/placeholder rows (553) remain in the original extraction and are not turned into complete property identities.

## Source acquisition and provenance

Chrome extension research verified the official AdE bulk service documentation and CC BY 4.0 attribution requirement:
https://www.agenziaentrate.gov.it/portale/download-massivo-cartografia-catastale
https://www.agenziaentrate.gov.it/portale/accedi-al-servizio-cartografici

The official regional URL is https://wfs.cartografia.agenziaentrate.gov.it/inspire/wfs/GetDataset.php?dataset=PIEMONTE.zip . The 1,496,390,577-byte region ZIP supports HTTP ranges. `scripts/fetch_city_parcels.py` reads its ZIP directory, downloads/decompresses the approximately 450 MB `TO.zip` province entry with size/CRC verification, selects the observed `L219_TORINO.zip` entry, and retains the municipal GML files. Raw downloads stay under ignored `_raw/city-parcels/`.

Torino municipal parcel GML SHA256: `c3eeed7bc5d555bc7ac7994e52325fa912f7cf7ce858a43ddc710f5de206e5af` (122,788,373 bytes). Cartographic sheet GML: `104fadf30af6afafbe051470622636413962e80d6bcc58213374afbc10699861`.

Other sources are existing acquired municipal civic CSV, BDTRE 2026 municipal GPKG, regional general APE CSV and reviewed pilot source read models. Their provider links and source timestamps remain in the catalogue. No raw downloads or local notes are published.

## Data architecture and joins

`scripts/build_city_catalog.py` produces an independent ignored `output/city/catalog.sqlite`, boundary GeoJSON and summary. SQLite R-tree supports viewport geometry; FTS5 supports bounded search. Full source reference strings remain visible. APE coordinates are not trusted for placement. Exact normalized full municipal street/civic matches supply address candidates; no fuzzy proximity or street abbreviation expansion is used. Building representative-point/parcel intersection and civic-point/parcel intersection are spatial candidates only, retaining multiple matches. No arbitrary nearest parcel is assigned.

Property-to-cartography links compare sheet/parcel, retaining all cartographic variants; they do not establish equivalence between urban cadastral section and map allegato/sviluppo. Blank and `=` sections are not collapsed. Group records retain all source members, including any other municipality, while only L219 members join Torino parcel geometry. Existing pilot-only extensions preserve source identifiers; local notes, case workflow and relationship decisions are not copied.

The source catalogue is read-only through `scripts/city_api.py`; it does not change either pilot ledger. Search pages contain at most 50 records. Geometry responses contain at most 1,500 features per layer and broad extents request further zoom rather than returning the whole city. API validation rejects malformed bounds/layers/offsets; queries are parameterized. The loopback service remains port 8766.

## Interface

Open http://127.0.0.1:8765/?city=1 and select **Whole Torino / Tutta Torino**. White, thin ArcGIS-style map with address/key search, property/parcel/civic/building filters, source inspector, original IDs, parcel-to-property list, municipal observations and APE history. Search is token-prefix search; search results are not exact identity matches. Selected geometry is highlighted. Selecting a civic automatically opens the same embedded Street View panel, with upper-left resizing, minimize/restore and close. The previous Property register, pilot map and review notes remain available. IT/EN and mobile stacking are supported.

Sources have different dates and acquisition scope. The coverage panel states that this is not an apartment census. Current legal entrances, unit geometry and present source validity remain unverified. Physical apartment interiors, company data and energy modelling remain out of scope. No completion percentage is shown against an unknown apartment denominator.

## Reproduction and verification

1. `py scripts/fetch_city_parcels.py`
2. `py scripts/build_city_catalog.py`
3. `py scripts/check_city_catalog.py`
4. Start the static loopback server on 8765 and `py scripts/serve_registry.py` on 8766.

Source catalogue checks cover SQLite integrity, IDs, membership grain, preserved municipality and cartographic components, no fabricated current entrance truth, viewport/search limits and invalid inputs. Existing property-workspace and identity-evidence checks remain passing. Chrome verification covers citywide search and actual Via Roma parcel geometry outside the pilot, entrance selection and automatic Street View controls, IT/EN, pilot navigation and 390px layout without horizontal overflow. Final screenshots: `output/qa/whole-torino-v2.5-local.png` (city overview) and `output/qa/whole-torino-v2.5-parcel.png` (Via Roma parcel). Full rebuild succeeded with the same reconciled counts; final Chrome city/pilot navigation produced no captured application errors.

Final quality profile: 127,978 identities have one exact municipal address candidate; 220,132 have at least one cartographic sheet/parcel candidate; 1,742 identities have incomplete identifiers. These are source-link counts, not independent validation or apartment coverage. Submission dates across bulk plus pilot extension span 2 October 2015 to 23 October 2026.

## Publication

No push/deployment is authorized or performed. Public 2.2.0 remains unchanged. Runtime allowlist knows the city JS/CSS, but city data/publication packaging is not prepared. Future publication needs explicit authorization, a reviewed static/tiled city read model or suitable hosted read API, and a new size/performance/licence review. Never push the primary development branch's restricted historical geometry; continue from the clean public checkout specified in RELEASES.md.

## Static public edition 2.5.0

The user subsequently authorized publication. `prepare_city_publication.py` exports gzip-compressed source-only record shards, spatial tiles, token-prefix indexes, parcel memberships and a read-only pilot workbench. `city-data-client.js` implements the city and pilot reads without a server database. Current city map/search and pilot tabs work on static Pages; review notes/status remain local and public writes are disabled. The public catalogue contains 491,895 city entities/source identities, including 226,951 property/group identities, plus the preserved 24,884-record pilot read model. All generated files are explicitly manifest-allowlisted and recursively checked for local/private fields. Neither local SQLite database nor raw downloads are copied. Final deployment evidence belongs in RELEASES.md.
