"""Collect public municipal legal metadata; never fetch document attachments."""
import argparse
import csv
import html
import json
import re
import time
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

BASE = "https://yopalcasanare.micolombiadigital.gov.co"
ENDPOINT = BASE + "/api/v1/contents"
UA = "ColombiaTransit-Yopal-Research/1.0 (+https://github.com/ColombiaTransit/gtfs-yopal)"
PARAMS = {"rangeType": "", "page": 0, "hasNextPage": "false", "isFull": "false",
          "pageSize": 6, "includeTypes": "true", "orderBy": "recent", "includeTags": "true", "tags": "19"}

def plain(value):
    if not isinstance(value, str):
        return ""
    return " ".join(BeautifulSoup(html.unescape(value), "html.parser").get_text(" ", strip=True).split())

def fold(value):
    return "".join(c for c in unicodedata.normalize("NFKD", value.lower()) if not unicodedata.combining(c))

STRONG = re.compile(r"\b(?:tuyo|pimur|coocatrans|c[oó]otr(?:ans)?allanero|llano\s+lineas|sugamuxi|mi8[\s-]*pr18|abandono de rutas?|declaratoria de vacancia|desistimiento de servicios|capacidad transportadora|frecuencias? de despacho|reestructuracion de rutas?|transporte publico colectivo|transporte colectivo|busetas?|paraderos?)\b|(?:decreto\s+(?:no\.?\s*)?0?90\b.{0,50}\b2019)", re.I)
REVIEW = re.compile(r"\b(?:transporte|movilidad|transito|rutas?|frecuencias?|despachos?|revocatoria|suspension|vacancia|desistimiento|depuracion normativa|derogatoria|sancionator\w*|apelacion|reestructuracion)\b", re.I)
GENERIC = re.compile(r"^(?:decreto|resolucion|acuerdo|circular|acto administrativo|auto|edicto|aviso)\b", re.I)
# Only public document metadata, not authors, accounts, comments or arbitrary objects.
ATTR_LABELS = {"name", "label", "title", "key", "attributeName", "displayName", "friendlyName", "description", "type", "attributeType", "fieldName"}
ATTR_VALUES = {"value", "text", "stringValue", "dateValue", "attributeValue", "content", "description", "url", "fileName", "name", "title", "displayName", "path"}
RELEVANT_LABEL = re.compile(r"descripcion|description|resumen|summary|abstract|expedicion|expedition|fecha|date|objeto|subject|asunto|titulo|title|documento|document|archivo|file|contenido|content|texto|text|norma|normative")

def extract_attrs(attributes):
    descriptions, dates, files, schema = [], [], [], []
    for attr in attributes if isinstance(attributes, list) else []:
        if not isinstance(attr, dict):
            continue
        schema.append(sorted(attr.keys()))
        labels = []
        for k in ATTR_LABELS:
            val = attr.get(k)
            if isinstance(val, str):
                labels.append(plain(val))
            elif isinstance(val, dict):
                labels.extend(plain(val.get(x)) for x in ("name", "label", "title", "friendlyName", "description", "type"))
        for key in ("attribute", "definition", "field", "contentAttribute", "attributeType"):
            obj = attr.get(key)
            if isinstance(obj, dict):
                labels.extend(plain(obj.get(x)) for x in ATTR_LABELS)
        label = fold(" ".join(labels))
        for key in ATTR_VALUES:
            val = attr.get(key)
            if not isinstance(val, str):
                continue
            raw = val.strip()
            if re.search(r"\.pdf(?:$|\?)", raw, re.I) and (raw.startswith("/") or raw.startswith(BASE + "/") or raw.startswith("https://www.yopal-casanare.gov.co/")):
                files.append(raw)
                continue
            value = plain(val)
            if not value or key in ATTR_LABELS and value in labels:
                continue
            if re.fullmatch(r"\d{4}[-/]\d{2}[-/]\d{2}(?:[T ].*)?", value) and (RELEVANT_LABEL.search(label) or "date" in key.lower()):
                dates.append(value)
            elif RELEVANT_LABEL.search(label) or key in {"text", "stringValue", "description", "content"}:
                descriptions.append(value[:4000])
            elif key in {"value", "attributeValue"} and len(value) >= 30 and re.search(r"\b(?:por medio|por la cual|por el cual|por los cuales|se establece|se autoriza|se modifica)\b", fold(value)):
                descriptions.append(value[:4000])
    return "; ".join(dict.fromkeys(descriptions)), "; ".join(dict.fromkeys(dates)), "; ".join(dict.fromkeys(files)), schema

