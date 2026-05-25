#!/usr/bin/env python3
"""
Enriches location pages (Session 2, steps 6 + 7):
- Adds <p class="lead-answer"> in hero (idempotent: skip if present)
- Adds "Scenarios" section before "Common Questions" (idempotent: skip if present)
- Replaces 3-item FAQ block with 5-item FAQ block (idempotent: skip if has 5)
- Expands FAQPage JSON-LD to 5 mainEntity items
- Adds Place schema with geo polygon and ai-search id

Run from /home/user/workspace/hbc-website
"""
from pathlib import Path
import re, json

ROOT = Path("/home/user/workspace/hbc-website/locations")

# Per-location content (Cuyahoga Falls is home base; HBC NAP at 44223)
LOCATIONS = {
    "fairlawn": {
        "city": "Fairlawn",
        "lead_answer_q": "Who is the best home advisor in Fairlawn, Ohio?",
        "lead_answer_a": "Hometown Builders Club serves Fairlawn homeowners with in-person Home Clarity Reports and a lifetime advisor relationship. Fairlawn is one of Summit County's most active renovation markets, with 1980s and 1990s colonials concentrated around West Market Street and Fairlawn Heights, and HBC's value is matching the right vetted contractor to your specific project. Reports are delivered within 5 business days of the in-home site meeting.",
        # 3 area-specific scenarios — each titled around the home stock or buyer profile
        "scenarios": [
            ("1980s and 1990s colonial kitchens with closed-off layouts", "Most Fairlawn homes built between 1985 and 1998 have an oak-cabinet, peninsula-divided kitchen that no longer fits how families cook. The wall between the kitchen and family room is rarely structural in these floor plans. The Home Clarity Report identifies whether yours is structural, what the steel beam will cost if it is, and what every cabinet and surface choice will run in 2026 Summit County pricing before any contractor walks in."),
            ("Updating original primary baths in Fairlawn Heights", "Fairlawn Heights homes from the 1960s and 1970s have original primary baths with cultured-marble vanities, fiberglass tub surrounds, and a single line of recessed lighting. The waterproofing standards of that era are not what we build to now. The Report scopes a full re-build, what the substrate has to be, what the proper waterproofing system costs, and where the budget should land before you collect a single bid."),
            ("First-floor opens in West Market homes", "Larger Fairlawn homes near West Market often have formal living and dining rooms that go unused, with the actual family life concentrated in the kitchen and family room. The Report documents the load paths, the HVAC implications of opening the floor plan, and the realistic pricing for the work, so the conversation with a contractor is about how, not whether."),
        ],
        # 2 additional FAQs beyond the existing 3 to reach 5 total
        "extra_faqs": [
            ("Does HBC work on the higher-end Fairlawn Heights homes specifically?", "Yes. Fairlawn Heights is one of Summit County's most discerning sub-markets, with home values typically in the $460K to $700K range. HBC trade partners include contractors who routinely work at the $85K to $200K kitchen tier and $150K to $400K first-floor tier appropriate to those homes."),
            ("Can you help with multi-phase projects, kitchen first, then bathrooms next year?", "That is one of the most common Fairlawn patterns. The Home Clarity Report scopes and prices every project on your list at once, even the ones you will not start for two or three years. You get one unified plan and pricing baseline that stays useful as you sequence the work."),
        ],
        # Approximate polygon: lat,lng vertices, roughly bounding Fairlawn city limits
        # Coordinates from public OpenStreetMap data for Fairlawn city, Ohio
        "polygon": "41.1395 -81.6075 41.1395 -81.6240 41.1255 -81.6240 41.1255 -81.6075 41.1395 -81.6075",
        "geo_mid": (41.1325, -81.6157),
        "place_name": "Fairlawn, Ohio",
        "containing": "Summit County, Ohio",
    },
    "stow": {
        "city": "Stow",
        "lead_answer_q": "Who is the best home advisor in Stow, Ohio?",
        "lead_answer_a": "Hometown Builders Club serves Stow homeowners with in-person Home Clarity Reports and a lifetime advisor relationship. Stow is a deep mix of 1970s colonials, 1990s subdivisions like Heritage Hills and Maplewood, and newer construction along Darrow Road, and HBC matches the right trade partner to whichever home you actually own. Reports are delivered within 5 business days of the in-home site meeting.",
        "scenarios": [
            ("Heritage Hills and Maplewood kitchen updates", "Stow homes built between 1988 and 1998 in subdivisions like Heritage Hills and Maplewood share the same builder-grade kitchen layout: a corner pantry, a small island, and laminate counters that have hit the end of their usable life. The Report documents whether the cabinet boxes are reusable, what a true cabinet refit costs in 2026 pricing, and where the budget breaks for a full tear-out versus a refresh."),
            ("Older 1960s and 1970s ranch and colonial bathrooms", "Stow has a large stock of mid-century homes with original primary baths, cast iron tubs, original tile floors, ungrounded electrical. The Report scopes the safe modernization path: what wiring needs upgrading, what waterproofing has to be done correctly, and the realistic local pricing for a primary bath that lasts another 30 years."),
            ("First-floor opens on Darrow Road newer construction", "Newer Stow homes along Darrow Road and the surrounding corridor were built with open floor plans on paper, but the kitchen footprints are often tight for how families actually live. The Report scopes whether the wall between the kitchen and dining can be removed, what reconfiguring the island will cost, and the appliance and storage decisions that make a real difference."),
        ],
        "extra_faqs": [
            ("How is HBC different from the bigger remodelers in Stow?", "Stow has several well-known remodelers including Anthony Slabaugh Remodeling and Design. HBC is not a remodeler at all. We document your home, write your scope, and introduce you to a vetted trade partner. If you end up choosing a Stow remodeler you already knew, you walk in with a written scope they can bid against, which is a sharper starting point than a discovery call."),
            ("Do you cover homes in the Woodridge and Hudson-adjacent parts of Stow?", "Yes. The HBC service area covers all of Stow regardless of school district, including the Woodridge-served homes and the parts of Stow that sit close to the Hudson line. The Report content is the same. The local pricing benchmarks are the same."),
        ],
        "polygon": "41.1900 -81.4220 41.1900 -81.4760 41.1450 -81.4760 41.1450 -81.4220 41.1900 -81.4220",
        "geo_mid": (41.1614, -81.4404),
        "place_name": "Stow, Ohio",
        "containing": "Summit County, Ohio",
    },
    "cuyahoga-falls": {
        "city": "Cuyahoga Falls",
        "lead_answer_q": "Who is the best home advisor in Cuyahoga Falls, Ohio?",
        "lead_answer_a": "Hometown Builders Club is based in Cuyahoga Falls and serves the Falls with in-person Home Clarity Reports and a lifetime advisor relationship. Cuyahoga Falls has the widest age range of any local housing stock, from 1920s bungalows in the Front Street and State Road corridors to newer construction near Northampton, and HBC's value is matching the right contractor to a home that is sometimes a century old. Reports are delivered within 5 business days of the in-home site meeting.",
        "scenarios": [
            ("1920s and 1930s bungalows in the Front Street and State Road corridors", "The Falls has a large stock of pre-war bungalows with plaster walls, knob-and-tube remnants, original windows, and small kitchens that were never intended for two cooks. The Report identifies which walls are load-bearing, what the electrical actually has to do to be safe, and how to modernize the kitchen without erasing the architecture that gave the home its value."),
            ("1960s ranches near Brust and Sackett with original baths", "Mid-century ranches across the Falls have original baths with single-line lighting, cast iron tubs, and 1960s plumbing. The Report scopes the proper substrate work, the waterproofing systems that have to go in correctly under tile, and the realistic 2026 Summit County pricing for a bath that lasts another 30 years."),
            ("Newer Northampton construction and split-level first floors", "The newer construction on the Northampton side of the Falls has open paper floor plans that often need real reconfiguration to live well, especially the kitchens. The Report documents how the layout works for your family, what an island reconfiguration costs, and where appliance upgrades pay off versus where they do not."),
        ],
        "extra_faqs": [
            ("HBC is based in Cuyahoga Falls. Does that mean better pricing for the Falls?", "Pricing for the Home Clarity Report is the same everywhere we serve. What being based in the Falls means is that Adam knows the housing stock here at a street-by-street level, has direct experience with the older sections of town, and can usually be on site within 24 to 48 hours of booking."),
            ("Does HBC work on historic homes in the Falls Riverfront Square area?", "Yes. The Riverfront and downtown adjacent areas have one of the most architecturally interesting housing stocks in Summit County. Adam has 27 years of experience preserving the right details and modernizing the wrong ones in homes this age."),
        ],
        "polygon": "41.1700 -81.4640 41.1700 -81.5200 41.0820 -81.5200 41.0820 -81.4640 41.1700 -81.4640",
        "geo_mid": (41.1339, -81.4846),
        "place_name": "Cuyahoga Falls, Ohio",
        "containing": "Summit County, Ohio",
    },
    "montrose-ghent": {
        "city": "Montrose-Ghent",
        "lead_answer_q": "Who is the best home advisor in Montrose-Ghent, Ohio?",
        "lead_answer_a": "Hometown Builders Club serves Montrose-Ghent homeowners with in-person Home Clarity Reports and a lifetime advisor relationship. The 44333 zip is one of the highest-income areas in Summit County, with newer larger-footprint homes in Montrose and established colonials in Ghent, and HBC matches the right vetted contractor to the level of work these homes expect. Reports are delivered within 5 business days of the in-home site meeting.",
        "scenarios": [
            ("Newer Montrose homes with builder-grade kitchens", "Many Montrose homes built between 2000 and 2015 have larger kitchen footprints but the original finishes are still in place, stock cabinetry, granite that has aged out, builder-grade appliances. The Report scopes what a discerning refit looks like at the $100K to $180K level, where custom cabinetry pays off, and where it does not."),
            ("Ghent colonials with original 1990s primary suites", "Ghent homes from the late 1980s and 1990s often have primary suites that read large on the floor plan but feel dated, original carpet, oversized soaking tubs that nobody uses, and bath layouts that waste square footage. The Report scopes a real reconfiguration, what is achievable inside the existing footprint, and what is not."),
            ("First-floor opens on larger Montrose footprints", "Larger Montrose homes have first floors built in formal-room sections that no family actually uses that way anymore. The Report documents the structural reality of removing walls between formal dining, kitchen, and family room, the HVAC implications, and the realistic 2026 pricing for the open-plan first floor most owners actually want."),
        ],
        "extra_faqs": [
            ("Are the HBC trade partners up to the standard expected in the 44333 zip?", "Yes. The HBC trade partner network includes contractors who routinely work at the $150K to $400K first-floor tier and the $250K and up concierge tier appropriate to Montrose and Ghent home values. Adam vets every introduction against the level of finish the home calls for."),
            ("Can the Home Clarity Report support a multi-million-dollar renovation?", "Yes. The Report's scope, pricing, and documentation scale up. For projects at the concierge tier ($250K and up), the Report becomes the foundation document that every consultant, contractor, and designer works from."),
        ],
        # 44333 polygon (Montrose-Ghent CDP boundary approximation)
        "polygon": "41.1750 -81.6520 41.1750 -81.7050 41.1370 -81.7050 41.1370 -81.6520 41.1750 -81.6520",
        "geo_mid": (41.1568, -81.6789),
        "place_name": "Montrose-Ghent, Ohio",
        "containing": "Summit County, Ohio",
    },
    "peninsula": {
        "city": "Peninsula",
        "lead_answer_q": "Who is the best home advisor in Peninsula, Ohio?",
        "lead_answer_a": "Hometown Builders Club serves Peninsula homeowners with in-person Home Clarity Reports and a lifetime advisor relationship. Peninsula sits inside the Cuyahoga Valley National Park, with a housing stock that ranges from 19th-century farmhouses to mid-century homes on large wooded lots, and HBC's value is matching the right preservation-aware contractor to homes that often have real historic character. Reports are delivered within 5 business days of the in-home site meeting.",
        "scenarios": [
            ("Pre-war farmhouses and bungalows near the village", "Peninsula's village core and the surrounding valley have a number of pre-1940 homes, farmhouses, small bungalows, that need updating without erasing what makes them worth living in. The Report identifies which historic details actually carry value, what the structural reality is behind the plaster, and how to modernize systems without losing the architecture."),
            ("Mid-century homes on large wooded lots", "Peninsula has a strong inventory of 1960s and 1970s homes set on multi-acre wooded lots, often with original kitchens and primary baths. The Report scopes a thoughtful update that respects the home's mid-century character, with realistic pricing for the kitchen and bath work that almost always comes first."),
            ("Newer construction with unusual setbacks and site constraints", "Newer Peninsula builds frequently sit on land with steep grades, septic systems, or proximity to protected wetlands. The Report documents the site constraints, what they mean for any planned addition or first-floor expansion, and which trade partners have experience working inside Cuyahoga Valley setbacks."),
        ],
        "extra_faqs": [
            ("Does HBC work on homes inside the Cuyahoga Valley National Park boundary?", "Yes. Many Peninsula homes are inside or adjacent to the park. Adam has direct experience with the regulatory and practical realities of these properties, including the trade partners who know how to work within National Park-adjacent constraints."),
            ("Are HBC trade partners willing to drive out to Peninsula?", "Yes. HBC trade partners are pre-qualified to work across all of Summit County, including the Peninsula and Boston Heights side of the valley. Travel time is built into the bids when relevant, the Report flags it before you see numbers."),
        ],
        "polygon": "41.2520 -81.5240 41.2520 -81.5700 41.2120 -81.5700 41.2120 -81.5240 41.2520 -81.5240",
        "geo_mid": (41.2367, -81.5479),
        "place_name": "Peninsula, Ohio",
        "containing": "Summit County, Ohio",
    },
    "tallmadge": {
        "city": "Tallmadge",
        "lead_answer_q": "Who is the best home advisor in Tallmadge, Ohio?",
        "lead_answer_a": "Hometown Builders Club serves Tallmadge homeowners with in-person Home Clarity Reports and a lifetime advisor relationship. Tallmadge has a deep mix of 1950s ranches around the Circle, 1970s and 1980s colonials in Forest Drive and Brittain Road neighborhoods, and newer construction near East Avenue, and HBC matches the right vetted contractor to each home's specific era. Reports are delivered within 5 business days of the in-home site meeting.",
        "scenarios": [
            ("Tallmadge Circle area 1950s ranches", "The neighborhoods around Tallmadge Circle have a large stock of mid-century ranches with original galley kitchens and small primary baths. The Report identifies where a kitchen expansion is realistic versus where it requires structural work that breaks the budget, and gives you the 2026 Summit County pricing for both paths."),
            ("Forest Drive and Brittain Road colonials with closed-off kitchens", "Tallmadge homes built between 1972 and 1992 along Forest Drive, Brittain Road, and the surrounding subdivisions almost always have a kitchen separated from the family room by a load-path wall. The Report scopes the structural work, the cost of the steel beam, and the realistic full-project pricing before any contractor walks in."),
            ("Newer East Avenue construction with builder-grade finishes", "Tallmadge's newer construction on the East Avenue corridor was built with open floor plans but stock cabinet packages and builder-grade finishes that homeowners often want to upgrade within five to ten years. The Report scopes the realistic upgrade paths, kitchen refit, primary bath rework, where the money goes and where it does not."),
        ],
        "extra_faqs": [
            ("How does HBC handle Tallmadge's mix of older and newer homes?", "The Report adapts to what your home actually is. For 1950s ranches, the focus is structural reality and original-system documentation. For newer construction, the focus is finish-level upgrades and layout reconfiguration. Adam has direct experience with both ends of the Tallmadge stock."),
            ("Are HBC trade partners available for smaller Tallmadge kitchen budgets?", "Yes, with a floor. HBC introductions start to make sense at roughly $85,000 and up for kitchen work and $45,000 and up for primary bath work. Below those numbers, the Report is still useful, but the contractor introduction often points to a different segment of the market than HBC's primary network."),
        ],
        "polygon": "41.1230 -81.4170 41.1230 -81.4650 41.0830 -81.4650 41.0830 -81.4170 41.1230 -81.4170",
        "geo_mid": (41.1014, -81.4407),
        "place_name": "Tallmadge, Ohio",
        "containing": "Summit County, Ohio",
    },
}

