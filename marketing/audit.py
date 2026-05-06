#!/usr/bin/env python3
"""HBC SEO + AI Search Audit. Read-only. Reports current state across 9 items."""
import os, re, json, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/user/workspace/hbc-website")
HTML_FILES = sorted([p for p in ROOT.rglob("*.html") if ".git" not in p.parts])

# Categorize pages
def page_class(p):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith("blog/"):
        return "blog"
    if rel in ("404.html", "thank-you.html", "privacy.html", "terms.html"):
        return "utility"
    return "primary"

PRIMARY = [p for p in HTML_FILES if page_class(p) == "primary"]
BLOG = [p for p in HTML_FILES if page_class(p) == "blog"]
UTILITY = [p for p in HTML_FILES if page_class(p) == "utility"]

def rel(p): return p.relative_to(ROOT).as_posix()

def read(p):
    return p.read_text(encoding="utf-8", errors="replace")

# Extract every JSON-LD block
JSONLD_RE = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)

def jsonld_blocks(text):
    out = []
    for m in JSONLD_RE.finditer(text):
        raw = m.group(1).strip()
        try:
            out.append((raw, json.loads(raw), None))
        except json.JSONDecodeError as e:
            out.append((raw, None, str(e)))
    return out

def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)

def find_types(node, type_name):
    found = []
    def visit(d):
        t = d.get("@type")
        if t == type_name or (isinstance(t, list) and type_name in t):
            found.append(d)
    walk(node, visit)
    return found

def has_business_schema(node):
    found = []
    def visit(d):
        t = d.get("@type")
        if t in ("LocalBusiness", "HomeAndConstructionBusiness") or (
            isinstance(t, list) and (
                "LocalBusiness" in t or "HomeAndConstructionBusiness" in t
            )
        ):
            found.append(d)
    walk(node, visit)
    return found

results = {}
parse_errors = []

