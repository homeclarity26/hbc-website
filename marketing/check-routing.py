#!/usr/bin/env python3
"""
HBC routing audit. Compares URLs advertised in sitemap.xml and llms.txt
against rewrites in vercel.json. Fails (exit 1) if any advertised URL
has no matching rewrite or built-in static path.

Run before every commit that adds or removes pages.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://www.hometownbuildersclub.com"

def load_vercel_rewrites():
    cfg = json.loads((ROOT / "vercel.json").read_text())
    return {r["source"] for r in cfg.get("rewrites", [])}

def load_sitemap_urls():
    text = (ROOT / "sitemap.xml").read_text()
    locs = re.findall(r"<loc>([^<]+)</loc>", text)
    out = set()
    for u in locs:
        if u.startswith(DOMAIN):
            path = u[len(DOMAIN):].split("#")[0] or "/"
            out.add(path.rstrip("/") if path != "/" else "/")
    return out

def load_llms_urls():
    text = (ROOT / "llms.txt").read_text()
    out = set()
    for u in re.findall(r"https?://www\.hometownbuildersclub\.com[^\s)\"']*", text):
        path = u[len(DOMAIN):].split("#")[0] or "/"
        out.add(path.rstrip("/") if path != "/" else "/")
    return out

def native_static_path(url_path):
    """Vercel serves these without rewrites: / -> index.html, /foo.html -> foo.html."""
    if url_path == "/":
        return (ROOT / "index.html").exists()
    rel = url_path.lstrip("/")
    if rel.endswith(".html") and (ROOT / rel).exists():
        return True
    # /foo with foo.html present is NOT native — Vercel needs explicit rewrite
    return False

def has_html_target(url_path):
    """Is there a corresponding .html file we could rewrite to?"""
    rel = url_path.lstrip("/")
    return (ROOT / f"{rel}.html").exists() or (ROOT / rel / "index.html").exists()

def main():
    rewrites = load_vercel_rewrites()
    sitemap = load_sitemap_urls()
    llms = load_llms_urls()
    advertised = sitemap | llms

    rows = []
    gaps = []
    for url in sorted(advertised):
        sources = []
        if url in sitemap: sources.append("sitemap")
        if url in llms: sources.append("llms.txt")
        in_rewrites = url in rewrites
        is_native = native_static_path(url)
        ok = in_rewrites or is_native
        target_exists = has_html_target(url)
        rows.append((url, ",".join(sources), in_rewrites, is_native, target_exists, ok))
        if not ok:
            gaps.append((url, target_exists))

    # Print table
    print(f"{'URL':<60} {'Source':<16} {'Rewrite':<8} {'Native':<7} {'HTML?':<6} {'OK':<3}")
    print("-" * 100)
    for url, src, rw, nv, ht, ok in rows:
        print(f"{url:<60} {src:<16} {str(rw):<8} {str(nv):<7} {str(ht):<6} {'OK' if ok else 'GAP'}")
    print()

    if gaps:
        print(f"GAPS ({len(gaps)}):")
        for url, ht in gaps:
            if ht:
                print(f"  {url}  — .html file exists, add rewrite to vercel.json")
            else:
                print(f"  {url}  — no .html file. Either build the page or remove from sitemap/llms.txt")
        sys.exit(1)
    print(f"All {len(advertised)} advertised URLs resolve. 0 gaps.")
    sys.exit(0)

if __name__ == "__main__":
    main()