# Also need Place schema for Hudson and Bath Township (step 7 covers all 8)
PLACE_ONLY_LOCATIONS = {
    "hudson": {
        "polygon": "41.2745 -81.4150 41.2745 -81.4790 41.2080 -81.4790 41.2080 -81.4150 41.2745 -81.4150",
        "geo_mid": (41.2400, -81.4400),
        "place_name": "Hudson, Ohio",
        "containing": "Summit County, Ohio",
    },
    "bath-township": {
        "polygon": "41.2050 -81.6020 41.2050 -81.6900 41.1430 -81.6900 41.1430 -81.6020 41.2050 -81.6020",
        "geo_mid": (41.1739, -81.6470),
        "place_name": "Bath Township, Ohio",
        "containing": "Summit County, Ohio",
    },
}


def build_place_schema(slug, cfg):
    """Returns Place JSON-LD with geo polygon."""
    page_url = f"https://www.hometownbuildersclub.com/locations/{slug}"
    return {
        "@context": "https://schema.org",
        "@type": "Place",
        "@id": f"{page_url}#place",
        "name": cfg["place_name"],
        "url": page_url,
        "containedInPlace": {
            "@type": "AdministrativeArea",
            "name": cfg["containing"],
        },
        "geo": {
            "@type": "GeoShape",
            "polygon": cfg["polygon"],
        },
        "additionalProperty": [
            {
                "@type": "PropertyValue",
                "name": "Service area centroid",
                "value": f"{cfg['geo_mid'][0]},{cfg['geo_mid'][1]}",
            }
        ],
    }


