"""Route a human-reviewed ordered anchor chain on the private bus profile.
Output is candidate geometry/time only, never approved pattern or boarding stops.
"""
import argparse,json,math,os
from pathlib import Path
import requests

def main():
    p=argparse.ArgumentParser();p.add_argument("--anchors",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    data=json.loads(a.anchors.read_text(encoding="utf-8"));rid=str(data["route_id"]);points=data["coordinates"]
    if data.get("reviewed") is not True or not 1<=int(rid)<=14 or not 3<=len(points)<=200 or points[0]!=points[-1]:raise SystemExit("Require reviewed closed ordered anchor chain")
    for lon,lat in points:
        if not (-72.7<float(lon)<-72.1 and 5.0<float(lat)<5.6):raise SystemExit("Anchor outside Yopal")
    url=os.environ.get("GRAPHHOPPER_URL","").rstrip("/")
    if not url:raise SystemExit("GRAPHHOPPER_URL missing")
    if not url.endswith("/route"):url+="/route"
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36","Accept":"application/json","Content-Type":"application/json"}
    cid,secret=os.environ.get("CF_ACCESS_CLIENT_ID"),os.environ.get("CF_ACCESS_CLIENT_SECRET")
    if cid and secret:headers.update({"CF-Access-Client-Id":cid,"CF-Access-Client-Secret":secret})
    # Route adjacent ordered points in small batches; preserve every intermediate anchor.
    geometry=[];distance=0;elapsed=0;legs=[]
    for i in range(len(points)-1):
        try:
            r=requests.post(url,headers=headers,json={"profile":"bus","points":[points[i],points[i+1]],"points_encoded":False,"instructions":False,"calc_points":True},timeout=(15,90),allow_redirects=False)
            if r.status_code!=200:raise SystemExit(f"GraphHopper HTTP {r.status_code} at leg {i+1}")
            path=r.json()["paths"][0];c=path["points"]["coordinates"];snaps=path["snapped_waypoints"]["coordinates"]
        except (requests.RequestException,ValueError,KeyError,IndexError,TypeError) as e:raise SystemExit(f"GraphHopper leg {i+1}: {type(e).__name__}") from None
        def gap(a,b):return 6371000*math.hypot(math.radians(b[0]-a[0])*math.cos(math.radians((a[1]+b[1])/2)),math.radians(b[1]-a[1]))
        if len(c)<2 or len(snaps)!=2 or max(gap(points[i],snaps[0]),gap(points[i+1],snaps[-1]))>50:raise SystemExit(f"Snap/geometry check failed at leg {i+1}")
        if geometry and gap(geometry[-1],c[0])>5:raise SystemExit(f"Disconnected leg {i+1}")
        geometry.extend(c if not geometry else c[1:]);distance+=float(path["distance"]);elapsed+=int(path["time"])
        legs.append({"leg":i+1,"distance_m":path["distance"],"time_ms":path["time"]})
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps({"type":"Feature","properties":{"route_id":rid,"status":"candidate_not_approved","profile":"bus","distance_m":distance,"time_ms":elapsed,"legs":legs,"source":"OpenStreetMap contributors / private GraphHopper"},"geometry":{"type":"LineString","coordinates":geometry}},indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
