**Publication authorized — 24 October 2026:** The user requested publishing the latest interface as **2.13.0** to the existing GitHub repository and Pages site. Includes browser-local references, record links, source comparisons/export and refined desktop/mobile navigation. Published 2.9.0 source datasets are preserved byte-for-byte. Raw archives, local databases/reviews/notes, QA and unresolved-licence geometry remain excluded. This authorization supersedes historical local-only notes for this release. Further work returns to local-only.

# Comparison clarity — local 2.12.0-dev.1

24 October 2026. User requested further local improvement. Public 2.9.0 and its clean public checkout remain unchanged; no publication or shutdown is authorized.

## Changes

The source-record comparison now has an at-a-glance summary of 15 displayed fields: different literal values, same literal values, or incomplete acquired data. Each row carries a text status; a native select filters All / Different / Incomplete / Same with a live visible-row count. Colour is supplementary. Certificate date ranges are shown separately for the reference and selection. White ArcGIS-style layout and complete IT/EN labels are preserved.

Classification is descriptive, never an accuracy score, identity equivalence or contradiction finding. Arrays are compared independent of order with multiplicity retained; original records and displayed observations are never reordered or rewritten. Missing values on either side take precedence over difference classification. Blank cadastral sections remain incomplete. Truncated certificate collections are incomplete for observation fields. Zero remains a reported value. The date range describes acquired certificate observations, not current validity or source-snapshot freshness. Per-certificate dates remain visible in the detailed table. No area deltas or group splits are calculated.

Export schema and its allowlist are unchanged. Raw geometry, reviews and notes remain excluded. Source identities/data were not rebuilt. Current legal entrances remain unverified; source-property counts are not an apartment census. No new energy/company or LoD2 work.

## Verification

Module checks cover all 15 statuses, incomplete-value precedence, blank sections, order-independent values, truncation, zero/missing inputs, bilingual overview, date range, grouped totals, privacy allowlist and safe markup/URLs. JavaScript syntax, existing reference, city-static and evidence-label checks passed.

Chrome extension testing on actual source records 1282/94/39 and /40 returned 4 different / 5 same / 6 incomplete fields. All three filter counts matched displayed rows; All restored 15 rows. IT/EN labels and certificate dates 2022-01-17 versus 2017-11-22 were checked. At mobile width 390px, document width remained 390px and overview width 339px; screenshot visually reviewed. Viewport was reset. No captured application errors. QA: output/qa/atlas-comparison-v2.12-desktop.png, atlas-comparison-v2.12-mobile.png, atlas-comparison-v2.12-browser.json (local only).

Preview: http://127.0.0.1:8765/?release=2.12.0-dev.1

Future publication requires a separate user instruction and release review. The 2.9 publication helpers remain pinned to that release; no artifact was built or published here.