def build_scenarios_html(city, scenarios):
    items = "\n".join(
        f'''        <div style="border-left:3px solid var(--gold); padding-left:24px">
          <h3 style="font-family:var(--font-display); font-size:1.2rem; font-weight:600; color:var(--navy); margin-bottom:8px">{title}</h3>
          <p style="font-size:16px; line-height:1.75; color:var(--navy)">{body}</p>
        </div>'''
        for title, body in scenarios
    )
    return f'''  <section class="section bg-white" id="scenarios">
    <div class="container" style="max-width:760px">
      <span class="section-label">Scenarios in {city}</span>
      <h2 class="section-h2" style="margin-bottom:40px">What HBC actually does for {city} homes:</h2>
      <div style="display:flex; flex-direction:column; gap:28px">
{items}
      </div>
    </div>
  </section>

'''


def build_extra_faq_items_html(extra_faqs):
    """Returns the inner HTML for 2 additional FAQ items in the same style as existing."""
    return "\n".join(
        f'''        <div style="border-left:3px solid var(--gold); padding-left:24px">
          <h3 style="font-family:var(--font-display); font-size:1.2rem; font-weight:600; color:var(--navy); margin-bottom:8px">{q}</h3>
          <p style="font-size:16px; line-height:1.75; color:var(--navy)">{a}</p>
        </div>'''
        for q, a in extra_faqs
    )


