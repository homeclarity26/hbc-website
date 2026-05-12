#!/usr/bin/env python3
"""
rollout-nav.py — Replace every page's hand-written <header>...</header>
block with a canonical <header data-nav></header> placeholder, and inject
<script src="/nav.js" defer></script> at the end of <head>.

After this runs, nav.js is the single source of truth for header markup.

Idempotent: skips pages already converted.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pages to convert. Skip pages where converting would be wrong:
# - 404.html: technically a page but Vercel serves it for any unknown route, OK to convert
# - blog/index.html and blog post pages: convert
# - everything in start/ and locations/: convert
# - exclude any non-HTML and node_modules-like dirs
SKIP_DIRS = {"node_modules", ".git", "marketing", "assets", "blog-archive"}

def find_pages():
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # prune
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(dirpath, ROOT)
        for f in filenames:
            if f.endswith(".html"):
                pages.append(os.path.normpath(os.path.join(rel, f)))
    return sorted(pages)


HEADER_PATTERN = re.compile(
    r"<header(?![^>]*data-nav)[^>]*>.*?</header>\s*",
    re.DOTALL | re.IGNORECASE,
)

CANONICAL_HEADER = '<header data-nav></header>\n'

NAV_SCRIPT = '  <script src="/nav.js" defer></script>\n'
HEAD_END = re.compile(r"</head>", re.IGNORECASE)


def has_nav_script(html: str) -> bool:
    return ('src="/nav.js"' in html) or ("src='./nav.js'" in html) or ('src="./nav.js"' in html)


def has_canonical_header(html: str) -> bool:
    return bool(re.search(r"<header[^>]*\bdata-nav\b", html, re.IGNORECASE))


def convert(html: str) -> tuple[str, list[str]]:
    changes = []
    # 1) Replace the first <header>...</header> block (the site nav)
    if not has_canonical_header(html):
        new_html, count = HEADER_PATTERN.subn(CANONICAL_HEADER, html, count=1)
        if count == 1:
            html = new_html
            changes.append("replaced <header> block")
        else:
            changes.append("WARNING: no <header> block found to replace")
    else:
        changes.append("canonical header already present")

    # 2) Add <script src="/nav.js" defer></script> at end of <head>
    if not has_nav_script(html):
        new_html, count = HEAD_END.subn(NAV_SCRIPT + "</head>", html, count=1)
        if count == 1:
            html = new_html
            changes.append("inserted nav.js script tag")
        else:
            changes.append("WARNING: no </head> found")
    else:
        changes.append("nav.js script already present")

    return html, changes


def main():
    pages = find_pages()
    print(f"Found {len(pages)} HTML pages")
    converted = 0
    skipped = 0
    warned = []
    for page in pages:
        path = os.path.join(ROOT, page)
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
        new, changes = convert(original)
        warning = any("WARNING" in c for c in changes)
        if warning:
            warned.append((page, changes))
        if new != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            converted += 1
            print(f"  ✓ {page}: {', '.join(changes)}")
        else:
            skipped += 1
    print(f"\nConverted: {converted}, unchanged: {skipped}")
    if warned:
        print("\nWarnings:")
        for p, cs in warned:
            print(f"  ⚠ {p}: {', '.join(cs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
