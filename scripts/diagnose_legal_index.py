"""Diagnose the public municipal SPA after a zero-record static HTML probe."""
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from collect_legal_index import UA, HOSTS, BINARY, extract

URLS = [
    "https://yopalcasanare.micolombiadigital.gov.co/normatividad",
    "https://www.yopal-casanare.gov.co/normatividad",
    "https://www.yopal-casanare.gov.co/normatividad/decreto-no-116-de-24--de-agosto-de-2026",
]

def public_path(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

def main():
    out = Path("archive-index")
    out.mkdir(exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    diagnostics = []
    robots = {}
    def allowed(url):
        p = urlsplit(url)
        if p.hostname not in HOSTS or p.scheme != "https" or p.username or p.password:
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
                observed, blocked, errors = [], [], []
                def route_request(route):
                    req = route.request
                    p = urlsplit(req.url)
                    if p.scheme in ("data", "blob") or req.resource_type in ("image", "media", "font") or BINARY.search(p.path) or "/content/files/" in p.path:
                        route.abort()
                    elif req.method != "GET" or not allowed(req.url):
                        blocked.append({"url": public_path(req.url), "type": req.resource_type, "method": req.method})
                        route.abort()
                    else:
                        route.continue_()
                page.route("**/*", route_request)
                page.on("response", lambda response: observed.append({
                    "url": public_path(response.url), "status": response.status,
                    "type": response.request.resource_type,
                    "content_type": response.headers.get("content-type", ""),
                }) if response.request.resource_type in ("document", "xhr", "fetch", "script") else None)
                page.on("pageerror", lambda error: errors.append(str(error)[:300]))
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(8000)
                    rendered = BeautifulSoup(page.content(), "html.parser")
                    result["rendered"] = {
                        "title": page.title(), "url": public_path(page.url),
                        "body_text_length": len(rendered.get_text(" ", strip=True)),
                        "link_count": len(rendered.select("a[href]")),
                        "headings": [x.get_text(" ", strip=True)[:200] for x in rendered.select("h1,h2,h3")][:30],
                        "listing_links": [{"title": a.get_text(" ", strip=True)[:200], "url": public_path(urljoin(page.url, a["href"]))} for a in rendered.select("a[href]") if "normatividad" in a["href"] or "resoluciones" in a["href"] or "decretos" in a["href"]][:60],
                        "metadata": extract(rendered, page.url)[:30],
                    }
                except Exception as exc:
                    result["render_error"] = type(exc).__name__
                finally:
                    result["responses"] = observed[:100]
                    result["blocked"] = blocked[:100]
                    result["page_errors"] = errors[:20]
                    context.close()
            except requests.RequestException as exc:
                result["error"] = type(exc).__name__
            print(json.dumps({k: v for k, v in result.items() if k not in ("responses", "blocked")}, ensure_ascii=False), flush=True)
            print(json.dumps({"responses": result.get("responses", [])[:30], "blocked": result.get("blocked", [])[:15]}, ensure_ascii=False), flush=True)
        browser.close()
    (out / "spa-diagnostics.json").write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
