**Publication authorized — 24 October 2026:** The user requested publishing the latest interface as **2.13.0** to the existing GitHub repository and Pages site. Includes browser-local references, record links, source comparisons/export and refined desktop/mobile navigation. Published 2.9.0 source datasets are preserved byte-for-byte. Raw archives, local databases/reviews/notes, QA and unresolved-licence geometry remain excluded. This authorization supersedes historical local-only notes for this release. Further work returns to local-only.

# Map and record usability — local 2.13.0-dev.1

24 October 2026. User requested a better UI/UX. Local implementation only; public 2.9.0, its reviewed data/artifact and clean public checkout remain unchanged. No publication or shutdown authorized.

## Implemented

- Mobile now starts on the map and has dedicated Search / Map / Details navigation. One panel fills the available workspace; each search/details panel scrolls internally. Selection opens Details; civic selection with Street View opens Map. Language changes preserve panel state. North/South/Whole and Locate bring Map into view. Saved opens over Map. Returning to a panel retains loaded content and connection state.
- Selected-record card on the map names the current selection and reopens Details. Desktop source-result and search controls have clearer spacing, readable typography and focus outlines. The details column is 390px on wide screens; existing intermediate breakpoints are preserved.
- Record details have a prominent type/title/uncertainty heading. Long exact source IDs remain accessible in a native collapsible disclosure. Connection controls, dossiers, original certificate facts and comparison/export tools remain available.
- Mobile selected-record focus moves to the record heading; closing Details focuses the Map navigation button. Selecting the map card returns focus to the heading. Controls use text and pressed state; keyboard focus has a visible outline. Reduced-motion preference disables added result hover transitions.
- Embedded Street View retains upper-left resize control, minimize/restore and close. Nearby imagery is not verified current access or proof of a legal entrance.

## Verified

Chrome extension at desktop 1440x900 and mobile 390x844. Desktop 1282/94 search/selection showed record heading, source disclosure, connection controls and selected map card. Mobile reload started Map; Search found 1282/94, selection opened Details, six-civic connection category loaded, and VIA ROMA 360 opened embedded Street View on Map. Minimize/restore/close and returning to civic Details passed. The Google embed exposed nearby imagery, not a verified facade identity; its address may differ from the selected source civic.

Mobile document width 390px and height 844px matched the viewport; only active content panels were shown. IT/EN navigation and source headings checked. Exact source ID disclosure worked. Property 1282/94/39 still has Locate disabled because it lacks acquired individual geometry. Final script cache key dev.1d verified focus return and heading focus; no captured application errors. Temporary viewport override reset.

Syntax and reference/comparison checks passed; city-static and bilingual evidence checks passed. QA screenshots: output/qa/atlas-ux-v2.13-desktop.png, mobile-map.png, mobile-details.png, mobile-details-it.png and mobile-street.png, plus atlas-ux-v2.13-browser.json. QA remains local and excluded from publication. Screenshots were captured during normal asynchronous map/iframe loading; interaction verification also used the completed accessibility state.

## Limits and continuation

Source records, joins, counts and geometry are unchanged. Current legal entrances remain unverified; source counts are not verified apartment counts. No new energy/company work or LoD2 claims. Comparison/export preserves previous observation and group-total rules. New phase documentation is in the future reviewed build allowlist only; 2.9 publication helpers were not run.

Preview: http://127.0.0.1:8765/?release=2.13.0-dev.1
