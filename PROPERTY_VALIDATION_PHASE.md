# Property investigation — local 2.2.0-dev.1

**Publication authorization — 23 October 2026:** the user requested publishing the current property-investigation version as 2.2.0 to the existing GitHub repository and Pages site. This supersedes earlier local-only statements for this release. Publish source-only static investigation dossiers, the reviewed municipal inventory pilot references and historical factual summaries, with attribution. Rebuild without reading local review events. Raw evidence, local reviews and unresolved-licence geometry remain excluded from both the artifact and new public history. Later development returns to local-only. Deployment verification is recorded in `RELEASES.md`.


23 October 2026. User authorized the next refinement phase locally. Published 2.1.0 remains unchanged. Energy and company-data development remain deferred. Read this before older phase notes.

## Completed acquisition

All 1,150 pilot parcel queries associated with the 26 originally capped SIPEE street searches have been attempted. Three server errors were retried successfully; original failed responses are preserved under ignored `_raw/ape/inventory/history/`. Final status: 0 errors, 0 parcel responses at the observed 500-record cap, 179 empty responses. Neither an empty nor a below-cap response proves cadastral completeness. The 26 original street cap warnings remain visible.

The register now contains **24,706 property/group identities, 27,137 certificate entities and APE evidence on 3,116 of 6,361 parcels**. Compared with published 2.1.0 this adds 1,184 identities, 1,704 certificates and evidence on 13 additional parcels. These are not apartment counts. SIPEE bulk and citizen portal are one source lineage. Non-Torino and unknown-municipality query rows are not silently assigned to Torino.

## Additional municipal evidence

