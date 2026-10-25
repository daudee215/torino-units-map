> Historical local development record. Reviewed derived access/navigation data and runtime were authorized for publication as 2.16.0 on 25 October 2026. See RELEASES.md and SOURCE_ATTRIBUTION.md. Raw/local-only references below are development paths, not shipped artifacts.

# Entrance evidence and civic-to-parcel navigation — local 2.16.0-dev.1

25 October 2026. Implements the two recommended priorities authorized by the user: stronger entrance evidence and investigation of all 6,819 source identities without acquired parcel geometry. The user then clarified that clicking a blue civic point outside a parcel should select its related parcel and open the normal parcel sidebar. This is included. **Public 2.15.0 remains unchanged; no new publication is authorized.**

## Preview and primary interaction

http://127.0.0.1:8765/?release=2.16.0-dev.1

Click a blue civic marker. The app now opens and highlights the related **parcel candidate**, with its normal buildings/properties/civics workspace, rather than treating the footprint under the point (often a street parcel) as the property relationship. A banner identifies the originating civic, the actual method and alternatives. Street View continues to use the clicked point. Map bounds include the point and selected parcel. On mobile the parcel Details panel opens first; Street View remains available in Map.

Navigation uses the first acquired evidence level with candidates:

1. Reported property-address observations linked to cartographic parcel candidates.
2. BDTRE access-point intersections with numeric cadastral parcels, using full address agreement and the existing 20 m civic comparison bound.
3. Municipal civic-point intersection with a numeric parcel.

**Exactly one candidate at that level opens automatically. More than one requires a choice.** Source-record counts do not break ties. No nearest-parcel assignment is made; street/water-style nonnumeric geometry does not become a default property parcel merely because the civic point lies on it. Other acquired candidates remain available. Choosing a candidate changes navigation, not source identities, membership or legal-access status.

All 119,108 mapped civic points are profiled. Under this navigation policy, 25,745 have one property-address parcel candidate, 47,651 have one BDTRE-point parcel candidate at the next level, and 22,450 have one municipal-point parcel candidate at the final level. There are 4,378 multiple-candidate cases and 18,884 without a candidate at these levels. These are navigation/evidence counts, **not accuracy percentages or verified property entrances**.

Actual outside-point fixtures:

- `civic:50320`, Via Luigi Cibrario 73 → `cadastre:L219_117600.311`, parcel 1176/311, from two source-property address observations. The municipal point does not intersect that parcel.
- `civic:50282`, Via Luigi Cibrario 87/B → `cadastre:L219_117400.359`, parcel 1174/359, from BDTRE access-point geometry; the municipal point does not intersect it.
- `civic:72519`, Via Mongrando 2 bis → two property-address parcel candidates, 1276/160 and 1276/162. The app offers choices instead of ranking their counts.
- `civic:75715`, Via Netro 9/B → no acquired candidate under these methods; the civic remains selected, with an explicit unknown and no nearest-parcel guess.

2D civic markers now use a shared SVG renderer with semantic buttons and Enter/Space activation. Other feature layers keep their existing canvas renderer and bounded loading. A dedicated SVG selection pane keeps the blue parcel outline above ordinary feature layers and below civic markers. 3D/search/record selections share the same source-selection resolver; the actual marker/keyboard browser checks covered 2D, not a separate 3D pointer test. The original-point detail view remains available. Also fixed a pre-existing connected-view error that bound a page-filter input when no parcel had been selected and that input did not exist.

## Entrance evidence workspace

Parcel → Investigate / Indaga → Entrances / Ingressi now shows source access classes on each civic card. Expand **Access-type sources** for literal source IDs, source street/civic/suffix, dates, production method, spatial comparison distance and original-source links. The workbench keeps its parcel open during explicit Street View previews.

- Acquired BDTRE exterior view: 82,296 external-direct records, 36,490 vehicle-access records and 52 unknown-type records.
- Acquired BDTRE internal-access view: 118,879 records. Internal-access class does not identify an apartment or a staircase.
- 102,521 municipal civics have a candidate under the full-address/20 m method. Multiple matches are retained. Full-street-word reordering is accepted only when the complete word set identifies one street in both source inventories. Numeric suffixes remain separated: 12/1 cannot become 121; lettered 12/A and 12A share only a formatting comparison.
- Companion BDTRE views can share coordinates and production; they are **not independent corroboration**. Types and dates are reported observations, not current legal-access confirmation. An external-direct class does not verify a current pedestrian door, and a vehicle-access class does not establish a physical gate.
- A separate collapsible documentary section retains 22 previously acquired subjects (the earlier 13 cases, including two land controls, plus nine selected municipal summaries). Reported gates, courtyard routes, stairs, landing doors and courtyard assets remain at their document/property scope, without assigning them to a civic point. Full reported cadastral keys accompany the scoped roles: Mongreno's stair/attic evidence belongs to 1204/98/37 and is not transferred to garage 1204/98/68. Bologna's subalterni 2/4 remain under parcel 1145/98, not the additional parcel 1145/97 with unreported subalterno.

