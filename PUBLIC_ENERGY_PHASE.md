# Public-data phase — property, demand and solar

**Historical phase:** on 23 October 2026 the user pivoted to refined parcel/property data, prioritising subalterno identity and entrance links. `PARCEL_DATA_PHASE.md` now controls the active work. Energy calculations/data described below are preserved, with prominent energy navigation removed.

Local version: **2.0.0-dev.3**, 22 October 2026 (Europe/Berlin).

The user's current scope is the four steps proposed in chat: (1) a joined property investigation view, (2) public-data electricity-demand estimates, (3) rooftop solar screening and (4) annual/monthly comparisons. **Company-data integration is deferred and removed from the active interface. No v2 publication or push is authorized.** These four steps are a current delivery phase, not a renumbering of the original six-priority roadmap.

## What is available locally

Open `http://127.0.0.1:8765/#lotto-1175-434` and select **Demand & solar / Domanda e solare**. Start both local services with `serve-v2.bat` if needed.

- Select a parcel, building or attested property. The property register's analysis button preserves the selected property; returning to evidence preserves it too.
- Inspect cadastral identity, reported floor/area, certificate count, candidate/reviewed physical links, GIS building attributes, allocated ISTAT dwellings and civic entrances. Entrance buttons open the existing embedded Street View, including the upper-left resize control.
- Compare twelve monthly electricity-demand and potential-PV values, annual totals and monthly accounting balances. Edit the domestic reference power class, equivalent-supply assumption, usable-footprint percentage, density, orientation and weather scenario.
- A single, complete residential cadastral property starts with **one hypothetical equivalent domestic supply**, explicitly labelled as an assumption. Groups and whole-building attestations require an explicit count. Non-residential properties receive **no domestic-demand estimate**. This does not personalize a bill from APE area.
- Building/parcel defaults use the existing ISTAT 2023 household allocation. Incomplete geographic coverage stays null unless the user supplies an explicit scenario count. The household-to-supply equivalence is an assumption; fractional allocations do not identify apartments.
- Apartment PV starts **unassigned**. Select a building explicitly and enter a share to compare allocated generation. Building selection does not accept an identity relationship. Each calculation is a standalone hypothetical allocation, not ownership or a cumulative share ledger; never sum independently configured apartment scenarios.
- Demand sensitivity defaults to ±30%; usable-footprint sensitivity to ±15 percentage points around the central 45%. These are editable scenario choices, **not fitted uncertainty estimates or confidence intervals**. They do not cover all uncertainty in occupancy, geometry, shading, existing PV or usage.
- Download twelve-month CSV or a JSON snapshot with assumptions, input origins, source identifiers, provenance and limits. Unknowns export blank/null, distinct from zero. JSON and CSV totals were checked against an actual Chrome download.
- Company contract buttons, POD-template copy controls and generated blank POD-template files were removed from the active runtime. Historical documentation, v1 artifacts and the unused future private-schema design are preserved; no actual company data was present or deleted.

## Newly processed public evidence

### ARERA 2025 regional demand

Official source: https://www.arera.it/dati-e-statistiche/dettaglio/analisi-dei-consumi-dei-clienti-domestici

Workbook archive: https://www.arera.it/fileadmin/allegati/dati/monitoraggioretail/Dati_regione_2025.zip

The source page and its attachment definitions were verified through Chrome. The previously cached archive was processed more fully:

| Piemonte resident cohort, all markets | Sum of monthly means, kWh |
|---|---:|
| >0–1.5 kW | 452.868 |
| >1.5–3 kW | 1,609.908 |
| >3–4.5 kW | 2,797.221 |
| >4.5–6 kW | 3,473.248 |
| >6 kW | 7,002.133 |

There are **five** power classes in the retained source rows. Each has exactly twelve monthly rows and reconciles with the source annual row. They are different supply populations, not bounds of an apartment confidence interval. The customer's actual power class is unknown unless independently verified; the menu is a scenario choice.

Also retained **936 hourly reference bins** for the >1.5–3 kW class: thirteen periods (annual plus twelve months), three original day types and 24 source hour labels. Hourly means concern hourly-treated customers; monthly means concern a broader population. The interface keeps Ora1–Ora24 labels and does not infer an unverified UTC/DST mapping or holidays. The chart is a separate reference, **not a simultaneous demand-versus-PV calculation**.

Prepared read model: `data/public_demand_profiles.json`. SHA256 and archive-member names retained; raw archive stays in ignored `_raw/`.

### ISTAT municipal energy series, reference 2024

