"""Reconstruct provisional legal circuits from ordered waypoints and independent OSM.

No candidate is promoted to approved shape or boarding stop. Unresolved waypoints
remain visible; a connector across them is a routing hypothesis, not legal evidence.
"""
import argparse
import csv
import heapq
import json
import math
import re
from collections import defaultdict, Counter
from functools import lru_cache
from pathlib import Path

from resolve_waypoints import norm, objects
from osm_route9 import allowed, orientations, distance

ROOT = Path(__file__).resolve().parents[1]
# Explicit name equivalents, not blanket interchange of Carrera/Transversal.
ALIASES = {
    "via a sirivana": ["via sirivana"],
    "via sirivana": ["via a sirivana"],
    "marginal de la selva": ["via monterrey - yopal", "via yopal - paz de ariporo"],
    "avenida la cultura": ["diagonal15"],
    "c37c": ["c37c"],
}
# Candidate intersection references explicitly written in compound landmark labels.
LANDMARK_INTERSECTIONS = {
    "entrada la decision c15/k8": "c15/k8",
    "intercambiador vial c24/k5": "c24/k5",
    "villa lucia d44/c31": "d44/c31",
    "entrada llano lindo calle 60 carrera 5": "c60/k5",
    "k8/c14 (esquina hospital)": "k8/c14",
}
LANDMARKS = {
    "villa david": ["villa david"],
    "ciudadela la bendicion": ["bendicion"],
    "la guafilla": ["guafilla"],
    "torres del silencio (k3 oeste por c40)": ["torres del silencio"],
    "nuevo hospital": ["hospital regional", "hospital de la orinoquia", "hospital horo"],
    "glorieta estadio": ["estadio"],
    "glorieta estadio calle 40": ["estadio"],
    "alcaldia municipal": ["alcaldia"],
    "alcaldia municipal - diagonal 15": ["alcaldia"],
    "entrada torres de san marcos": ["torres de san marcos"],
    "glorieta entrada club real casanare": ["real casanare"],
    "marginal de la selva frente a enerca": ["enerca"],
    "marginal de la selva - gaula ejercito": ["gaula"],
    "entrada llano lindo calle 60": ["llano lindo"],
    "k1/senderos y bosques de manare": ["senderos", "bosques de manare"],
}
# Approximate 100 m spatial buckets. Distances and checks are in metres.
STEP = .0009
MAX_NEAR = 65
MAX_LANDMARK_SNAP = 120
MAX_LAYER = 20
MAX_LEG = 18000

def canon(s):
    s = norm(s)
    return re.sub(r"^(calle|carrera|diagonal|transversal)(?=\d)",
                  lambda m: {"calle":"c","carrera":"k","diagonal":"d","transversal":"t"}[m[1]],s)

def grid(p):return (math.floor(p[0]/STEP),math.floor(p[1]/STEP))

