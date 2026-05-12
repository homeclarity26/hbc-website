#!/usr/bin/env python3
"""Replace em-dashes, en-dashes, and their entities with hyphens, sitewide.

Per the standing rule: REMOVE EM DASHES FROM EVERYTHING. Banned:
    — (U+2014), – (U+2013), &mdash;, &ndash;

All occurrences in HTML files are replaced with a plain hyphen '-'.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = [
    ("\u2014", "-"),     # em dash
    ("\u2013", "-"),     # en dash
    ("&mdash;", "-"),
    ("&ndash;", "-"),
]

changed = 0
total = 0
for p in sorted(ROOT.rglob("*.html")):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(("node_modules/", ".git/", ".vercel/")):
        continue
    total += 1
    text = p.read_text(encoding="utf-8", errors="replace")
    new = text
    for old, repl in REPLACEMENTS:
        new = new.replace(old, repl)
    if new != text:
        p.write_text(new, encoding="utf-8")
        changed += 1
        print(f"fixed {rel}")

print(f"\n{changed} of {total} HTML files updated")
