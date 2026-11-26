# OpenStreetMap review — 2026-11-26

Source: user-provided Overpass export (9).json, OSM base timestamp 2026-11-26T07:50:09Z. © OpenStreetMap contributors, ODbL (https://www.openstreetmap.org/copyright). Query bounding box south 5.260, west -72.470, north 5.390, east -72.340.

19 top-level objects: 4 bus stop nodes, 3 bus station ways (two terminal sites), 10 urban route relations (7 distinct route numbers), 2 regional route relations. No explicit urban relation stop/platform members. Regional routes excluded from urban scope.

## Stop candidates

Minimum point-to-line distances computed in EPSG:32618 against both branches of all available ColMind route records, after removing null coordinate slots. 50 m is a proximity screening threshold, not proof of boarding service.

| OSM node | Name | Latitude | Longitude | Routes within 50 m | Assessment |
|---|---|---:|---:|---|---|
| 6966216387 | Parada Colectivos La Paz, Pore | 5.3469345 | -72.4024313 | 2,8,9,11,13 | Likely regional; urban boarding unverified |
| 13161325707 | Unnamed | 5.3430002 | -72.387352 | 3,9 | Candidate urban stop; name and service unknown |
| 13417472101 | Nuevo Terminal de Yopal | 5.3144117 | -72.4255617 | None | Regional; nearest route 9 approx. 1.2 km |
| 13423682418 | Terminal de Yopal | 5.3353875 | -72.3904276 | 11,12 | Regional; urban boarding unverified |

Terminal ways: 179051489 and 1474128115 (old terminal site); 1462006023 (new terminal site). Do not count station polygons as separate urban stops.

## Urban route relations

| Route | Relation IDs | ColMind enabled |
|---|---|---|
| 1 | 3216817, 13266149 | false |
| 3 | 2920060 | true |
| 4 | 3245640 | false |
| 5 | 2918237 | false |
| 6 | 3216818 | true |
| 9 | 3245641, 13195183, 13266086 | true |
| 12 | 3221908 | false |

PTv2 relations 13195183 and 13266086 (route 9 both directions), and 13266149 (route 1, Estadio to undefined) contain operator Llano Lineas SA, interval 00:07 and opening_hours Mo-Fr 05:15-19:00; Sa 05:40-19:00; Su 06:00-19:00. Identical tags across the three relations may reflect copied defaults; source and validity are not verified. Route 9 conflicts with ColMind (9/8/10 min; 05:10-18:30, 05:20-17:20, 06:00-17:30). No public-holiday-specific OSM hours. Keep both observations; applicable municipal acts remain authoritative. Route 1's OSM evidence is an additional research lead, not confirmation of current operation.

## Geometry checks

For each OSM urban relation, unique member linework was compared to the union of both same-number Firebase branches (null slots removed; 50 m buffer). This is a geometric proximity metric, not direction or service verification.

| Route | Relation | Unique OSM km | OSM length within 50 m of Firebase (%) |
|---|---:|---:|---:|
| 1 | 3216817 | 0.41 | 96 |
| 1 | 13266149 | 5.11 | 93 |
| 3 | 2920060 | 10.47 | 80 |
| 4 | 3245640 | 4.60 | 96 |
| 5 | 2918237 | 9.87 | 82 |
| 6 | 3216818 | 8.44 | 84 |
| 9 | 3245641 | 0.48 | 97 |
| 9 | 13195183 | 10.71 | 95 |
| 9 | 13266086 | 10.90 | 89 |
| 12 | 3221908 | 7.45 | 7 |

Route 12 is a significant same-number geometry mismatch, potentially a changed or historical route; reconcile with applicable acts. Other incomplete OSM relations are not automatically usable as complete shapes. Firebase has two usable coordinate lists (not quality-validated) for 13 routes, including disabled IDs 1,4,5,11,12; route 14 has no usable geometry. Do not filter by enabled alone.

## Conclusion

OSM is inadequate as a full urban stop inventory. Seek official stop maps or evidence of actual continuous boarding policy before adopting continuous_pickup/drop_off. Do not invent stops or infer boarding rights from missing OSM mapping. Preserve OSM provenance and ODbL attribution. No raw Firebase telemetry or individual location data retained in the repository; no GTFS generation or publication yet.
