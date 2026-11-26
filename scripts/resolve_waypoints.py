"""Independent OSM exact intersection candidates; never auto-promote to stops or approved shapes."""
import argparse
import csv
import json
import re
import unicodedata
from collections import defaultdict,Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def norm(s):
    s="".join(c for c in unicodedata.normalize("NFKD",s.lower()) if not unicodedata.combining(c))
    s=re.sub(r"\s+"," ",s).strip()
    m=re.fullmatch(r"(calle|carrera|diagonal|transversal|c|k|d|t|cra|cl|kr|dg|tv)\.?\s*(\d+)\s*([a-z])?(?:\s+(oeste|este|sur|norte))?",s)
    if m:
        a,n,b,d=m.groups();a={"calle":"c","cl":"c","carrera":"k","cra":"k","kr":"k","diagonal":"d","dg":"d","transversal":"t","tv":"t"}.get(a,a)
        return a+n+(b or "")+(" "+d if d else "")
    return s
def objects(data):
    out={}
    for e in data["elements"]:
        key=(e["type"],e["id"]);old=out.get(key,{})
        out[key]={**old,**e,"tags":{**old.get("tags",{}),**e.get("tags",{})}}
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument("--osm",type=Path,required=True);p.add_argument("--out",type=Path,default=Path("build"));a=p.parse_args()
    obj=objects(json.loads(a.osm.read_text(encoding="utf-8")))
    nodes={i:e for (typ,i),e in obj.items() if typ=="node" and "lat" in e}
    by_name=defaultdict(set)
    for (typ,i),e in obj.items():
        tags=e["tags"]
        if typ!="way" or "highway" not in tags or tags["highway"] in {"footway","cycleway","path","steps","pedestrian","construction","proposed"}:continue
        for name in (tags.get("name"),tags.get("alt_name"),tags.get("official_name")):
            if name:by_name[norm(name)].update(n for n in e.get("nodes",[]) if n in nodes)
    with (ROOT/"data/official-waypoint-candidates.csv").open(encoding="utf-8",newline="") as f:rows=list(csv.DictReader(f))
    report=[];counts=defaultdict(Counter)
    for row in rows:
        label=row["waypoint"];parts=label.split("/")
        exact=[]
        if len(parts)==2:
            first,second=map(norm,parts)
            # Do not strip ambiguous landmark prefixes or parentheses.
            exact=sorted(by_name.get(first,set()) & by_name.get(second,set()))
        status="unique_exact_intersection" if len(exact)==1 else "multiple_exact_intersections" if exact else "unresolved"
        counts[row["route_id"]][status]+=1
        report.append({**row,"resolution":status,"candidates":[{"osm_node_id":i,"lon":nodes[i]["lon"],"lat":nodes[i]["lat"]} for i in exact]})
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"waypoint-matches.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary={rid:dict(c) for rid,c in counts.items()}
    (a.out/"waypoint-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary))
if __name__=="__main__":main()
