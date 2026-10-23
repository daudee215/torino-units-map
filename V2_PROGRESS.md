# Local v2 — priorities 1, 2 and 3

Snapshot: 22 October 2026. **Local only. Do not push or publish until the user declares v2 finished.**

**Newer local phase:** `PUBLIC_ENERGY_PHASE.md` covers `2.0.0-dev.3`: the public-data property/demand/solar workspace, additional institutional source processing and monthly comparison exports. Company integration is deferred and removed from the active controls. The section below preserves the previous inventory/roof milestone; its final statement that all priorities 4–6 are future work is now superseded for the public monthly screening part of priority 4.

## 1. Public property inventory

- Downloaded the published Regione Piemonte / CSI general APE file: 921,418 rows, 224,759 Torino rows, 20,985 rows selected by the pilot's existing sheet/parcel keys. The retained JSON excludes contacts, declarations and free-text notes.
- Official catalog: [general APE data](https://www.dati.gov.it/view-dataset/dataset_id/dettaglio-attestato-di-prestazione-energetica-ape-sezione-dati-generali). Download and source checksum are recorded in `data/ape_bulk_general.json`; license is CC BY 4.0. The catalog's modification date is stale (2019); the actual latest Torino submission in the downloaded file is **2026-07-31**.
- Used the public SIPEE citizen UI in Chrome to verify its address, street and cadastral requests. Acquired all 196 pilot street queries, with official address normalization. Twenty-six queries returned the observed 500-row limit and remain explicitly flagged. Live results supplement the older bulk snapshot; they do not establish complete historical coverage.
- Current registry: **25,400 distinct certificate entities**, **23,501 property/group identities**, evidence on **3,101 / 6,361 parcels**. These are not verified apartment counts. Only the original two PDFs were individually inspected.
- Counts refer to internal evidence entities after the implemented matching, not a legally verified unique-certificate or apartment inventory. Unresolved source identities can still represent duplicates; 252 section-equivalence relationship proposals are available for review. Accepted proposals preserve the original observations rather than silently rewriting totals.
- Reconciled 14,056 bulk certificate IDs with live records using the observed encoded certificate key, submission date and corroborating cadastral members. Equal date/floor/area alone is insufficient: actual counterexamples were found and kept separate. Basements, floor zero, missing values, grouped properties and certificate expiry retain their meanings.
- Blank, dash and declared cadastral sections remain distinct. Unknown municipality/cadastral records are held in `data/registry/unmatched.json`, not silently assigned to Torino. Its count includes records returned for entire streets outside the pilot; it is not a pilot apartment denominator.

## 2. Persistent relationships and review

- New **Property register / Registro immobili** workspace, reached from the main tab bar or parcel details. Search by parcel or civic address, inspect the source fields/history and compare section aliases.
- SQLite: `output/registry/properties.sqlite` (ignored). Contains typed GIS entities, properties, certificates, cadastral members, source runs, candidate relationships and an append-only review ledger. Integrity and foreign-key checks pass.
- Exact source cadastral relationships are separated from proposed property→entrance, property→building and property→property equivalence relationships. Inherited GIS/proximity assignments remain proposals. Accept/reject/reopen decisions, notes and optional validity dates persist locally; unknown dates stay null. Source refreshes preserve review events.
- Accepting an identity-equivalence proposal does **not** silently merge source records, sum energy or delete competing evidence. Full entity-resolution decisions remain reviewable.
- Local review service: `http://127.0.0.1:8766`. Exact local Host/Origin checks, JSON-only bounded writes and existing-link validation prevent arbitrary writes. No meters or company data are stored here. `scripts/private_meter_schema.sql` is a contract for a future **separate private** database, with many-to-many validity-dated meter links.
- Public-source CSV package: `data/download/torino_property_registry_v2.zip`. Exports source facts/proposals and provenance; excludes the review ledger, review notes and all future company data. The existing v1 GIS ZIP remains a separate baseline product.

## 3. Roof/LoD2 investigation — actual data gap remains

- ARPA's real height service was queried for a small pilot tile: **152 2D footprints**, all with DES `To`; **19** match existing footprints at IoU ≥ 0.8. Metadata traces Torino eaves heights to the municipal 2015 technical map. This is **height evidence, not roof planes**. No automatic transfer of heights was made to weak geometry matches. Absolute vertical datum remains unverified. The map-service license URL returned 404; the inspected geometry stays local and outside the publication allowlist.
- [MASE's official PST service](https://gn.mase.gov.it/portale/distribuzione-dati-pst) states CC BY 4.0 and GeoTIFF DTM/DSM First/DSM Last downloads. Its public [WFS catalog](https://gn.mase.gov.it/portale/wfs) links a working LiDAR tile index. The pilot query returns **eight advertised 1 m tiles**, Contract 140. Tile `D45070765_0101` includes the example parcel. Raw date `080623` is preserved; its format has not been confirmed.
- **Index coverage is not valid raster-pixel coverage.** The download viewer's configured `/core/api/pst-ms/ogc-services` endpoint returned HTTP 404. No DSM/DTM pixels, co-registered height grid or roof reconstruction have been acquired from that route. Do not claim LoD2/2.5 availability from the index alone.
- [Turin3D](https://huggingface.co/datasets/links-ads/Turin3D) is genuine aerial LiDAR from January 2022, but the [original paper §3.3](https://arxiv.org/html/2504.05882v1) places the released area in **San Salvario**, outside this pilot. Its 1.39 GB archive was not downloaded.
- Regional DSM ICE 2009–2011 metadata specifies a 5 m grid and CC BY 4.0, but no raster distribution was recovered from that metadata record. The municipal DBGT portal remained unreachable. Neither establishes surveyed pilot roofs.
- The register shows these findings and can open the ARPA sample plus MASE index outlines on the map. The existing 3D scene remains explicitly LoD1-style. No CityGML roof solids or apartment interiors were fabricated.

## Run and reproduce

Double-click `serve-v2.bat` to start the static app on 8765 and the local review service on 8766 if not already running. Both bind to loopback. Logs are under `output/ingestion/`.

```text
py scripts/fetch_bulk_ape.py
py scripts/fetch_property_inventory.py --retry-unresolved
py scripts/build_property_registry.py
py scripts/fetch_roof_reference.py
py scripts/prepare_roof_evidence.py
py scripts/check_property_registry.py
py scripts/build_registry_package.py
node scripts/check-energy.cjs
```

Raw sources are cached in `_raw/`; the bulk CSV is approximately 575 MB. Certificate eligibility is evaluated against the explicit reference date in `build_property_registry.py` (2026-10-22 for this snapshot). Update that date deliberately for a new dated run.

Browser verification covers IT/EN, parcel/property selection, source observations, dated review save/reset, and map/Street View navigation. Automated review checks are reset to **unreviewed** and are not human confirmations. See `output/qa/` for local evidence. No v2 updates have been pushed.

Final QA: 390×844 phone layout had no horizontal overflow; Street View stayed within the map. Height/index layers can be switched off in Layers. The upper-left Street View resize handle remains available. Desktop screenshot: `output/qa/v2-property-register.png`. No application errors were captured during the final checks.

The publication allowlist/workflow still targets v1 runtime assets. Preparing v2 for a future authorized release must explicitly add the new register assets and approved datasets, keep the review database and raw downloads excluded, and resolve or exclude ARPA sample redistribution rights. Do not publish the local tree wholesale.

Next roof-data dependency: acquire actual matching DSM/DTM or LAS/LAZ data through a working provider route, verify valid pixels, dates, horizontal/vertical references and units, and test one roof before attempting district reconstruction. Priorities 4–6 remain future work; this is not a completed energy platform.
