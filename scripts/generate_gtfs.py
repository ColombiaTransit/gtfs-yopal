"""Create canonical GTFS schedule plan and build only from reviewed route patterns.
The default command never invents geometry or stops. All test fixture data are synthetic.
"""
import argparse
import csv
import datetime as dt
import io
import json
import math
import zipfile
from pathlib import Path
import holidays

ROOT = Path(__file__).resolve().parents[1]
OP = {"Cootrallanero Ltda.":"cootrallanero", "Coocatrans Ltda.":"coocatrans",
      "Flota Sugamuxi S.A.":"sugamuxi", "Llano Líneas S.A.":"llano-lineas", "TUYO":"tuyo"}
DAY = {"weekday": [1,1,1,1,1,0,0], "saturday":[0,0,0,0,0,1,0], "sunday":[0,0,0,0,0,0,1]}
MUNICIPAL_URL = "https://www.yopal-casanare.gov.co/"
FARE = "2700"
FIELDS = {
    "agency.txt":"agency_id agency_name agency_url agency_timezone agency_lang",
    "routes.txt":"route_id agency_id route_short_name route_long_name route_type continuous_pickup continuous_drop_off",
    "calendar.txt":"service_id monday tuesday wednesday thursday friday saturday sunday start_date end_date",
    "calendar_dates.txt":"service_id date exception_type",
    "trips.txt":"route_id service_id trip_id trip_headsign direction_id shape_id",
    "frequencies.txt":"trip_id start_time end_time headway_secs exact_times",
    "stops.txt":"stop_id stop_name stop_lat stop_lon location_type",
    "stop_times.txt":"trip_id arrival_time departure_time stop_id stop_sequence pickup_type drop_off_type shape_dist_traveled timepoint",
    "shapes.txt":"shape_id shape_pt_lat shape_pt_lon shape_pt_sequence shape_dist_traveled",
    "fare_attributes.txt":"fare_id price currency_type payment_method transfers agency_id",
    "fare_rules.txt":"fare_id route_id",
    "attributions.txt":"attribution_id route_id organization_name is_operator",
    "feed_info.txt":"feed_publisher_name feed_publisher_url feed_lang feed_start_date feed_end_date feed_version",
}

def read_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def sec(t):
    h,m,*s=map(int,t.split(":"))
    if h<0 or not 0<=m<60 or (s and not 0<=s[0]<60):raise ValueError("Invalid time")
    return h*3600+m*60+(s[0] if s else 0)

def clock(s):
    s=int(s);return f"{s//3600:02d}:{s//60%60:02d}:{s%60:02d}"

def date8(d):return d.strftime("%Y%m%d")
def distance(a,b):
    x=math.radians(b[0]-a[0])*math.cos(math.radians((a[1]+b[1])/2))
    y=math.radians(b[1]-a[1])
    return 6371000*math.hypot(x,y)

def coords(p):
    if not isinstance(p,(list,tuple)) or len(p)!=2:raise ValueError("Coordinate needs lon,lat")
    lon,lat=map(float,p)
    if not (-72.7<lon<-72.1 and 5.0<lat<5.6):raise ValueError("Point outside Yopal review extent")
    return lon,lat

def legal_inputs():
    routes=read_csv(ROOT/"research/decreto_090_2019_routes.csv")
    wins=read_csv(ROOT/"research/decreto_090_2019_service_windows.csv")
    waypoints=read_csv(ROOT/"data/official-waypoint-candidates.csv")
    ids={str(i) for i in range(1,15)}
    if len(routes)!=14 or {r["route_id"] for r in routes}!=ids:raise ValueError("Route inventory mismatch")
    if len(wins)!=42 or {(w["route_id"],w["day_type"]) for w in wins}!={(r,d) for r in ids for d in DAY}:raise ValueError("Service matrix mismatch")
    if {r["route_id"] for r in waypoints}!=ids:raise ValueError("Missing waypoint candidates")
    for w in wins:
        if w["source_id"]!="DEC_090_2019" or not 0<=sec(w["start_local"])<sec(w["end_local"])<=86400 or not 0<int(w["maximum_headway_minutes"])<=120:raise ValueError("Invalid legal window")
    return routes,wins,waypoints

