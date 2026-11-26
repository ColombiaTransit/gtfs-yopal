# Findeter MIB Yopal stop-map review

Reviewed 2026-11-26. Source: user-supplied 66-page 2023_PerfilTécnicoDefinitivo_MIB_Yopal.pdf; [public source](https://www.fiducentral.com/images/files/2024/convocatorias/findeter/obras/2023_PerfilT%C3%A9cnicoDefinitivo_MIB_Yopal.pdf).

Page 35 describes TUYO service in Llano Lindo / Comuna 6 on routes 2, 3 and 13. Page 39 states the city network is defined by 14 routes, identifies the same three as operating in the area, describes route 13 as having the most frequencies (no numerical headway), and reports a historical COP 2,000 fare. It separately discusses proposed future routes on Carrera 8 Oeste and Avenida Primera. This is historical official operational evidence, not a 2026 timetable or proof all 14 currently operate.

Figures 30–32 on pages 40–41 reproduce municipal mobility maps. Title blocks identify Rutas de transporte público colectivo urbano y paraderos, dated July 2017, scale 1:8000, sheets 2, 3 and 13 of 15. Blue stop symbols appear in the legend. Map content is likely from the earlier PIMUR operational design; whether every mapped stop was implemented is unknown. The PDF has no embedded original GIS attachments.

| Route | Figure | Page | PDF image xref | Native raster px | Preliminary symbol count |
|---|---|---|---|---|---:|
| 2 | 30 | 40 | 165 | 1202 x 835 | 46 |
| 3 | 31 | 40 | 166 | 1065 x 735 | 53 |
| 13 | 32 | 41 | 170 | 1104 x 766 | 39 |

Total 138 route-specific candidate markers, not 138 unique stops. Manual native-resolution inspection assisted by blue-color component detection; close pairs and small marks can be ambiguous. Pixel centers in findeter-stop-candidates.csv are approximate (origin top left of extracted native raster, not page). IDs are research IDs, not official stop IDs or route sequence. No WGS84 coordinates are asserted. Route 13 includes an isolated blue symbol requiring particular review.

Use original street intersections and stable road geometry to georeference each map independently. The street grid is rotated relative to north. Use at least 4 well-distributed ground controls and additional independent check points, assess residuals, avoid relying solely on a newer route alignment, and preserve historical position separately from any snapped coordinate. Compare with OSM and Firebase directions, then deduplicate only after distinguishing opposite-side stops and shared stops. Do not convert all historical symbols automatically to operational GTFS stops. Look for all 15 original plan sheets and original GIS data in municipal PIMUR records. No original PDF or map images redistributed; no feed generated.