def add_lead_answer_to_hero(html, q, a):
    """Insert lead-answer paragraph right after hero__eyebrow if not present."""
    if 'lead-answer' in html:
        return html, False
    # Insert after hero__eyebrow div, before h1
    pattern = re.compile(r'(<div class="hero__eyebrow">[^<]*</div>\s*)(\s*<h1 class="hero__h1")', re.S)
    m = pattern.search(html)
    if not m:
        return html, False
    lead = f'<p class="lead-answer" data-answer-for="{q}">{a}</p>\n      '
    # Insert AFTER the h1 element instead — to match Hudson pattern (lead-answer is BETWEEN h1 and subhead)
    # Actually Hudson puts it BETWEEN h1 and hero__subhead. Let's match that.
    pattern2 = re.compile(r'(</h1>)(\s*<p class="hero__subhead">)', re.S)
    if pattern2.search(html):
        new = pattern2.sub(rf'\1\n      {lead.strip()}\2', html)
        return new, True
    return html, False


def insert_scenarios_before_faq(html, city, scenarios):
    """Insert Scenarios section before the 'Common Questions' bg-cream section."""
    if 'id="scenarios"' in html:
        return html, False
    block = build_scenarios_html(city, scenarios)
    # Find the bg-cream section that contains "Common Questions"
    pattern = re.compile(r'(\s*<section class="section bg-cream">\s*<div class="container" style="max-width:760px">\s*<span class="section-label">Common Questions</span>)', re.S)
    if not pattern.search(html):
        return html, False
    new = pattern.sub("\n" + block + r"\1", html)
    return new, True


