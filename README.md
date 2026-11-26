# Yopal urban bus GTFS

Static GTFS research and preparation for urban bus services in Yopal, Casanare, Colombia.

**Status (2026-11-26): legal research closed for the initial generator.** Technical generator and geometry workflow added; reviewed input patterns and public feed not yet available.

- [Research closure and generator handover](research/research-closure.md)
- [Legal route baseline](research/legal-route-baseline.csv)
- [Official service windows](research/decreto_090_2019_service_windows.csv)
- [Official route assignments](research/decreto_090_2019_routes.csv)
- [Legal chronology](research/legal-act-chronology.csv)
- [Source register](research/sources.md)
- [Route 8 observed journey times](research/route8-observed-travel-times.csv)
- [Shape validation](research/shape-validation/README.md)
- [Historical stop research](research/historical-stops/stop-research-closure.md)

Decreto 090/2019 is the latest verified route-specific framework: 14 route candidates and 42 authorized day-type windows. Decreto 030/2026 establishes COP 2700 and explicitly references 090. The complete published Normatividad index was collected (4574 records); 18 shortlisted acts and 21 PDFs retrieved, with no later permanent numbered-route amendment or withdrawal identified in reviewed sources. Metadata screening is not exhaustive legal verification. No further general archive crawl is planned.

Route selection follows applicable acts chronologically; the independent ColMind enabled flag is not a legal decision. The eight reported enabled routes and nine reported operating routes remain distinct from the 14-route legal baseline. No current operation is asserted for every authorized route. Official headways are maximum intervals, not exact observed timetables. Source reuse rights, current stop locations and boarding policy, independent shape construction, and actual service evidence remain release considerations. Do not publish an unverified traveler feed. See the handover for decisions and remaining engineering work.

## Technical build

See [technical realization](research/technical-realization.md) and [official waypoint candidates](data/official-waypoint-candidates.csv). GitHub Actions builds a partial schedule plan, validates an isolated synthetic fixture, and retrieves independent OSM geometry candidates using private Overpass. It does not publish a traveler feed.
