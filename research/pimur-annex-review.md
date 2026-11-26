# PIMUR annex review — 2026-11-26

This note supersedes earlier tentative claims about the contents of the Findeter annexes. Raw third-party files are not committed.

## Archive provenance

The user supplied inventories for both archives. SHA-256:
- AnexosPT_Yopal.zip: 20a08eadcfb63a4c8692aecf01a1a7830c7b2a458a8ad83a1db3fe15cf0a572f
- Anexos PT Yopal.zip: 114105d558422e3358ce39e3e69cf8c269726eb4a63c06dbd93e63fbb166bd16

The inventories show largely overlapping contents with different packaging and minor changes. Individual archive members have not been hash-compared. The transport-specific operational report and separate route map annexes are not listed in either inventory.

## Primary documents inspected

- Decreto 267, 26 October 2018 (24-page supplied PDF): Article 3 (p. 2) lists the transport structuring report as a separate component. Article 5 (p. 4) specifies 12 years from publication. Articles 16–18 (p. 6) provide for subsequent legal adoption of 14 proposed routes, cite 14 route/stop maps and tables 3-5 to 3-19 of the separate transport report. The maps are not included in this PDF and there are no embedded PDF attachments. Article 66 (p. 24) addresses authorized companies. This decree is a planning instrument, not a per-route schedule or proof of current operation.
- Municipal press release 1003.116-0247, 22 May 2019 (3 pages), p. 2: confirms a decree setting 14 modified routes with altered frequencies and expanded operating hours was being implemented by TUYO through its constituent companies. This is primary historical confirmation of TUYO, but not current operator assignments or numerical frequencies.
- Metodología para la elaboración del PIMUR (76 pages), p. 10: correct agreement reference is Convenio de Cooperación 1004 of 19 June **2015**, not 2016. Activity 2, pp. 36–60, describes collection of itineraries, stop locations, frequencies, service hours, fares, company data and GPS travel times (p. 55), dispatch counts (p. 56), and proposed operational summary sheets (p. 60). These are methodology, not measured results.
- Formulacion de Tránsito - Espacio público (194 pages), p. 188: specifically identifies Anexo 3, Estructuración del Sistema de Transporte Público del Municipio de Yopal. Diseño Operativo. Pages 105–120 mainly concern intermunicipal/rural transport; do not use them as urban route schedules.
- Diagnostico PLSV municipio de Yopal (147 pages), p. 128: cites lack of stops in the municipal 2012–2015 diagnostic. This is historical and not evidence for current continuous boarding. Page 135 confirms the distinct transport structuring component.
- Formulacion PLSV Municipio Yopal (218 pages): safety-policy report; no per-route schedule tables located in targeted text review.

## ArcGIS package PMI_COMUNA_VI.mpk

Successfully extracted the 7z archive (412 files) and enumerated shapefile and FileGDB layers using GDAL/pyogrio. v10 and v108 contain parallel geodatabases; do not count them as distinct networks. 14 shapefile layers plus six logical FileGDB layers (including annotation), for 20 logical layer entries. Selected useful layers:

| Layer | Features | Content |
|---|---:|---|
| NOMENCLATURA_VIAL_DECRETO | 1644 | Street lines and NOMENCLATURA_NUEVA field; CTM12 Origen Unico CRS |
| BARRIOS_25_04_2023 | 186 | Neighborhood polygons and NOMBRE |
| COMUNAS_POT | 7 | Comuna polygons |
| VIAS_DESCRIPCION | 115 | Street lines with names and pavement |
| PROPUESTA_FINAL | 21 | Pavement/infrastructure improvements, not bus routes |
| P1 | 15 | Lines, unclear purpose; not identified as bus routes |
| A_ACTIVIDAD_POT | 693 | Land use and facilities, includes bus terminal polygon |
| BARRIOS_SOLICITUD | 16 | Neighborhood project areas |
| Veredas_025_2020_2 | 95 | Rural areas |

Most layers use EPSG:3117. No dedicated transit route or bus stop layers were found. Keep street and neighborhood data as potential reference data; use only after checking reuse rights. No GIS geometries committed.

## Next research targets

1. Locate Decreto 090 dated 15 April 2019, including all tables and annexes. Secondary confirmation: https://manantialstereo.com.co/noticia/2342900/nueva-tarifa-del-transporte-publico-entra-en-vigencia-en-yopal and https://prensalibrecasanare.com/yopal/53700-2400-nueva-tarifa-para-transporte-pblico-colectivo-urbano-en-yopal-tambiyn-reajuste-en-rutas-rurales.html .
2. Recover the separate PIMUR operational report / Anexo 3 and the 14 route maps, through the municipal archive or original cooperation agreement deliverables.
3. Verify whether 2019 planned/authorized routes and stops were actually implemented and remain current; compare against ColMind eight active routes.
4. The 2024 municipal statement reported no modification of Decreto 090: https://prensalibrecasanare.com/yopal/52844-cuestionamientos-a-la-gestiun-del-secretario-de-movilidad-de-yopal-durante-control-polntico-en-el-concejo.html . This is not proof of no subsequent amendments.
5. Existing 2026 service-window and route inventory remains provisional. No scraper or generator built.
