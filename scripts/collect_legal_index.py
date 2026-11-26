"""Bounded, metadata-only reconnaissance of the official Yopal normativity index."""
import argparse
import csv
import json
import re
import time
import unicodedata
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

HOSTS = {"yopalcasanare.micolombiadigital.gov.co", "www.yopal-casanare.gov.co", "yopal-casanare.gov.co"}
BASE = "https://yopalcasanare.micolombiadigital.gov.co"
UA = "ColombiaTransit-Yopal-Research/1.0 (+https://github.com/ColombiaTransit/gtfs-yopal)"
ACT = re.compile(r"\b(resoluci[oó]n(?:es)?|decretos?|acuerdos?|circulares?|edictos?|actos administrativos)\b", re.I)
DIRECT = re.compile(r"\b(090\s*(?:de\s*)?2019|mi8[\s-]*pr18|tuyo|coocatrans|c[oó]otr(?:ans)?allanero|llano\s+l[ií]neas|sugamuxi|pimur|paraderos?|frecuencias?|despachos?|capacidad transportadora|abandono de rutas?|desistimiento de servicios|declaratoria de vacancia)\b", re.I)
TOPIC = re.compile(r"\b(transporte|movilidad|tr[aá]nsito|rutas?|busetas?|depuraci[oó]n normativa|revocatoria|suspensi[oó]n|reestructuraci[oó]n|apelaci[oó]n)\b", re.I)
BINARY = re.compile(r"\.(pdf|docx?|xlsx?|zip|rar|jpg|png|jpeg|gif|mp4|csv|kmz|kml)(?:$|\?)", re.I)

def clean(s):
    return " ".join(s.split())

def fold(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))

def normalize(url):
    p = urlsplit(url)
    if p.scheme not in ("http", "https") or p.hostname not in HOSTS or p.username or p.password or p.port not in (None, 80, 443):
        return None
    if BINARY.search(p.path) or "/content/files/" in p.path:
        return None
    return urlunsplit(("https", p.hostname, p.path or "/", p.query, ""))

def listing(url):
    p = urlsplit(url)
    path = fold(p.path).rstrip("/")
    return path in ("/normatividad", "/resoluciones", "/decretos", "/actos-administrativos", "/avisos", "/notificaciones") or bool(re.fullmatch(r"/normatividad/(?:resoluciones|decretos|actos-administrativos)(?:-\d{4})?", path))

def score(text):
    if DIRECT.search(text):
        return "high"
    if TOPIC.search(text):
        return "review"
    return "other"

def extract(soup, page):
    entries = []
    for a in soup.select("a[href]"):
        href = urljoin(page, a["href"])
        parsed = urlsplit(href)
        if parsed.hostname not in HOSTS:
            continue
        title = clean(a.get_text(" ", strip=True) or a.get("title", ""))
        if not title or len(title) > 400 or not ACT.search(title):
            continue
        if len(title) < 10 or re.fullmatch(r"(normatividad|resoluciones|decretos|acuerdos|circulares)", fold(title)):
            continue
        container = a.find_parent(["article", "li", "tr"])
        if container is None:
            container = a.find_parent(class_=re.compile(r"(?:card|item|result|media|document)", re.I))
        # Avoid grabbing a whole list or unrelated neighboring records.
        desc = clean(container.get_text(" ", strip=True)) if container else title
        if len(desc) > 1000:
            desc = title
        date = ""
        if container:
            el = container.find("time")
            if el:
                date = clean(el.get("datetime") or el.get_text(" ", strip=True))
        years = sorted(set(re.findall(r"\b(?:19|20)\d{2}\b", title + " " + desc)))
        priority = score(title + " " + desc + " " + href)
        entries.append(dict(title=title, description=desc, date_display=date,
                            year_mentions=";".join(years), url=href,
                            priority=priority, index_url=page))
    return entries

