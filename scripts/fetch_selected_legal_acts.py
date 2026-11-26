"""Fetch only shortlisted public acts, preserving original PDFs in a private-to-run artifact."""
import csv
import hashlib
import html
import json
import re
import time
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from collect_legal_api import BASE, UA, plain

HOSTS = {"yopalcasanare.micolombiadigital.gov.co", "www.yopal-casanare.gov.co", "yopal-casanare.gov.co"}
ROOT = Path("selected-legal-acts")
MAX_PDF = 25 * 1024 * 1024
MAX_TOTAL = 150 * 1024 * 1024
MAX_ATTACHMENTS = 3

def safe_pdf(value):
    if not isinstance(value, str):
        return None
    value = html.unescape(value).strip()
    url = urljoin(BASE, value)
    p = urlsplit(url)
    if p.scheme != "https" or p.hostname not in HOSTS or p.username or p.password or p.port not in (None, 443):
        return None
    if not p.path.startswith("/sites/yopalcasanare/content/files/") or not unquote(p.path).lower().endswith(".pdf") or p.query or p.fragment:
        return None
    return url

def find_pdfs(value, depth=0):
    if depth > 12:
        return set()
    if isinstance(value, dict):
        return set().union(*(find_pdfs(v, depth + 1) for k, v in value.items() if k.lower() not in {"user", "author", "comments", "account"}))
    if isinstance(value, list):
        return set().union(*(find_pdfs(v, depth + 1) for v in value))
    if not isinstance(value, str):
        return set()
    found = set()
    direct = safe_pdf(value)
    if direct:
        found.add(direct)
    stripped = value.strip()
    if stripped.startswith(("[", "{")):
        try:
            found.update(find_pdfs(json.loads(stripped), depth + 1))
        except (ValueError, TypeError):
            pass
    if "<" in value:
        for a in BeautifulSoup(value, "html.parser").select("[href], [src]"):
            for attr in ("href", "src"):
                direct = safe_pdf(a.get(attr))
                if direct:
                    found.add(direct)
    for match in re.findall(r'(?:https://[^\s"<>\\]+|/sites/yopalcasanare/content/files/[^\s"<>\\]+?)\.pdf\b', html.unescape(value), re.I):
        direct = safe_pdf(match)
        if direct:
            found.add(direct)
    return found

def unwrap(payload, expected_id):
    if isinstance(payload, dict):
        if str(payload.get("contentID")) == expected_id:
            return payload
        for key in ("data", "result", "content", "results"):
            val = payload.get(key)
            if isinstance(val, dict):
                found = unwrap(val, expected_id)
                if found:
                    return found
            elif isinstance(val, list):
                for obj in val:
                    if isinstance(obj, dict):
                        found = unwrap(obj, expected_id)
                        if found:
                            return found
    return None

def main():
    ROOT.mkdir(exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    robots = {}
    manifest = []
    total_bytes = 0
    def allowed(url):
        p = urlsplit(url)
        if p.hostname not in HOSTS or p.scheme != "https":
            return False
        if p.hostname not in robots:
            r = s.get("https://" + p.hostname + "/robots.txt", timeout=20, allow_redirects=False)
            if r.status_code == 200:
                rp = RobotFileParser()
                rp.parse(r.text.splitlines())
                robots[p.hostname] = rp
            elif r.status_code == 404:
                robots[p.hostname] = None
            else:
                robots[p.hostname] = False
        rule = robots[p.hostname]
        return rule is None or (rule is not False and rule.can_fetch(UA, url))
    with Path("research/legal-act-shortlist.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if row["category"] == "baseline":
            continue
        item = {**row, "documents": []}
        manifest.append(item)
        slug = row["slug"]
        if not re.fullmatch(r"[\w.-]+", slug):
            item["error"] = "Invalid slug"
            continue
        endpoint = BASE + "/api/v1/contents/" + slug
        try:
            if not allowed(endpoint):
                raise RuntimeError("Robots policy disallows or unavailable")
            response = s.get(endpoint, headers={"Accept": "application/json"}, timeout=40, allow_redirects=False)
            item["detail_status"] = response.status_code
            if response.status_code != 200 or "json" not in response.headers.get("Content-Type", "").lower():
                raise RuntimeError("Detail API response not JSON HTTP 200")
            payload = response.json()
            obj = unwrap(payload, row["content_id"])
            if obj is None:
                item["response_keys"] = sorted(payload) if isinstance(payload, dict) else type(payload).__name__
                raise RuntimeError("Detail ID/schema mismatch; no attachments fetched")
            item["title"] = plain(obj.get("name"))
            item["description"] = plain(obj.get("description") or obj.get("metaDescription"))[:4000]
            item["starting_date"] = str(obj.get("startingDate") or "")
            item["attribute_schema"] = [sorted(a) for a in obj.get("attributes", []) if isinstance(a, dict)]
            urls = sorted(find_pdfs({k: obj.get(k) for k in ("attributes", "description", "metaDescription", "attachments", "files", "documents", "content")}))
            item["attachment_urls"] = urls
            if not urls:
                raise RuntimeError("No official PDF URL extracted; inspect attribute schema")
            if len(urls) > MAX_ATTACHMENTS:
                raise RuntimeError("More than three attachments; manually review")
            for i, url in enumerate(urls, 1):
                doc = {"url": url}
                item["documents"].append(doc)
                try:
                    if not allowed(url):
                        raise RuntimeError("Attachment robots disallowed")
                    with s.get(url, timeout=60, stream=True, allow_redirects=False) as pdf:
                        doc["http_status"] = pdf.status_code
                        if pdf.status_code != 200:
                            raise RuntimeError("Attachment HTTP " + str(pdf.status_code))
                        declared = int(pdf.headers.get("Content-Length", "0") or 0)
                        if declared > MAX_PDF or total_bytes + declared > MAX_TOTAL:
                            raise RuntimeError("Attachment size bound")
                        chunks, n = [], 0
                        for chunk in pdf.iter_content(65536):
                            n += len(chunk)
                            if n > MAX_PDF or total_bytes + n > MAX_TOTAL:
                                raise RuntimeError("Attachment size bound")
                            chunks.append(chunk)
                        data = b"".join(chunks)
                        if not data.startswith(b"%PDF-"):
                            raise RuntimeError("Response is not PDF")
                        target = ROOT / (row["content_id"] + "-" + str(i) + ".pdf")
                        target.write_bytes(data)
                        total_bytes += n
                        doc.update({"filename": target.name, "size": n, "sha256": hashlib.sha256(data).hexdigest()})
                except (requests.RequestException, RuntimeError, ValueError) as exc:
                    doc["error"] = str(exc)[:300]
                time.sleep(1.5)
        except (requests.RequestException, RuntimeError, ValueError, KeyError, TypeError) as exc:
            item["error"] = str(exc)[:300]
        finally:
            print(json.dumps({"instrument": row["instrument"], "detail_status": item.get("detail_status"), "pdfs": len([d for d in item["documents"] if "filename" in d]), "error": item.get("error"), "attachment_urls": item.get("attachment_urls", [])}, ensure_ascii=False), flush=True)
            (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            time.sleep(1.5)
    count = sum("filename" in d for x in manifest for d in x["documents"])
    print(json.dumps({"selected_acts": len(manifest), "pdfs": count, "bytes": total_bytes}))
    if not count:
        raise SystemExit("No PDFs retrieved; inspect manifest")

if __name__ == "__main__":
    main()
