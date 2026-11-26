"""Candidate route 9 circuit from the two OSM route relations, not an approved shape."""
import argparse,json,math,heapq
from collections import defaultdict
from pathlib import Path
from resolve_waypoints import objects

def distance(a,b):
    x=math.radians(b[0]-a[0])*math.cos(math.radians((a[1]+b[1])/2));y=math.radians(b[1]-a[1]);return 6371000*math.hypot(x,y)
def allowed(t):
    h=t.get("highway","");access=next((t[k] for k in ("bus","psv","motor_vehicle","vehicle","access") if k in t),"yes")
    return h in {"motorway","motorway_link","trunk","trunk_link","primary","primary_link","secondary","secondary_link","tertiary","tertiary_link","residential","unclassified","service","living_street","road"} and access not in {"no","private","agricultural","forestry","customers"}
def orientations(w):
    t=w["tags"];n=w["nodes"];v=next((t[k] for k in ("oneway:bus","oneway:psv","oneway") if k in t),"yes" if t.get("junction")=="roundabout" or t.get("highway")=="motorway" else "no")
    if v in ("yes","1","true"):return [n]
    if v=="-1":return [n[::-1]]
    if v in ("no","0","false"):return [n,n[::-1]]
    return []
def build(raw):
    obj=objects(raw)
    nodes={i:(e["lon"],e["lat"]) for (typ,i),e in obj.items() if typ=="node" and "lat" in e}
    ways={i:e for (typ,i),e in obj.items() if typ=="way" and allowed(e["tags"]) and all(n in nodes for n in e.get("nodes",[])) and len(e.get("nodes",[]))>=2}
    adj=defaultdict(dict)
    for w in ways.values():
        for seq in orientations(w):
            for a,b in zip(seq,seq[1:]):adj[a][b]=distance(nodes[a],nodes[b])
    def bridge(a,b):
        if a==b:return 0,[a]
        if distance(nodes[a],nodes[b])>500:return math.inf,[]
        q=[(0,a)];ds={a:0};prev={}
        while q:
            cost,n=heapq.heappop(q)
            if cost!=ds[n]:continue
            if n==b:
                p=[b]
                while p[-1]!=a:p.append(prev[p[-1]])
                return cost,p[::-1]
            for m,w in adj[n].items():
                c=cost+w
                if c<=500 and c<ds.get(m,math.inf):ds[m]=c;prev[m]=n;heapq.heappush(q,(c,m))
        return math.inf,[]
    ids=[13195183,13266086];members=[]
    for rid in ids:
        r=obj["relation",rid]
        for m in r["members"]:
            if m["type"]=="way" and m.get("role","") in ("","forward","backward"):
                w=ways.get(m["ref"])
                if not w:raise ValueError("missing or inaccessible way "+str(m["ref"]))
                opts=orientations(w)
                if m.get("role")=="forward":opts=[x for x in opts if x==w["nodes"]]
                if m.get("role")=="backward":opts=[x for x in opts if x==w["nodes"][::-1]]
                if not opts:raise ValueError("no permitted orientation")
                members.append((rid,m["ref"],opts))
    best=None
    for first in members[0][2]:
        states=[(0,first,[])]
        for rid,wid,opts in members[1:]:
            nxt=[]
            for seq in opts:
                choices=[]
                for cost,path,gaps in states:
                    d,p=bridge(path[-1],seq[0])
                    if math.isfinite(d):choices.append((cost+d,path+p[1:]+seq[1:],gaps+([{"before_way":wid,"distance_m":round(d,1),"from_node":path[-1],"to_node":seq[0]}] if d else [])))
                if choices:nxt.append(min(choices,key=lambda x:x[0]))
            states=nxt
            if not states:break
        for cost,path,gaps in states:
            d,p=bridge(path[-1],first[0])
            if math.isfinite(d):
                candidate=(cost+d,path+p[1:],gaps+([{"before_way":members[0][1],"distance_m":round(d,1),"from_node":path[-1],"to_node":first[0]}] if d else []))
                if best is None or candidate[0]<best[0]:best=candidate
    if best is None:raise ValueError("No closed directed route within 500 m join limits")
    cost,path,gaps=best
    assert path[0]==path[-1] and all(b in adj[a] for a,b in zip(path,path[1:]))
    coords=[nodes[i] for i in path];length=sum(distance(a,b) for a,b in zip(coords,coords[1:]))
    return {"type":"Feature","properties":{"route_id":"9","source":"OpenStreetMap contributors","source_relations":ids,"status":"candidate_not_approved","length_m":round(length,1),"points":len(coords),"bridge_m":round(cost,1),"bridges":gaps,"turn_restrictions_checked":False,"stop_policy_verified":False},"geometry":{"type":"LineString","coordinates":coords}}
def main():
    p=argparse.ArgumentParser();p.add_argument("--osm",type=Path,required=True);p.add_argument("--out",type=Path,default=Path("build"));a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    try:
        f=build(json.loads(a.osm.read_text(encoding="utf-8")))
        (a.out/"route9-candidate.geojson").write_text(json.dumps(f,ensure_ascii=False)+"\n")
        props=f["properties"]
    except (ValueError,KeyError) as e:props={"route_id":"9","status":"blocked","error":str(e)}
    (a.out/"route9-shape-report.json").write_text(json.dumps(props,indent=2)+"\n")
    print(json.dumps(props))
if __name__=="__main__":main()