Class interpretation was checked against the [official national catalogue, page 221](https://geodati.gov.it/geoportale/images/Specifica_GdL2_09-05-2016.pdf#page=221). This explains the internal-building-access class; it is not treated as a schema-level route relationship acquired from this package. Only the two flattened access views were found in the acquired package; no external-to-internal route association table was acquired. The older regional specification URL returned HTML rather than a PDF, so it was not used as a verified PDF. National-catalogue text was inspected through the official source; its Chrome PDF navigation was slow and that temporary tab was closed. No new raw PDF was republished.

## All 6,819 unlocated source identities investigated

Sources & tools → **Unlocated properties / Immobili non localizzati** searches the complete set, with reason/evidence filters, 50-row pages and preserved source details. An unlocated property opened from the existing catalogue can also use Investigate to reach the same record evidence.

| Source-profile reason | Identities/groups |
| --- | ---: |
| Reported sheet absent from acquired cartography | 5,471 |
| Reported parcel absent on an available sheet | 1,304 |
| Compound or non-simple reference | 44 |

Of these, 245 source identities are incomplete. Original scopes remain: 5,930 reported cadastral properties, 542 inventory keys, 334 whole-building attestations and 13 groups. All source members and reported sections remain literal; placeholders and apparent field-placement differences are not normalized into verified identities.

Bounded field interpretation produces hypotheses for **44 identities**: 30 section-field-as-sheet hypothesis links and 30 compound-component hypothesis links (links overlap at record level; do not sum as identities). Numeric-format rules produced no additional matches. Separately, **1,719 identities** have civic-point parcel context from their original observed addresses. There is **no overlap between a reference hypothesis and its acquired address-point parcel context** in this run. None is promoted to a repaired cadastral relationship.

The UI explicitly separates reference hypotheses from civic-point context, shows source dates/URLs and original full keys, and offers Explore buttons. These buttons navigate to a candidate without rewriting the source. For example, original `L219 / 1245 / 243 / 26 /` stays unchanged beside the hypothesis 1245/26. Addresses sometimes name a different locality; this is retained as source wording, not proof of a municipal-code correction. Further evidence needs a dated document tying the complete key, section, parcel and route together.

## Data, reproduction and checks

New `data/access-resolution/` is local-only and not reviewed for publication. Its manifest lists **771 files / 20,367,622 bytes**, plus the manifest itself: compressed civic, parcel and unlocated-record buckets; a complete compact unlocated search index; source summary and curated documentary roles. Lazy loading uses a bounded 16-resource cache. Existing city/property catalogues and the 2.15 public data are not rewritten.

Reproduce in this order:

1. `py -X utf8 scripts/curate_access_roles.py`
2. `py -X utf8 scripts/build_access_resolution.py`
3. `py -X utf8 scripts/build_civic_parcel_navigation.py`
4. `py -X utf8 scripts/check_access_resolution.py`
5. `node scripts/check-access-resolution.cjs`

Source SQLite/GPKG files are opened read-only. The full check compares all unlocated identities/members/scopes and certificate counts with the catalogue; reconstructs every property-address civic/parcel relation from the original evidence; checks candidate counts/examples, literal field hypotheses, original civic IDs, source-role classes, distance bounds, parcel briefs, document-member scopes and every manifest hash/size. Result: `output/qa/access-resolution-checks.json`. Navigation population/fixtures: `output/qa/access-navigation-fixtures.json`.

Runtime fixtures verify outside-point property and BDTRE navigation, ambiguity despite unequal source counts, no street/nearest fallback, scoped documentary stairs, numeric/letter civic distinctions, search beyond the first page, HTML escaping and IT/EN labels. Existing full-parcel search, source context, saved references, render-cache and city/municipal static-adapter checks pass. Syntax checks pass for all changed runtime modules.

Chrome verified actual blue-marker click and keyboard activation, the full related-parcel sidebar, explicit choice for Via Mongrando 2 bis, unknown handling at Via Netro 9/B, original-point details without the former missing-filter error, normal local/API and static-only modes, Italian/English context preservation, 1440px desktop and 390px mobile layouts without horizontal page overflow, and source/date/role details. QA: `output/qa/access-resolution-v216/`. Street View is nearby imagery, not confirmation of a current doorway. Temporary viewport overrides are reset after checks.

## Continuation boundary

New runtime `access-resolution.js`; modified municipal selection/marker flow, connected-view null guard and parcel investigation entrance cards. Future top-level publication file list may name the runtime and this phase only; **new derived data is not added to the public allowlist**. A future release needs separate publication authorization and source/data review. Public 2.15.0 remains at `0fe8c2b54bc669e22496b0b1a39c00c43e1bf68c`. No push/deploy or shutdown was performed. Energy/company/LoD2 work remains deferred.