Chrome source research found the [April 2023 municipal asset inventory](https://risorse.comune.torino.it/amministrazionetrasparente/bm~doc//fabbricati_di_propr_della_citt_e_loro_destinazione_d_uso_aprile_2023.pdf). Positional extraction reads the first 51 complete landscape table pages. The remaining 415 portrait pages repeat partial column blocks; they are excluded rather than reconstructed or counted again.

Extracted 4,439 Torino rows. The loaded pilot contains **228 references on 65 parcels**, representing 216 distinct complete reported cadastral keys. Of these, 38 keys also occur exactly in the acquired APE register; 178 do not. This is additional reported evidence, not 178 newly verified apartments. Incomplete/placeholder identifiers and legacy sheets remain unchanged. Municipal row codes are source row identifiers, not legal cadastral keys. Asset primary address and description belong to the asset group and do not confirm each property's entrance. Square metres, rooms and cubic metres remain separate; blanks remain unknown. Every row links to its original page.

Extraction is automated; every row has not been individually inspected. Header/column layout and the Digione 113/114 rows were visually checked, with five dimensional anchors checked automatically. Current validity is unknown. Inventory reuse conditions require a separate publication review. This inventory and its read models remain ignored/local-only.

Nine manually page-checked historical observations from three municipal PDFs are also curated, eight attached to eight loaded parcels. Sources:

- [2022 premises list](https://risorse.comune.torino.it/comuneaffitta/bm~doc/deliberazione_gc_2022_741_all_2_elenco_beni_destinati.pdf): Digione 3, 1175/643/sub113 (p2); Francia 73, 1223/9/sub2 (p1); Fabrizi 55, 1173/331/sub2 (p3).
- [2023 disposal annex](https://risorse.comune.torino.it/bilancio/pdf/2023/DEL-685-2023-All_6-29545_2023_06.pdf): Digione sub114, access from vehicle entrance hall and shared courtyard facility (p13); Regina Margherita CT1179/415 land (p8); Beaumont 1221/149/sub2, pending cadastral update (p12); Borsellino CT1222/476-part right of way (p24); Racconigi market group with 32 explicit members across 1224/562 and 1224/546 (p25).
- [2019 Buon Pastore technical sheet](https://risorse.comune.torino.it/comunevende/bm~doc/16_2019_all_25_lotto21_schedatecnicopatrimoniale_principeeugenio.pdf): access narrative p1 and cadastral group p7. Its parcels are outside the loaded set; no pilot attribution is inferred.

Digione sub113 and sub114 remain separate. Grouped market members are not split into apartments or allocated areas. Land/right-of-way references remain separate from urban properties. Historical courtyard references do not establish current courtyard geometry. No owner, tenant, fiscal or contact attributes are extracted into curated evidence. The original two inspected APE certificates remain the only individually reviewed APE PDFs.

## Investigation workspace

The bilingual white register now provides:

- Evidence facets for each property: reported identity, active register entrance links, inspected APEs, exact-key documentary and municipal inventory references, and unknown physical unit position.
- A queue of 2,264 parcels, scored for work priority rather than probability or confidence, with export.
- A reproducible purposive cohort of 30 distinct buildings/parcels: five each for simple access, multiple entrances, shared parcel, civic extensions, multiple streets and identity ambiguity. All have automated checks; **documentary entrance validation and site review remain pending**. This is not an accuracy benchmark or 30 legally validated buildings.
- All nearby parcel alternatives within 25 m of an entrance; BDTRE external/internal access candidates with existing building footprint alternatives within 3 m. Candidate routes are hypotheses, not surveyed paths or known served properties.
- Additional full street/civic plus nearby-parcel proposals for 3,894 property identities. Existing GIS assignments and original review decisions remain intact; rejected or expired original targets are not reintroduced through this proposal list. Candidate buttons open embedded Street View.
- Historical documents and municipal inventory references with source pages. Local JSON exports retain evidence grain.

BDTRE CS_EDI means contiguous building envelope, not courtyard or a surveyed access complex. No courtyard polygons, apartment interiors, PODs or LoD2/2.5 roofs are generated.

## Verification and reproduction

Completed: registry identity/FK/grain checks; address coordinate/suffix/key/distance checks; investigation checks over generated dossiers, 30-case uniqueness and pending status, proposal exclusions, grouped/land/document semantics, municipal layout and dimensional anchors; identity-filter and historical energy-grain regression checks; JavaScript syntax checks.

Chrome verified final counts and acquisition status, Digione 113 versus 114, inventory page links and separate dimensions, 30-case table, Italian/English, and 390 px layout with no horizontal page overflow. A new 1157/125 address candidate opened Street View at Corso Alessandro Tassoni 73. Keyboard upper-left resizing changed width 410→420 px with bottom/right fixed; minimize/restore preserved it. Street imagery rendered and no captured application errors were found. Temporary viewport overrides were reset. No review decisions were changed. Screenshots: ignored `output/qa/property-investigation-local.png` and `output/qa/property-candidate-street-view.png`.

Rebuild order: document observations; municipal inventory; property registry; `prepare_address_publication.py --version 2.2.0-dev.1` (attaches previously reviewed source address fields locally, does not deploy); registry ZIP; investigation. Run `serve-v2.bat` for loopback ports 8765/8766. API-only ignored investigation outputs are intentionally absent from the public artifact. New JS is added to the future runtime allowlist; new evidence still needs publication review.

Continue with dated exact-key-to-entrance documents for the selected 30 cases, current identity changes/splits and explicit evidence-based reviews. Public sources found so far do not supply complete current legal entrance truth. Expand the geographic client only after these join rules are assessed. Do not push the primary branch: its older history contains excluded geometry; future authorized publication must use clean public history.

## 2.2.0 publication review

Chrome inspected the official Torino content licence at https://www.comune.torino.it/note-legali on 23 October 2026. It specifies CC BY 4.0 for city data/documents unless otherwise stated, with source attribution and exceptions for third-party content. The municipal inventory is a city-authored asset table; the 228 pilot references contain asset descriptions and cadastral/consistency fields, not individual owner, tenant, contact or fiscal data. All distinct pilot descriptions were inspected for scope. Publish only those pilot rows, not the entire extracted city inventory. No contrary licence notice was found in the table. Attribution and transformation notices accompany the static dossiers; original PDFs remain excluded.

The public model is generated with `build_investigation.py --public`, which never opens the local review database. It preserves unreviewed source proposals and all unknowns. Public queues can differ from the local queue if local review decisions exist. The online register loads static per-parcel investigation files and remains read-only. Source/publication checks reject local review fields and extra inventory fields. The outside-pilot Buon Pastore observation is not included; eight curated historical observations are included across eight loaded parcels.
