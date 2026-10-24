**Publication authorized — 24 October 2026:** The user requested publishing the latest interface as **2.13.0** to the existing GitHub repository and Pages site. Includes browser-local references, record links, source comparisons/export and refined desktop/mobile navigation. Published 2.9.0 source datasets are preserved byte-for-byte. Raw archives, local databases/reviews/notes, QA and unresolved-licence geometry remain excluded. This authorization supersedes historical local-only notes for this release. Further work returns to local-only.

# Persistent references and connected records — local 2.10.0-dev.1

24 October 2026. The user requested further improvement after publishing 2.9.0. This phase remains local. Public 2.9.0 (4c4b7057d6fdf4ce25ef9651093a58034ac19945), its clean checkout, prepared release data and deployed artifact are unchanged. No new publication or shutdown is authorized.

## What changed

- **Saved places:** up to 50 source references in this browser, with save/remove controls and a map drawer. Only ID, display title and kind are stored under torino-atlas-saved-v1. No geometry, local reviews, notes or measurements are stored. Storage failure is reported as session-only; the limit never silently evicts a reference. Saved references are not property verification.
- **Record links:** Link reveals a read-only URL using #record= plus an encoded exact source ID. Users select/copy it themselves; the app does not replace the system clipboard. A fresh URL opens that record; source geometry is focused when available. Legacy #lotto links retain city-first startup. Malformed or unsupported fragment IDs fall back to the city atlas. Unknown acquired IDs produce an error without reusing an earlier record's geometry or save controls. Current local links work on this computer; they are not a newly published online feature.
- **Clickable connection counts:** building candidates, source properties and civic candidates are direct navigation controls. They replace duplicate count summaries and navigation tabs, while preserving evidence grain and uncertainty.
- **Filter loaded rows:** addresses and reported cadastral keys can be filtered within the current loaded page. The result explicitly states that this is not a whole-catalogue search. Switching connection categories or pages resets the filter.
- **Continuous exploration:** Back restores the parcel, category, subtype, page and filter for up to 30 recently visited records in the current session. Browser-local saved references are separate from this temporary view history.
- **Focus controls:** selection can be reframed when it has source geometry; that control is disabled for properties without acquired individual geometry. Case-only panels do not offer a misleading generic record save/link.
- Controls bind before optional documentary context finishes fetching. Startup restoration does not overwrite a newer user selection. Initial city fitting is unanimated to prevent an initial zoom transition from swallowing a record-link focus request.

## Verified

Node checks exercise the real reference module: allowed source IDs, round-trip links, invalid/legacy fragments, persisted field allowlist, 50-record limit and storage failure. Existing city-static and bilingual evidence checks pass; syntax checks pass.

Chrome extension checks covered saving 1282/94, reopening it after reload and in another tab, exact record-link startup, and filtering /40 to one of 14 reported property records. The underlying VIA ROMA 266 observation remains unchanged and unresolved; it is not silently rewritten to a different civic. Filtering the civic page to 360 gave one of six loaded rows; entering Street View and returning restored the civic category and filter. Property 1282/94/40 has no acquired individual geometry, and the zoom control remained disabled.

Static-source mode also returned the same one-of-14 property result with no local API fallback. Italian mobile testing at 390px found no horizontal overflow; Saved scrolls the map drawer into view, and a direct parcel URL focuses street detail. English desktop checks confirmed the property filter, share field and active count card. No captured application errors. QA screenshots and verification JSON live under output/qa/atlas-record-tools-v2.10* and remain excluded from publication. Test-created saved references are removed after verification; existing user references are preserved.

## Publication boundary

No source files or source identities were rebuilt. Source counts remain neither an apartment census nor verification of legal/current access. There is no new energy/company or LoD2 work. This version introduces atlas-selections.js and must include it and this phase document in any future reviewed publication manifest. The 2.9 publishing helper is pinned to 2.9 data/version; do not rerun it blindly for 2.10. A separate publication instruction is required.

Preview: http://127.0.0.1:8765/?release=2.10.0-dev.1
