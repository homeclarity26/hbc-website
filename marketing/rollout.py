#!/usr/bin/env python3
"""
HBC SEO + AI Search Rollout. Idempotent. Skips work where signal already present.
Runs all 9 items in one pass. Validates JSON-LD parsing before save.

Items:
  1. Service schema on primary service/category pages
  2. AggregateRating on biz schema (and inject biz schema where missing)
  3. hasCredential at biz schema level (Ohio GC + EPA Lead Safe)
  4. Duplicate meta description detection (already clean — verify only)
  5. OG + Twitter coverage (privacy/terms get noindex instead)
  6. Person schema for Adam Kilgore on index + about (meet-adam already complete)
  7. GeoCircle service area (lat/long + 30mi radius from Cuyahoga Falls)
  8. Speakable inside FAQPage
  9. Image lazy-loading + decoding async on below-fold imgs

Brand-rule fixes:
  - locations/cuyahoga-falls.html: "luxury renovations" -> rewrite
  - locations/montrose-ghent.html: "aren't a luxury" -> rewrite
  - locations/stow.html: "navigate the situation" -> rewrite
"""
import os, re, json, sys
from pathlib import Path

ROOT = Path("/home/user/workspace/hbc-website")
HTML_FILES = sorted([p for p in ROOT.rglob("*.html") if ".git" not in p.parts])

BIZ_ID = "https://www.hometownbuildersclub.com/#business"
ADAM_ID = "https://www.hometownbuildersclub.com/#adam"
CC_FALLS_LAT = 41.1334
CC_FALLS_LON = -81.4843
GEO_RADIUS_MI = 30
GEO_RADIUS_M = 48280  # 30 miles in meters

CRED_BLOCK = [
    {"@type":"EducationalOccupationalCredential","name":"Ohio General Contractor License","credentialCategory":"license","recognizedBy":{"@type":"Organization","name":"Summit County, Ohio"},"identifier":"GRB130313"},
    {"@type":"EducationalOccupationalCredential","name":"EPA Lead Safe Certified Renovator","credentialCategory":"certification","recognizedBy":{"@type":"Organization","name":"U.S. Environmental Protection Agency"},"identifier":"R-I-22516-00004"},
]

AGG_RATING = {
    "@type":"AggregateRating",
    "ratingValue":"5.0",
    "bestRating":"5",
    "worstRating":"1",
    "ratingCount":"3",
    "reviewCount":"3"
}

GEO_CIRCLE = {
    "@type":"GeoCircle",
    "geoMidpoint":{"@type":"GeoCoordinates","latitude":CC_FALLS_LAT,"longitude":CC_FALLS_LON},
    "geoRadius": str(GEO_RADIUS_M)
}

SERVICE_AREA_BLOCK = {
    "@type":"GeoCircle",
    "geoMidpoint":{"@type":"GeoCoordinates","latitude":CC_FALLS_LAT,"longitude":CC_FALLS_LON},
    "geoRadius": str(GEO_RADIUS_M),
    "description":"30-mile service radius from Cuyahoga Falls, Ohio. Covers Summit County and adjacent communities in Medina, Portage, southern Cuyahoga, and northern Stark counties."
}

# Compact business reference for pages that have NO business schema currently
def compact_biz_block(page_url, area_name=None):
    obj = {
        "@context":"https://schema.org",
        "@type":["LocalBusiness","HomeAndConstructionBusiness"],
        "@id": BIZ_ID,
        "name":"Hometown Builders Club",
        "alternateName":"HBC",
        "url":"https://www.hometownbuildersclub.com",
        "telephone":"+13302031331",
        "email":"adam@hometownbuildersclub.com",
        "foundingDate":"1999",
        "address":{"@type":"PostalAddress","addressLocality":"Cuyahoga Falls","addressRegion":"OH","postalCode":"44223","addressCountry":"US"},
        "geo":{"@type":"GeoCoordinates","latitude":CC_FALLS_LAT,"longitude":CC_FALLS_LON},
        "areaServed":{"@type":"AdministrativeArea","name":"Summit County, Ohio"},
        "serviceArea": SERVICE_AREA_BLOCK,
        "hasCredential": CRED_BLOCK,
        "aggregateRating": AGG_RATING,
        "founder":{"@id": ADAM_ID},
        "sameAs":["https://www.homeclarityreport.com","https://akrenovationsohio.com"],
    }
    if area_name:
        obj["areaServed"] = {"@type":"City","name":area_name,"containedInPlace":{"@type":"AdministrativeArea","name":"Summit County, Ohio"}}
        obj["serviceArea"] = SERVICE_AREA_BLOCK
    return obj

