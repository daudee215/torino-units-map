# Reviewed public-data integration — 22 October 2026

Publication note: attribution remains with each original provider; the project does not grant a blanket license over third-party data. The GSE public web-map item has an empty `licenseInfo` field (checked 22 October 2026); public query access is not an explicit open-data license. Its indicative pilot extract preserves source attribution. Verify further redistribution terms before expanded reuse. Consultation PDFs and certifier contact details are excluded from publication.

This is a San Donato / Campidoglio rectangle pilot, not an official neighbourhood boundary or a complete Torino inventory. Research used the Chrome extension and original institutional pages. Raw source files are retained in `_raw/`, which is ignored by Git.

## Accepted inputs

| Input | Grain and date | How used | Material limitation |
|---|---|---|---|
| Existing cadastral WFS / Torino technical map / civic-number layers | Parcel, building polygon, entrance point; source vintages not fully specified in inherited files | Existing map and stable cadastral/building/entrance identifiers | Proximity matches and floor counts are estimates; no apartment geometry or PODs |
| ISTAT R01_21 polygons + Torino Comuni_2023 workbook | 2021 section geometry, 2023 dwelling/household counts | Spatial join using building representative points; allocate section counts by residential GFA | 541 intersecting sections, 431 at least 99.5% within rectangle, 396 with 2023 rows. 3,731 buildings allocated; 395 residential buildings in partial sections excluded; 954 non-residential buildings not allocated. Missing values stay null |
| ARERA regional 2025 workbook | Resident domestic supplies in Piemonte, >1.5–3 kW, all markets, monthly means | 12 monthly rows sum to 1,609.908 kWh and match the original annual row | Not an apartment bill, not a fixed cohort, not a household/POD census. Common services, commercial loads and other power classes excluded |
| PVGIS 5.3 SARAH3 | One representative location, long-term monthly and annual model | 1 kWp, 14% losses; south/east/west at 30° and horizontal at 0° | Annual yields: 1,338.88 / 1,044.27 / 1,043.65 / 1,097.53 kWh/kWp. Not measured generation; no resolved urban shading or surveyed roofs |
| SIPEE public consultation PDFs | Two certificate records at Via Cordero di Pamparato 17 | Cadastral keys and energy fields transcribed from pages 1–3 | Only one address sampled. One residential unit (75); one non-residential property referencing subalterni 8+9. APE standard-use energy is not meter consumption; the property total is not duplicated per subalterno |
| GSE AC 2025–2027 public query service | Four areas intersecting the rectangle | Optional map overlay and entrance spatial membership | Coordinate-based area is indicative; official GSE POD lookup takes precedence near boundaries. Source attribution retained; no claim of legal CER eligibility |

## Rejected or withheld interpretations

- Legacy `SEZCENS` numbers were not joined to newer census data by number. Only 377/540 matched the 2011 archive, and only 17 household totals agreed; the geographic source vintages were incompatible.
- The downloaded ARERA provincial 2023 archive contains BTA/ATECO non-domestic rows. It was not used as a residential benchmark.
- APE coordinates 45.116667, 7.716667 are outside the pilot and conflict with the cadastral parcel/address. They were rejected for geolocation.
- APE certificate counts are not a confirmed minimum apartment count: renewals, cancelled records and grouped units matter. The portal returned 15 records at the example address; only two PDFs were inspected.
- The two PDFs disagree on a declared building-unit count (35 versus 1) and differ from inherited construction-period attributes. No single authoritative building total or construction date was inferred.
- ARPA Edifici 3D 2017 metadata documents real Torino eaves-height attributes from the 2015 technical map, plus explicit invalid/estimated codes. That dataset was not imported. It does not by itself establish LoD2 roof surfaces.
- Piemonte DSM ICE 2009–2011 metadata describes a 5 m grid with ±0.30 m vertical accuracy. Raster data was not imported; this resolution is not sufficient for detailed small roof structures.
- The newly indexed municipal DBGT page could not be read: HTTP was blocked and HTTPS closed the connection. Downloadable LoD2/2.5 coverage remains unverified.

## Reproduction and checks

1. `py scripts/fetch_energy_sources.py`
2. `py scripts/enrich_public_data.py`
3. `py scripts/prepare_demand_benchmark.py`
4. `py scripts/prepare_energy_sources.py` (requires the two reviewed PDF transcriptions in that script; raw PDFs stay ignored)
5. `node scripts/check-energy.cjs`
6. `py scripts/build_energy_package.py` — writes the enhanced GeoPackage/CSV ZIP. Six GIS layers use EPSG:32632; APE geometry is explicitly an entrance proxy. SQLite integrity and ZIP CRC checks passed.

The census processor asserts that allocated counts conserve each eligible section total before display rounding. It rejects ambiguous building-to-section joins. JavaScript checks cover kW/kWh calculations, zero denominators, source totals, missing electricity values and grouped certificate semantics.

The 3D view uses existing `ALT_EDIFIC` where valid (4,977 buildings). The other 103 heights use an explicit 3 m/floor assumption. It is a flat-roof LoD1-style extrusion, not a certified CityGML or surveyed LoD2/2.5 model. Actual apartment interiors remain unknown.

The UI exports a company-data contract with separate unit, meter, many-to-many link and interval-reading entities. It does not contain fictional PODs or load company data into public static files. Whole-Torino work will need complete source layers, spatial loading and a private meter-data backend.

The PDF checkboxes mark both inspected attestations as individual properties (`Unità immobiliare`). The non-residential record lists subalterno 8 and additional subalterno 9. This is stored as `unit_multi_subalterno`; no claim is made that these identifiers represent two separate apartments.
