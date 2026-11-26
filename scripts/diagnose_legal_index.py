"""Diagnose the public municipal SPA after a zero-record static HTML probe."""
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from collect_legal_index import UA, HOSTS, BINARY, extract

URLS = [
    "https://yopalcasanare.micolombiadigital.gov.co/tema/normatividad",
    "https://yopalcasanare.micolombiadigital.gov.co/transparencia",
]

GLOBAL_HOST = "www.micolombiadigital.gov.co"
GLOBAL_PATHS = {"/api/v1/globallogo", "/api/v1/featuredsitemenu/yopalcasanare", "/api/v1/banners/territorial/yopalcasanare", "/api/v1/settings/govcorequest", "/api/v1/settings/content/settingcontentglobal"}

def public_path(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

def summarize_json(value, depth=0):
    """Keep schema, pagination counts and public document metadata only."""
    if depth > 5:
        return type(value).__name__
    if isinstance(value, list):
        return {"type": "array", "count": len(value), "sample": [summarize_json(x, depth + 1) for x in value[:3]]}
    if isinstance(value, dict):
        out = {"type": "object", "keys": sorted(value)}
        public = {"title", "name", "slug", "alias", "description", "summary", "publishedat", "publicationdate", "createdat", "date", "contenttype", "type", "url", "total", "totalcount", "totalpages", "page", "pagesize", "hasnextpage", "count", "nextpage", "id"}
        for key, val in value.items():
            if key.lower() in public and isinstance(val, (str, int, float, bool, type(None))):
                if isinstance(val, str):
                    val = BeautifulSoup(val, "html.parser").get_text(" ", strip=True)[:350]
                out[key] = val
            elif key.lower() in {"items", "data", "results", "records", "contents", "content", "list", "pagination", "meta", "tags", "types", "contenttypes"} and isinstance(val, (dict, list)):
                out[key] = summarize_json(val, depth + 1)
            elif isinstance(val, list):
                out[key + "_count"] = len(val)
        return out
    return type(value).__name__

def main():
    out = Path("archive-index")
    out.mkdir(exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    diagnostics = []
    robots = {}
    def allowed(url):
        p = urlsplit(url)
        if (p.hostname not in HOSTS and not (p.hostname == GLOBAL_HOST and p.path in GLOBAL_PATHS)) or p.scheme != "https" or p.username or p.password:
            return False
        if p.hostname not in robots:
            rp = RobotFileParser()
            try:
                response = s.get("https://" + p.hostname + "/robots.txt", timeout=15, allow_redirects=False)
                if response.status_code == 404:
                    robots[p.hostname] = None
                elif response.status_code == 200:
                    rp.parse(response.text.splitlines())
                    robots[p.hostname] = rp
                else:
                    robots[p.hostname] = False
            except requests.RequestException:
                robots[p.hostname] = False
        rule = robots[p.hostname]
        return rule is None or (rule is not False and rule.can_fetch(UA, url))

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for url in URLS:
            result = {"url": url}
            diagnostics.append(result)
            if not allowed(url):
                result["error"] = "robots unavailable or disallowed"
                print(json.dumps(result), flush=True)
                continue
            try:
                r = s.get(url, timeout=25, allow_redirects=False)
                soup = BeautifulSoup(r.text, "html.parser")
                result["static"] = {
                    "status": r.status_code, "bytes": len(r.content),
                    "title": soup.title.get_text(strip=True) if soup.title else "",
                    "scripts": [public_path(urljoin(url, x["src"])) for x in soup.select("script[src]")][:40],
                    "body_text_length": len(soup.get_text(" ", strip=True)),
                    "link_count": len(soup.select("a[href]")),
                }
                if r.status_code != 200 or "html" not in r.headers.get("Content-Type", "").lower():
                    print(json.dumps(result), flush=True)
                    continue
                context = browser.new_context(user_agent=UA, accept_downloads=False, service_workers="block")
                page = context.new_page()
                observed, blocked, errors, list_responses = [], [], [], []
                def route_request(route):
                    req = route.request
                    p = urlsplit(req.url)
                    if p.scheme in ("data", "blob") or req.resource_type in ("image", "media", "font") or BINARY.search(p.path) or "/content/files/" in p.path or p.path.rstrip("/").endswith("/comments"):
                        route.abort()
                    elif req.method != "GET" or not allowed(req.url):
                        blocked.append({"url": public_path(req.url), "type": req.resource_type, "method": req.method})
                        route.abort()
                    else:
                        route.continue_()
                page.route("**/*", route_request)
                def record_response(response):
                    kind = response.request.resource_type
                    if kind not in ("document", "xhr", "fetch", "script"):
                        return
                    item = {"url": public_path(response.url), "status": response.status,
                            "type": kind, "content_type": response.headers.get("content-type", "")}
                    if kind in ("xhr", "fetch"):
                        item["query_keys"] = sorted({k for k, v in parse_qsl(urlsplit(response.url).query)})
                        item["pagination"] = {k: v for k, v in parse_qsl(urlsplit(response.url).query)
                                              if k.lower() in ("page", "limit", "size", "offset", "perpage", "per_page", "pagesize", "skip", "take") and v.isdigit()}
                    if kind in ("xhr", "fetch") and urlsplit(response.url).path.rstrip("/") == "/api/v1/contents" and response.status == 200:
                        params = parse_qsl(urlsplit(response.url).query, keep_blank_values=True)
                        permitted = {"page", "pagesize", "limit", "offset", "contenttype", "tags", "tag", "fromdate", "todate", "rangetype", "featured", "hasnextpage", "includetags", "includetypes", "isfull", "orderby", "search", "query", "category", "type"}
                        item["list_parameters"] = {k: v[:500] for k, v in params if k.lower() in permitted}
                        list_responses.append((response, item))
                    observed.append(item)
                page.on("response", record_response)
                page.on("pageerror", lambda error: errors.append(str(error)[:300]))
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(8000)
                    result["list_schema"] = []
                    for response, item in list_responses[:12]:
                        try:
                            if "json" not in item["content_type"].lower():
                                continue
                            payload = response.json()
                            result["list_schema"].append({
                                "endpoint": item["url"],
                                "parameters": item.get("list_parameters", {}),
                                "schema": summarize_json(payload),
                            })
                        except Exception as exc:
                            result["list_schema"].append({"endpoint": item["url"], "error": type(exc).__name__})
                    rendered = BeautifulSoup(page.content(), "html.parser")
                    result["rendered"] = {
                        "title": page.title(), "url": public_path(page.url),
                        "body_text_length": len(rendered.get_text(" ", strip=True)),
                        "link_count": len(rendered.select("a[href]")),
                        "headings": [x.get_text(" ", strip=True)[:200] for x in rendered.select("h1,h2,h3")][:30],
                        "listing_links": [{"title": a.get_text(" ", strip=True)[:200], "url": public_path(urljoin(page.url, a["href"]))} for a in rendered.select("a[href]") if any(t in (a["href"] + " " + a.get_text(" ", strip=True)).lower() for t in ("normativ", "resoluci", "decret", "transparencia", "acto administrativo", "publicaciones", "documentos", "notificaci", "avisos"))][:100],
                        "metadata": extract(rendered, page.url)[:30],
                    }
                except Exception as exc:
                    result["render_error"] = type(exc).__name__
                finally:
                    result["responses"] = [x for x in observed if x["type"] != "script"][:100] + [x for x in observed if x["type"] == "script"][:60]
                    result["blocked"] = blocked[:100]
                    result["page_errors"] = errors[:20]
                    context.close()
            except requests.RequestException as exc:
                result["error"] = type(exc).__name__
            print(json.dumps({k: v for k, v in result.items() if k not in ("responses", "blocked")}, ensure_ascii=False), flush=True)
            print(json.dumps({"responses": result.get("responses", [])[:60], "blocked": result.get("blocked", [])[:15]}, ensure_ascii=False), flush=True)
        browser.close()
    (out / "spa-diagnostics.json").write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
