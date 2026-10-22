# San Donato apartment energy atlas

## Agreed scope
Public data first, for the full available San Donato study area. Preserve the original goal: parcel → building → civic number and lettered entrance → individual apartment → POD. Company consumption data comes later. Never label inferred apartments, consumption or PV generation as observed.

## Work queue
- [x] Read the handoff, all application files and all four data pipeline scripts.
- [x] Inspect local GIS schemas and downloaded ISTAT archives.
- [x] Identify incompatible legacy section identifiers; do not join census vintages by section number alone.
- [x] Fix the temporary full-height layout regression during workspace construction.
- [x] Research advanced official datasets in Chrome before choosing further models.
- [x] Acquire compatible 2021 census geometry and 2023 dwelling counts; validate geographic joins.
- [x] Verify public APE search and inspect two PDFs; reject invalid coordinates and preserve grouped-unit semantics.
- [x] Verify DSM/LiDAR metadata, acquire PVGIS scenarios and four primary-substation polygons.
- [x] Produce a source inventory recording dates, resolution, join keys and gaps in DATA_REVIEW.md and the Data & method view.
- [x] Integrate usable public data and preserve original observations separately from estimates.
- [x] Finish Italian/English workspace, feature query, paginated table and data-model view.
- [x] Add automatic entrance Street View in a bottom-right window with close/minimize/restore and resizing.
- [x] Add inspected apartment/group records with explicit consumption provenance and optional PV allocation shares.
- [x] Prepare separate unit, meter, link and reading entities in a downloadable company-data contract.
- [x] Verify calculations, joins, CSV export, language switching, Street View, 3D rendering and phone-size layout.

## Further data acquisition and later expansion
- [ ] Expand individually inspected APE coverage beyond the two example PDFs; deduplicate by cadastral unit and validity. No complete San Donato apartment inventory is claimed.
- [ ] Verify reusable rights for additional datasets before any external publication.
- [ ] Obtain an actual roof-plane/LoD2/2.5 dataset if available. Current view is LoD1-style, not surveyed roof geometry.
- [ ] Verify existing PV-system data and newer/high-resolution roof data; do not infer installed production from roof potential.
- [ ] Import company consumption when supplied, with private storage and validated POD-to-unit relationships.
- [ ] Extend source coverage to all Torino and replace full-area static loading with spatial loading.

## Key limits
- Existing public layers contain no apartment subalterni or PODs.
- APE certificate count is not a confirmed minimum unit count: renewals and duplicates must be resolved.
- Annual PV/demand ratio is not hourly self-consumption or CER shared energy.
- Footprint is a roof proxy, not measured usable roof geometry.
- Local GIS extent includes part of Campidoglio; do not claim an official San Donato boundary without a verified neighborhood polygon.
