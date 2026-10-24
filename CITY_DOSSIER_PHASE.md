# Whole-Torino parcel dossiers — local 2.6.0-dev.1

23 October 2026. User authorized all five proposed steps: a unified parcel dossier, property/entrance evidence, cross-city investigation, clearer exploration, and targeted public-source research. Development is local. Public 2.5.1 and the clean release checkout are unchanged. No push is authorized by this instruction.

## Implemented local workflow

At http://127.0.0.1:8765/?release=2.6.0-dev.1 select a parcel in Whole Torino. Its dossier combines full cartographic reference/components, source dates, property/source identity records, candidate BDTRE buildings, municipal civic points, and additional BDTRE access/volumetric records. Property cards expand; the full record retains original cadastral members, source scope, certificate dates and inventory observations. Property records paginate 50 at a time; related spatial/source records display at most 100 per type with totals. A filter explicitly applies to the displayed dossier page; the left-hand evidence filter applies across the whole city and respects address/key search and parcel membership.

Selecting an unambiguous property cartographic candidate highlights its source parcel. Multiple cartographic variants remain unresolved. Return links are shown only for records connected to the active dossier. Layer controls are expanded and the white inspector is wider. Complete IT/EN controls remain. Selecting a municipal civic or point access opens the existing embedded Street View panel, preserving upper-left resizing, minimize/restore and close. A civic coordinate is an imagery viewpoint, not evidence of a private doorway.

## Evidence method and grain

`build_city_dossiers.py` reads the source catalogue in read-only mode and creates a separate source-only inverse-link/evidence database. It does not read either local review ledger or modify the original catalogue. Exact normalized municipal street/civic candidates are retained for **every acquired certificate observation**, including older ones. Agreement between a civic's geometric parcel candidate and the property's sheet/parcel candidates supplies a second candidate signal. It does not establish section equivalence, cadastral access or physical apartment location. Lettered/scalal civic strings and IDs remain distinct. No nearest-civic fallback is applied. A group/whole-building address is not assigned separately to each member.

Mutually exclusive source classifications across 226,951 unchanged identities:

| Classification | Records |
|---|---:|
| No exact municipal address candidate in acquired observations | 98,397 |
| One address candidate, also spatially agreeing with a cartographic candidate | 57,915 |
| One address candidate without that spatial agreement | 70,502 |
| Multiple candidates or changed candidate sets across observations | 137 |

These all-observation categories differ from the older summary's latest-observation unique-address count. They are not independent accuracy scores or counts of verified apartments. Every current-access flag remains false. A single exact address outside the property's candidate parcels stays an address candidate with no spatial corroboration; it is not silently corrected.

## Cross-city investigation

50 distinct BDTRE building records, ten each in north/south/east/west/centre coordinate strata, selected using deterministic farthest-point sampling for spatial spread. Thresholds and IDs are saved in `output/city/dossier-audit.json`; they are geographic strata, not official neighbourhoods. This is nonrandom source-link investigation, not a representative estimate of citywide accuracy, a cadastral certification or 50 documentary/site inspections.

The cases contain 127 property-source record memberships and 92 civic spatial candidates (sums across cases, not citywide unique entity counts). 27 cases have no acquired property-source record on their candidate parcel keys; 26 have no civic point intersecting those parcels; two contain incomplete property identities. Neither absence establishes that the real property/entrance is absent. Boundary setbacks, source vintages, source coverage and cartographic correspondence remain possible causes; no unsupported cause is asserted. The UI offers an inspectable 50-building investigation view with links to the actual building and parcel records.

## Additional public data actually integrated

Re-inspection of the acquired **BDTRE 2026 municipal GeoPackage** adds separate local source tables:

- `v_un_vol`: 70,829 volumetric footprint records intersecting the municipality. 68,806 have finite positive `un_vol_av` values under 300 m with `un_vol_ex='altezza'`; 2,023 remain unknown. Raw values are retained. Every record's production method is `banche dati esterne - catasto`. Values may be conventional; the 2026 package date does not turn them into new surveyed heights. Per-record acquisition/update dates remain visible.
- `v_acc_pc_civico_tp_str`: 118,838 access records, with original type, street, civic, suffix and dates. Access may serve a courtyard/complex. An address suffix called `civico_sub` is not a cadastral subalterno. No apartment-access truth is assigned.

