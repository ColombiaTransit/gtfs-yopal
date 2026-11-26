# Route status and frequency reconciliation — 2026-11-26

## Legal framework: chronological evidence

| Date | Instrument / evidence | Finding | Limit |
|---|---|---|---|
| 2013 | Decreto 088/2013, amending Decreto 044/2013 and repealing art. 1 of Resolución 0882/2009 | Route 13 incorporated into urban service; reported 5–6 min after fleet increase | Historical, before 2019 restructuring |
| 2017-10-11 | [Decreto 209/2017](https://vlex.com.co/vid/decreto-209-2017-municipio-1038201409) | Temporary operation of PIMUR trial routes 3, 4, 5, 12 | Only opening page accessible; expiry and operative articles not recovered |
| 2018-07-19 | [La Reportería](https://lareporteria.com/2018/07/19/en-yopal-abren-nuevas-rutas-de-transporte-colectivo/) | Municipal transit secretary reported dispatches every 8 minutes, extended service | Network-level statement before 2019; not route/day-specific |
| 2018-10-26 | Decreto 267/2018 | PIMUR adopted; routes, stop maps and operational tables referenced | Planning framework |
| 2019-04-15 | [Decreto 090/2019](https://vlex.com.co/vid/decreto-no-090-2019-1038224107) | Located bibliographic record and page 1 of 15; title explicitly adopts restructuring of 14 urban routes | Remaining pages require authorized vLex access or original municipal copy; no numerical tables extracted |
| 2019-09-12 | [Prensa Libre Casanare](https://prensalibrecasanare.com/yopal/34629-obras-de-mantenimiento-en-las-vnas-de-la-ciudadela-la-bendiciun-.html) | Municipal road maintenance explicitly prioritized route 12 in La Bendición | Historical operation, not proof of 2026 service |
| 2020-06-23 | [Mi Canal 2](https://www.micanal2.tv/alcaldia/secretaria-de-transito-de-yopal-viene-trabajando-en-todos-los-frentes-para-mejorar-la-movilidad-en-la-capital/) | Municipal secretary reported reopening routes 2,3,7,8,9,12 | Historical reopening during pandemic; Decreto 017 mentioned in same report concerns interdepartmental transport, not urban route frequencies |
| 2023 | Findeter MIB profile pp. 39–41 | Routes 2,3,13 identified in Comuna 6 | Historical |
| 2024-06-06 | Decreto 099/2024, technical study | Route 8 observed 8-min frequency, 25.5 km, April 10–12 fieldwork; see operator-research.md | Study not a legal dispatch interval |
| 2024-07-25 | [Prensa Libre Casanare](https://prensalibrecasanare.com/yopal/52190-cambio-no-autorizado-de-ruta-de-transporte-pblico-en-yopal-generu-controversia.html) | Route 3 terminal relocation from Torres de San Marcos to near Alameda Martha Mojica was unauthorized at that time | Current approval unresolved; separate from Calle 25 direction issue |
| 2024 | [Municipal council reporting](https://prensalibrecasanare.com/yopal/52844-cuestionamientos-a-la-gestiun-del-secretario-de-movilidad-de-yopal-durante-control-polntico-en-el-concejo.html) | Secretary stated Decreto 090 had not been modified; operator technical proposals under review | Not evidence that no amendments occurred after statement |
| 2025-02-10 | [Decreto 017/2025 reporting](https://prensalibrecasanare.com/yopal/53700-2400-nueva-tarifa-para-transporte-pblico-colectivo-urbano-en-yopal-tambiyn-reajuste-en-rutas-rurales.html) | Fare applies to 14 routes established under Decreto 090 | Network-level legal reference, not route-by-route confirmation |
| 2026-02-04 | [Decreto 030/2026 reporting](https://manantialstereo.com.co/noticia/2342900/nueva-tarifa-del-transporte-publico-entra-en-vigencia-en-yopal) | COP 2700 fare still references 2019 act | Tariff not operating authorization |
| 2026-02 | [Municipal secretary statement](https://prensalibrecasanare.com/yopal/56455-decreto-fiju-en-2700-tarifa-de-busetas-en-yopal-usuarios-con-sideraron-que-el-incremento-de-300-pesos-es-excesivo.html) | 13 established and nine operating routes | No individual IDs, discrepancy with 14-route references unresolved |

## Current disposition

All 14 route IDs remain in the research scope. The eight ColMind-enabled routes are provisional operational observations, not verified legal authorizations. The six disabled records must not be rejected solely on the enabled flag. Route 12 has particularly strong historical post-2019 operation evidence (2019 road maintenance, June 2020 reopening), but its OSM geometry also differs substantially from Firebase. Route 11 is the only disabled Firebase record with usable schedule values (weekday 05:20–17:40 every 15 min, Saturday 06:00–18:00 every 20 min, Sunday/holiday no service). Its snapshot schedule is undated and not current-service evidence. Route 1 has OSM 7-min interval and operating hours, but no independent current-service confirmation; tags also duplicated on route 9. Routes 4 and 5 have 2017 trial authorization, not verified continuing authority. Route 14 has no geometry or usable schedule.

The ninth operating route in the February 2026 report remains unidentified. Route 11 and route 12 are priority leads, not asserted active. No route-level legal expiry or withdrawal was verified; no disabled route is classified as permanently withdrawn.

## Frequency decision

Retain service_windows.csv unchanged as factual secondary-source observations (21 service day-types, three explicit no-service day-types). Keep observed historic alternatives in frequency_evidence.csv; none is a verified currently applicable route/day headway under Decreto 090. Do not apply the 2018 network-level 8-minute statement across all 14 routes or replace current reported values with the 2013 route 13 or 2024 route 8 observations without confirming applicability. No fabricated peak/off-peak blocks. Source labels distinguish reported service, official-study observations, OSM tags and legal acts. Full text of Decreto 090, subsequent amendments and annexes remains the highest priority.

## Next evidence to obtain

Request a lawful copy of all 15 pages of Decreto 090/2019 plus incorporated tables and subsequent amendments, suspension/withdrawal/reactivation acts and the current route dispatch schedule from Secretaría de Movilidad. vLex preview establishes the document identity but does not expose operational articles. A tariff decree cannot establish specific frequencies. No access restriction was bypassed. Search did not locate a free complete copy. No GTFS release or activation changes made.
