# Shape validation — 2026-11-26

## Sources and scope

- User-supplied InfoBusetas Yopal Firebase route snapshot, yopal-rutas.json, SHA-256 7a2db4385027130c3b531bc126f8f39bdfe4e8c49783b678732d0456094512e3. Only numbered routes, enabled flags and geometry arrays inspected for validation. No original geometry or crowdsourced vehicle telemetry redistributed.
- User-supplied Overpass export (10).json, SHA-256 5bb7368e85d7f2bf5410c31c65740406d563fae1794f53eb0e000843ba4ba861; OSM base timestamp 2026-11-26T08:22:51Z, bbox 5.265,-72.460,5.365,-72.355. © OpenStreetMap contributors, https://www.openstreetmap.org/copyright, ODbL.
- All 14 route IDs retained for research, 13 with both geometry arrays (26 shapes). Route 14 has neither array; disabled flags do not establish legal status. All 26 shapes have local geographic coordinates inside the export bbox.

## Method

Project WGS84 [longitude, latitude] to EPSG:32618. Strip null slots and consecutive points less than 0.01 m apart; preserve source point order and other coordinates. Measure shape lengths, self-intersection (Shapely is_simple), endpoint gaps, reciprocal branch proximity and long legs (at least 200 m). Sample every 20 m (midpoint offset 10 m) against 16,808 motor-road segments. Include trunk/primary/secondary/tertiary links, residential, unclassified, living street, service and track, exclude pedestrian-only and construction ways, apply simple access hierarchy bus/psv/motor_vehicle/vehicle/access and oneway:bus/oneway:psv/oneway (roundabout default). 141 private and 2 no-access ways excluded. Directed network: 13,786 nodes and 29,875 edges. Heading compatibility requires a road direction within 45 degrees. A strong reverse-risk sample is within 15 m of the nearest explicitly directed segment, traveling within 30 degrees of its forbidden direction, with no heading-compatible alternative within 25 m. Consecutive runs of two or more samples are listed separately, with isolated samples identified below. These are screening heuristics, not full map matching or proof of an illegal maneuver. Turn restrictions, conditional access, vehicle dimensions and time-dependent constraints are not modeled; the supplied OSM export does not include a full turn-restriction inventory.

## Normalization and null gaps

3,565 input slots, 3,289 valid non-null points, 276 null slots (251 leading, 25 internal), no invalid non-null coordinates, two consecutive duplicates (route 4 salida and route 10 salida). Local normalization test produced 3,287 points across all 26 shapes, retaining route 14 as an empty record. All 26 cleaned lines were simple. Combined branch length is 248.984 km before any reroutes.

Initial node-based routing estimated 18 straightforward gap candidates, one detour and three unresolved gaps. This was superseded by a refined edge-projection check: inspect each of 22 internal null bridges at approximately 5 m spacing, snap to nearby road segments rather than only nodes, and test a directed path including partial edges. All 22 straight connectors remain within 6.7 m of permitted motor-road geometry at the samples, with 100% heading-compatible samples within 25 m and no reverse flags. Each has a directed path candidate. Longest straight bridge 152.5 m. No synthetic points or replacement alignments needed for these gaps on the available evidence; skip nulls and retain the adjacent valid points. Do not interpret leading null padding as a measured missing length before the first valid point. Index values are zero-based in the raw array.

The 186 long legs were screened separately. Four had less than 95% of samples within 25 m of a heading-compatible road (routes 1, 5 twice, and 12 salida); these overlap or supplement the warnings below. A long leg by itself is not a break.

## OSM geometry / direction results

24 of 26 shapes have every sampled point within 25 m of eligible roads. The other two (route 12) have 99.6% and 99.5% respectively within 25 m. Across all shapes only three samples are more than 35 m from eligible roads. Direction screening flags 61 possible reverse samples, not 61 distinct maneuvers.

| Route | Branch | Finding | Disposition |
|---|---|---|---|
| 1 | llegada | Carrera 12, approximately 220 m against tagged direction, way 220972120 | Review if route selected; 498.3 m directed alternative for 300 m anchor interval |
| 3 | salida | Calle 25, approximately 200 m against tagged direction, ways 102474998 and 220675141 | Priority active-route issue; 533.3 m directed alternative for 280 m anchor interval |
| 4 | llegada | One isolated reverse-risk sample at 3470 m (way 1281962806), nearest 2.7 m, compatible alternative 28.0 m | Low-confidence manual review if selected |
| 5 | llegada | Carrera 6, two reverse-risk runs of 580 and 200 m, ways 85172998 and 102475030 | Review if selected; alternatives calculated for overlapping anchor intervals, do not combine them blindly |
| 12 | llegada | 40 m sampled off-road run near 7980–8020 m, max 39.2 m | Review if selected; directed candidate 644.5 m for 120 m anchor interval is not a reliable automatic repair |
| 12 | salida | One isolated off-road sample at 3130 m, 46.5 m; long leg 16–17 (203.9 m) has 70% compatible samples within 25 m | Review if selected |

For routes 1, 3, 5 and 12 candidate alternative paths are computed using the local directed OSM graph, snapping to edge positions (nearby alternatives within 5 m of nearest, maximum 25 m) and using shortest-path cost plus snap penalty. These are diagnostic route proposals, not accepted bus reroutes; path_osm_way_ids are distinct way IDs in first-encounter order, not a fully navigable ordered edge list. Turn restrictions not modeled. Preserve route geometry until authoritative direction, any bus exemptions and the actual route are checked. No GraphHopper calls were made; the local OSM graph was used instead. Route 3 is the only enabled route with a sustained reverse-risk run. Do not infer that the other shapes have been field-verified.

## Endpoint pairing and trip model

All 13 pairs connect llegada end to salida start within 8.8 m and salida end to llegada start within 3.7 m. Each individual branch has distinct termini (endpoint separation 2.8–6.9 km); neither branch is a closed loop by itself. Reciprocal branch proximity within 25 m varies substantially; not simply identical reverse geometry. Combined branches form a geometrically closed round-trip candidate, subject to checking the short connections against the road network and actual dispatch origin. The geometry does not establish whether trips are operated and scheduled independently or as one full circuit. Keep both original branches; model one full circuit per reported dispatch as a provisional hypothesis only if the timetable origin/headway evidence supports it, not as two independent departures by default. Confirm route-level headway applicability before GTFS generation.

## Disposition

Geometric screening and normalization completed for every available shape. 22 internal null bridges passed the refined local road check; no route changes made. Priority repair verification: active route 3 salida/Calle 25. Historical/disabled routes 1, 4, 5 and 12 retain explicit warnings, and route 14 needs a source geometry if legally included. Do not treat the eight source-enabled routes as the full legal network. Current boarding policy, legal authorization and source reuse rights remain unresolved; no GTFS release or raw geometry published.

## Files

| File | Data rows |
|---|---:|
| yopal_shape_validation.csv | 26 |
| yopal_shape_endpoint_review.csv | 13 |
| yopal_shape_gap_review.csv | 22 |
| yopal_shape_long_leg_review.csv | 186 |
| yopal_shape_osm_flags.csv | 9 |
| yopal_shape_gap_detailed_review.csv | 22 |
| yopal_shape_repair_candidates.csv | 5 |
| yopal_route_shape_disposition.csv | 14 |

The CSVs were reconstructed from the generated analysis file text and row counts verified; original byte-level equivalence is not asserted. The local normalizer preserves the source geometry order, validates the reviewed bounding box, removes nulls/near duplicates, and outputs transit-only geometry for private testing; it is not an automatic repair tool.
