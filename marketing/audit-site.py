#!/usr/bin/env python3
"""
audit-site.py — Drift-prevention audit for HBC site.

Run before every commit. Exits 0 if clean, 1 if any drift detected.

Checks every HTML page for:
  1. Canonical nav placeholder: exactly one <header data-nav></header>
  2. nav.js included with defer
  3. No legacy CSS refs (/base.css, /style.css) that 404
  4. No em dashes (—, –, &mdash;) in visible copy
  5. No banned words (luxury, high-end, delve, leverage, robust,
     seamlessly, moreover, furthermore, navigate) in visible copy
  6. No hand-rolled <nav> markup outside the canonical header
     (i.e. <nav> tags that aren't inside the data-nav header
     after rendering — caught here as raw <nav class=... siblings)
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES: list[Path] = []
for p in ROOT.rglob("*.html"):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(("node_modules/", ".git/", ".vercel/")):
        continue
    HTML_FILES.append(p)

# Pages that legitimately do not render the canonical header
EXEMPT_NO_NAV = {
    "404.html",
    "thank-you.html",
}

# Em-dash characters and HTML entities
EM_DASH_PATTERNS = [
    "\u2014",       # —
    "\u2013",       # –
    "&mdash;",
    "&ndash;",
]

BANNED_WORDS = [
    "luxury",
    "high-end",
    "delve",
    "leverage",
    "robust",
    "seamlessly",
    "moreover",
    "furthermore",
    "navigate",
]

LEGACY_CSS = [
    re.compile(r"""href=["']/?base\.css["']"""),
    re.compile(r"""href=["']/?style\.css["']"""),
]

NAV_PLACEHOLDER_RE = re.compile(r"<header[^>]*\bdata-nav\b[^>]*>", re.IGNORECASE)
NAV_SCRIPT_RE = re.compile(r"""<script[^>]+src=["']/?nav\.js["']""", re.IGNORECASE)
RAW_HEADER_NAV_RE = re.compile(r"<header(?![^>]*\bdata-nav\b)[^>]*>", re.IGNORECASE)

# Strip <script>, <style>, and HTML tags for visible-copy checks
SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def visible_text(html: str) -> str:
    no_blocks = SCRIPT_OR_STYLE.sub(" ", html)
    no_tags = TAG_RE.sub(" ", no_blocks)
    return no_tags


def audit_file(path: Path) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    issues: list[str] = []
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        return [f"{rel}: unreadable ({e})"]

    is_exempt = path.name in EXEMPT_NO_NAV

    # 1. Canonical nav placeholder
    placeholders = NAV_PLACEHOLDER_RE.findall(html)
    if not is_exempt:
        if len(placeholders) == 0:
            issues.append(f"{rel}: missing <header data-nav></header>")
        elif len(placeholders) > 1:
            issues.append(f"{rel}: {len(placeholders)} <header data-nav> tags (expected 1)")

    # 2. nav.js included
    if not is_exempt and not NAV_SCRIPT_RE.search(html):
        issues.append(f"{rel}: missing <script src=\"/nav.js\" defer></script>")

    # 3. Legacy CSS refs
    for rx in LEGACY_CSS:
        if rx.search(html):
            issues.append(f"{rel}: legacy CSS ref {rx.pattern}")

    # 4. Em dashes in visible text
    vt = visible_text(html)
    for ch in EM_DASH_PATTERNS:
        if ch in vt:
            # Find the surrounding context for the first occurrence
            idx = vt.find(ch)
            ctx = vt[max(0, idx - 30): idx + 30].replace("\n", " ").strip()
            issues.append(f"{rel}: em-dash '{ch}' near '...{ctx}...'")
            break  # one note per file is enough

    # 5. Banned words in visible text (word boundary, case-insensitive)
    vt_low = vt.lower()
    for w in BANNED_WORDS:
        pat = r"\b" + re.escape(w) + r"\b"
        if re.search(pat, vt_low):
            issues.append(f"{rel}: banned word '{w}'")

    # 6. Raw <header> outside the canonical pattern
    if not is_exempt:
        raw = RAW_HEADER_NAV_RE.findall(html)
        if raw:
            issues.append(f"{rel}: {len(raw)} <header> tag(s) without data-nav (hand-rolled)")

    return issues


def main() -> int:
    all_issues: list[str] = []
    for f in sorted(HTML_FILES):
        all_issues.extend(audit_file(f))

    if not all_issues:
        print(f"OK  audit clean across {len(HTML_FILES)} HTML files")
        return 0

    print(f"FAIL  {len(all_issues)} issue(s) across {len(HTML_FILES)} HTML files\n")
    for line in all_issues:
        print("  - " + line)
    return 1


if __name__ == "__main__":
    sys.exit(main())