class Graph:
    def __init__(self,raw):
        self.obj=objects(raw)
        self.nodes={i:(e["lon"],e["lat"]) for (typ,i),e in self.obj.items() if typ=="node" and "lat" in e}
        self.adj=defaultdict(dict)
        self.by_name=defaultdict(set)
        self.node_names=defaultdict(set)
        self.ways={}
        self.landmarks=[]
        self.restrictions=[]
        for (typ,i),e in self.obj.items():
            t=e.get("tags",{})
            if typ=="way" and allowed(t) and all(n in self.nodes for n in e.get("nodes",[])) and len(e.get("nodes",[]))>=2:
                names={canon(t[k]) for k in ("name","official_name","alt_name") if t.get(k)}
                self.ways[i]=e
                for name in names:
                    self.by_name[name].update(e["nodes"])
                for n in e["nodes"]:self.node_names[n].update(names)
                for seq in orientations(e):
                    for a,b in zip(seq,seq[1:]):
                        if a==b:continue
                        d=distance(self.nodes[a],self.nodes[b])
                        old=self.adj[a].get(b)
                        if old is None or d<old[0]:self.adj[a][b]=(d,i,names)
            if t.get("name") and any(s in canon(t["name"]) for terms in LANDMARKS.values() for s in terms):
                points=[self.nodes[i]] if typ=="node" and i in self.nodes else [self.nodes[n] for n in e.get("nodes",[]) if n in self.nodes]
                if typ=="relation":
                    for m in e.get("members",[]):
                        if m["type"]=="way":
                            w=self.obj.get(("way",m["ref"]),{})
                            points.extend(self.nodes[n] for n in w.get("nodes",[]) if n in self.nodes)
                if points:
                    center=(sum(p[0] for p in points)/len(points),sum(p[1] for p in points)/len(points))
                    self.landmarks.append((canon(t["name"]),typ,i,center))
            if typ=="relation" and t.get("type")=="restriction":
                self.restrictions.append(e)
        self.road_nodes=set(self.adj)|{b for edges in self.adj.values() for b in edges}
        self.grid=defaultdict(list)
        for n in self.road_nodes:self.grid[grid(self.nodes[n])].append(n)
        self.turns=defaultdict(list);self.unsupported_restrictions=0
        for r in self.restrictions:
            t=r["tags"];ex={x.strip() for x in t.get("except","").split(";")}
            if ("bus" in ex or "psv" in ex) and not (t.get("restriction:bus") or t.get("restriction:psv")):continue
            kind=t.get("restriction:bus") or t.get("restriction:psv") or t.get("restriction")
            members=r.get("members",[])
            via=[m["ref"] for m in members if m["role"]=="via" and m["type"]=="node"]
            fr=[m["ref"] for m in members if m["role"]=="from" and m["type"]=="way"]
            to=[m["ref"] for m in members if m["role"]=="to" and m["type"]=="way"]
            if not kind or len(via)!=1 or len(fr)!=1 or len(to)!=1 or "restriction:conditional" in t:
                self.unsupported_restrictions+=1;continue
            if kind.startswith(("no_","only_")):self.turns[via[0],fr[0]].append((kind,to[0],r["id"]))
            else:self.unsupported_restrictions+=1

    def near(self,p,limit):
        x,y=grid(p);n=math.ceil(limit/95)+1
        for i in range(x-n,x+n+1):
            for j in range(y-n,y+n+1):
                for node in self.grid.get((i,j),[]):
                    d=distance(p,self.nodes[node])
                    if d<=limit:yield d,node

    def names(self,label):
        n=canon(label)
        vals={n}
        vals.update(canon(x) for x in ALIASES.get(n,[]))
        return vals

    def intersection(self,label):
        parts=label.split("/")
        if len(parts)!=2:return [],set()
        names=[self.names(p) for p in parts]
        left,right=[set().union(*(self.by_name.get(n,set()) for n in ns))&self.road_nodes for ns in names]
        exact=left&right
        if exact:return [(n,0.,"exact_intersection") for n in sorted(exact)],set.union(*names)
        # Divided roads/roundabout approaches: require both named roads within 65 m.
        # Do not invent graph connections between merely nearby nodes.
        cand={}
        small,big=(left,right) if len(left)<len(right) else (right,left)
        for n in small:
            for d,m in self.near(self.nodes[n],MAX_NEAR):
                if m not in big:continue
                for node in (n,m):cand[node]=min(cand.get(node,math.inf),d)
        return [(n,25+d,"near_named_intersection") for n,d in sorted(cand.items(),key=lambda x:(x[1],x[0]))[:MAX_LAYER]],set.union(*names)

    def candidates(self,label):
        key=canon(label)
        if key in LANDMARK_INTERSECTIONS:
            c,names=self.intersection(LANDMARK_INTERSECTIONS[key])
            if c:return [(n,p+15,"landmark_named_intersection") for n,p,_ in c],names
        c,names=self.intersection(label)
        if c:return c,names
        if key in LANDMARKS:
            result={}
            for name,typ,id,p in self.landmarks:
                if any(term in name for term in LANDMARKS[key]):
                    for d,n in sorted(self.near(p,MAX_LANDMARK_SNAP))[:6]:
                        penalty=80+d
                        if n not in result or penalty<result[n][0]:result[n]=(penalty,"named_landmark_snap",f"{typ}/{id}")
            return [(n,p,k+":"+src) for n,(p,k,src) in sorted(result.items(),key=lambda x:(x[1][0],x[0]))[:MAX_LAYER]],names
        return [],names

    def turn_violations(self,path):
        violations=[]
        for a,b,c in zip(path,path[1:],path[2:]):
            w1=self.adj[a][b][1];w2=self.adj[b][c][1]
            for kind,to,id in self.turns.get((b,w1),[]):
                # Same-way no_u_turn means returning to previous node.
                violates=(kind=="no_u_turn" and w1==to and a==c) or (kind.startswith("no_") and kind!="no_u_turn" and w2==to) or (kind=="no_u_turn" and w1!=to and w2==to) or (kind.startswith("only_") and w2!=to)
                if violates:violations.append({"node":b,"relation":id,"restriction":kind})
        return violations

    @lru_cache(maxsize=8192)
    def paths(self,start,targets,preferred):
        # Bounded Dijkstra by road length; favor the street shared by adjacent
        # official intersections, while permitting legal one-way detours.
        targets=set(targets);preferred=set(preferred)
        q=[(0.,start)];ds={start:0.};prev={};found={}
        while q and targets:
            cost,n=heapq.heappop(q)
            if cost!=ds[n]:continue
            if cost>MAX_LEG:break
            if n in targets:
                path=[n]
                while path[-1]!=start:path.append(prev[path[-1]])
                path.reverse()
                length=sum(self.adj[a][b][0] for a,b in zip(path,path[1:]))
                found[n]=(cost,length,path);targets.remove(n)
            for m,(d,wid,names) in self.adj.get(n,{}).items():
                mult=1. if not preferred or names&preferred else 1.8 if names else 1.25
                c=cost+d*mult
                if c<=MAX_LEG and c<ds.get(m,math.inf):
                    ds[m]=c;prev[m]=n;heapq.heappush(q,(c,m))
        return found

