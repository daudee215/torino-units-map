# Property workspace — local 2.4.0-dev.1

23 October 2026. Authorized scope: make the 178 municipal-only keys searchable, compare the 38 shared keys, investigate the two section discrepancies, and redesign the prototype with a thin white ArcGIS-style interface. Development remains local; published 2.2.0 is unchanged.

## Data and identity

The local catalogue contains 24,884 source records: 24,706 existing APE identities/property groups plus 178 separately reported municipal cadastral references. This is not an apartment or unique-property census. Stable APE identifiers and original full cadastral tuples are preserved. Municipal addresses and descriptions refer to asset groups; no unit floor, geometry or entrance is inferred from them.

The 38 shared keys connect to 31 existing APE records and produce 41 distinct record/inventory-row comparisons. Nine rows have the same complete address words and 32 differ in text or group scope. Two contain both municipal MQ and APE heated area; these remain different measurements, with no area difference calculated. Twenty-six contain municipal room counts and six contain volume fields. These are source-comparison counts, not accuracy scores. Group certificates remain whole-object observations.

The blank-section inventory references 1179/259/2 and 1179/259/3 remain separate from the corresponding SIPEE section `=` records. The official SIPEE manual (https://servizi.regione.piemonte.it/media/960/download, PDF page 37) defines the section field; the citizen guide (https://servizi.regione.piemonte.it/media/508/download, page 6) shows it as optional for searches. Neither establishes blank/`=` equivalence. Both local cases are marked Needs a document with explanatory notes. No automatic merge occurred.

## Interface and implementation

Property register now opens a white, thin workspace: searchable/paginated record list at left, Overview / Connections / Sources & comparison / History in the centre, and case status/notes at right. Filters cover the selected parcel or whole pilot and source categories. The 30-building queue and Advanced evidence preserve access to earlier investigations.

Connections distinguish candidate and curated historical access observations from parcel GIS context. Selecting an entrance opens the existing embedded Street View. Its upper-left resizing, minimize/restore and close controls remain available. IT/EN controls and responsive stacking are retained.

`scripts/build_property_workspace.py` builds the ignored `output/property-workspace/catalog.sqlite`, summary and comparisons. `scripts/workspace_api.py` provides bounded, parameterized search (50 rows/page) and record details through the loopback review service. Notes and workflow events append to a separate `cases.sqlite`; source records and the original relationship-review ledger are unchanged. Workflow states never imply legal verification. Browser drafts survive record/language changes.

New runtime files: `property-workbench.js`, `property-workbench.css`. Integration changes: `registry-workspace.js`, `workspace.js`, `index.html`, `scripts/serve_registry.py`. The static publication allowlist knows the new runtime filenames, but the local catalogue and workflow ledger have not been prepared or authorized for publication.

## Verification

`py scripts/check_property_workspace.py` passes: counts, preserved identities/sections, no invented municipal unit facts, comparison grain, bounded search, and isolated append-only workflow writes. JavaScript syntax and identity-evidence checks passed. Chrome extension verification covered IT/EN, 390px mobile layout without horizontal overflow, municipal/shared/section filters, case save and persistence, legacy return, candidate/historical connections and embedded Street View controls. Final navigation between Property register, Data & method and Attribute table passed without the new workspace styles leaking onto other pages; no captured browser errors. Desktop screenshot: `output/qa/property-workspace-v2.4-local.png`.

Resume locally with `py -m http.server 8765 --bind 127.0.0.1` and `py scripts/serve_registry.py` (8766). Rebuild with `py scripts/build_property_workspace.py`. Both services were restarted during the final resumed checks.

## Limits and next evidence

Inventory extraction remains automated and not every source row was visually reviewed. Current legal entrances, staircase/interior positions and source current validity remain unverified. Search hits are discovery leads. No completed cadastral changes or precision/recall are inferred. San Donato/Campidoglio study coverage is unchanged; whole Torino expansion, energy/company data and LoD2/2.5 remain deferred.

No Git push or deployment was performed. Raw documents, generated databases, notes and QA stay ignored/local. Future publication requires explicit authorization and a reviewed static read model copied onto clean public history. Never push primary branch history containing excluded ARPA geometry; use the existing clean public checkout described in RELEASES.md.