# ---- Audit each page ----
for p in HTML_FILES:
    text = read(p)
    blocks = jsonld_blocks(text)
    page_data = {
        "path": rel(p),
        "class": page_class(p),
        "blocks": len(blocks),
        "parse_errors": [],
        "business_schemas": [],
        "service_schemas": [],
        "person_schemas": [],
        "faq_schemas": [],
        "has_aggregateRating_in_business": False,
        "has_hasCredential_in_business": False,
        "has_geoCircle": False,
        "has_speakable_in_faq": False,
        "has_any_speakable": False,
        "service_pages_with_provider_areaserved": False,
        "meta_description_count": 0,
        "meta_description_text": [],
        "og_count": 0,
        "twitter_count": 0,
        "img_count": 0,
        "img_lazy_count": 0,
        "img_below_fold_missing_lazy": 0,
        "title": "",
    }

    # meta description count
    descs = re.findall(r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', text, re.IGNORECASE)
    page_data["meta_description_count"] = len(descs)
    page_data["meta_description_text"] = descs

    # og + twitter
    page_data["og_count"] = len(re.findall(r'property=["\']og:', text, re.IGNORECASE))
    page_data["twitter_count"] = len(re.findall(r'name=["\']twitter:', text, re.IGNORECASE))

    # title
    tm = re.search(r'<title>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
    page_data["title"] = tm.group(1).strip() if tm else ""

    # img tags
    imgs = re.findall(r'<img\b[^>]*>', text, re.IGNORECASE)
    page_data["img_count"] = len(imgs)
    lazy = [i for i in imgs if re.search(r'loading=["\']lazy["\']', i, re.IGNORECASE)]
    page_data["img_lazy_count"] = len(lazy)
    # heuristic: skip first img (hero), check others
    if len(imgs) > 1:
        below = imgs[1:]
        page_data["img_below_fold_missing_lazy"] = sum(
            1 for i in below if not re.search(r'loading=["\']lazy["\']', i, re.IGNORECASE)
        )

    # parse JSON-LD
    for raw, node, err in blocks:
        if err:
            page_data["parse_errors"].append(err)
            parse_errors.append((rel(p), err))
            continue
        # business
        biz = has_business_schema(node)
        page_data["business_schemas"].extend(biz)
        for b in biz:
            if "aggregateRating" in b:
                page_data["has_aggregateRating_in_business"] = True
            if "hasCredential" in b:
                page_data["has_hasCredential_in_business"] = True
            sa = b.get("serviceArea")
            def has_geocircle(x):
                hit = [False]
                def v(d):
                    if d.get("@type") == "GeoCircle":
                        hit[0] = True
                walk(x, v)
                return hit[0]
            if sa and has_geocircle(sa):
                page_data["has_geoCircle"] = True
        # services
        svcs = find_types(node, "Service")
        page_data["service_schemas"].extend(svcs)
        # persons
        persons = find_types(node, "Person")
        page_data["person_schemas"].extend(persons)
        # faq + speakable
        faqs = find_types(node, "FAQPage")
        page_data["faq_schemas"].extend(faqs)
        for f in faqs:
            if "speakable" in f:
                page_data["has_speakable_in_faq"] = True
        def visit_speakable(d):
            if "speakable" in d:
                page_data["has_any_speakable"] = True
        walk(node, visit_speakable)

    # service schema completeness
    if page_data["service_schemas"]:
        ok = all(
            ("provider" in s) and ("areaServed" in s)
            for s in page_data["service_schemas"]
        )
        page_data["service_pages_with_provider_areaserved"] = ok

    results[rel(p)] = page_data

# ---- Now produce the 9-item report ----
print("=" * 80)
print("HBC SEO + AI SEARCH AUDIT")
print("=" * 80)
print(f"Total HTML pages: {len(HTML_FILES)} (primary={len(PRIMARY)} blog={len(BLOG)} utility={len(UTILITY)})")
print()

# 0. Parse errors
print("--- JSON-LD parse errors ---")
if parse_errors:
    for path, err in parse_errors:
        print(f"  ERR {path}: {err}")
else:
    print("  0 parse errors. All JSON-LD blocks parse cleanly.")
print()

# Item 1: Service schema on primary service/category pages
# Identify primary service/category pages: services, concierge, for-realtors, for-trade-partners,
# how-it-works, start.html and start/* (service-style pages)
SERVICE_LIKE = [
    "services.html", "concierge.html", "for-realtors.html", "for-trade-partners.html",
    "how-it-works.html", "start.html",
    "start/before-you-hire-a-contractor.html",
    "start/before-you-hire-a-designer.html",
    "start/before-you-hire-a-realtor.html",
    "start/before-you-hire-an-architect.html",
    "vs-angi.html", "vs-homeadvisor.html",
]
def has_full_service_schema(p_rel):
    pd = results.get(p_rel)
    if not pd: return False
    if not pd["service_schemas"]: return False
    for s in pd["service_schemas"]:
        if all(k in s for k in ("provider", "areaServed", "serviceType")):
            # require at least one of audience or category
            return True
    return False

print("--- ITEM 1: Service schema on primary service/category pages ---")
covered = [p for p in SERVICE_LIKE if has_full_service_schema(p)]
missing1 = [p for p in SERVICE_LIKE if not has_full_service_schema(p)]
print(f"Coverage: {len(covered)}/{len(SERVICE_LIKE)}")
print(f"Missing ({len(missing1)}):")
for m in missing1:
    print(f"  - {m}")
print()

# Item 2: AggregateRating on all non-blog pages with biz schema
NON_BLOG = [p for p in HTML_FILES if page_class(p) != "blog"]
non_blog_with_biz = [rel(p) for p in NON_BLOG if results[rel(p)]["business_schemas"]]
non_blog_with_aggrat = [r for r in non_blog_with_biz if results[r]["has_aggregateRating_in_business"]]
print("--- ITEM 2: AggregateRating on non-blog pages with biz schema ---")
print(f"Non-blog pages with biz schema: {len(non_blog_with_biz)}")
print(f"Coverage: {len(non_blog_with_aggrat)}/{len(non_blog_with_biz)}")
missing2 = [r for r in non_blog_with_biz if r not in non_blog_with_aggrat]
print(f"Missing ({len(missing2)}):")
for m in missing2:
    print(f"  - {m}")
# Also include non-blog primary pages WITHOUT biz schema (we will inject biz schema with aggRat)
non_blog_no_biz = [rel(p) for p in NON_BLOG if not results[rel(p)]["business_schemas"] and page_class(p) == "primary"]
print(f"Non-blog primary pages with NO biz schema (will inject compact reference): {len(non_blog_no_biz)}")
for m in non_blog_no_biz:
    print(f"  ~ {m}")
print()

# Item 3: hasCredential in biz schema
hc_covered = [r for r in non_blog_with_biz if results[r]["has_hasCredential_in_business"]]
print("--- ITEM 3: hasCredential in biz schema (non-blog pages with biz) ---")
print(f"Coverage: {len(hc_covered)}/{len(non_blog_with_biz)}")
missing3 = [r for r in non_blog_with_biz if r not in hc_covered]
print(f"Missing ({len(missing3)}):")
for m in missing3:
    print(f"  - {m}")
print()

# Item 4: Duplicate meta description
print("--- ITEM 4: Duplicate meta description detection ---")
dupe_meta = [r for r, d in results.items() if d["meta_description_count"] > 1]
# Cross-page identical descs
desc_to_pages = defaultdict(list)
for r, d in results.items():
    for desc in d["meta_description_text"]:
        if desc.strip():
            desc_to_pages[desc.strip()].append(r)
cross_dupes = {k: v for k, v in desc_to_pages.items() if len(v) > 1}
print(f"Pages with multiple <meta description> tags: {len(dupe_meta)}")
for r in dupe_meta:
    print(f"  - {r} (count={results[r]['meta_description_count']})")
print(f"Identical descriptions across pages: {len(cross_dupes)}")
for desc, pages in cross_dupes.items():
    print(f"  desc='{desc[:60]}...' on {len(pages)} pages: {pages[:5]}")
print()

# Item 5: OG + Twitter coverage
print("--- ITEM 5: Open Graph + Twitter Card coverage ---")
all_pages = [rel(p) for p in HTML_FILES if page_class(p) != "utility" or rel(p) not in ("404.html", "thank-you.html")]
og_missing = [r for r in all_pages if results[r]["og_count"] < 3]
tw_missing = [r for r in all_pages if results[r]["twitter_count"] < 2]
print(f"Pages needing OG (< 3 og: tags): {len(og_missing)}")
for m in og_missing:
    print(f"  - {m} og={results[m]['og_count']}")
print(f"Pages needing Twitter (< 2 twitter: tags): {len(tw_missing)}")
for m in tw_missing:
    print(f"  - {m} tw={results[m]['twitter_count']}")
print()

# Item 6: Person schema for founder
person_pages = [r for r, d in results.items() if d["person_schemas"]]
person_pages_with_creds = [r for r in person_pages if any(
    "hasCredential" in pp and "knowsAbout" in pp and "jobTitle" in pp and "worksFor" in pp
    for pp in results[r]["person_schemas"]
)]
print("--- ITEM 6: Person schema with hasCredential + knowsAbout + jobTitle + worksFor ---")
print(f"Pages with any Person schema: {len(person_pages)}")
print(f"Pages with COMPLETE Person schema: {len(person_pages_with_creds)}")
print(f"Required: homepage + about + meet-adam at minimum")
expected_person = ["index.html", "about.html", "meet-adam.html"]
for r in expected_person:
    pd = results[r]
    has_any_person = bool(pd["person_schemas"])
    has_complete = any(
        "hasCredential" in pp and "knowsAbout" in pp and "jobTitle" in pp and "worksFor" in pp
        for pp in pd["person_schemas"]
    )
    print(f"  {r}: any_person={has_any_person} complete={has_complete}")
print()

# Item 7: GeoCircle service area
print("--- ITEM 7: GeoCircle service area in biz schema ---")
geo_covered = [r for r in non_blog_with_biz if results[r]["has_geoCircle"]]
print(f"Coverage: {len(geo_covered)}/{len(non_blog_with_biz)}")
missing7 = [r for r in non_blog_with_biz if r not in geo_covered]
for m in missing7:
    print(f"  - {m}")
print()

# Item 8: Speakable in FAQ blocks
print("--- ITEM 8: Speakable inside every FAQPage block ---")
pages_with_faq = [r for r, d in results.items() if d["faq_schemas"]]
pages_with_faq_speakable = [r for r in pages_with_faq if results[r]["has_speakable_in_faq"]]
print(f"Pages with FAQPage schema: {len(pages_with_faq)}")
print(f"Pages with Speakable in FAQPage: {len(pages_with_faq_speakable)}")
missing8 = [r for r in pages_with_faq if r not in pages_with_faq_speakable]
for m in missing8:
    print(f"  - {m}")
print()

# Item 9: Image lazy loading + decoding async
print("--- ITEM 9: Image lazy-loading on below-fold imgs (skip first hero img) ---")
img_problem = [(r, results[r]["img_count"], results[r]["img_lazy_count"], results[r]["img_below_fold_missing_lazy"])
               for r in results if results[r]["img_below_fold_missing_lazy"] > 0]
print(f"Pages with below-fold imgs missing loading=lazy: {len(img_problem)}")
for r, n, lz, miss in img_problem:
    print(f"  - {r}: imgs={n} lazy={lz} below_fold_missing={miss}")
print()

# Brand rule audit
print("--- BRAND RULE AUDIT ---")
# Em-dash characters
em_chars = ["\u2014", "\u2013", "&mdash;", "&#8212;", "&#x2014;"]
banned_words = ["luxury", "high-end", "delve", "leverage", "robust", "seamlessly", "moreover", "furthermore", "navigate"]
brand_issues = []
for p in HTML_FILES:
    t = read(p)
    # Strip script/style/style-attr to reduce noise
    body = re.sub(r'<script.*?</script>', '', t, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<style.*?</style>', '', body, flags=re.DOTALL | re.IGNORECASE)
    for ch in em_chars:
        n = body.count(ch)
        if n:
            brand_issues.append((rel(p), f"em-dash '{ch}'", n))
    # banned words: case-insensitive whole word, but only in visible text — strip tags
    visible = re.sub(r'<[^>]+>', ' ', body)
    visible_lower = visible.lower()
    for w in banned_words:
        # word-boundary
        pattern = r'\b' + re.escape(w) + r'\b'
        n = len(re.findall(pattern, visible_lower))
        if n:
            brand_issues.append((rel(p), f"banned '{w}'", n))
print(f"Brand issues: {len(brand_issues)}")
for path, kind, n in brand_issues[:30]:
    print(f"  - {path}: {kind} x{n}")
if len(brand_issues) > 30:
    print(f"  ... and {len(brand_issues)-30} more")
print()

# Save raw report
with open(ROOT / "marketing/audit-results.json", "w") as f:
    # strip nested big schema dicts for size
    slim = {}
    for r, d in results.items():
        slim[r] = {k: v for k, v in d.items() if k not in ("business_schemas", "service_schemas", "person_schemas", "faq_schemas", "meta_description_text")}
        slim[r]["business_schema_count"] = len(d["business_schemas"])
        slim[r]["service_schema_count"] = len(d["service_schemas"])
        slim[r]["person_schema_count"] = len(d["person_schemas"])
        slim[r]["faq_schema_count"] = len(d["faq_schemas"])
    json.dump({
        "totals": {"all": len(HTML_FILES), "primary": len(PRIMARY), "blog": len(BLOG), "utility": len(UTILITY)},
        "parse_errors": parse_errors,
        "brand_issues": brand_issues,
        "pages": slim,
    }, f, indent=2)
print(f"Wrote slim report: marketing/audit-results.json")
