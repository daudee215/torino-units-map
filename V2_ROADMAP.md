# Version two — six agreed priorities

The user approved these priorities after reviewing version one and calling it too basic. Preserve the public version-one baseline, then implement this roadmap. Research only counts as integration when source access, coverage, identifiers and reuse conditions have been verified.

## 1. San Donato apartment/property inventory

Build a repeatable ingestion process for available public SIPEE records across the pilot. Retain original source identifiers, submission/expiry/cancellation states, source dates and acquisition provenance. Resolve renewals and multiple-subalterno properties before counting units. Add floor, usable area, use category and energy indicators when actually present. Do not assume every property has an APE or invent records for the remainder.

Acceptance: district-wide acquisition coverage is inspectable by parcel and entrance; source records and deduplicated entities are separately counted; missing/ambiguous records are reviewable. Public-record absence is not treated as apartment absence.

## 2. Relationship database and review workflow

Replace ad hoc lookups with persistent parcel, building, entrance, cadastral-property, certificate, meter and time-series entities. Preserve many-to-many relationships and validity dates. Keep competing matches and their evidence instead of overwriting uncertainty. Provide a human review workflow for ambiguous joins.

Acceptance: every apartment/property detail can trace its links and source evidence; a certificate spanning several subalterni retains one energy total; future meter links can represent common services and multiple supplies per property. Public read models and private future meter data remain separate.

## 3. Verified roof geometry and solar potential

Seek actual downloadable roof planes, LiDAR point clouds or suitable DSM/DTM pairs for Torino. Verify pilot coverage, resolution, vertical reference, dates and reuse conditions. Test on a small tile before acquiring large volumes. Use roof area, pitch, orientation, obstacles and urban shading where supported. Check existing PV installations separately from potential.

Acceptance: roof geometry has provenance and coverage flags; existing systems and proposed capacity are distinct; LoD1 approximations remain labelled when better data is absent. Never relabel an extrusion as LoD2/2.5.

## 4. Time-resolved apartment energy scenarios

Use public consumption profiles with documented population and sampling scope, plus hourly PV production for explicit weather/roof scenarios. Support annual/monthly/hourly views as the evidence permits. Calculate simultaneous demand/generation, surplus and shortfall. Prepare private company-data import with time-zone/DST, interval, unit, duplicate and meter-identity validation.

Acceptance: kWh and kW stay distinct; standard-use APE figures remain separate from household withdrawal and measurements; hourly sharing is not inferred from annual ratios. Every allocation method and uncertainty is visible and exportable.

## 5. Building investigation workspace

Keep the white ArcGIS-style IT/EN interface. Make a building click reveal linked parcels, entrances, inspected properties, estimated missing coverage, source documents, energy scenarios and unresolved joins together. Preserve the automatic, closable/minimizable Street View utility panel. Add clear comparison and evidence inspection rather than additional decorative tiles.

Acceptance: a user can follow parcel → building → lettered entrance → property → future POD without losing context; can distinguish observations, estimates and unknowns; can review a suspect link and export the evidence.

## 6. Whole-Torino architecture and coverage dashboard

Use municipality-stable identifiers, configurable extents and versioned ingestion runs. Add spatial indexing, bounding-box/tile loading and a deployment path suitable for a growing dataset. Build a coverage dashboard that distinguishes source acquisition, spatial matching, deduplication, apartment evidence and meter readiness. Never show a completion percentage when its denominator is unknown.

Acceptance: a second Torino area can be loaded without duplicating implementation; the client does not download the entire future city dataset to inspect one street; source refreshes are reproducible; the published v1 baseline remains recoverable.

## Order of work

Start with source/API feasibility and the relationship schema (1–2). Establish roof-data feasibility in parallel within the same workflow (3). Then build the time-resolved model (4), investigation UI (5) and scalable loading/coverage view (6). Integrate and test each milestone. Do not claim unavailable source data has been obtained merely because a downloader, schema or interface was created.
