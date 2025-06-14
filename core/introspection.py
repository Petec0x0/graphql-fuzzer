# /core/introspection.py (Updated)

import os
import re
import time
import subprocess
import requests
from bs4 import BeautifulSoup
import tldextract
from playwright.sync_api import sync_playwright

INTROSPECTION_QUERY = {
    "query": """
    query IntrospectionQuery {
        __schema {
            types {
                name
                kind
                fields {
                    name
                    args {
                        name
                        type {
                            name
                            kind
                        }
                    }
                    type {
                        name
                        kind
                    }
                }
            }
        }
    }
    """
}

def try_direct_introspection(endpoint, headers=None):
    try:
        r = requests.post(endpoint, json=INTROSPECTION_QUERY, headers=headers or {}, timeout=10)
        if r.status_code == 200 and "__schema" in r.text:
            return r.json()
        return None
    except Exception as e:
        print(f"[!] Introspection failed: {e}")
        return None

def generate_urls_file(frontend_domain, out_file):
    print(f"[*] Creating URL list from Wayback Machine for domain: {frontend_domain}")
    try:
        with open(out_file, "w") as f:
            subprocess.run(["waybackurls", frontend_domain], stdout=f, check=True)
        print(f"[+] Saved URLs to {out_file}")
    except Exception as e:
        print(f"[!] waybackurls failed: {e}")

def load_urls(url_file, max_urls=5):
    try:
        with open(url_file, "r") as f:
            #urls = [line.strip() for line in f if ".js" in line]
            urls = [line.strip() for line in f]
        return urls[:max_urls]
    except Exception as e:
        print(f"[!] Failed to read {url_file}: {e}")
        return []

def get_latest_archive_url(original_url):
    try:
        cdx_url = (
            f"http://web.archive.org/cdx/search/cdx?url={original_url}"
            f"&output=json&limit=1&filter=statuscode:200&collapse=digest&fl=timestamp,original"
        )
        resp = requests.get(cdx_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 1:
                timestamp, original = data[1]
                return f"https://web.archive.org/web/{timestamp}/{original}"
    except Exception as e:
        print(f"[!] Failed to get Wayback archive for {original_url}: {e}")
    return None

def extract_queries_from_text(text):
    pattern = r"\{[\s\S]{10,2000}?\}"
    matches = re.findall(pattern, text)
    return [m for m in matches if any(x in m for x in ["query", "mutation", "__typename", "__schema"])]

def extract_queries_from_wayback(url):
    archived_url = get_latest_archive_url(url)
    if not archived_url:
        return []
    try:
        resp = requests.get(archived_url, timeout=10)
        if resp.status_code == 200:
            return extract_queries_from_text(resp.text)
    except:
        pass
    return []

def extract_queries_playwright_wayback(url):
    archived_url = get_latest_archive_url(url)
    if not archived_url:
        return []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(archived_url, timeout=30000)
            content = page.content()
            browser.close()
            print("AAAAAAAAAAAAA", content)
            return extract_queries_from_text(content)
    except Exception as e:
        print(f"[!] Playwright failed for {archived_url}: {e}")
        return []

def recover_queries_from_urls_file(url_file, max_urls=5, use_playwright=False):
    urls = load_urls(url_file, max_urls)
    print(f"[*] Processing {len(urls)} archived URLs via Wayback")
    all_queries = []
    for url in urls:
        queries = (extract_queries_playwright_wayback(url)
                   if use_playwright else
                   extract_queries_from_wayback(url))
        if queries:
            all_queries.extend(queries)
        time.sleep(0.5)
    return list(set(all_queries))

def recover_schema(endpoint, frontend_domain=None, headers=None, url_file_path="urls.txt", max_urls=5, use_playwright=False):
    print(f"[*] Trying direct introspection on {endpoint}")
    schema = try_direct_introspection(endpoint, headers)
    if schema:
        print("[+] Full introspection succeeded.")
        return schema

    if not frontend_domain:
        frontend_domain = extract_root_domain(endpoint)

    if not os.path.exists(url_file_path):
        print(f"[*] {url_file_path} not found. Fetching Wayback data...")
        generate_urls_file(frontend_domain, url_file_path)
    else:
        print(f"[*] Found cached URL file: {url_file_path}")

    recovered_queries = recover_queries_from_urls_file(url_file_path, max_urls=max_urls, use_playwright=use_playwright)
    if recovered_queries:
        print(f"[+] Recovered {len(recovered_queries)} queries from cached Wayback data.")
        return {"recovered_queries": recovered_queries}

    print("[-] No schema or queries recovered.")
    return None

def extract_root_domain(url_or_host):
    ext = tldextract.extract(url_or_host)
    return f"{ext.domain}.{ext.suffix}"
