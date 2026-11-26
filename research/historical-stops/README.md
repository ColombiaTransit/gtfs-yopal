# Historical stop candidate research — Yopal

Research snapshot: 2026-11-26. These files are **not verified operational GTFS stops**. They preserve the analyses of the historical route maps for routes 2, 3 and 13 and the comparison with contemporary route data. The earlier [pixel-only review](../findeter-stop-review.md) and [OSM review](../osm-review-2026-11-26.md) remain available as separate research stages.

## Provenance and limitations

- Findeter, [2023 MIB Yopal technical profile](https://www.fiducentral.com/images/files/2024/convocatorias/findeter/obras/2023_PerfilT%C3%A9cnicoDefinitivo_MIB_Yopal.pdf), pp. 40–41, figures 30–32: original municipal PIMUR maps dated July 2017. The report also describes service on routes 2, 3 and 13 in 2023.
- OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright): user-provided Overpass export (10).json, OSM base 2026-11-26T08:22:51Z, bounding box 5.265,-72.460,5.365,-72.355. OSM-derived data remain subject to ODbL and applicable attribution requirements.
- ColMind Studio / InfoBusetas Yopal: [route endpoint](https://rutas-busetas-yopal-default-rtdb.firebaseio.com/features/0/rutas.json), user-provided snapshot reviewed 2026-11-26. The source's redistribution rights have not been established. Raw source geometries, crowdsource identifiers, individual location reports and original map images are not included here.
- Georeferencing uses SIFT map alignment, street-centerline alignment and visual review, not independently surveyed ground-control accuracy. Pixel centers are approximate; three merged symbols on route 3 were split approximately. Null Firebase coordinates were removed; straight connections across gaps can affect distances. The two shape keys are retained as `llegada` and `salida`, rather than asserted official direction labels.

## File inventory

| File | Records | Interpretation |
|---|---:|---|
| [Historical candidates CSV](yopal_historical_stop_candidates.csv) | 138 | Original route-specific candidates, pixel centers, approximate WGS84 positions and distances |
| [Historical candidates GeoJSON](yopal_historical_stop_candidates.geojson) | 138 | Same candidates for GIS inspection |
| [Georeference metadata](yopal_georeference_metadata.json) | — | Coordinate transforms, method and limitations |
| [Deviation review](yopal_historical_stop_deviation_review.csv) | 20 | Candidates beyond 50 m: 4 require further own-route review, 6 are candidates for other routes, 10 historical only |
| [Direction review](yopal_stop_direction_review.csv) | 118 | 29 single-direction hypotheses and 89 ambiguous candidates |
| [Shape order](yopal_stop_shape_order.csv) | 200 | Candidate-direction associations and chainage; not final stop sequences |
| [Duplicate review](yopal_stop_duplicate_review.csv) | 32 | Nearby pairs; 10 possible same-direction locations, 22 require direction review; no merges |
| [Cross-route candidates](yopal_stop_cross_route_candidates.csv) | 218 | Proximity-only associations with other active routes; no service assertion |
| [Side review](yopal_stop_side_review.csv) | 89 | 24 additional side-based hypotheses and 65 insufficient-evidence candidates |
| [OSM route comparison](yopal_osm_route_comparison.csv) | 12 | OSM relation geometry and timetable comparison, including regional/inactive relations |

## Decisions and next steps

Of 138 route-specific candidates, 118 are within 50 m of either current same-number shape, 9 are between 50 and 100 m, and 11 are beyond 100 m. These counts are before deduplication. All direction, stop-use and cross-route hypotheses remain provisional. No coordinates have been automatically moved, no candidates were merged or reassigned in this original snapshot, and no final stops.txt or GTFS feed is generated here. Retain historical IDs for traceability.

Deduplication is now documented in [deduplication-review.md](deduplication-review.md): 109 conservative candidate locations or 104 including side hypotheses, preserving all 118 source records. Next: calculate spatial coverage and large stop gaps per active route/direction, assess boarding policy before selecting fixed stops versus continuous pickup/drop-off, and resolve licensing and current-service verification before release. Preserve differences between OSM and Firebase schedules (especially route 9); official acts remain the preferred authority.

## Integrity

The following Git blob SHA-1 hashes identify the ten archived research files. CSV text was reconstructed from the file reader (including removal of its displayed index); original upload byte-for-byte equivalence was not independently verified:

- `b28aa5f0616f8578082102ebd4b65d25c3ce8a8f`  `yopal_historical_stop_candidates.csv`
- `5e7728062bbcb30b9af2d5297ff70a9c15cc9cfb`  `yopal_historical_stop_candidates.geojson`
- `0211ce6b92a1c038e584b0c75855a16da171ff39`  `yopal_georeference_metadata.json`
- `7267328dc5e05262510591cebf9e367b2e22d93f`  `yopal_historical_stop_deviation_review.csv`
- `0de31a0fa0f8de87f39fd09cd5c50bee186d89ef`  `yopal_stop_direction_review.csv`
- `72b7632f59b0bc537f59b364771cdaab118898fd`  `yopal_stop_shape_order.csv`
- `1c88cc051afbea5b0d5e9248aafb7e7f59ace064`  `yopal_stop_duplicate_review.csv`
- `891bde9504dc3717ff011d54b92de7fa6a16a9f5`  `yopal_stop_cross_route_candidates.csv`
- `51d336f6a4a6d51234e05637c60316161a488be2`  `yopal_stop_side_review.csv`
- `81a9f412a4127eeb5e9201b3133bd412a5126634`  `yopal_osm_route_comparison.csv`
