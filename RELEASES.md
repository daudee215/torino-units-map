# Releases and deployment

## 2.0.0 — parcel/property identity release, 23 October 2026

The user authorized publication to the existing repository and GitHub Pages site. Includes the parcel identity dossier, subalterno search and investigation filters, per-entrance property lists with civic letters, and embedded Street View with upper-left resizing. Public review controls are read-only; local reviews and review notes are not published.

Publication uses an explicit runtime/data allowlist and source-only parcel read models. The ARPA geometry sample with unresolved redistribution rights is excluded from both this public release commit and Pages. Local development history and the v1.0.0 baseline remain preserved. Energy work stays deferred. Deployment verification follows the Pages workflow status and live browser checks.

## 2.0.0-dev.4 — local parcel/property identity pivot

23 October 2026. The user selected property/subalterno identity and entrance links as the priority, deferring energy development. Main navigation and map actions now prioritise the register. Added a parcel identity dossier with cadastral/address/floor search, investigation filters and per-entrance property drill-down preserving lettered civic numbers. Active counts exclude rejected/out-of-validity links without deleting review evidence. No new source-confirmed identities are claimed. See `PARCEL_DATA_PHASE.md`.

Local only. Earlier energy work and published v1 remain preserved; nothing is pushed or deployed.

## 2.0.0-dev.3 — local public-data energy phase

New **Demand & solar** workspace connects selected parcel/building/property evidence to explicit demand assumptions, footprint-based PV screening and annual/monthly comparisons. IT/EN controls, sensitivity ranges and source-backed CSV/JSON exports are included. Company/POD-template controls are removed from the active runtime; that integration is deferred.

Additional public evidence: five ARERA resident power cohorts with monthly/annual reconciliation, 936 hourly reference bins, six ISTAT Torino municipal series through 2024, and four PVGIS weather-year scenarios derived from 4 × 8,760 hourly power samples. Reference profiles are not used to claim simultaneous self-consumption; roof planes remain unverified. See `PUBLIC_ENERGY_PHASE.md` for provenance, formulas, checks and limits.

Local only; no push or deployment. Published v1 remains unchanged.

## 2.0.0-dev.2 — local property registry and roof evidence

Priorities 1–2 implemented as a source-backed inventory and local SQLite review workflow. New bilingual register exposes 25,400 certificate entities and 23,501 property/group identities, candidate physical/identity links, source differences, validity dates and source CSV exports. Private company data is not loaded.

Priority 3: inspected 152 ARPA height footprints and verified eight advertised 1 m MASE coverage-index tiles. Actual DSM/DTM download is blocked by the provider's configured endpoint returning 404. No verified LoD2/2.5 roofs are claimed. Details, sources and reproduction steps: `V2_PROGRESS.md`.

Local only. Existing public v1 is preserved. No v2 publication is authorized yet.

## 2.0.0-dev.1 — local development only

User instruction: all new work stays at `http://127.0.0.1:8765/`; publish v2 only when the user declares it finished. Added an upper-left Street View resize grip with pointer capture, map-area bounds, keyboard controls and IT/EN labels. Bottom-right anchoring and minimize/restore were verified in Chrome. No v2 changes have been pushed or deployed after that instruction.

## v1.0.0 — public baseline, 22 October 2026

Repository: https://github.com/daudee215/torino-units-map

Pages target: https://daudee215.github.io/torino-units-map/

Status: publicly deployed and verified over HTTPS on 22 October 2026.

Release tag `v1.0.0` preserves commit `908c3c1`. The current publication also includes the source-note/package follow-up `05fc84b`.

Deployment: https://github.com/daudee215/torino-units-map/actions/runs/39800420217 — Pages deployment status `succeed` for `05fc84bd1a229b2d420d9fb8ed4be84bc1d9a223`.

Verified: public index, metadata, census allocation, APE records, JavaScript and enhanced GIS download returned HTTP 200. Chrome loaded all 6,361 parcels, 5,080 buildings and 9,759 entrances; the apartment panel and automatically opened Street View worked, with no application errors captured. Screenshot: local `output/qa/github-pages-live.png` (ignored).

Scope: white ArcGIS-style IT/EN static prototype; original GIS layers; reviewed ISTAT/ARERA/PVGIS/GSE additions; two inspected public APE records; embedded Street View; attribute tables and downloads; LoD1-style height scene.

This release does not contain a complete San Donato apartment inventory, actual company consumption/PODs, or verified LoD2/2.5 roofs. See `HANDOFF.md` and `DATA_REVIEW.md`.

Version two is the six-point roadmap in `V2_ROADMAP.md` and should be developed separately from this stable baseline.

Work queue: https://github.com/daudee215/torino-units-map/milestone/1 — six open issues (#1–#6). These are planned improvements, not completed v2 integrations. Start with the repeatable apartment-source inventory and relationship database.