`build_city_detail_sources.py` reads the acquired package read-only, retains full source IDs, geometry/attributes and provider URL in a separate ignored database, and proposes parcel relations by representative-point intersection. No raw geometry or source records are merged into existing legal identities. These source tables are available through parcel dossiers and selection highlights; a complete 3D renderer is not added in this phase.

The source's 2026 edition, checked in Chrome, explicitly covers data updated to 31 March 2026, metadata revision 25 May 2026, CC BY 4.0:
https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:da9b12ba-866a-4f0f-8704-5b7b753e4f15

Legacy UN_VOL class metadata defines real/ideal flat-top bodies and possible symbolic heights; its unknown reuse conditions are distinct from the acquired 2026 edition licence. It is used for interpretation, not as a licence override:
https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:6dacd512-8862-491a-a37b-c032cd54d081

Municipal **Edificato del DBGT** metadata, newly verified in Chrome, advertises all-municipality buildings, revision 31 December 2025, quarterly maintenance, 1:1000, CC BY 4.0 and WMS. This is a useful newer layer lead; no downloadable roof mesh, vector enrichment or LoD2 coverage was verified/imported from that service:
https://www.geoportale.piemonte.it/geonetwork/serv/api/records/c_l219:78dc5b8a-6c9d-4b1d-8257-5d27dfbc5378

## New selective documentary observation

Using the PDF skill, extracted and visually checked pages 2–3 of the municipal 2026 Cavour 9 technical sheet. Page 3 reports L219, sheet 1281, parcel 107, subalterno 7, floor T, category C/2, cadastral area 95 m². Page 2 describes courtyard openings reached through the vehicle passage at Via Cavour 9. This is **non-residential documentary evidence**, not an apartment example. It supports a dated access description, not present-day physical/legal entrance truth. Section is not reported, so no exact-full-identity merge is made.

The source-only observation and document SHA256 are retained in `city-source-observations.json`, displayed separately in parcel 1281/107; its document subalterno is not fabricated into the APE registry. Raw PDF and rendered QA pages stay ignored, with no redistribution of plans or sensitive/personal document contents:
https://bandi.comune.torino.it/sites/default/files/allegati/avvisi/2026/4534/2_2026_assoc_confisc_allegato_2_scheda_tecnico_patrimoniale_cavour_9.pdf

## Reproduction, checks and boundaries

1. `py scripts/build_city_dossiers.py`
2. `py scripts/build_city_detail_sources.py`
3. `py scripts/check_city_dossiers.py`
4. `py scripts/check_city_catalog.py`
5. `node scripts/check-city-static.cjs` and `node scripts/check-identity-evidence.cjs`
6. Start static server 8765 and `py -u scripts/serve_registry.py` on loopback 8766.

Checks passed: exact preservation of all 226,951 identity IDs, SQLite integrity, no orphan inverse links, full-source membership grain, all candidate flags remaining unconfirmed, all 50 case dossiers, classification counts/filters, valid source-height conditions, bounded pagination, invalid input rejection and documentary section ambiguity. Existing city/source/static/pilot checks pass. Automated QA is saved under ignored `output/qa/`.

Browser verification is recorded in HANDOFF after final checks. No local notes, review events, raw PDFs, credentials, company data or excluded ARPA geometry were added to publication data. The new dossier/extra APIs and evidence filters are **local-only**; a future publication needs a reviewed static export of these additional read models and a new version/build review. The static fallback remains compatible with public 2.5.1 data. Primary development history still must never be pushed; publication must start from the clean public checkout.

No complete subalterno census, property interior geometry, cadastral/current entrance certification, independently surveyed heights, LoD2/2.5 roof surfaces, company measurements or new energy modelling is claimed.
