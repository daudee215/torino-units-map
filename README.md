**Current correction — 23 October 2026:** version `2.5.1` fixes saved `#lotto-…` links opening the San Donato pilot and adds all 82,434 parcel outlines at city overview zoom, with North/South controls. Read `WHOLE_TORINO_PHASE.md`. This is a correction to the user-authorized published citywide release; unrelated future work remains local.

**Published and verified — 23 October 2026:** whole-Torino release **2.5.0** is live at https://daudee215.github.io/torino-units-map/ . Runtime commit `418e59a1250af0f56ae55bcadfae59902ba208d0`; successful build/deploy: https://github.com/daudee215/torino-units-map/actions/runs/39995396107 . Citywide geometry/search and the read-only 24,884-record pilot workbench are online. Raw archives, local databases/reviews and excluded ARPA geometry are not published. Source counts are not verified apartment counts; legal entrances remain unverified. Further development returns to local-only until separately authorized.

**Publication authorization — 23 October 2026:** the user requested publishing the whole-Torino version to the existing GitHub repository and Pages site. Prepare release `2.5.0` from clean public history. Include the reviewed source-only static city tiles/search/record shards and pilot workbench; exclude raw archives, SQLite databases, local workflow/notes and unresolved-licence ARPA geometry. Public review remains disabled. Later development returns to local-only.

**Whole-Torino local expansion — 23 October 2026:** read [WHOLE_TORINO_PHASE.md](WHOLE_TORINO_PHASE.md). Local `2.5.0-dev.1` adds actual citywide AdE parcel geometry (82,434 distinct cartographic references), 63,402 BDTRE footprints, 119,108 municipal civic points and 226,951 property/source identities with bounded map/search loading. Existing pilot identities and ledgers remain preserved. These are source records, not verified apartments or legal entrance links. No new publication is authorized.

**Latest local phase — 23 October 2026:** read [PROPERTY_WORKSPACE_PHASE.md](PROPERTY_WORKSPACE_PHASE.md). Local `2.4.0-dev.1` adds the white property workspace, 178 searchable municipal-only references, 38 shared-key comparisons (31 APE records / 41 comparison rows), and two explicitly unresolved section cases. Case notes/status remain separate from source facts. Source/API and Chrome IT/EN/mobile/Street View/navigation checks passed. Published 2.2.0 is unchanged; no new push is authorized.

# Unità San Donato

**Release 2.2.0 — 23 October 2026:** property investigation with 24,706 property/group identities, 27,137 certificates, source-backed entrance alternatives, a 30-building review sample and municipal documentary/inventory references. Candidate access and historical evidence remain unconfirmed; this is not a complete apartment census. Online reviews are read-only. See `PROPERTY_VALIDATION_PHASE.md` and `RELEASES.md`. Earlier notes below preserve history.

**Latest release 2.1.0 (23 October 2026):** address evidence now connects municipal civic numbers with ANNCSU and BDTRE access candidates in the online Property register. Reported interior observations retain their provenance. The register contains 25,433 certificate records and 23,522 property/group identities, not a complete apartment census. Source-only address comparisons are static; review decisions remain local. See `ADDRESS_REFINEMENT_PHASE.md` and `RELEASES.md`. Future development remains local until separately authorized. Earlier release notes below preserve history.