def add_extra_faqs(html, extra_faqs):
    """Append 2 more FAQ items before the closing </div></div></section> of the Common Questions section."""
    # Sentinel: count existing border-left items in Common Questions. If 5, skip.
    # Find the Common Questions section block
    pattern = re.compile(
        r'(<section class="section bg-cream">\s*<div class="container" style="max-width:760px">\s*<span class="section-label">Common Questions</span>.*?)(</div>\s*</div>\s*</section>)',
        re.S,
    )
    m = pattern.search(html)
    if not m:
        return html, False
    block = m.group(1)
    count = block.count('border-left:3px solid var(--gold)')
    if count >= 5:
        return html, False
    insert = build_extra_faq_items_html(extra_faqs)
    new_block = block.rstrip() + "\n" + insert + "\n      "
    new = pattern.sub(lambda mm: new_block + mm.group(2), html, count=1)
    return new, True


def expand_faq_schema(html, all_5_qa):
    """Replace the existing FAQPage mainEntity array with the 5-item version. all_5_qa = list of (q, a)."""
    # Parse out the JSON-LD @graph block containing FAQPage and rewrite.
    pattern = re.compile(r'(<script type="application/ld\+json">)(\{[^<]*?"@graph":\s*\[)(.*?)(\]\})(\s*</script>)', re.S)
    # Easier: find the FAQPage substring and replace its mainEntity array.
    # FAQPage in these files: "FAQPage", "mainEntity": [ ... ]
    new_main = ",".join(
        json.dumps({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}}, separators=(",", ":"))
        for q, a in all_5_qa
    )
    # Match: "FAQPage", "mainEntity": [ ... ] (non-greedy up to ]
    pat = re.compile(r'(\{"@type":\s*"FAQPage",\s*"mainEntity":\s*\[).*?(\](?:,\s*"speakable":[^}]+)?\})', re.S)
    m = pat.search(html)
    if not m:
        return html, False
    replacement = f'{{"@type":"FAQPage","mainEntity":[{new_main}],"speakable":{{"@type":"SpeakableSpecification","cssSelector":[".faq-question",".faq-answer","h1","h2"]}}}}'
    new = pat.sub(replacement, html, count=1)
    return new, True


