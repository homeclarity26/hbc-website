#!/usr/bin/env python3
"""Remove orphaned inline mobile-menu wiring scripts.

Now that nav.js owns mobile menu wiring via event delegation, the old
per-page inline IIFEs (which directly reference #hamburger / #mobile-menu /
#mobile-close at page-load time) crash with 'addEventListener of null'
because nav.js hasn't injected the markup yet at the moment they run.

This script finds every <script>...</script> block that references both
'getElementById' AND 'hamburger', and deletes the entire block.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT_RE = re.compile(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL)

changed = 0
total = 0
for p in sorted(ROOT.rglob("*.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(("node_modules/", ".git/", ".vercel/")):
        continue
    total += 1
    text = p.read_text(encoding="utf-8", errors="replace")

    def maybe_drop(m: re.Match) -> str:
        body = m.group(1)
        if "getElementById" in body and "hamburger" in body:
            return ""  # delete the whole <script>...</script>
        return m.group(0)

    new = SCRIPT_RE.sub(maybe_drop, text)
    if new != text:
        p.write_text(new, encoding="utf-8")
        changed += 1
        print(f"stripped {rel}")

print(f"\n{changed} of {total} HTML files updated")