def discover(soup, page):
    links = set()
    for a in soup.select("a[href]"):
        u = normalize(urljoin(page, a["href"]))
        if not u:
            continue
        t = fold(clean(a.get_text(" ", strip=True)))
        rel = a.get("rel") or []
        if isinstance(rel, str):
            rel = rel.split()
        if listing(u):
            links.add(u)
        elif listing(page) and urlsplit(u).path.rstrip("/") == urlsplit(page).path.rstrip("/"):
            if "next" in rel or t in {"siguiente", "next", ">", "»", "›"} or t.isdigit():
                links.add(u)
    return sorted(links)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max-pages", type=int, default=25)
    p.add_argument("--seed", action="append", default=[])
    p.add_argument("--out", default="archive-index")
    args = p.parse_args()
    if not 1 <= args.max_pages <= 250:
        p.error("max-pages must be 1–250")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    seeds = [BASE + "/normatividad", "https://www.yopal-casanare.gov.co/normatividad"] + args.seed
    if any(not normalize(u) or not listing(u) for u in seeds):
        p.error("only official listing URLs allowed")
    queue = deque(dict.fromkeys(normalize(u) for u in seeds))
    seen, rows, pages, robots = set(), {}, [], {}
    def allowed(url):
        host = urlsplit(url).hostname
        if host not in robots:
            # Respect published restrictions; stop on authorization or rate-limit failures.
            rp = RobotFileParser()
            try:
                rr = s.get("https://" + host + "/robots.txt", timeout=20, allow_redirects=False)
                if rr.status_code == 200:
                    rp.parse(rr.text.splitlines())
                    robots[host] = rp
                elif rr.status_code == 404:
                    robots[host] = None
                else:
                    robots[host] = False
            except requests.RequestException:
                robots[host] = False
        rule = robots[host]
        return rule is None or (rule is not False and rule.can_fetch(UA, url))
    while queue and len(seen) < args.max_pages:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        item = {"url": url, "status": None, "entries": 0, "discovered_listing_links": 0}
        pages.append(item)
        try:
            if not allowed(url):
                item["error"] = "robots policy unavailable or disallowed; not requested"
                continue
            r = s.get(url, timeout=30, allow_redirects=False)
            item["status"] = r.status_code
            if r.is_redirect:
                target = normalize(urljoin(url, r.headers.get("Location", "")))
                item["redirect"] = target
                if target and listing(target) and target not in seen:
                    queue.append(target)
                continue
            if r.status_code != 200 or "html" not in r.headers.get("Content-Type", "").lower():
                item["error"] = "non-HTML or non-success"
                continue
            soup = BeautifulSoup(r.content, "html.parser")
            item["page_title"] = clean(soup.title.get_text(" ", strip=True)) if soup.title else ""
            items = extract(soup, url)
            item["entries"] = len(items)
            for x in items:
                key = (x["url"], fold(x["title"]))
                if key not in rows or len(x["description"]) > len(rows[key]["description"]):
                    rows[key] = x
            next_links = discover(soup, url)
            item["discovered_listing_links"] = len(next_links)
            item["listing_links"] = next_links
            queue.extend(u for u in next_links if u not in seen and u not in queue)
        except requests.RequestException as exc:
            item["error"] = type(exc).__name__
        finally:
            print(json.dumps(item, ensure_ascii=False), flush=True)
            time.sleep(1.5)
    fields = ["title", "description", "date_display", "year_mentions", "url", "priority", "index_url"]
    records = sorted(rows.values(), key=lambda x: (x["priority"], x["title"], x["url"]))
    for name, records_to_write in [
        ("all-act-metadata.csv", records),
        ("transport-candidates.csv", [x for x in records if x["priority"] != "other"]),
    ]:
        with (out / name).open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(records_to_write)
    result = {"pages_attempted": len(seen), "records": len(records),
              "high_priority": sum(x["priority"] == "high" for x in records),
              "review_priority": sum(x["priority"] == "review" for x in records),
              "remaining_discovered_pages": len(set(queue) - seen),
              "coverage_verified": False, "pdf_downloads": 0,
              "pages": pages}
    (out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "pages"}))
    if not records:
        raise SystemExit("No act metadata extracted; inspect diagnostics, not evidence of no acts.")

if __name__ == "__main__":
    main()