def base(start,end,fixture=False):
    if end<start or (end-start).days>730:raise ValueError("Invalid feed date range")
    routes,wins,waypoints=legal_inputs()
    out={k:[] for k in FIELDS}
    for name,id in OP.items():
        out["agency.txt"].append([id,("TEST FIXTURE - " if fixture else "")+name,MUNICIPAL_URL,"America/Bogota","es"])
        out["fare_attributes.txt"].append(["fare-"+id,FARE,"COP",0,0,id])
    for day,bits in DAY.items():out["calendar.txt"].append([day,*bits,date8(start),date8(end)])
    for day in sorted(holidays.country_holidays("CO",years=range(start.year,end.year+1))):
        if start<=day<=end and day.weekday()!=6:
            out["calendar_dates.txt"].extend([["weekday" if day.weekday()<5 else "saturday",date8(day),2],["sunday",date8(day),1]])
    for r in routes:
        rid=r["route_id"];aid=OP[r["operator_as_assigned_2019"]]
        name=r["official_origin"]
        out["routes.txt"].append([rid,aid,rid,"Circuito desde "+name,3,1,1])
        out["fare_rules.txt"].append(["fare-"+aid,rid])
        if aid=="tuyo":
            for operator in OP:
                if operator!="TUYO":out["attributions.txt"].append([rid+"-"+OP[operator],rid,operator,1])
    for w in wins:
        rid=w["route_id"];day=w["day_type"];tid=rid+"-"+day
        out["trips.txt"].append([rid,day,tid,next(r["official_origin"] for r in routes if r["route_id"]==rid),0,"shape-"+rid])
        out["frequencies.txt"].append([tid,clock(sec(w["start_local"])),clock(sec(w["end_local"])),int(w["maximum_headway_minutes"])*60,0])
    out["feed_info.txt"].append(["TEST FIXTURE - ColombiaTransit" if fixture else "ColombiaTransit","https://github.com/ColombiaTransit/gtfs-yopal","es",date8(start),date8(end),"fixture" if fixture else "research-"+date8(start)])
    return out,routes,wins,waypoints

def attach(out,patterns,fixture=False):
    wanted={r[0] for r in out["routes.txt"]}
    if set(patterns)!=wanted:raise ValueError("All 14 route patterns required; no silent route omission")
    stops={}
    for rid,p in patterns.items():
        if not all(p.get(k) is True for k in ("shape_approved","stop_policy_verified","reuse_verified")):
            raise ValueError("Unapproved shape, boarding or reuse for route "+rid)
        if not p.get("source") or not p.get("stop_source") or not p.get("time_source"):raise ValueError("Missing provenance for route "+rid)
        if bool(p.get("synthetic"))!=fixture:raise ValueError("Synthetic and actual inputs must not mix")
        geom=[coords(q) for q in p["shape"]]
        if len(geom)<3 or distance(geom[0],geom[-1])>15:raise ValueError("Circuit not closed for "+rid)
        dist=[0.]
        for a,b in zip(geom,geom[1:]):
            d=distance(a,b)
            if d<=0 or d>1000:raise ValueError("Duplicate or long segment for "+rid)
            dist.append(dist[-1]+d)
        if dist[-1]<100:raise ValueError("Degenerate shape")
        for i,(lon,lat) in enumerate(geom):out["shapes.txt"].append(["shape-"+rid,lat,lon,i+1,round(dist[i],3)])
        seq=p["stops"]
        if len(seq)<2 or seq[0]["stop_id"]!=seq[-1]["stop_id"]:raise ValueError("Circuit must return to original stop: "+rid)
        last_index=-1;last_time=-1
        for i,s in enumerate(seq):
            if s.get("designated_stop") is not True:raise ValueError("Unverified boarding point")
            index=s["shape_index"]
            if type(index)is not int or not last_index<index<len(geom):raise ValueError("Nonmonotonic stop order")
            last_index=index
            lon,lat=coords([s["lon"],s["lat"]])
            if distance((lon,lat),geom[index])>50:raise ValueError("Stop exceeds 50m snap distance")
            stopid=str(s["stop_id"]);name=s["name"].strip()
            if not stopid or not name:raise ValueError("Empty stop identity")
            stop=[stopid,name,lat,lon,0]
            if stopid in stops and stops[stopid]!=stop:raise ValueError("Conflicting stop identity")
            stops[stopid]=stop
            arr,dep=s["arrival_secs"],s["departure_secs"]
            if type(arr)is not int or type(dep)is not int or not 0<=arr<=dep or arr<=last_time:raise ValueError("Nonmonotonic times")
            if i==0 and (index!=0 or arr!=0 or dep!=0):raise ValueError("First departure must be zero and shape origin")
            if i==len(seq)-1 and index!=len(geom)-1:raise ValueError("Last stop must be shape endpoint")
            last_time=dep
            for day in DAY:out["stop_times.txt"].append([rid+"-"+day,clock(arr),clock(dep),stopid,i+1,1 if i==len(seq)-1 else 0,1 if i==0 else 0,round(dist[index],3),1])
    out["stops.txt"]=list(stops.values())

