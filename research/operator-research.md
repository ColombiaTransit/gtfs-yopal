# Operator assignment research — 2026-11-26

## Network-level operator

Municipal Decree 099 of 6 June 2024, annex 1 (technical tariff study, section 6.1, printed p. 8 of 34) explicitly describes Resolution 130/2010 authorizing the business collaboration among COOTRALLANERO, COOCATRANS, LLANO LINEAS and FLOTA SUGAMUXI S.A. The union temporal TUYO covers the urban route network using vehicles legally affiliated to the member companies and provides for unified dispatch and branding. This is primary municipal documentary evidence of the network arrangement in 2024; the original 2010 resolution and any later amendments are still missing. Indexed PDF text was accessible but direct screenshot retrieval returned HTTP 404.

Source: https://www.lavozdeyopal.co/wp-content/uploads/2024/06/113185_decreto-no-099-de-6-junio-2024-se-fijan-tarifas-para-servicio-publico-transporte-automotor-colectivo-pasajeros.pdf

Recommended GTFS representation: TUYO as one network-level agency, with individual route operator attribution only when supported by adequate evidence. This does not establish current legal validity of every route or the exclusive operating company.

## Route-level observations

| Route | Historical evidence | Current individual assignment |
|---|---|---|
| 2 | Coocatrans, April 2020 reopening | Unverified |
| 3 | Cotrallanero (spelling in 2020 reporting; municipal tariff study uses Cootrallanero) | Unverified |
| 6 | OSM relation 3216818 has no operator; Sueño Real itinerary from Firebase | Unknown |
| 7 | Flota Sugamuxi, May 2020 reopening | Unverified |
| 8 | Coocatrans, April 2020 and April 2024 municipal field survey | Unverified |
| 9 | Llano Líneas, 2020 and OSM relations 13195183 and 13266086 | Current assignment plausible, not independently confirmed for 2026 |
| 10 | Villa David itinerary; Cootrallanero vehicle reported in that neighborhood in May 2026, no route ID | Unknown; no attribution |
| 13 | Llano Lindo itinerary; Coocatrans vehicle reported in that sector in May 2026, no route ID | Unknown; no attribution |

Reopening source (29 April 2020): https://lareporteria.com/2020/04/29/con-3-de-las-14-rutas-se-reactivo-transporte-publico-en-yopal/
Route 7 corroboration: https://prensalibrecasanare.com/yopal/37424-niegan-operacion-a-ruta-urbana-de-pasajeros-por-no-disponer-medidas-de-bioseguridad.html
May 2026 neighborhood-only leads: https://prensalibrecasanare.com/yopal/57072-incendio-de-otra-buseta-ayer-en-yopal-fue-por-un-corto-circuito.html ; https://prensalibrecasanare.com/judicial/57065-delincuencia-comn-estarna-tras-intento-de-incineraciun-de-buseta-la-madrugada-de-este-jueves-en-yopal.html
Do not infer route assignments from neighborhood presence. Route 7 historically also served Villa David. Route 2 also serves Llano Lindo.

## Additional historical route and frequency evidence

- Decreto 088/2013 added route 13 to Decreto 044 of 2 May 2013, replacing the rural classification under article 1 of Resolución 0882/2009. The municipal report dated 18 June 2013 reports a planned increase from 8 to 12 vehicles and an interval reduction from 10–12 to 5–6 minutes. It does not name individual companies. Historical evidence only, predating Decreto 090/2019. https://prensalibrecasanare.com/yopal/7203-ruta-de-transporte-colectivo-a-8220llano-lindo8221-en-yopal-ahora-es-urbana.html
- Decree 099/2024 annex 1, printed p. 18 of 34, explicitly identifies Coocatrans route 8, 8-minute frequency and 25.5 km route length in its April 10–12, 2024 field survey. This is official observed/study evidence, not a verified legally authorized frequency. Keep distinct from ColMind 10/12/15 minute day-type values.
- The Consejo de Estado decision of 22 March 2013, case 85001-23-31-000-2007-00151-01, quotes Resolution 100540092 of 24 July 2007 and identifies Resolution 100.54.0065 of 15 May 2007 as the earlier urban fleet-capacity instrument for the four companies. It does not assign numbered urban routes. https://www.arielapp.co/es/biblioteca/documento/ce-85001-23-31-000-2007-00151-01-2013-04be4386
- Reporting on Decreto 030/2026 reiterates Decreto 090 of 15 April 2019. February 2026 reporting quotes 13 established and nine operating routes. Neither source identifies the three missing operators. https://manantialstereo.com.co/noticia/2342900/nueva-tarifa-del-transporte-publico-entra-en-vigencia-en-yopal ; https://prensalibrecasanare.com/yopal/56455-decreto-fiju-en-2700-tarifa-de-busetas-en-yopal-usuarios-con-sideraron-que-el-incremento-de-300-pesos-es-excesivo.html

## Conclusion

Five of the eight ColMind-enabled routes have named historical operating companies. Routes 6, 10 and 13 remain unresolved at company level. Use TUYO as the proposed agency and leave individual attribution blank for those routes. Preserve legal reconciliation of all 14 route records; do not infer exclusion from ColMind disabled flags. No current exclusive operator claims or new route authorizations are established. Request the original 2019 act and annexes or a municipal route-to-company dispatch list if further individual attribution is required.