def reconstruct(graph,rows):
    rid=rows[0]["route_id"]
    layers=[];missing=[]
    for row in rows:
        c,names=graph.candidates(row["waypoint"])
        # Cap layer, but keep all small exact-match sets; truncation is recorded.
        if c:
            layers.append((row,c[:MAX_LAYER],names,len(c)))
        else:missing.append({"sequence":int(row["sequence"]),"waypoint":row["waypoint"]})
    if len(layers)<3:return None,{"route_id":rid,"status":"blocked_insufficient_anchors","unresolved":missing}
    first=layers[0];last=layers[-1]
    # Same legal origin must resolve to same node. If endpoint missing, close
    # the partial chain at the first resolved point, label it incomplete.
    ends_same=canon(first[0]["waypoint"])==canon(last[0]["waypoint"])
    start_candidates=first[1]
    if ends_same:
        end_nodes={n for n,_,_ in last[1]}
        start_candidates=[c for c in start_candidates if c[0] in end_nodes]
    best=None
    for start,pen,kind in start_candidates:
        states={start:(pen,[start],[(first[0],start,kind,0.,len(first[1]))])}
        old=first
        for layer in layers[1:]:
            row,candidates,names,nc=layer
            if layer is last and ends_same:candidates=[c for c in candidates if c[0]==start]
            if not candidates:states={};break
            target=tuple(sorted(n for n,_,_ in candidates))
            common=tuple(sorted(old[2]&names))
            new={}
            for n,(cost,path,selected) in states.items():
                options=graph.paths(n,target,common)
                for m,p,k in candidates:
                    if m not in options:continue
                    weighted,length,leg=options[m]
                    # Guard against collapsing two genuinely different points.
                    if n==m and canon(old[0]["waypoint"])!=canon(row["waypoint"]):extra=100
                    else:extra=0
                    if len(path)>1 and len(leg)>1 and path[-2]==leg[1]:extra+=250
                    total=cost+weighted+p+extra
                    if m not in new or total<new[m][0]:
                        new[m]=(total,path+leg[1:],selected+[(row,m,k,length,nc)])
            states=new;old=layer
            if not states:break
        for n,(cost,path,selected) in states.items():
            close_len=0
            if n!=start:
                opts=graph.paths(n,(start,),())
                if start not in opts:continue
                weighted,close_len,leg=opts[start]
                cost+=weighted;path=path+leg[1:]
            if best is None or cost<best[0]:best=(cost,path,selected,close_len)
    if best is None:return None,{"route_id":rid,"status":"blocked_disconnected_anchors","unresolved":missing,"resolved_layers":len(layers)}
    cost,path,selected,closing=best
    assert path[0]==path[-1] and all(b in graph.adj[a] for a,b in zip(path,path[1:]))
    coords=[graph.nodes[n] for n in path]
    length=sum(graph.adj[a][b][0] for a,b in zip(path,path[1:]))
    anchors=[]
    for row,node,kind,leg,nc in selected:
        anchors.append({"sequence":int(row["sequence"]),"waypoint":row["waypoint"],"osm_node_id":node,"lon":graph.nodes[node][0],"lat":graph.nodes[node][1],"match":kind,"candidate_count":nc,"leg_m":round(leg,1)})
    turns=graph.turn_violations(path+path[1:2])
    reversals=sum(a==c for a,b,c in zip(path,path[1:],path[2:]))
    edge_counts=Counter(zip(path,path[1:]));repeated=sum((c-1)*graph.adj[a][b][0] for (a,b),c in edge_counts.items() if c>1)
    endpoints_resolved=int(first[0]["sequence"])==1 and int(last[0]["sequence"])==int(rows[-1]["sequence"])
    gaps=[{"from_sequence":a["sequence"],"to_sequence":b["sequence"],"leg_m":b["leg_m"]} for a,b in zip(anchors,anchors[1:]) if b["sequence"]-a["sequence"]>1]
    status="candidate_all_waypoints_linked" if not missing and endpoints_resolved and closing<1 else "candidate_partial_waypoint_coverage"
    report={"route_id":rid,"status":status,"approved":False,"length_m":round(length,1),"point_count":len(path),"waypoints":len(rows),"resolved":len(anchors),"unresolved":missing,"endpoints_resolved":endpoints_resolved,"inferred_closing_m":round(closing,1),"skipped_waypoint_connectors":gaps,"long_legs":[a for a in anchors if a["leg_m"]>1500],"immediate_reversals":reversals,"repeated_directed_edge_m":round(repeated,1),"known_turn_violations":turns,"unsupported_restrictions_in_export":graph.unsupported_restrictions,"anchors":anchors,"source":"Decreto 090/2019 ordered candidate waypoints / OpenStreetMap contributors","conditional_access_checked":False}
    return {"type":"Feature","properties":{k:v for k,v in report.items() if k not in ("anchors","unresolved","skipped_waypoint_connectors","long_legs","known_turn_violations")},"geometry":{"type":"LineString","coordinates":coords}},report

