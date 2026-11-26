"""Apply pinned route-specific node-chain patches, without changing reconstruction.
Requires the exact prior artifact and supplied independent OSM snapshot.
Produces draft geometry only, never approvals or boarding stops.
"""
import argparse, hashlib, json, zipfile
from pathlib import Path
from collections import Counter
from osm_route9 import allowed, orientations, distance
from resolve_waypoints import objects

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifact",type=Path,required=True)
    p.add_argument("--osm",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    reg=json.loads((ROOT/"data/route-specific-geometry-patches.json").read_text())
    raw=args.osm.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=reg["osm_snapshot_sha256"]:
        raise SystemExit("OSM snapshot hash mismatch; explicit review required")
    obj=objects(json.loads(raw))
    nodes={i:(e["lon"],e["lat"]) for (t,i),e in obj.items() if t=="node" and "lat" in e}
    coord_to_nodes={}
    for i,c in nodes.items():coord_to_nodes.setdefault(c,[]).append(i)
    edges=set()
    for (t,i),w in obj.items():
        if t=="way" and allowed(w.get("tags",{})) and all(n in nodes for n in w.get("nodes",[])):
            for seq in orientations(w):
                edges.update(zip(seq,seq[1:]))
    with zipfile.ZipFile(args.artifact) as z:
        features=json.loads(z.read("all-route-candidates.geojson"))
    by={f["properties"]["route_id"]:f for f in features["features"]}
    if set(by)!={str(i) for i in range(1,15)}:raise ValueError("Unexpected baseline coverage")
    report=[]
    for rid,review in reg["routes"].items():
        feature=by[rid];geom=feature["geometry"]["coordinates"]
        candidates=[coord_to_nodes.get(tuple(c),[]) for c in geom]
        # Baseline coordinates must identify a directed edge chain. Resolve duplicate
        # coordinates by connectivity rather than assuming a single node ID.
        states={n:[n] for n in candidates[0]}
        for cs in candidates[1:]:
            nxt={}
            for m in cs:
                for n,path in states.items():
                    if (n,m) in edges:nxt[m]=path+[m];break
            states=nxt
            if not states:raise ValueError("Baseline coordinate chain not present for "+rid)
        old=next((path for path in states.values() if path[0]==path[-1]),None)
        if old is None:raise ValueError("Baseline not closed for "+rid)
        chain=old[:]
        for patch in sorted(review["patches"],key=lambda x:x["start_index"],reverse=True):
            s,e=patch["start_index"],patch["end_index"];new=patch["nodes"]
            if not 0<=s<e<len(old) or new[0]!=old[s] or new[-1]!=old[e]:raise ValueError("Patch seam mismatch for "+rid)
            if not all((a,b) in edges for a,b in zip(new,new[1:])):raise ValueError("Patch uses forbidden/missing directed edge for "+rid)
            chain[s:e+1]=new
        if chain[0]!=chain[-1] or not all((a,b) in edges for a,b in zip(chain,chain[1:])):raise ValueError("Invalid patched circuit")
        if any(a["node"] not in chain for a in review.get("anchor_updates",[])):raise ValueError("Review anchor missing")
        def measures(path):
            d=lambda a,b:distance(nodes[a],nodes[b])
            return {"length_m":round(sum(d(a,b) for a,b in zip(path,path[1:])),1),
                    "vertices":len(path),"immediate_reversals":sum(a==c for a,b,c in zip(path,path[1:],path[2:])),
                    "repeat_m":round(sum((v-1)*d(a,b) for (a,b),v in Counter(zip(path,path[1:])).items()),1)}
        feature["geometry"]["coordinates"]=[nodes[n] for n in chain]
        feature["properties"].update({"approved":False,"status":review["status"],"length_m":measures(chain)["length_m"],"point_count":len(chain),"immediate_reversals":measures(chain)["immediate_reversals"],"repeated_directed_edge_m":measures(chain)["repeat_m"],"reviewed_from_run":reg["baseline_run"],"remaining":review["remaining"],"anchor_updates":review.get("anchor_updates",[]),"post_patch_turn_restrictions_verified":False})
        report.append({"route_id":rid,"before":measures(old),"after":measures(chain),"status":review["status"],"remaining":review["remaining"]})
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"route-specific-draft.geojson").write_text(json.dumps(features,ensure_ascii=False)+"\n")
    (args.out/"route-specific-review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