def write_table(path,headers,rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.writer(f);writer.writerow(headers);writer.writerows(rows)
def zip_feed(path,out):
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for k,rows in out.items():
            if k=="calendar_dates.txt" and not rows:continue
            f=io.StringIO(newline="")
            w=csv.writer(f,lineterminator="\n");w.writerow(FIELDS[k].split());w.writerows(rows)
            z.writestr(k,f.getvalue().encode("utf-8"))

def fixture_patterns():
    # Only for exercising code and canonical validator; never a traveler dataset.
    result={}
    for i in range(1,15):
        x=-72.43+i*0.002;y=5.31
        geom=[[x,y],[x+.001,y],[x+.001,y+.001],[x,y+.001],[x,y]]
        def stop(id,name,index,t):
            lon,lat=geom[index]
            return {"stop_id":id,"name":"TEST FIXTURE "+name,"lon":lon,"lat":lat,"shape_index":index,"arrival_secs":t,"departure_secs":t,"designated_stop":True}
        result[str(i)]={"synthetic":True,"shape_approved":True,"stop_policy_verified":True,"reuse_verified":True,"source":"synthetic fixture","stop_source":"synthetic fixture","time_source":"synthetic fixture","shape":geom,"stops":[stop(f"fixture-{i}-a","A",0,0),stop(f"fixture-{i}-b","B",2,300),stop(f"fixture-{i}-a","A",4,600)]}
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",type=dt.date.fromisoformat,default=dt.date.today())
    p.add_argument("--end",type=dt.date.fromisoformat)
    p.add_argument("--out",type=Path,default=Path("build"))
    p.add_argument("--mode",choices=["plan","build","fixture"],default="plan")
    p.add_argument("--patterns",type=Path,default=ROOT/"data/approved-patterns.json")
    args=p.parse_args()
    end=args.end or args.start+dt.timedelta(days=364)
    out,routes,wins,waypoints=base(args.start,end,args.mode=="fixture")
    args.out.mkdir(parents=True,exist_ok=True)
    if args.mode=="plan":
        # These are explicitly partial GTFS-shaped tables, not a GTFS feed.
        plan=args.out/"schedule-plan";plan.mkdir(exist_ok=True)
        for k in ("agency.txt","routes.txt","calendar.txt","calendar_dates.txt","trips.txt","frequencies.txt","fare_attributes.txt","fare_rules.txt","attributions.txt"):
            write_table(plan/k.replace(".txt",".csv"),FIELDS[k].split(),out[k])
        report={"route_candidates":len(routes),"service_windows":len(wins),"waypoint_candidates":len(waypoints),"agency_count":len(OP),"holiday_exceptions":len(out["calendar_dates.txt"]),"approved_patterns":0,"feed_created":False,"status":"awaiting_reviewed_shapes_and_stops","fare_COP":FARE,"exact_times":0}
        (args.out/"readiness.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps(report))
        return
    patterns=fixture_patterns() if args.mode=="fixture" else json.loads(args.patterns.read_text(encoding="utf-8"))
    attach(out,patterns,args.mode=="fixture")
    name="gtfs-yopal-SYNTHETIC-TEST.zip" if args.mode=="fixture" else "gtfs-yopal-research-draft.zip"
    zip_feed(args.out/name,out)
    print(json.dumps({"mode":args.mode,"filename":name,"rows":{k:len(v) for k,v in out.items()}}))

if __name__=="__main__":main()
