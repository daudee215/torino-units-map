# Public-data refinement plan — 23 October 2026

Research for the user's request to exploit Torino public data as fully as possible. Current priority remains property/subalterno identity and entrance links; energy and company data remain deferred. This note does not authorize another publication. Browser research used the Chrome extension. No new source below has been integrated into the application in this research pass.

## Verified acquisition: ANNCSU Piemonte

- Official documentation: https://www.anncsu.gov.it/it/consultazione-dellarchivio/open-data/
- Official download index: https://www.anncsu.gov.it/it/consultazione-dellarchivio/open-data/Accedi-ai-servizi-di-dowload-massivo-in-Open-data/
- Observed Piemonte address endpoint: https://anncsu.open.agenziaentrate.gov.it/age-inspire/opendata/anncsu/getds.php?INDIR_PIEM
- Download returned HTTP 200; archive member `INDIR_PIEM_20260915.csv`. Local raw ZIP: `_raw/anncsu/INDIR_PIEM_download.zip` (ignored; not public).
- 1,707,892 regional rows; 109,700 rows selected by Torino municipality L219 / ISTAT 001272. These are source rows, not a deduplicated count of homes or entrances.
- All Torino rows contain national street identifier, municipal street code, street name, access identifier and civic number. 68,509 contain an ESPONENTE; only 2 contain CODICE_COMUNALE_ACCESSO.
- None of the 109,700 Torino rows supplies COORD_X_COMUNE, COORD_Y_COMUNE, QUOTA or METODO. This file cannot locate entrances by itself.
- Documentation says monthly CSV/ZIP publication. Dataset filename date is 15 September 2026, not the retrieval date.
- Next: establish key uniqueness and duplicates, interpret suffix/specificity semantics, compare street codes with municipal civics, inspect unmatched addresses and dates. Do not join civic numbers alone across streets. Check the exact redistribution licence in source metadata before adding derived records to the public allowlist.

## Verified municipal civic metadata; file not acquired in this pass

https://www.geoportale.piemonte.it/geonetwork/srv/api/records/c_l219:8987bd22-fea8-44e0-a900-7a6400032b30

Torino's civic-number catalogue advertises revision 30 September 2026, quarterly updates, CC BY 4.0, point locations originating from its 1:1,000 technical map. It excludes conventional streets and inactive civic numbers. The complete shapefile is explicitly restricted; public simplified CSV downloads are separately advertised.

Observed public WGS84 CSV: http://geoportale.comune.torino.it/geodati/civici_WGS84_EPSG4326_csv.csv

Next: acquire the current public CSV, inspect actual fields, compare with inherited civics and ANNCSU. Preserve municipal IDs, civic letters, discrepancies and snapshot dates. Do not assume its schema or current row count from catalogue metadata alone.

## Verified BDTRE 2026 edition metadata; Torino package not acquired

https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:da9b12ba-866a-4f0f-8704-5b7b753e4f15

Annual municipal GeoPackage 1.4.0 distribution, data updated 31 March 2026, explicit CC BY 4.0. Inspect the actual Torino package before promising populated tables or usable relationships. Its sources include cadastral data, so overlap with cadastral geometry is not necessarily independent confirmation.

Related class semantics:

- CIVICO: https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:5a94b0e3-6385-4c5a-a361-5f8a3db1ff75
- EDIFC: https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:753327be-7ef2-4aa6-bf49-19e9eb6e0af4

The CIVICO definition separates the address from an external access, which may be direct or indirect. Distribution relates it to ACC_PC point geometry and TP_STR street naming. A civic address is not automatically a particular building doorway; one access can serve a courtyard or complex. Address terminology such as a civic 'subalterno' must not be confused with the cadastral subalterno. Legacy class records have older data vintages and unknown reuse conditions; the explicit 2026 edition licence must be associated with the actual acquired edition.

Next: inspect Torino table list, schema, non-null coverage, foreign keys, geometries and acquisition dates; test access/building relations in San Donato. No verified LoD2/2.5 roofs were found in this research pass.

## Verified richer, selective documentary evidence

Municipal 2024 technical property sheet:
https://risorse.comune.torino.it/comuneaffitta/bm~doc/5_2024_allegato_1_scheda_tecnico_patrimoniale_rossana_24.pdf

Downloaded transiently for text inspection (HTTP 200). Explicitly describes Torino sheet 1289 parcel 135, subalterni 15, 16, 17 and 18; includes reported floor, category, cadastral area and descriptions of access. It distinguishes courtyard portions from the premises. This is outside the San Donato pilot and demonstrates a source type, not newly integrated pilot coverage. The public document is not a uniform open-data unit census; do not republish raw documents, personal information or plans by default.

Next: investigate municipal sale/concession technical sheets for exact pilot cadastral keys. Record page, date, source, property scope and the precise supported relationship. Do not infer that every property has such a document or that historical descriptions remain current.

## Existing APE data is underused for property evidence

Audit of existing `data/ape_bulk_general.json`: 20,985 rows (not unique properties).

- `interno`: 2,300 nonempty source values, including 808 '-', 444 '0' and 101 '.'. Nonempty is not necessarily a usable interior number. The current registry constructor does not preserve this field in the normalized certificate record.
- `piano`: 20,659 nonempty values.
- `sup_riscaldata`: 20,924 nonempty values; heated area is not interchangeable with cadastral area.
- Construction year and descriptive use are populated but remain certificate declarations; construction years can refer to the building, not a distinct unit.
- `nr_um` is already retained as a declared building-unit field; never interpret it as a count of units actually identified by the project.

Next: retain raw interno and normalize placeholders with explicit rules; preserve full civic syntax, source scope and conflicting certificate observations. Do not split grouped certificates or use an interior number as a cadastral key. Extract property evidence without resuming energy calculation work.

## Recommended implementation order

1. Address reconciliation: fresh municipal civic geometry + ANNCSU street/access identifiers + inherited civic IDs. Build a discrepancy table before replacing existing links.
2. Inspect and integrate relevant BDTRE 2026 access/building relationships. Review inherited nearest-25m and first-duplicate spatial matching; retain competing candidates rather than arbitrary certainty.
3. Recover property detail already present in APE (especially interno); resolve the 26 capped street searches through verified targeted public queries. Bulk and live APE are one source lineage.
4. Add selective documentary confirmation, starting with ambiguous pilot parcels. Show exactly what each document establishes.
5. Build a representative manually checked sample and report source presence, identity completeness and entrance-link support separately. Unknown denominators must stay unknown.
6. Scale the same ingestion and QA pipeline to Torino; split map files by area/zoom while preserving citywide identities. Avoid a hand-curated San Donato-only data model.

The desired product is a dated parcel dossier linking parcels, buildings, addresses/accesses and observed cadastral properties. It must distinguish reported information, geometric proposals, review decisions and unknowns. Public data does not yet establish complete interior apartment polygons, actual occupancy or a verified citywide count of cadastral units.
