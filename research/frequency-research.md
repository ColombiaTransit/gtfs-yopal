# Yopal frequency research

Review date: 2026-11-26.

## Source hierarchy

1. Applicable municipal decrees/resolutions and their technical annexes: preferred for authorized routes, dispatch intervals and operating hours. Check later amendments and actual operating status separately.
2. Official operator/TUYO publications: preferred for current operating information where available.
3. ColMind Studio / InfoBusetas: provisional secondary source. Independent local initiative; the user observed extensive advertising on the websites. Hobby-project/advertising-funded status is an impression, not a verified organizational or funding classification. Advertising is not proof of inaccurate data. The original source of its numerical schedules is unknown.
4. Historic studies and counts: useful for comparison, not automatically a replacement for an applicable operating act.

## Official research already performed

- Decreto 267 of 26 October 2018, articles 16–18: proposed 14 routes, references to route/stop maps and tables 3-5 through 3-19 in Estructuración de Sistema Integrado de Transporte Público de Yopal. The operational annexes were not obtained.
- Municipal press release 1003.116-0247, 22 May 2019: implementation by TUYO, modified frequencies and expanded service hours; no numerical route-level schedules.
- Decreto 090 of 15 April 2019: identified as the route restructuring instrument through subsequent references; full text and annexes remain missing. No claim that a specific ColMind headway is authorized by this decree.
- Original study: Convenio 1004/2015, SECOP I 15-4-3970516. Missing operational report and maps.
- PIMUR update: MYCA-SM-CM-008-2023, CO1.NTC.5098429, CO1.PCCNTR.5634056. Technical procurement documents prescribe route inventory, georeferencing, frequency/occupancy and operational design; actual numerical deliverables not obtained.
- Decreto 099/2024: earlier lead for a route 8 travel-time survey; original table still to verify. Not a verified headway source.
- See [annex review](pimur-annex-review.md) and [update procurement review](pimur-update-procurement.md). Park further administrative contract-document investigation unless it leads directly to technical transport data.

## ColMind cross-check

Sources:
- COLMIND_INDEX: https://infobusetas.click/yopal (MHT displayed last update 2026-02-27).
- COLMIND_R2: route 2 detail page.
- COLMIND_FIREBASE: https://rutas-busetas-yopal-default-rtdb.firebaseio.com/features/0/rutas.json (user-provided export reviewed 2026-11-26; dataset update timestamp not established).
- IndexController and DetalleRutaController source supplied by user; website displays start as AM and end as PM. Normalize end hours 01–11 by adding 12, 12:00 remains noon. No-service placeholders are not actual times. Do not infer a service from a disabled record.

The Firebase export has 14 route records; enabled IDs 2,3,6,7,8,9,10,13. All 24 active-route day-type records agree with the existing [service windows](service_windows.csv), including 21 service records and three explicit no-service records. This is same-publisher cross-checking, NOT independent official validation.

| Route | Weekday minutes | Saturday minutes | Sunday/holiday minutes |
|---|---:|---:|---:|
| 2 | 8 | 10 | 15 |
| 3 | 8 | 10 | 30 |
| 6 | 10 | 10 | No service |
| 7 | 30 | 40 | 40 |
| 8 | 10 | 12 | 15 |
| 9 | 9 | 8 | 10 |
| 10 | 16 | No service | No service |
| 13 | 10 | 8 | 12 |

Disabled route 11 retains weekday 05:20–17:40 / 15 min, Saturday 06:00–18:00 / 20 min, Sunday no service. Undated disabled-record evidence only; do not activate or describe as an established historical timetable.

## GTFS decisions pending

- No independently verified numerical legal headways yet (0/8 enabled routes).
- No confirmed peak/off-peak windows. Do not invent them.
- Headway applicability (direction, whole loop or corridor), dispatch origin and end-window inclusivity remain unverified; both geometry branches meeting at termini do not prove two independent scheduled services. Avoid double-counting departures.
- Sundays and public holidays grouped by source; use Python holidays for Colombian calendar exceptions if adopted.
- User reports estimateTime=false for Yopal. Do not treat simulated positions or estimated departures as observations. Route 2 has velocity=20; not validated travel time. Other enabled routes lack velocity.
- Both geometry branches available in the JSON. Check nulls, gaps and endpoints; official stops remain missing. Use GraphHopper for estimated travel times as appropriate, not as a source of legal frequency.
- Exclude ubiStreams and other crowdsourced individual location/telemetry records completely from retained/public datasets. No raw Firebase export committed.
- Reuse terms remain unresolved; no redistribution of original geometry or derived GTFS release until reviewed. Public access does not establish an open license.

Preserve current service_windows.csv as reported observations; when official numerical evidence is obtained, keep the source and effective date separately, compare route/day values and record discrepancies rather than silently replacing evidence.
