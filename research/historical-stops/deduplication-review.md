# Historical stop deduplication — 2026-11-26

This stage groups 118 historical candidates within 50 m of the current same-number Firebase shape. The 20 deviations remain separately preserved and excluded from grouping. This is not a verified operational stop inventory.

## Rules

- Review the 32 pairs in yopal_stop_duplicate_review.csv (separation at most 15 m).
- Require different source routes, the same nonempty nearest OSM way ID, an explicit direction hypothesis for both candidates, and local travel-bearing difference at most 20 degrees (circular angle). Compare bearings, not the route-specific llegada/salida names alone.
- Use the direction review's shape-distance hypothesis first, otherwise use the side review's road-side hypothesis. Only two shape-distance hypotheses qualify for conservative grouping; the expanded alternative also permits road-side hypotheses.
- Require every pair in a merged component to satisfy the rules (complete-link check), with at most one member per historical route. Preserve all source IDs, original coordinates and route associations. Group ID derives from lexically first member; representative is the original member closest to either of its own shapes (tie by ID), not a snapped or averaged position. This choice is not evidence of greater positional accuracy.
- No current use or boarding direction is verified. Keep unresolved pairs separate; 15 have insufficient direction evidence, two have different nearest OSM ways. Do not manufacture opposite-side stops or infer service from proximity.

## Results

10 shape-supported edges form 8 non-singleton groups (7 pairs and one triple; 17 source records), reducing 118 to 109 locations. Five additional side-based pairs reduce the expanded alternative to 104; they are NOT applied in the conservative file. The underlying 118 source records and 200 possible shape-direction associations are preserved in both mappings. The triple is R2-004 / R3-004 / R13-002. Original georeferenced data and uncertainty remain unchanged.

| File | Records |
|---|---:|
| yopal_deduplicated_locations.csv | 109 |
| yopal_deduplicated_locations_expanded.csv | 104 |
| yopal_stop_location_mapping.csv | 118 |
| yopal_stop_merge_decisions.csv | 32 |
| yopal_deduplicated_shape_order.csv | 200 |

The order file retains original source-specific chainage and distances; it does not recalculate distances from representative coordinates or assert both directions serve a location. The next coverage analysis must separate direction hypotheses from ambiguous associations and assess large gaps. No GTFS publication or operational validation is authorized by this research result.

Source: existing historical-stops research files; see README.md for PIMUR maps, OSM attribution/ODbL, Firebase provenance and limitations. CSV files are derived from the repository snapshots, not asserted byte-identical to original uploaded files.