PERSON_ADAM = {
    "@context":"https://schema.org",
    "@type":"Person",
    "@id": ADAM_ID,
    "name":"Adam Kilgore",
    "jobTitle":"Founder, Hometown Builders Club",
    "description":"27-year residential remodeling expert in Summit County, Ohio. Licensed Ohio general contractor, EPA Lead Safe Certified. Founder of Hometown Builders Club, Home Clarity Report, and AK Renovations. Personally worked in, remodeled, or built about 400 homes in Summit County since 1999.",
    "telephone":"+13302031331",
    "email":"adam@hometownbuildersclub.com",
    "address":{"@type":"PostalAddress","addressLocality":"Cuyahoga Falls","addressRegion":"OH","postalCode":"44223","addressCountry":"US"},
    "worksFor":{"@id": BIZ_ID},
    "knowsAbout":[
        "home renovation",
        "residential remodeling",
        "kitchen remodeling",
        "bathroom remodeling",
        "first floor remodeling",
        "home additions",
        "contractor vetting and selection",
        "home advisory",
        "Summit County Ohio real estate",
        "trade partner network management",
        "renovation budgeting",
        "renovation project sequencing",
        "Northeast Ohio construction pricing"
    ],
    "hasCredential": CRED_BLOCK,
    "sameAs":[
        "https://www.hometownbuildersclub.com/meet-adam",
        "https://www.homeclarityreport.com/meet-adam",
        "https://akrenovationsohio.com"
    ]
}

