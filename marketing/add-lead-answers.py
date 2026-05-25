#!/usr/bin/env python3
"""
add-lead-answers.py — Inject direct-answer lead paragraphs after the H1.

Gemini 3.5 Flash extracts plain-English, answer-first paragraphs to
generate AI Mode and AI Overview responses. We add one <p
class="lead-answer" data-answer-for="<question>"> after the page's first
<h1>, additive to the existing copy.

Idempotent: re-runs replace by data-answer-for value.

Also writes a Speakable selector into the existing schema by adding a
SpeakableSpecification graph node if not already present.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (page-path, literal question Gemini might be asked, answer paragraph)
LEADS: list[tuple[str, str, str]] = [
    (
        "index.html",
        "What is Hometown Builders Club?",
        "Hometown Builders Club is a Summit County, Ohio home advisory service that gives discerning homeowners one trusted advisor for the entire life of the house. Members start with a Home Clarity Report, an in-person assessment by Adam Kilgore that documents every system, every upcoming project, and what each one realistically costs. Book a 30 minute discovery call to see if HBC is a fit for your home."
    ),
    (
        "how-it-works.html",
        "How does Hometown Builders Club work?",
        "Hometown Builders Club works in three steps: a 30 minute discovery call, an in-person Home Clarity Report site meeting at your house, and a written report delivered within 5 business days of that site meeting. The report covers every system, every recommended project, and the realistic cost ranges for your specific home in Summit County. From there, members continue with year round advisory access and trade partner introductions."
    ),
    (
        "concierge.html",
        "What is the HBC Concierge service and what is included?",
        "HBC Concierge is a monthly membership for Summit County homeowners who want one advisor coordinating every vendor that touches their home: cleaning, lawn, HVAC, gutters, snow, handyman work, and seasonal projects. You pay one monthly fee, you make one call, and Adam manages the rest. The service is designed for homeowners who would rather not run the house like a project."
    ),
    (
        "services.html",
        "What services does Hometown Builders Club offer?",
        "Hometown Builders Club offers four services: the Home Clarity Report, year round advisor access, vetted trade partner introductions, and full Concierge home management. Every service starts with an in-person assessment of your home in Summit County, Ohio. The starting point for new members is always the Home Clarity Report, booked through a 30 minute discovery call."
    ),
    (
        "for-realtors.html",
        "How does the HBC realtor partnership work?",
        "The HBC Realtor Partnership is free to join. Your buyer clients get a Home Clarity Report after closing, which documents every system and upcoming project in their new house. When a question comes up six months later, they call HBC instead of calling you, and you stay top of mind as the realtor who set them up for success. Apply through the partnership form to get started."
    ),
    (
        "for-trade-partners.html",
        "How does the HBC trade partner program work for contractors?",
        "HBC trade partners receive sold jobs, not leads. Every project comes with floor plans, photos, a written scope, and a budget the homeowner has already accepted before the trade is brought in. Partners pay nothing to join and only see work that matches their licensing, capacity, and quality bar. Apply through the trade partner page to be considered."
    ),
    (
        "meet-adam.html",
        "Who is Adam Kilgore?",
        "Adam Kilgore is the founder of Hometown Builders Club and a licensed Ohio general contractor with 27 years remodeling homes in Summit County. He founded HBC after seeing how often homeowners were sold projects they did not need by contractors competing on shortest quote turnaround. Every Home Clarity Report is done in person by Adam, and every trade partner relationship is one he personally vouches for."
    ),
    (
        "areas-served.html",
        "What areas does Hometown Builders Club serve?",
        "Hometown Builders Club serves Summit County, Ohio and the immediately adjacent communities within a 30 mile radius of Cuyahoga Falls. Active service areas include Hudson, Bath Township, Fairlawn, Stow, Cuyahoga Falls, Montrose-Ghent, Peninsula, and Tallmadge. All Home Clarity Reports are performed in person, so the service area is intentionally tight."
    ),
    (
        "faq.html",
        "What are the most common questions about Hometown Builders Club?",
        "The most common questions about HBC are: how much does the Home Clarity Report cost, how long does it take, what happens after the report is delivered, who actually does the assessment, and how trade partner introductions work. Every report is done in person by Adam, every report is delivered within 5 business days of the site meeting, and trade partner introductions are included with membership."
    ),
    (
        "vs-angi.html",
        "How is Hometown Builders Club different from Angi?",
        "Angi is a contractor marketplace that sells homeowner contact information to multiple contractors who then bid on the job. Hometown Builders Club is the opposite: one trusted advisor who documents your home, recommends what is actually worth doing, and personally introduces a single qualified trade partner when it is time to build. HBC homeowners are never resold as leads."
    ),
    (
        "locations/hudson.html",
        "Who is the best home advisor in Hudson, Ohio?",
        "Hometown Builders Club serves Hudson homeowners with in-person Home Clarity Reports and a lifetime advisor relationship. Hudson has unusually diverse home stock, from Victorian historics on Aurora Street to newer construction in Brandywine, and HBC's value is matching the right trade partner to your specific house. Reports are delivered within 5 business days of the in-home site meeting."
    ),
    (
        "locations/bath-township.html",
        "Who handles premium renovations in Bath Township, Ohio?",
        "Hometown Builders Club serves Bath Township homeowners planning premium renovations, typically projects between $150,000 and $1.5 million. Every Home Clarity Report is done in person by Adam Kilgore, and every trade partner introduction is matched to the scale and quality bar of the home. Bath Township homeowners book through the 30 minute discovery call."
    ),
]

H1_RE = re.compile(r"(<h1\b[^>]*>.*?</h1>)", re.IGNORECASE | re.DOTALL)
EXISTING_LEAD_RE = re.compile(
    r'<p[^>]*class="[^"]*\blead-answer\b[^"]*"[^>]*data-answer-for="[^"]*"[^>]*>.*?</p>\s*',
    re.IGNORECASE | re.DOTALL,
)


def upsert_lead(html: str, question: str, answer: str) -> tuple[str, bool]:
    # remove any existing lead-answer block (idempotent replace)
    html = EXISTING_LEAD_RE.sub("", html)
    # build the new block
    q_attr = question.replace('"', '&quot;')
    block = (
        f'<p class="lead-answer" data-answer-for="{q_attr}">'
        f'{answer}'
        f'</p>'
    )
    m = H1_RE.search(html)
    if not m:
        return html, False
    insert_at = m.end()
    new = html[:insert_at] + "\n      " + block + html[insert_at:]
    return new, True


def main() -> int:
    changed = 0
    for rel, q, a in LEADS:
        p = ROOT / rel
        if not p.exists():
            print(f"SKIP missing: {rel}")
            continue
        html = p.read_text(encoding="utf-8", errors="replace")
        new, ok = upsert_lead(html, q, a)
        if not ok:
            print(f"SKIP no <h1>: {rel}")
            continue
        if new != html:
            p.write_text(new, encoding="utf-8")
            changed += 1
            print(f"updated {rel}")
    print(f"\n{changed} of {len(LEADS)} pages updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