def main():
    p=argparse.ArgumentParser();p.add_argument("--osm",type=Path,required=True);p.add_argument("--out",type=Path,default=Path("build"));a=p.parse_args()
    graph=Graph(json.loads(a.osm.read_text(encoding="utf-8")))
    with (ROOT/"data/official-waypoint-candidates.csv").open(encoding="utf-8",newline="") as f:rows=list(csv.DictReader(f))
    by=defaultdict(list)
    for r in rows:by[r["route_id"]].append(r)
    a.out.mkdir(parents=True,exist_ok=True)
    features=[];reports=[]
    for rid in sorted(by,key=int):
        feature,report=reconstruct(graph,by[rid])
        reports.append(report)
        if feature:features.append(feature)
        print(json.dumps({k:v for k,v in report.items() if k not in ("anchors","unresolved","long_legs","skipped_waypoint_connectors","known_turn_violations")},ensure_ascii=False),flush=True)
    (a.out/"all-route-candidates.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features},ensure_ascii=False)+"\n",encoding="utf-8")
    (a.out/"circuit-reconstruction-report.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    fields=["route_id","status","waypoints","resolved","length_m","point_count","endpoints_resolved","inferred_closing_m","immediate_reversals","repeated_directed_edge_m","unresolved_count","turn_violation_count","approved"]
    with (a.out/"circuit-summary.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader()
        for r in reports:w.writerow({**r,"unresolved_count":len(r.get("unresolved",[])),"turn_violation_count":len(r.get("known_turn_violations",[])),"approved":False})
    print(json.dumps({"route_count":len(reports),"candidate_circuits":len(features),"approved":0,"road_nodes":len(graph.road_nodes),"named_landmarks":len(graph.landmarks),"turn_restriction_relations":len(graph.restrictions)}))
if __name__=="__main__":main()