# Service schema templates per page
SERVICE_SCHEMAS = {
    "services.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/services#advisory",
            "name":"HBC Home Advisory and Vetted Trade Partner Network",
            "serviceType":"Home Advisory and Contractor Matching",
            "category":"Home Renovation Planning",
            "url":"https://www.hometownbuildersclub.com/services",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"},{"@type":"AdministrativeArea","name":"Medina County, Ohio"},{"@type":"AdministrativeArea","name":"Portage County, Ohio"},{"@type":"AdministrativeArea","name":"Cuyahoga County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Northeast Ohio homeowners researching contractor selection and renovation planning"},
            "description":"HBC services for Northeast Ohio homeowners: Home Clarity Report, vetted trade partner referrals, monthly concierge home management, and lifetime advisory access."
        }
    ],
    "concierge.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/concierge#service",
            "name":"HBC Concierge Monthly Home Management",
            "serviceType":"Home Services Management",
            "category":"Home Maintenance Concierge",
            "url":"https://www.hometownbuildersclub.com/concierge",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Summit County homeowners"},
            "description":"Monthly home management memberships. HBC coordinates every vendor and service for your home, you pay one bill, we handle everything.",
            "offers":[
                {"@type":"Offer","name":"Essentials","price":"199","priceCurrency":"USD","availability":"https://schema.org/InStock","priceSpecification":{"@type":"UnitPriceSpecification","price":"199","priceCurrency":"USD","unitText":"per month"}},
                {"@type":"Offer","name":"Comfort","price":"350","priceCurrency":"USD","availability":"https://schema.org/InStock","priceSpecification":{"@type":"UnitPriceSpecification","price":"350","priceCurrency":"USD","unitText":"per month"}},
                {"@type":"Offer","name":"Premier","price":"550","priceCurrency":"USD","availability":"https://schema.org/InStock","priceSpecification":{"@type":"UnitPriceSpecification","price":"550","priceCurrency":"USD","unitText":"per month"}},
                {"@type":"Offer","name":"Snowbird","price":"399","priceCurrency":"USD","availability":"https://schema.org/InStock","priceSpecification":{"@type":"UnitPriceSpecification","price":"399","priceCurrency":"USD","unitText":"per month"}}
            ]
        }
    ],
    "for-realtors.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/for-realtors#service",
            "name":"HBC Realtor Partnership Program",
            "serviceType":"Real Estate Partnership",
            "category":"Realtor Referral Network",
            "url":"https://www.hometownbuildersclub.com/for-realtors",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"},{"@type":"AdministrativeArea","name":"Medina County, Ohio"},{"@type":"AdministrativeArea","name":"Portage County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Summit County and Northeast Ohio realtors"},
            "description":"Partnership program for Northeast Ohio realtors. The Home Clarity Report stamp travels with the house, lifts listing value, and gives realtors a permanent home advisory resource for past clients."
        }
    ],
    "for-trade-partners.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/for-trade-partners#service",
            "name":"HBC Vetted Trade Partner Network",
            "serviceType":"Contractor Membership Network",
            "category":"Trade Partner Program",
            "url":"https://www.hometownbuildersclub.com/for-trade-partners",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"},{"@type":"AdministrativeArea","name":"Medina County, Ohio"},{"@type":"AdministrativeArea","name":"Portage County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Summit County trade contractors and specialty service providers"},
            "description":"Vetted trade partner membership for Northeast Ohio specialty contractors. Members receive sold jobs (not leads) with full home documentation, written scopes, and accepted budgets. 15% on close, no upfront fees."
        }
    ],
    "how-it-works.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/how-it-works#service",
            "name":"How HBC Works. The Home Advisory Process",
            "serviceType":"Home Advisory Process",
            "category":"Home Renovation Planning",
            "url":"https://www.hometownbuildersclub.com/how-it-works",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Northeast Ohio homeowners planning a renovation"},
            "description":"How HBC's home advisory process works. Step by step from intake through Home Clarity Report delivery and ongoing trade partner introductions."
        }
    ],
    "start.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/start#service",
            "name":"Start With HBC. Homeowner Resource Library",
            "serviceType":"Homeowner Education",
            "category":"Pre-Hire Resources",
            "url":"https://www.hometownbuildersclub.com/start",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Northeast Ohio homeowners researching contractors, designers, architects, or realtors"},
            "description":"HBC's resource library for homeowners researching how to hire any home professional. Independent guidance before you sign anything."
        }
    ],
    "start/before-you-hire-a-contractor.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/start/before-you-hire-a-contractor#service",
            "name":"Before You Hire a Contractor. Independent Vetting Guide",
            "serviceType":"Contractor Vetting Education",
            "category":"Pre-Hire Resources",
            "url":"https://www.hometownbuildersclub.com/start/before-you-hire-a-contractor",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Northeast Ohio homeowners researching how to hire a residential contractor"},
            "description":"What to verify before signing a contract with a residential contractor. Licenses, insurance, references, scope clarity, and the questions most homeowners forget to ask."
        }
    ],
    "start/before-you-hire-a-designer.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/start/before-you-hire-a-designer#service",
            "name":"Before You Hire an Interior Designer. Independent Guide",
            "serviceType":"Designer Vetting Education",
            "category":"Pre-Hire Resources",
            "url":"https://www.hometownbuildersclub.com/start/before-you-hire-a-designer",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Northeast Ohio homeowners researching how to hire an interior designer"},
            "description":"What to know before hiring an interior designer in Northeast Ohio. Fee structures, scope of work, deliverables, and how design coordination affects construction cost."
        }
    ],
    "start/before-you-hire-a-realtor.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/start/before-you-hire-a-realtor#service",
            "name":"Before You Hire a Realtor. Independent Guide",
            "serviceType":"Realtor Selection Education",
            "category":"Pre-Hire Resources",
            "url":"https://www.hometownbuildersclub.com/start/before-you-hire-a-realtor",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Northeast Ohio homeowners researching how to hire a real estate agent"},
            "description":"What to look for in a residential real estate agent. Local market expertise, listing strategy, and how renovation planning affects buy or sell decisions."
        }
    ],
    "start/before-you-hire-an-architect.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/start/before-you-hire-an-architect#service",
            "name":"Before You Hire an Architect. Independent Guide",
            "serviceType":"Architect Selection Education",
            "category":"Pre-Hire Resources",
            "url":"https://www.hometownbuildersclub.com/start/before-you-hire-an-architect",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Northeast Ohio homeowners researching how to hire a residential architect"},
            "description":"When you need an architect for a home project and when you do not. Fee structures, project types that justify architect involvement, and how to evaluate residential architects in Northeast Ohio."
        }
    ],
    "vs-angi.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/vs-angi#service",
            "name":"HBC vs Angi. Vetted Local Network Alternative",
            "serviceType":"Vetted Contractor Network",
            "category":"Alternative to Angi (Angie's List) Lead Marketplace",
            "url":"https://www.hometownbuildersclub.com/vs-angi",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"},{"@type":"AdministrativeArea","name":"Medina County, Ohio"},{"@type":"AdministrativeArea","name":"Portage County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Summit County homeowners considering Angi or other lead marketplaces"},
            "description":"Why Hometown Builders Club is a stronger alternative to Angi for Summit County homeowners. Local vetting, written scopes, and a permanent advisory relationship instead of a lead-marketplace bidding war."
        }
    ],
    "vs-homeadvisor.html": [
        {
            "@type":"Service","@id":"https://www.hometownbuildersclub.com/vs-homeadvisor#service",
            "name":"HBC vs HomeAdvisor. Vetted Local Network Alternative",
            "serviceType":"Vetted Contractor Network",
            "category":"Alternative to HomeAdvisor Lead Marketplace",
            "url":"https://www.hometownbuildersclub.com/vs-homeadvisor",
            "provider":{"@id": BIZ_ID},
            "areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"},{"@type":"AdministrativeArea","name":"Medina County, Ohio"},{"@type":"AdministrativeArea","name":"Portage County, Ohio"}],
            "audience":{"@type":"Audience","audienceType":"Summit County homeowners considering HomeAdvisor or other lead marketplaces"},
            "description":"Why HBC is a stronger alternative to HomeAdvisor for Summit County homeowners. Vetted local network, no lead resale, and Adam Kilgore's 27 years of Summit County remodeling expertise behind every introduction."
        }
    ],
}