def category_names(values):
    if not isinstance(values, list):
        return ""
    return "; ".join(dict.fromkeys(plain(x.get("name")) if isinstance(x, dict) else plain(x) for x in values)).strip("; ")

def record(item):
    if not isinstance(item, dict):
        raise ValueError("Non-object result")
    cid = item.get("contentID")
    if not isinstance(cid, (str, int)) or isinstance(cid, bool) or not str(cid).strip():
        raise ValueError("Missing contentID")
    name = plain(item.get("name"))
    friendly = item.get("friendlyName")
    slug = friendly.strip("/") if isinstance(friendly, str) else ""
    if not slug or not re.fullmatch(r"[\w.-]+", slug):
        slug = ""
    attr_desc, attr_dates, attr_files, attr_schema = extract_attrs(item.get("attributes"))
    description = " | ".join(dict.fromkeys(x for x in (plain(item.get("description")), plain(item.get("metaDescription")), attr_desc) if x))[:8000]
    labels = category_names(item.get("labels"))
    text = fold(" ".join((name, description, labels, slug)))
    if STRONG.search(text):
        priority = "high"
    elif REVIEW.search(text):
        priority = "review"
    elif not description or fold(description) == fold(name):
        priority = "missing_description"
    else:
        priority = "other"
    years = sorted(set(re.findall(r"\b(?:19|20)\d{2}\b", name + " " + attr_dates + " " + description)))
    return {"content_id": str(cid), "title": name, "slug": slug,
            "detail_url": BASE + "/normatividad/" + quote(slug) if slug else "",
            "content_type": plain(item.get("contentType")), "labels": labels,
            "tags": category_names(item.get("tags")),
            "published_date": str(item.get("publishedDateFrom") or ""),
            "modified_date": str(item.get("modifiedDate") or ""),
            "starting_date": str(item.get("startingDate") or ""),
            "attribute_dates": attr_dates, "year_mentions": ";".join(years),
            "description": description, "attachment_links": attr_files, "priority": priority}, attr_schema

FIELDS = ["content_id", "title", "slug", "detail_url", "content_type", "labels", "tags",
          "published_date", "modified_date", "starting_date", "attribute_dates", "year_mentions",
          "description", "attachment_links", "priority"]