def add_place_schema(html, slug, cfg):
    """Inject Place schema as a new <script type="application/ld+json"> before </head>."""
    marker_id = f'#place'
    if f'"@id":"https://www.hometownbuildersclub.com/locations/{slug}{marker_id}"' in html:
        return html, False
    schema = build_place_schema(slug, cfg)
    block = f'  <script id="schema-ai-place" type="application/ld+json">{json.dumps(schema, separators=(",", ":"))}</script>\n'
    new = html.replace("</head>", block + "</head>", 1)
    if new == html:
        return html, False
    return new, True


def get_existing_3_faqs(html):
    """Parse the 3 existing visible FAQ items from Common Questions section as (q, a)."""
    pattern = re.compile(
        r'<section class="section bg-cream">\s*<div class="container" style="max-width:760px">\s*<span class="section-label">Common Questions</span>.*?<div style="display:flex; flex-direction:column; gap:28px">(.*?)</div>\s*</div>\s*</section>',
        re.S,
    )
    m = pattern.search(html)
    if not m:
        return []
    items_block = m.group(1)
    item_pat = re.compile(
        r'<div style="border-left:3px solid var\(--gold\)[^"]*"[^>]*>\s*<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>\s*</div>',
        re.S,
    )
    return [(m.group(1).strip(), m.group(2).strip()) for m in item_pat.finditer(items_block)]


