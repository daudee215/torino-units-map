# Releases and deployment

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