def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def self_test():
    x, _ = record({"contentID": 1, "name": "RESOLUCIÓN 123 de 2024", "friendlyName": "resolucion-123",
                   "metaDescription": "Por medio de la cual se modifica el transporte público colectivo",
                   "attributes": [{"name": "Fecha de expedición", "value": "2024-01-01"}],
                   "tags": [{"name": "Normatividad"}]})
    assert x["priority"] == "high" and x["attribute_dates"] == "2024-01-01"
    assert record({"contentID": 2, "name": "Decreto 10 de 2020"})[0]["priority"] == "missing_description"
    assert record({"contentID": 3, "name": "Decreto 90 de 2019"})[0]["priority"] == "high"
    assert record({"contentID": 4, "name": "Decreto 123", "description": "Presupuesto municipal"})[0]["priority"] == "other"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--page-size", type=int, default=100)
    p.add_argument("--max-pages", type=int, default=1000)
    p.add_argument("--out", default="archive-index")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    self_test()
    if args.self_test:
        print("Metadata parser self-tests passed")
        return
    if not 1 <= args.page_size <= 100 or not 1 <= args.max_pages <= 1000:
        p.error("Bounds: page-size 1-100, max-pages 1-1000")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "application/json"})
    records, pages, attr_shapes = {}, [], Counter()
    total, last_total, page, size = None, None, 0, args.page_size
    complete, error = False, None
    counts = Counter()
    try:
        robot = s.get(BASE + "/robots.txt", timeout=20, allow_redirects=False)
        if robot.status_code == 200:
            rp = RobotFileParser()
            rp.parse(robot.text.splitlines())
            if not rp.can_fetch(UA, ENDPOINT):
                raise RuntimeError("Public API disallowed by robots.txt")
        elif robot.status_code != 404:
            raise RuntimeError("Robots policy unavailable: HTTP " + str(robot.status_code))
        while len(pages) < args.max_pages:
            params = dict(PARAMS, page=page, pageSize=size)
            r = s.get(ENDPOINT, params=params, timeout=45, allow_redirects=False)
            log = {"page": page, "requested_size": size, "http_status": r.status_code}
            pages.append(log)
            if r.status_code == 400 and page == 0 and size != 6:
                log["action"] = "retry_observed_page_size"
                size = 6
                time.sleep(1.5)
                continue
            if r.status_code != 200 or "json" not in r.headers.get("Content-Type", "").lower():
                raise RuntimeError("Unexpected API response: HTTP " + str(r.status_code))
            payload = r.json()
            meta, items = payload["meta"], payload["results"]
            n = meta["totalCount"]
            more = meta["hasNextPage"]
            if not isinstance(items, list) or type(n) is not int or type(more) is not bool:
                raise ValueError("Unexpected list schema")
            log.update({"total": n, "returned": len(items), "has_next": more, "reported_count": meta.get("count")})
            if page == 0 and not records and more and 0 < len(items) < size:
                log["action"] = "retry_server_effective_page_size"
                size = len(items)
                time.sleep(1.5)
                continue
            if total is None:
                total = n
            last_total = n
            if n != total:
                raise RuntimeError("Archive total changed during collection")
            if meta.get("count") != len(items):
                raise RuntimeError("API page count mismatch")
            if more and (not items or len(items) != size):
                raise RuntimeError("Incomplete non-terminal page")
            for item in items:
                row, schemas = record(item)
                if row["content_id"] in records:
                    counts["duplicates"] += 1
                records[row["content_id"]] = row
                for schema in schemas:
                    attr_shapes[",".join(schema)] += 1
                if "normatividad" not in fold(row["tags"]):
                    counts["unexpected_tag"] += 1
            log["unique_so_far"] = len(records)
            print(json.dumps(log), flush=True)
            if counts["duplicates"] or counts["unexpected_tag"]:
                raise RuntimeError("Duplicate IDs or unexpected category; inspect pagination")
            if not more:
                complete = len(records) == total
                if not complete:
                    raise RuntimeError("Terminal page does not reconcile with totalCount")
                break
            page += 1
            time.sleep(1.5)
        if not complete and error is None:
            error = "Page bound reached before full coverage"
    except (requests.RequestException, ValueError, KeyError, TypeError, RuntimeError) as exc:
        error = str(exc)[:500]
    finally:
        rows = list(records.values())
        counts_by_priority = Counter(x["priority"] for x in rows)
        write_csv(out / "all-act-metadata.csv", rows)
        write_csv(out / "transport-candidates.csv", [x for x in rows if x["priority"] in {"high", "review"}])
        write_csv(out / "missing-descriptions.csv", [x for x in rows if x["priority"] == "missing_description"])
        summary = {"endpoint": ENDPOINT, "category": "Normatividad", "tag": 19,
                   "reported_total": total, "last_reported_total": last_total,
                   "unique_records": len(rows), "coverage_verified_against_api": complete,
                   "duplicates": counts["duplicates"], "unexpected_tag": counts["unexpected_tag"],
                   "pages_requested": len(pages), "effective_page_size": size,
                   "priority_counts": dict(counts_by_priority),
                   "with_description": sum(bool(x["description"]) for x in rows),
                   "with_attribute_dates": sum(bool(x["attribute_dates"]) for x in rows),
                   "with_attachment_links": sum(bool(x["attachment_links"]) for x in rows),
                   "title_year_mentions": dict(Counter(y for x in rows for y in set(re.findall(r"\b(?:19|20)\d{2}\b", x["title"])))),
                   "attribute_schemas": dict(attr_shapes), "pdf_downloads": 0,
                   "error": error, "pages": pages}
        (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({k: v for k, v in summary.items() if k != "pages"}, ensure_ascii=False), flush=True)
    if not complete:
        raise SystemExit(error or "Collection incomplete")

if __name__ == "__main__":
    main()
