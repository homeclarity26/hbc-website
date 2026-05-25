#!/usr/bin/env python3
"""
add-ai-search-schema.py — Inject Gemini-friendly schema sitewide.

For Google I/O 2026 / AI Mode optimization. Idempotent.

Adds, where missing:
  1. <script id="schema-ai-website"> on EVERY page:
       WebSite + PotentialAction:ReserveAction pointing to Calendly,
       plus a sitewide ContactPoint nested in an Organization ref.
  2. <script id="schema-ai-location"> on /locations/*.html:
       Service schema (Kitchen / Bath / First-Floor / Concierge) with
       offers.priceRange, areaServed = the specific locality.
  3. <script id="schema-ai-offercatalog"> on index.html:
       OfferCatalog with three line items (Concierge, Kitchen, Whole-Home).

Each block carries a stable `id=` attribute so re-runs replace rather
than duplicate.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUSINESS_ID = "https://www.hometownbuildersclub.com/#business"
SITE_URL = "https://www.hometownbuildersclub.com"
CALENDLY = "https://calendly.com/homeclarityreport/30min"
PHONE = "+13302031331"

# ---------- 1. WebSite + ReserveAction + ContactPoint (sitewide) ----------

WEBSITE_BLOCK = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "WebSite",
            "@id": f"{SITE_URL}/#website",
            "url": SITE_URL + "/",
            "name": "Hometown Builders Club",
            "publisher": {"@id": BUSINESS_ID},
            "potentialAction": [
                {
                    "@type": "SearchAction",
                    "target": {
                        "@type": "EntryPoint",
                        "urlTemplate": f"{SITE_URL}/?q={{search_term_string}}"
                    },
                    "query-input": "required name=search_term_string"
                },
                {
                    "@type": "ReserveAction",
                    "name": "Book a discovery call",
                    "target": {
                        "@type": "EntryPoint",
                        "urlTemplate": CALENDLY,
                        "actionPlatform": [
                            "https://schema.org/DesktopWebPlatform",
                            "https://schema.org/MobileWebPlatform"
                        ]
                    },
                    "result": {
                        "@type": "Reservation",
                        "name": "30-minute discovery call with Hometown Builders Club",
                        "provider": {"@id": BUSINESS_ID}
                    }
                }
            ]
        },
        {
            "@type": "Organization",
            "@id": f"{SITE_URL}/#org-contact",
            "name": "Hometown Builders Club",
            "url": SITE_URL + "/",
            "contactPoint": [
                {
                    "@type": "ContactPoint",
                    "contactType": "customer service",
                    "telephone": PHONE,
                    "availableLanguage": ["en"],
                    "areaServed": "US-OH",
                    "url": f"{SITE_URL}/contact"
                },
                {
                    "@type": "ContactPoint",
                    "contactType": "reservations",
                    "url": CALENDLY,
                    "availableLanguage": ["en"]
                }
            ]
        }
    ]
}

# ---------- 2. Location page Service schema ----------
# locality -> dict with display name, postal area, and (optional) lat/lng
LOCATIONS = {
    "hudson":         {"name": "Hudson",            "region": "OH"},
    "bath-township":  {"name": "Bath Township",     "region": "OH"},
    "fairlawn":       {"name": "Fairlawn",          "region": "OH"},
    "stow":           {"name": "Stow",              "region": "OH"},
    "cuyahoga-falls": {"name": "Cuyahoga Falls",    "region": "OH"},
    "montrose-ghent": {"name": "Montrose-Ghent",    "region": "OH"},
    "peninsula":      {"name": "Peninsula",         "region": "OH"},
    "tallmadge":      {"name": "Tallmadge",         "region": "OH"},
}

SERVICE_CATALOG = [
    {
        "key": "concierge",
        "name": "Concierge Whole-Home Renovation",
        "type": "Whole-home renovation",
        "priceRange": "$250000-$1500000",
        "low": 250000,
        "currency": "USD",
        "description": "Full whole-home renovation with single-point project management, design coordination, and one general contract."
    },
    {
        "key": "kitchen",
        "name": "Kitchen Transformation",
        "type": "Kitchen remodeling",
        "priceRange": "$85000-$200000",
        "low": 85000,
        "currency": "USD",
        "description": "Discerning kitchen remodels with custom cabinetry, stone, and integrated appliances. Most projects 8 to 12 weeks of in-home work."
    },
    {
        "key": "first-floor",
        "name": "First-Floor Reset",
        "type": "Whole-floor renovation",
        "priceRange": "$150000-$400000",
        "low": 150000,
        "currency": "USD",
        "description": "Open up, reconfigure, and refinish the entire first floor with one coordinated build. Ideal for 1980s and 1990s homes."
    },
    {
        "key": "bath",
        "name": "Primary Bath Renovation",
        "type": "Bathroom renovation",
        "priceRange": "$45000-$120000",
        "low": 45000,
        "currency": "USD",
        "description": "Spa-grade primary bath renovations with custom tile, stone, and proper waterproofing."
    }
]


def make_location_block(slug: str) -> dict:
    loc = LOCATIONS[slug]
    services = []
    for s in SERVICE_CATALOG:
        services.append({
            "@type": "Service",
            "@id": f"{SITE_URL}/locations/{slug}#service-{s['key']}",
            "name": f"{s['name']} in {loc['name']}, Ohio",
            "serviceType": s["type"],
            "description": s["description"],
            "provider": {"@id": BUSINESS_ID},
            "areaServed": {
                "@type": "City",
                "name": loc["name"],
                "containedInPlace": {
                    "@type": "AdministrativeArea",
                    "name": "Summit County, Ohio"
                }
            },
            "offers": {
                "@type": "Offer",
                "priceCurrency": s["currency"],
                "priceSpecification": {
                    "@type": "PriceSpecification",
                    "priceCurrency": s["currency"],
                    "minPrice": s["low"]
                },
                "priceRange": s["priceRange"],
                "availability": "https://schema.org/InStock",
                "url": CALENDLY
            }
        })
    return {"@context": "https://schema.org", "@graph": services}


# ---------- 3. Homepage OfferCatalog ----------

OFFER_CATALOG_BLOCK = {
    "@context": "https://schema.org",
    "@type": "OfferCatalog",
    "@id": f"{SITE_URL}/#offer-catalog",
    "name": "Hometown Builders Club service offerings",
    "provider": {"@id": BUSINESS_ID},
    "itemListElement": [
        {
            "@type": "Offer",
            "name": s["name"],
            "description": s["description"],
            "priceCurrency": s["currency"],
            "priceRange": s["priceRange"],
            "priceSpecification": {
                "@type": "PriceSpecification",
                "priceCurrency": s["currency"],
                "minPrice": s["low"]
            },
            "category": s["type"],
            "url": CALENDLY,
            "itemOffered": {
                "@type": "Service",
                "name": s["name"],
                "serviceType": s["type"],
                "provider": {"@id": BUSINESS_ID}
            }
        }
        for s in SERVICE_CATALOG
    ]
}


# ---------- Injector ----------

def inject(html: str, script_id: str, payload: dict) -> str:
    """Insert or replace a <script id=script_id type='application/ld+json'>
    block. Idempotent."""
    pretty = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    new_block = f'<script id="{script_id}" type="application/ld+json">{pretty}</script>'
    # Replace if present
    pat = re.compile(
        r'<script\s+id="' + re.escape(script_id) + r'"[^>]*>.*?</script>',
        re.DOTALL,
    )
    if pat.search(html):
        return pat.sub(new_block, html, count=1)
    # Insert before </head>
    if "</head>" in html:
        return html.replace("</head>", "  " + new_block + "\n</head>", 1)
    return html  # malformed; leave alone


def process(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith(("node_modules/", ".git/", ".vercel/")):
        return False
    if rel == "404.html" or rel == "thank-you.html":
        return False
    html = path.read_text(encoding="utf-8", errors="replace")
    new = html

    # 1. Sitewide WebSite + ContactPoint
    new = inject(new, "schema-ai-website", WEBSITE_BLOCK)

    # 2. Location-specific Service schema
    if rel.startswith("locations/") and rel.endswith(".html"):
        slug = Path(rel).stem
        if slug in LOCATIONS:
            new = inject(new, "schema-ai-location", make_location_block(slug))

    # 3. Homepage OfferCatalog
    if rel == "index.html":
        new = inject(new, "schema-ai-offercatalog", OFFER_CATALOG_BLOCK)

    if new != html:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> int:
    files = sorted(ROOT.rglob("*.html"))
    changed = 0
    for p in files:
        if process(p):
            changed += 1
            print(f"updated {p.relative_to(ROOT).as_posix()}")
    total = sum(1 for p in files
                if not p.relative_to(ROOT).as_posix().startswith(("node_modules/", ".git/", ".vercel/")))
    print(f"\n{changed} of {total} HTML files updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