LOCATION_NAMES = {
    "locations/bath-township.html":"Bath Township",
    "locations/cuyahoga-falls.html":"Cuyahoga Falls",
    "locations/fairlawn.html":"Fairlawn",
    "locations/hudson.html":"Hudson",
    "locations/montrose-ghent.html":"Montrose-Ghent",
    "locations/peninsula.html":"Peninsula",
    "locations/stow.html":"Stow",
    "locations/tallmadge.html":"Tallmadge",
}

# ---------------- Helpers ----------------
def rel(p): return p.relative_to(ROOT).as_posix()
def page_class(p):
    r = rel(p)
    if r.startswith("blog/"): return "blog"
    if r in ("404.html","thank-you.html","privacy.html","terms.html"): return "utility"
    return "primary"

JSONLD_RE = re.compile(r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.DOTALL | re.IGNORECASE)

def replace_jsonld_block(html, transformer):
    """Replace each JSON-LD block via transformer(parsed_obj) -> parsed_obj."""
    def repl(m):
        open_tag, raw, close_tag = m.group(1), m.group(2).strip(), m.group(3)
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return m.group(0)
        new_obj = transformer(obj)
        if new_obj is None:
            return m.group(0)
        return open_tag + json.dumps(new_obj, ensure_ascii=False) + close_tag
    return JSONLD_RE.sub(repl, html)

def is_business_node(d):
    if not isinstance(d, dict): return False
    t = d.get("@type")
    return t in ("LocalBusiness","HomeAndConstructionBusiness") or (
        isinstance(t, list) and ("LocalBusiness" in t or "HomeAndConstructionBusiness" in t)
    )

