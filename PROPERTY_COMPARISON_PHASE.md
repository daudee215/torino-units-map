**Publication authorized — 24 October 2026:** The user requested publishing the latest interface as **2.13.0** to the existing GitHub repository and Pages site. Includes browser-local references, record links, source comparisons/export and refined desktop/mobile navigation. Published 2.9.0 source datasets are preserved byte-for-byte. Raw archives, local databases/reviews/notes, QA and unresolved-licence geometry remain excluded. This authorization supersedes historical local-only notes for this release. Further work returns to local-only.

# Source-record comparison — local 2.11.0-dev.1

24 October 2026. Further local improvement requested by the user. Public 2.9.0 and its clean public checkout remain unchanged; no publication or shutdown is authorized.

## Implemented

Pin a selected source record using Ref. / Rif., then select another record and choose Compare selection / Confronta selezione. A white responsive comparison panel displays exact source identities, scope, reported members and address, dates, original floor/interior observations, attested-object heated areas, source heights, original building-floor values, geometry type and source links. Reference is session-only and does not create a review, identity merge or persistent bookmark. Close or Escape returns focus to the comparison control. Selecting the same record disables comparison; clearing the reference removes the tray.

Facts remain per certificate with original dates. The panel displays the first 12 observations per record. JSON export includes at most 1,000 observations per record, the original count and an explicit truncation flag. Its allowlist excludes raw geometry, local reviews, notes and ownership/tenant fields. Zero is distinct from missing; invalid numeric values remain unknown. Source URLs must be HTTPS. No apartment geometry, identity equivalence, current legal entrance, cadastral change or split of group/whole-building totals is inferred.

## Verified

Module checks cover group scope, unchanged group totals, dated observations, zero/missing/invalid numeric input, escaped source text, rejected script URLs, export allowlist, truncation and bilingual labels. Reference, city-static and evidence-label checks and JavaScript syntax checks pass.

Chrome extension testing compared actual properties 1282/94/39 and 1282/94/40: source addresses VIA ROMA 366 and VIA ROMA 266, certificate dates 2022-01-17 and 2017-11-22, reported floors 2 and 3, and attested-object areas 72.68 and 184 m². The VIA ROMA 266 discrepancy remains unresolved. Export downloaded successfully and retained two allowlisted records. Same-record disablement, Escape/focus return, reference persistence during IT/EN switching and removal were checked. Italian mobile width 390px had document width 390px, panel width 376px and table width 339px. No captured application errors. Temporary viewport override was reset.

QA remains local under output/qa/atlas-comparison-v2.11*: desktop/mobile screenshots, the actual downloaded example JSON and browser verification JSON. Existing source snapshots and source counts are unchanged. This is not an apartment census or legal-access verification. No new energy/company or LoD2 work.

## Continuation

Preview: http://127.0.0.1:8765/?release=2.11.0-dev.1

Future reviewed publication must include property-comparison.js and this document. The 2.9 publication helpers remain pinned to their reviewed release and must not be rerun blindly for this version. No release artifact was built or published in this phase.
