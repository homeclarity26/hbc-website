#!/usr/bin/env python3
"""
Fix the FAQPage JSON-LD on the 6 location pages by:
1. Parsing the first <script type="application/ld+json"> block (which contains @graph with FAQPage)
2. Replacing the FAQPage's mainEntity with the 5 visible FAQs scraped from the page DOM
3. Re-serializing as compact JSON
"""
from pathlib import Path
import re, json

ROOT = Path("/home/user/workspace/hbc-website/locations")
PAGES = ["fairlawn", "stow", "cuyahoga-falls", "montrose-ghent", "peninsula", "tallmadge"]

def html_unescape(s):
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;","'").replace("&rarr;","→")

def extract_visible_faqs(html):
    """Returns list of (q, a) from the Common Questions section visible FAQ items."""
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
    out = []
    for mm in item_pat.finditer(items_block):
        q = re.sub(r'\s+', ' ', mm.group(1)).strip()
        a = re.sub(r'\s+', ' ', mm.group(2)).strip()
        # Strip inner anchors but keep their text
        a = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', a)
        q = html_unescape(q)
        a = html_unescape(a)
        out.append((q, a))
    return out

def fix_page(slug):
    path = ROOT / f"{slug}.html"
    html = path.read_text(encoding="utf-8")

    faqs = extract_visible_faqs(html)
    if len(faqs) != 5:
        print(f"  {slug}: expected 5 visible FAQs, found {len(faqs)} — skipping")
        return False

    # Find the first JSON-LD block (the @graph one)
    script_pat = re.compile(r'(<script type="application/ld\+json">)(\{.*?\})(\s*</script>)', re.S)
    m = script_pat.search(html)
    if not m:
        print(f"  {slug}: could not find first ld+json block")
        return False

    raw = m.group(2)
    # Try to parse. If it fails due to our prior corruption, surgically rebuild.
    try:
        data = json.loads(raw)
        parsed_ok = True
    except json.JSONDecodeError as e:
        parsed_ok = False
        print(f"  {slug}: block did not parse ({e}); attempting repair")

    if not parsed_ok:
        # Repair the known corruption: extra trailing `}` after speakable
        # Look for pattern: "h2"]}}}]} and replace with "h2"]}}]}
        repaired = re.sub(r'("h2"\]\})\}\}(\]\})$', r'\1}\2', raw)
        try:
            data = json.loads(repaired)
            print(f"  {slug}: repaired by removing extra brace")
        except Exception as e2:
            # Try alternative: maybe FAQPage has duplicate speakable
            # Strategy: find @graph array, identify FAQPage entry, fully rebuild
            # First, slice off the JSON suffix that's broken.
            # Find "FAQPage" and walk back to find {  start; replace whole FAQPage object with clean one
            # Simpler: rebuild the @graph manually
            # Find index of "FAQPage"
            i = raw.find('"FAQPage"')
            if i == -1:
                print(f"  {slug}: no FAQPage found, giving up")
                return False
            # Walk backward to find the opening `{` of FAQPage object
            depth = 0
            start = i
            while start > 0:
                start -= 1
                if raw[start] == '{':
                    # check this is the start of FAQPage object
                    if raw[start+1:start+15].lstrip().startswith('"@type"'):
                        break
            if raw[start] != '{':
                print(f"  {slug}: could not find FAQPage opening brace")
                return False
            # Walk forward from start, balancing braces to find end of FAQPage object
            depth = 0
            j = start
            in_str = False
            escape = False
            while j < len(raw):
                c = raw[j]
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == '"':
                    in_str = not in_str
                elif not in_str:
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            end = j + 1
                            break
                j += 1
            else:
                print(f"  {slug}: could not balance FAQPage braces")
                return False

            # Build the replacement FAQPage with the 5 visible FAQs
            new_faq = {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faqs
                ],
                "speakable": {
                    "@type": "SpeakableSpecification",
                    "cssSelector": [".faq-question", ".faq-answer", "h1", "h2"],
                },
            }
            new_str = json.dumps(new_faq, separators=(",", ":"))
            repaired = raw[:start] + new_str + raw[end:]
            try:
                data = json.loads(repaired)
                print(f"  {slug}: rebuilt FAQPage object inline")
            except Exception as e3:
                print(f"  {slug}: rebuild still invalid: {e3}")
                return False

    # At this point `data` is the parsed dict. Walk @graph for FAQPage and replace mainEntity.
    graph = data.get("@graph", [])
    fp_idx = None
    for idx, entry in enumerate(graph):
        if isinstance(entry, dict) and entry.get("@type") == "FAQPage":
            fp_idx = idx
            break
    if fp_idx is None:
        print(f"  {slug}: no FAQPage entry in @graph")
        return False

    graph[fp_idx] = {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": [".faq-question", ".faq-answer", "h1", "h2"],
        },
    }

    new_block = json.dumps(data, separators=(",", ":"))
    new_html = html[:m.start(2)] + new_block + html[m.end(2):]

    path.write_text(new_html, encoding="utf-8")
    print(f"  {slug}: FAQPage rewritten with 5 entries")
    return True

def main():
    print("=== FIX LOCATION FAQ SCHEMA ===\n")
    for slug in PAGES:
        fix_page(slug)

if __name__ == "__main__":
    main()
