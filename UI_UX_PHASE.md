# Whole-Torino UX refinement — local 2.9.0-dev.3

24 October 2026. User request: improve the UI/UX further. This is local interface work only. Public 2.5.1 and the prepared 2.9.0-rc.1 (dev.2 runtime) remain unchanged. No publication or shutdown is authorized.

## Changes

- A compact white application header and clearer typographic hierarchy replace the duplicate city navigation row. City coverage remains explicit; source-class totals are available in Coverage rather than the main title.
- The search panel provides Addresses / Parcels / Properties / Buildings buttons, clear search, two real example searches, and a session-only list of the last five selected public objects. Additional source categories and volume filters remain available under an expandable control.
- A map toolbar provides Show entrances, Layers and Focus map. Show entrances enables civic points and zooms the current map centre to at least level 18. It does not verify a legal entrance or invent a point. The independent layer drawer works with the search panel hidden. The 3D height-disagreement option is inside that drawer.
- Selection details have a Back action and close control. Back returns through selected source IDs. Existing source paths, complete dossiers, comparisons and documentary cases remain accessible.
- Connected parcel summaries emphasise building candidates, property-source records and candidate civics. Extra explanation of spatial joins remains expandable. Unknowns, candidate badges, reported keys and current-access limits are preserved.
- Press / to focus search from outside a text field. Escape closes the layer drawer, then Street View, then the detail pane. These shortcuts operate only while this explorer is mounted.
- Desktop panels have clearer borders, spacing, focus states and readable result descriptions. Mobile map actions wrap into two rows; civic selections and document route previews bring the map/Street View into view. Temporary test viewport settings are reset.

## Verified

Chrome extension checks covered example parcel 1282/94, its civic list, VIA ROMA 360 Street View, Back to the original parcel, clear search and recent selections, layer drawer with the search panel hidden, civic toggle followed by Show entrances, / search focus, IT/EN and 2D/3D. At 1440 x 900 the document has no horizontal or vertical overflow. At 390 px width the document width is 390 px; the 3D mobile toolbar stays 88 px high, with the model option visible in Layers.

Street View upper-left keyboard resize changed width from 410 to 420 px with right and bottom fixed; minimise and restore controls worked. Imagery is nearby imagery and can identify a different civic or street; the existing caution remains visible. No present legal access or current apartment geometry is established.

JavaScript syntax, static city and municipal source-adapter checks, and bilingual documentary-evidence module checks pass. Browser QA and screenshots are local under output/qa/atlas-ux-v2.9-dev3*. Source datasets and geometries have not been rebuilt or changed. No publication artifact has been refreshed for this UI iteration.

Preview: http://127.0.0.1:8765/?release=2.9.0-dev.3