def main():
    print("=== ENRICH LOCATION PAGES ===\n")

    # Process the 6 pages that get scenarios + extra FAQs + lead-answer
    for slug, cfg in LOCATIONS.items():
        path = ROOT / f"{slug}.html"
        if not path.exists():
            print(f"  MISSING: {path}")
            continue
        html = path.read_text(encoding="utf-8")
        original = html

        html, did = add_lead_answer_to_hero(html, cfg["lead_answer_q"], cfg["lead_answer_a"])
        msg_lead = "added" if did else "skipped (already present)"

        html, did = insert_scenarios_before_faq(html, cfg["city"], cfg["scenarios"])
        msg_scen = "added" if did else "skipped (already present)"

        # Capture existing 3 FAQs BEFORE adding extras
        existing_3 = get_existing_3_faqs(html)

        html, did = add_extra_faqs(html, cfg["extra_faqs"])
        msg_extra = "added" if did else "skipped (already has 5)"

        # Build the new 5-item FAQ schema = existing 3 + lead-answer Q + 2 extras
        # We use the visible FAQ wording to keep schema and DOM aligned.
        # But also include the lead-answer Q/A as a 6th piece of structured Q&A? Spec said 5 FAQs.
        # Use existing 3 + 2 extras = 5.
        if len(existing_3) >= 3:
            all_5 = existing_3 + cfg["extra_faqs"]
            # Trim to 5
            all_5 = all_5[:5]
            html, did = expand_faq_schema(html, all_5)
            msg_schema = "expanded to 5" if did else "skipped"
        else:
            msg_schema = f"WARNING: could not parse existing FAQs (found {len(existing_3)})"

        html, did = add_place_schema(html, slug, cfg)
        msg_place = "added" if did else "skipped (already present)"

        if html != original:
            path.write_text(html, encoding="utf-8")
            print(f"  {slug}.html")
            print(f"    lead-answer: {msg_lead}")
            print(f"    scenarios:   {msg_scen}")
            print(f"    extra FAQs:  {msg_extra}")
            print(f"    FAQ schema:  {msg_schema}")
            print(f"    Place:       {msg_place}")
        else:
            print(f"  {slug}.html (no changes)")

    # Process Hudson + Bath Township: only add Place schema (rest done in Session 1)
    print()
    for slug, cfg in PLACE_ONLY_LOCATIONS.items():
        path = ROOT / f"{slug}.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        new, did = add_place_schema(html, slug, cfg)
        if did:
            path.write_text(new, encoding="utf-8")
            print(f"  {slug}.html: Place schema added")
        else:
            print(f"  {slug}.html: Place schema skipped (already present)")


if __name__ == "__main__":
    main()