**Public parcel-focused release `2.0.0` (authorized 23 October 2026):** [open the atlas](https://daudee215.github.io/torino-units-map/). The online property register is read-only and excludes local review notes, raw evidence and the ARPA sample geometry with unresolved reuse rights. Future development remains local until separately authorized. See `RELEASES.md` for deployment verification.

**Current direction — 23 October 2026 (`2.0.0-dev.4`):** refined parcel and property evidence, prioritising subalterno identities and entrance links. Open **Property register / Registro immobili** for the new parcel dossier and entrance drill-down. Further energy work is deferred; the earlier energy sections below describe preserved historical work. Read `PARCEL_DATA_PHASE.md`. Everything remains local at `http://127.0.0.1:8765/`; no v2 publication is authorized.

Mappa web dei lotti catastali di San Donato e Campidoglio (Torino) con edifici, numeri civici, evidenze immobiliari pubbliche e scenari di domanda elettrica e potenziale solare.

## Latest local phase · 2.0.0-dev.3

Open **Demand & solar / Domanda e solare** for parcel, building and property screening, explicit assumptions, monthly comparisons and CSV/JSON exports. Company-data integration is deferred and its active controls/templates have been removed. Start `serve-v2.bat`; use `http://127.0.0.1:8765/`. **Do not push or publish v2 yet.** Read `PUBLIC_ENERGY_PHASE.md` for newly processed ARERA/ISTAT/PVGIS sources, validation and limits. Actual LoD2/2.5 roofs and validated simultaneous hourly demand/generation remain unavailable.

## Energy workspace · 22 October 2026

The local application now uses a white ArcGIS-style interface with persistent IT/EN controls. It includes:

- An ISTAT 2023 dwelling-estimate map, based on spatial joins to official 2021 census polygons. Partial boundary sections remain unallocated.
- Parcel, building, entrance and inspected APE attribute tables with search, numeric filtering, sorting, pagination and CSV export.
- Automatic Google Street View in a resizable bottom-right window when an entrance is selected; close and minimize/restore controls stay inside the application.
- Two inspected public APE records at civic number 17: residential subalterno 75 and one non-residential property referencing subalterni 8+9. This is a partial public-document sample, not a complete apartment inventory.
- Electricity screening using the ARERA 2025 Piemonte resident 1.5–3 kW benchmark and four PVGIS 5.3 production scenarios. Unit/group PV shares are explicit, initially unassigned and saved locally in the browser.
- A 3D scene using source building-height attributes, with 3 m/floor fallbacks marked orange. This is a LoD1-style flat-roof extrusion; no surveyed LoD2/2.5 roofs or apartment interiors are claimed.
- A source/method view with coverage, limitations and public-evidence downloads.

See [DATA_REVIEW.md](DATA_REVIEW.md) for provenance and rejected interpretations, and [TODO.md](TODO.md) for the handoff queue. The pilot rectangle includes part of Campidoglio and is not an official San Donato neighbourhood boundary. Whole-Torino coverage is a future expansion, not already present in this checkout.

All core map, geometry, ZIP and 3D libraries are pinned in `vendor/`. Google Street View, web fonts and optional external basemaps still require an internet connection. Run the source preparation scripts listed in `DATA_REVIEW.md` to regenerate reviewed additions. Check calculations with `node scripts/check-energy.cjs`.

The updated download is `data/download/torino_sandonato_energy.zip`: a GeoPackage (EPSG:32632), six CSV tables, source benchmarks and the data review. The original baseline archive remains available under its original filename.

## Avvio in locale

Serve un server HTTP, perché la pagina carica i dati da `data/`. Aprire `index.html` come file non funziona.

```
py -m http.server 8765 --bind 127.0.0.1
```

oppure doppio clic su `serve.bat` (Windows), poi apri http://localhost:8765.

Per pubblicarla su GitHub Pages basta attivare Pages sul branch principale, cartella radice. Il file `.nojekyll` è già presente.

## Cosa c'è nella mappa

- Lotti catastali colorati per famiglie stimate, piani, ingressi o affidabilità, con filtro e trasparenza.
- Edifici principali della Carta Tecnica, ingressi civici (con lettere, scale e interni), sezioni di censimento.
- Etichette di particelle (da zoom 18,5) e civici (da 19,5).
- Ricerca per indirizzo o per foglio/particella (`1175/434`).
- Scheda del lotto con riferimento SISTER da copiare, evidenze degli ingressi, link diretto (`#lotto-1175-434`) e download del lotto.
- Selezione per poligono o per vista corrente, con riepilogo e download ZIP (GeoJSON e CSV).
- Elenco dei lotti nella vista ordinati per famiglie stimate, per decidere le visure.
- Mappe di base Esri (grigio chiaro, grigio scuro, ortofoto).
- Tasti: `/` per cercare, `D` per disegnare un'area, `Esc` per annullare.

## Dati

| File | Contenuto |
|---|---|
| `data/*.json` | Livelli per la mappa, coordinate in interi delta a 1e-6 gradi (circa 0,1 m) |
| `data/download/torino_sandonato_dati.zip` | GeoPackage completo (EPSG:32632) e CSV |

Fonti: cartografia catastale dell'Agenzia delle Entrate (WFS INSPIRE, CC BY 4.0); Carta Tecnica, numerazione civica e sezioni di censimento della Città di Torino (CC BY 4.0). Elaborazione del 22 ottobre 2026.

## Metodo

1. Le particelle vengono scaricate dal WFS dell'Agenzia delle Entrate a riquadri (il servizio non risponde su aree grandi) e unite per riferimento.
2. Gli edifici della Carta Tecnica (EPSG:3003) sono riproiettati in EPSG:32632 e traslati di −1,1 m est e +1,0 m nord. La traslazione è stimata cercando lo spostamento che minimizza l'area di 1.500 edifici sulle particelle stradali (dal 3,8% allo 0,95%). I civici sono già nel sistema catastale e non vengono spostati.
3. Ogni ingresso viene assegnato al lotto che lo contiene o al più vicino entro 25 m (i punti stanno sulla linea di facciata), poi all'edificio più vicino sullo stesso lotto.
4. Le famiglie di ogni sezione di censimento sono ripartite tra gli edifici residenziali in proporzione alla superficie lorda (impronta × piani). Correlazione tra superficie e famiglie per sezione: r = 0,81.
5. Le sezioni con meno di 40 o più di 250 m² per famiglia sono segnate ad affidabilità bassa.

Le famiglie stimate non sono unità catastali: mancano le abitazioni vuote e la ripartizione dipende dai piani della Carta Tecnica. I subalterni reali vengono dalle visure SISTER (Catasto Fabbricati, foglio e particella).

## Script

In `scripts/`, da eseguire in ordine:

1. `fetch_parcels.py` scarica le particelle a riquadri.
2. `analysis.py` unisce particelle, edifici, civici e sezioni e produce il GeoPackage.
3. `build_web.py` genera i file in `data/`.

Requisiti: Python 3.11 o successivo, geopandas, shapely, pyproj, lxml.

# Public website and continuation

For the latest **local-only v2**, read [V2_PROGRESS.md](V2_PROGRESS.md). Double-click `serve-v2.bat`, then open the new **Property register / Registro immobili** tab. V2 must stay local until the user declares it finished. Roof evidence currently includes heights and a LiDAR coverage index, not verified LoD2 roofs.

Public atlas: https://daudee215.github.io/torino-units-map/

Start the next chat with `HANDOFF.md`, then read `DATA_REVIEW.md`, `V2_ROADMAP.md` and `RELEASES.md`. Version one is preserved before the six-point version-two programme. GitHub Pages deploys only the explicit allowlist in `scripts/build_public_site.py`; raw evidence, generated output and future company measurements are excluded.