Published **29 July 2026**:
https://www.istat.it/comunicato-stampa/trasformazioni-e-innovazioni-nei-consumi-elettrici-delle-citta-capoluogo-anno-2024/

Actual workbook acquired:
https://www.istat.it/wp-content/uploads/2026/07/ENERGIA_serie_storiche-1.xlsx

Six Torino series are retained with original table titles, years, units and notes: domestic electricity per 100 residents and in total (toe), PV installation count, installed MW, net PV GWh and self-consumed PV GWh. Examples for 2024: **2,976 PV installations; 56.632861 MW installed; 44.373635 GWh net PV generation**. These are whole-municipality statistics, derived by ISTAT from the identified administrative sources. They do not locate existing panels on individual pilot roofs and are not distributed into apartment estimates.

Prepared read model: `data/torino_energy_context.json`. The workbook checksum and original notes remain inspectable. No toe-to-kWh conversion is used in the property calculation.

### JRC PVGIS additional weather-year calculations

API parameters verified through the official documentation in Chrome:
https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/using-pvgis-5/api-non-interactive-service_en

Downloaded **four × 8,760 modelled hourly power samples** from PVGIS 5.3 `seriescalc`, SARAH3, weather year 2023, 45.078/7.654, 1 kWp, 14% system losses, terrain horizon. Timestamps are unique and consecutive at one-hour steps. Power P in W is integrated at 1 h / 1,000 into kWh; monthly bins follow source timestamps. Original hourly responses stay in `_raw/pvgis/hourly-2023-*.json`.

| Assumed orientation | Modelled 2023 kWh/kWp |
|---|---:|
| South 30° | 1,375.88328 |
| East 30° | 1,061.25679 |
| West 30° | 1,050.73661 |
| Horizontal 0° | 1,113.42253 |

Prepared read model: `data/solar_weather_2023.json`. The existing 2005–2023 PVcalc climatology stays separately selectable. Annual calculations sum the displayed monthly source values; tiny differences from rounded PVcalc E_y are expected. Do not combine 2023 weather and 2025 customer averages into a claim of one observed year.

## Material limits

- These are source-backed **screening scenarios**, not actual apartment consumption or installed generation.
- Real roof planes, roof obstacles, urban shadow geometry, existing installations and structural/legal suitability remain unresolved. The 152 ARPA height footprints and eight LiDAR index tiles described in `V2_PROGRESS.md` do not provide verified LoD2/2.5 roofs. Potential PV uses GIS footprint proxies and explicit assumptions.
- The original two PDFs remain the only individually inspected APEs. Their standard-use energy is not added to household electricity, and the grouped 8+9 record retains one total.
- Annual ratios and positive monthly net balances do not establish self-consumption, export, self-sufficiency or CER shared energy. Hourly source alignment must be resolved before modelling simultaneity.
- Heating, cooling, EV charging and common services have no separate end-use model here. ARERA averages can already include these uses; no guessed loads are added on top.
- No new assumption that every property has a certificate or that all internal identities are unique. The register's uncertainty and alias-review workflow remain relevant.
- Third-party rights stay with the providers. The publication allowlist still targets v1; a future authorized v2 release must review and add approved assets explicitly, excluding raw downloads, review data and unresolved redistribution rights. Nothing was pushed.

## Reproduce and verify

```text
py scripts/prepare_public_energy.py
node scripts/check-public-energy.cjs
node scripts/check-energy.cjs
py scripts/check_property_registry.py
```

The source processor validates monthly/annual reconciliation, unique hourly bins, unique/consecutive solar timestamps, sample counts and non-negative source values. Calculation checks cover missing versus zero scopes, unassigned PV, invalid shares, monthly conservation, sensitivity ordering and independent integrations of all four raw solar files. Existing source/registry checks remain required.

Chrome QA covers source research, register→property→analysis navigation, explicit PV shares, weather switching, grouped non-residential withholding, building scope, IT/EN, exports, entrance→Street View, and phone overflow. All scenario examples are hypothetical and do not accept relationship-review decisions. Detailed roof modelling and validated hourly matching remain unfinished.

Final verification: all new runtime/data URLs returned HTTP 200; 393 px phone layout had equal scroll/client width after the overflow repair; the new JSON/CSV and revised parcel ZIP were downloaded through Chrome and inspected successfully. No company/POD template is present in that generated ZIP. Source/calculation and registry checks passed. Local screenshot: `output/qa/v2-public-energy.png` (ignored). No application errors were captured in the final browser check. All temporary viewport overrides were cleared after QA.