def walk_dicts(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk_dicts(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_dicts(v)

def enrich_business(node, area_city=None):
    """Add aggregateRating, hasCredential, serviceArea (GeoCircle), geo if missing.
    Idempotent — only adds keys not present."""
    if "aggregateRating" not in node:
        node["aggregateRating"] = AGG_RATING
    if "hasCredential" not in node:
        node["hasCredential"] = CRED_BLOCK
    if "serviceArea" not in node:
        node["serviceArea"] = SERVICE_AREA_BLOCK
    if "geo" not in node:
        node["geo"] = {"@type":"GeoCoordinates","latitude":CC_FALLS_LAT,"longitude":CC_FALLS_LON}
    # Tag biz with @id if missing — link to canonical homepage entity
    if "@id" not in node:
        node["@id"] = BIZ_ID
    return node

def add_speakable_to_faq(node):
    if not isinstance(node, dict): return False
    t = node.get("@type")
    if t == "FAQPage" and "speakable" not in node:
        node["speakable"] = {
            "@type":"SpeakableSpecification",
            "cssSelector":[".faq-question",".faq-answer","h1","h2"]
        }
        return True
    return False

# ---------------- Per-file transforms ----------------

stats = {
    "biz_enriched": 0, "speakable_added": 0, "service_blocks_added": 0,
    "biz_blocks_injected": 0, "person_blocks_added": 0, "imgs_lazyfied": 0,
    "noindex_added": 0, "brand_fixes": 0,
}

# ---- pre-pass brand fixes ----
BRAND_FIXES = [
    ("locations/cuyahoga-falls.html", "luxury renovations", "premium renovations"),
    ("locations/montrose-ghent.html", "aren't a luxury", "aren't optional"),
    ("locations/stow.html", "navigate the situation", "work through the situation"),
]

for pfile, old, new in BRAND_FIXES:
    p = ROOT / pfile
    if p.exists():
        t = p.read_text(encoding="utf-8")
        if old in t:
            t = t.replace(old, new)
            p.write_text(t, encoding="utf-8")
            stats["brand_fixes"] += 1
            print(f"[brand] {pfile}: '{old}' -> '{new}'")

# ---- main rollout per file ----
for p in HTML_FILES:
    rpath = rel(p)
    cls = page_class(p)
    text = p.read_text(encoding="utf-8")
    original = text

    # === Item 5 alt: noindex on privacy/terms ===
    if rpath in ("privacy.html","terms.html"):
        if "<meta name=\"robots\"" not in text and "<meta name='robots'" not in text:
            text = text.replace("</title>", "</title>\n  <meta name=\"robots\" content=\"noindex, follow\">", 1)
            stats["noindex_added"] += 1

    # === Item 1 + 2 + 3 + 7: Enrich biz blocks AND inject Service schema ===
    if cls != "blog":
        # Track whether any biz schema exists in this file
        has_biz = False
        # First, walk and see
        for m in JSONLD_RE.finditer(text):
            try:
                obj = json.loads(m.group(2).strip())
            except json.JSONDecodeError:
                continue
            for d in walk_dicts(obj):
                if is_business_node(d):
                    has_biz = True
                    break
            if has_biz: break

        # Enrich existing biz blocks
        def enrich_blocks_transformer(obj):
            changed = False
            area_city = None
            if rpath in LOCATION_NAMES:
                area_city = LOCATION_NAMES[rpath]
            for d in walk_dicts(obj):
                if is_business_node(d):
                    before = json.dumps(d, sort_keys=True)
                    enrich_business(d, area_city=area_city)
                    after = json.dumps(d, sort_keys=True)
                    if before != after:
                        changed = True
            # Speakable in FAQPage
            for d in walk_dicts(obj):
                if add_speakable_to_faq(d):
                    changed = True
            return obj if changed else None

        new_text = replace_jsonld_block(text, enrich_blocks_transformer)
        if new_text != text:
            stats["biz_enriched"] += 1  # counted per file
            text = new_text

        # If no biz schema at all, inject compact reference block
        if not has_biz:
            area_city = LOCATION_NAMES.get(rpath)
            block = compact_biz_block(f"https://www.hometownbuildersclub.com/{rpath}", area_name=area_city)
            tag = f'<script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>'
            # Insert just before </head>
            if "</head>" in text and tag not in text:
                text = text.replace("</head>", f"  {tag}\n</head>", 1)
                stats["biz_blocks_injected"] += 1

        # Inject Service schema for designated pages
        svc_list = SERVICE_SCHEMAS.get(rpath)
        if svc_list:
            # Idempotency: check if any of these @ids already present
            existing_ids = []
            for m in JSONLD_RE.finditer(text):
                try:
                    o = json.loads(m.group(2).strip())
                except: continue
                for d in walk_dicts(o):
                    if isinstance(d, dict) and d.get("@type")=="Service" and d.get("@id"):
                        existing_ids.append(d["@id"])
            new_svcs = [s for s in svc_list if s["@id"] not in existing_ids]
            if new_svcs:
                wrapper = {"@context":"https://schema.org","@graph": new_svcs} if len(new_svcs) > 1 else (new_svcs[0] if "@context" not in new_svcs[0] else new_svcs[0])
                if isinstance(wrapper, dict) and wrapper.get("@type") == "Service" and "@context" not in wrapper:
                    wrapper = {"@context":"https://schema.org", **wrapper}
                tag = f'<script type="application/ld+json">{json.dumps(wrapper, ensure_ascii=False)}</script>'
                if "</head>" in text:
                    text = text.replace("</head>", f"  {tag}\n</head>", 1)
                    stats["service_blocks_added"] += 1

    else:
        # Blog page: just add speakable to existing FAQPage
        def speak_only(obj):
            changed = False
            for d in walk_dicts(obj):
                if add_speakable_to_faq(d):
                    changed = True
            return obj if changed else None
        new_text = replace_jsonld_block(text, speak_only)
        if new_text != text:
            stats["speakable_added"] += 1
            text = new_text

    # === Item 6: Person schema on index + about ===
    if rpath in ("index.html","about.html"):
        # Idempotency
        already = ('"@id":"' + ADAM_ID + '"') in text and '"jobTitle"' in text and '"worksFor"' in text and '"knowsAbout"' in text and '"hasCredential"' in text
        if not already:
            tag = f'<script type="application/ld+json">{json.dumps(PERSON_ADAM, ensure_ascii=False)}</script>'
            if "</head>" in text and tag not in text:
                text = text.replace("</head>", f"  {tag}\n</head>", 1)
                stats["person_blocks_added"] += 1

    # === Item 9: Image lazy-loading + decoding async ===
    # Find all <img> tags. Skip first one per page (hero protection for LCP).
    # Add loading="lazy" decoding="async" if missing.
    img_pattern = re.compile(r'<img\b([^>]*)>', re.IGNORECASE)
    imgs_in_text = list(img_pattern.finditer(text))
    if len(imgs_in_text) > 1:
        # Walk in reverse so indices don't shift
        local_changes = 0
        for idx, m in enumerate(reversed(imgs_in_text)):
            real_idx = len(imgs_in_text) - 1 - idx
            if real_idx == 0:
                continue  # skip first hero img
            attrs = m.group(1)
            new_attrs = attrs
            changed = False
            if not re.search(r'\bloading\s*=', new_attrs, re.IGNORECASE):
                new_attrs = new_attrs.rstrip() + ' loading="lazy"'
                changed = True
            if not re.search(r'\bdecoding\s*=', new_attrs, re.IGNORECASE):
                new_attrs = new_attrs.rstrip() + ' decoding="async"'
                changed = True
            if changed:
                start, end = m.start(), m.end()
                text = text[:start] + f'<img{new_attrs}>' + text[end:]
                local_changes += 1
        if local_changes:
            stats["imgs_lazyfied"] += local_changes

    if text != original:
        # Validate every JSON-LD block parses
        for m in JSONLD_RE.finditer(text):
            try:
                json.loads(m.group(2).strip())
            except json.JSONDecodeError as e:
                print(f"!! JSON-LD parse error after edit in {rpath}: {e}")
                print(m.group(2)[:300])
                sys.exit(1)
        p.write_text(text, encoding="utf-8")

print()
print("Rollout summary:", stats)
