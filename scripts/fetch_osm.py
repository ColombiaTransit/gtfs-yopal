"""Fetch named road and bus-route topology from the private Overpass endpoint only."""
import argparse
import json
import os
from pathlib import Path
import requests

QUERY = """[out:json][timeout:180];
(
  way["highway"](5.22,-72.49,5.40,-72.31);
  nwr["highway"="bus_stop"](5.22,-72.49,5.40,-72.31);
  nwr["public_transport"~"^(platform|stop_position|station)$"](5.22,-72.49,5.40,-72.31);
  nwr["amenity"="bus_station"](5.22,-72.49,5.40,-72.31);
  relation["type"="route"]["route"="bus"](5.22,-72.49,5.40,-72.31);
);
out body;
>;
out skel qt;"""

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=Path("build/osm.json"));args=p.parse_args()
    url=os.environ.get("API_OVERPASS","").rstrip("/")
    if not url:raise SystemExit("API_OVERPASS missing; no public fallback")
    if not url.endswith("/interpreter"):url+="/interpreter"
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36","Accept":"application/json","Content-Type":"application/x-www-form-urlencoded"}
    cid,secret=os.environ.get("CF_ACCESS_CLIENT_ID"),os.environ.get("CF_ACCESS_CLIENT_SECRET")
    if cid and secret:headers.update({"CF-Access-Client-Id":cid,"CF-Access-Client-Secret":secret})
    try:
        r=requests.post(url,data={"data":QUERY},headers=headers,timeout=(15,240),allow_redirects=False)
        if r.status_code!=200:raise SystemExit(f"Private Overpass HTTP {r.status_code}")
        data=r.json()
    except (requests.RequestException,ValueError) as e:raise SystemExit("Private Overpass failed: "+type(e).__name__) from None
    if not isinstance(data,dict) or not isinstance(data.get("elements"),list) or not data["elements"] or data.get("remark"):raise SystemExit("Incomplete/invalid Overpass response")
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
    print(f"OSM elements: {len(data['elements'])}")
if __name__=="__main__":main()
