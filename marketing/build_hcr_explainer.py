"""Home Clarity Report — homeowner explainer PDF (4 pages, full color, print-ready)."""

import urllib.request
from pathlib import Path

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ---------- Brand tokens ----------
NAVY = HexColor("#0A1628")
NAVY_DARK = HexColor("#060e1c")
GOLD = HexColor("#B87333")
GOLD_HOVER = HexColor("#A0622A")
CREAM = HexColor("#EDE9E1")
CREAM_DARK = HexColor("#E2DDD4")
WHITE = HexColor("#FFFFFF")
RUST = HexColor("#B7410E")
NAVY_72 = Color(10/255, 22/255, 40/255, alpha=0.72)
CREAM_70 = Color(237/255, 233/255, 225/255, alpha=0.7)
CREAM_55 = Color(237/255, 233/255, 225/255, alpha=0.55)
GOLD_30 = Color(184/255, 115/255, 51/255, alpha=0.3)

# ---------- Fonts ----------
FONT_DIR = Path("/tmp/hbc_fonts")
FONT_DIR.mkdir(exist_ok=True)

# Use variable fonts from Google Fonts repo (raw URLs).
# Cormorant Garamond ships variable wght (regular + italic).
# Inter ships variable opsz,wght (regular + italic).
FONTS = {
    "Cormorant-Variable":        "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
    "Cormorant-Italic-Variable": "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf",
    "Inter-Variable":             "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    "PlexMono-Regular":           "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf",
    "PlexMono-SemiBold":          "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-SemiBold.ttf",
}

for name, url in FONTS.items():
    fp = FONT_DIR / f"{name}.ttf"
    if not fp.exists():
        try:
            urllib.request.urlretrieve(url, fp)
        except Exception as e:
            print(f"WARN: could not fetch {name}: {e}")
    if fp.exists():
        try:
            pdfmetrics.registerFont(TTFont(name, str(fp)))
        except Exception as e:
            print(f"WARN: register {name}: {e}")

# Map logical names to the variable files we actually have. Variable fonts in
# ReportLab pick the default instance; that's fine for our purposes. We
# differentiate weight visually via larger sizes for headlines.
CORMORANT = "Cormorant-Variable"
CORMORANT_IT = "Cormorant-Italic-Variable"
INTER = "Inter-Variable"

# Aliases (collapsed to available variable fonts)
DISPLAY = CORMORANT
DISPLAY_BOLD = CORMORANT          # use larger size for emphasis
DISPLAY_ITALIC = CORMORANT_IT
DISPLAY_BOLDITALIC = CORMORANT_IT
BODY = INTER
BODY_MED = INTER
BODY_SEMI = INTER
BODY_BOLD = INTER
MONO = "PlexMono-Regular"
MONO_SEMI = "PlexMono-SemiBold"

# ---------- Page setup ----------
PAGE_W, PAGE_H = letter  # 612 x 792
MARGIN = 0.6 * 72  # 0.6"
OUT = "/home/user/workspace/hbc-website/marketing/home-clarity-report-explainer.pdf"

LOGO_PATH = "/home/user/workspace/hbc-website/assets/hbc-logo-horizontal-white.png"


def draw_wrapped(c, text, x, y, max_w, font, size, leading, color):
    """Word-wrap a paragraph onto canvas. Returns final y."""
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line = ""
    for w in words:
        trial = (line + " " + w).strip()
        if pdfmetrics.stringWidth(trial, font, size) <= max_w:
            line = trial
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def eyebrow(c, text, x, y, color=GOLD):
    c.setFont(MONO_SEMI, 9)
    c.setFillColor(color)
    # letter-spacing ~ 0.12em via manual draw
    cur = x
    for ch in text.upper():
        c.drawString(cur, y, ch)
        cur += pdfmetrics.stringWidth(ch, MONO_SEMI, 9) + 1.4
    return y


def hairline(c, x1, y, x2, color=GOLD, w=0.6):
    c.setStrokeColor(color)
    c.setLineWidth(w)
    c.line(x1, y, x2, y)


# =========================================================
c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("The Home Clarity Report. Hometown Builders Club.")
c.setAuthor("Perplexity Computer")
c.setSubject("Homeowner explainer for the Home Clarity Report")
c.setCreator("Hometown Builders Club")

# =========================================================
# PAGE 1 — COVER
# =========================================================
c.setFillColor(NAVY)
c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

# Subtle gold corner accents
c.setStrokeColor(GOLD)
c.setLineWidth(1.0)
inset = 0.45 * 72
arm = 0.4 * 72
# top-left
c.line(inset, PAGE_H - inset, inset + arm, PAGE_H - inset)
c.line(inset, PAGE_H - inset, inset, PAGE_H - inset - arm)
# top-right
c.line(PAGE_W - inset, PAGE_H - inset, PAGE_W - inset - arm, PAGE_H - inset)
c.line(PAGE_W - inset, PAGE_H - inset, PAGE_W - inset, PAGE_H - inset - arm)
# bottom-left
c.line(inset, inset, inset + arm, inset)
c.line(inset, inset, inset, inset + arm)
# bottom-right
c.line(PAGE_W - inset, inset, PAGE_W - inset - arm, inset)
c.line(PAGE_W - inset, inset, PAGE_W - inset, inset + arm)

# Logo top center
try:
    img = ImageReader(LOGO_PATH)
    iw, ih = img.getSize()
    target_w = 2.0 * 72
    scale = target_w / iw
    target_h = ih * scale
    c.drawImage(img, (PAGE_W - target_w) / 2, PAGE_H - 1.5 * 72,
                width=target_w, height=target_h, mask='auto')
except Exception as e:
    c.setFont(BODY_SEMI, 12)
    c.setFillColor(CREAM)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.2 * 72, "HOMETOWN BUILDERS CLUB")

# Eyebrow above title
c.setFont(MONO_SEMI, 10)
c.setFillColor(GOLD)
eb = "FOR HOMEOWNERS"
cx = PAGE_W / 2
total_w = sum(pdfmetrics.stringWidth(ch, MONO_SEMI, 10) + 1.6 for ch in eb)
cur = cx - total_w / 2
ey = PAGE_H / 2 + 1.2 * 72
for ch in eb:
    c.drawString(cur, ey, ch)
    cur += pdfmetrics.stringWidth(ch, MONO_SEMI, 10) + 1.6

# Hairline under eyebrow
c.setStrokeColor(GOLD)
c.setLineWidth(0.7)
c.line(cx - 0.6 * 72, ey - 10, cx + 0.6 * 72, ey - 10)

# Title — large gold script-feel (Cormorant italic)
title = "The Home Clarity Report"
c.setFillColor(GOLD)
c.setFont(DISPLAY_BOLDITALIC, 60)
c.drawCentredString(cx, PAGE_H / 2 + 0.1 * 72, title)

# Subhead — cream
c.setFillColor(CREAM)
c.setFont(DISPLAY_ITALIC, 19)
sub_y = PAGE_H / 2 - 0.55 * 72
c.drawCentredString(cx, sub_y, "A complete expert assessment of your home.")
c.drawCentredString(cx, sub_y - 24, "Delivered in 5 business days.")

# Decorative gold rule
c.setStrokeColor(GOLD)
c.setLineWidth(0.8)
c.line(cx - 1.0 * 72, sub_y - 50, cx + 1.0 * 72, sub_y - 50)

# Mid-cover small label
c.setFillColor(CREAM_70)
c.setFont(BODY, 10.5)
c.drawCentredString(cx, sub_y - 75, "$4,500  ·  In person  ·  No sales pressure")

# Bottom line
c.setFillColor(CREAM_70)
c.setFont(MONO, 9)
bottom = "Hometown Builders Club   ·   Summit County, Ohio   ·   hometownbuildersclub.com"
c.drawCentredString(cx, 0.85 * 72, bottom)

c.showPage()

# =========================================================
# PAGE 2 — WHAT IT IS
# =========================================================
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

# Top navy band with page label
c.setFillColor(NAVY)
c.rect(0, PAGE_H - 0.5 * 72, PAGE_W, 0.5 * 72, fill=1, stroke=0)
c.setFillColor(CREAM)
c.setFont(MONO_SEMI, 8.5)
cur = MARGIN
label = "HOMETOWN BUILDERS CLUB   ·   THE HOME CLARITY REPORT"
for ch in label:
    c.drawString(cur, PAGE_H - 0.32 * 72, ch)
    cur += pdfmetrics.stringWidth(ch, MONO_SEMI, 8.5) + 1.0
c.setFillColor(GOLD)
c.setFont(MONO_SEMI, 8.5)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.32 * 72, "PAGE 02")

# Layout: left content column ~ 60%, right side panel ~ 40%
content_top = PAGE_H - 0.5 * 72 - 0.55 * 72
left_x = MARGIN
right_panel_x = PAGE_W * 0.62
left_w = right_panel_x - MARGIN - 0.25 * 72

# Eyebrow
eyebrow(c, "What it is", left_x, content_top)
hairline(c, left_x, content_top - 8, left_x + 1.6 * 72)

# H1
h1_y = content_top - 0.45 * 72
c.setFillColor(NAVY)
c.setFont(DISPLAY_BOLD, 30)
# wrap headline manually
headline = "Before you hire anyone, find out what's actually going on with your house."
words = headline.split()
lines = []
line = ""
max_w_h = left_w
for w in words:
    trial = (line + " " + w).strip()
    if pdfmetrics.stringWidth(trial, DISPLAY_BOLD, 30) <= max_w_h:
        line = trial
    else:
        lines.append(line)
        line = w
if line:
    lines.append(line)
y = h1_y
for ln in lines:
    c.drawString(left_x, y, ln)
    y -= 32

y -= 14
# Body paragraphs
para1 = ("A Home Clarity Report is a 5-business-day assessment of your home, "
         "conducted in person by Adam Kilgore and the HBC team. We document every "
         "system, measure every room, photograph every space, and write a "
         "plain-English scope and budget for every project you're considering. "
         "Then we give it all to you. No sales pressure. No upsell. Just clarity.")

para2 = ("The Report costs $4,500. The homeowners we've worked with save an "
         "average of $16,100 on their first major project after going through the "
         "process. The math is simple: knowing what your home actually needs, and "
         "what fair pricing looks like, saves more than it costs.")

para3 = ("And it doesn't end when the Report is delivered. Every Report includes "
         "lifetime access to your Home Clarity Hub, a private digital portal that "
         "knows your house and answers your questions for as long as you own it.")

for para in [para1, para2, para3]:
    y = draw_wrapped(c, para, left_x, y, left_w, BODY, 10.5, 15.5, NAVY_72)
    y -= 9

# Pull quote / accent
y -= 4
hairline(c, left_x, y, left_x + 1.0 * 72, GOLD, 1.0)
y -= 18
c.setFillColor(NAVY)
c.setFont(DISPLAY_ITALIC, 14)
c.drawString(left_x, y, "Find HBC first. Before you hire anyone.")

# ----- Right side panel: "What's included" -----
panel_x = right_panel_x
panel_y_top = content_top + 6
panel_w = PAGE_W - MARGIN - panel_x
panel_h = PAGE_H - 0.5 * 72 - 0.55 * 72 - MARGIN + 6 - (PAGE_H - panel_y_top) + (panel_y_top - MARGIN)

# Draw navy panel
panel_bottom = MARGIN + 0.2 * 72
c.setFillColor(NAVY)
c.roundRect(panel_x, panel_bottom, panel_w, panel_y_top - panel_bottom, 8, fill=1, stroke=0)

# panel content
px = panel_x + 16
py = panel_y_top - 22

c.setFont(MONO_SEMI, 9)
c.setFillColor(GOLD)
cur = px
for ch in "WHAT'S INCLUDED":
    c.drawString(cur, py, ch)
    cur += pdfmetrics.stringWidth(ch, MONO_SEMI, 9) + 1.3
py -= 8
c.setStrokeColor(GOLD)
c.setLineWidth(0.7)
c.line(px, py, px + 1.2 * 72, py)
py -= 22

c.setFillColor(CREAM)
c.setFont(DISPLAY_BOLD, 18)
c.drawString(px, py, "Every Report")
py -= 19
c.drawString(px, py, "delivers")
py -= 22

items = [
    ("Interior floor plans", "accurate to 1/8 inch, every level"),
    ("Exterior 3D model", "roof, siding, windows, measured"),
    ("360° photography", "every room and mechanical space"),
    ("Written project scope", "for every priority area"),
    ("Realistic budgets", "Summit County pricing ranges"),
    ("System ages and condition", "every major mechanical system"),
    ("Vetted trade network", "already briefed on your home"),
    ("Lifetime advisor relationship", "one call, forever, any question"),
]

c.setFont(BODY, 9.3)
for title, sub in items:
    # gold square "check" mark — drawn shape (avoids missing glyphs)
    c.setFillColor(GOLD)
    c.rect(px, py, 4, 9, fill=1, stroke=0)
    c.setFillColor(CREAM)
    c.setFont(BODY_SEMI, 9.6)
    c.drawString(px + 12, py, title)
    c.setFillColor(CREAM_70)
    c.setFont(BODY, 8.6)
    c.drawString(px + 12, py - 11, sub)
    py -= 26

# Panel bottom callout
py -= 4
c.setStrokeColor(GOLD_30)
c.setLineWidth(0.5)
c.line(px, py + 8, panel_x + panel_w - 16, py + 8)
py -= 6
c.setFillColor(GOLD)
c.setFont(MONO_SEMI, 8.5)
c.drawString(px, py, "$4,500   ·   5 BUSINESS DAYS")

# Page footer
c.setFillColor(NAVY_72)
c.setFont(MONO, 7.5)
c.drawString(MARGIN, MARGIN - 4, "hometownbuildersclub.com")
c.drawRightString(PAGE_W - MARGIN, MARGIN - 4, "(330) 203-1331  ·  adam@hometownbuildersclub.com")

c.showPage()

# =========================================================
# PAGE 3 — THE HUB
# =========================================================
c.setFillColor(NAVY)
c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

# Top thin gold rule
c.setStrokeColor(GOLD)
c.setLineWidth(0.7)
c.line(MARGIN, PAGE_H - 0.55 * 72, PAGE_W - MARGIN, PAGE_H - 0.55 * 72)

# top label
c.setFillColor(CREAM_70)
c.setFont(MONO_SEMI, 8.5)
cur = MARGIN
for ch in "HOMETOWN BUILDERS CLUB   ·   THE HOME CLARITY REPORT":
    c.drawString(cur, PAGE_H - 0.42 * 72, ch)
    cur += pdfmetrics.stringWidth(ch, MONO_SEMI, 8.5) + 1.0
c.setFillColor(GOLD)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.42 * 72, "PAGE 03")

# Eyebrow + H1
top_y = PAGE_H - 1.0 * 72
eyebrow(c, "Your Home Clarity Hub", MARGIN, top_y)
c.setStrokeColor(GOLD)
c.line(MARGIN, top_y - 8, MARGIN + 2.0 * 72, top_y - 8)

c.setFillColor(CREAM)
c.setFont(DISPLAY_BOLD, 34)
c.drawString(MARGIN, top_y - 0.55 * 72, "An operating system for your house.")

c.setFillColor(CREAM_70)
c.setFont(DISPLAY_ITALIC, 13.5)
c.drawString(MARGIN, top_y - 0.55 * 72 - 22,
             "The portal lives forever. Trained on your home, and your home only.")

# Layout: left bullets column ~ 58%, right phone mockup ~ 38%
left_x = MARGIN
left_w = PAGE_W * 0.55 - MARGIN
right_x = PAGE_W * 0.59
right_w = PAGE_W - MARGIN - right_x

bullets = [
    ("01",
     "Your house, on call. Forever.",
     "Your Home Clarity Hub doesn't get filed away. It lives in a private "
     "portal you and your family can open from any phone, any time. The paint "
     "color in the den. The year the roof was replaced. What that valve under "
     "the sink does. It's all there."),
    ("02",
     "A second opinion before you say yes to anyone.",
     "Quote from a contractor seems off? Ask the Hub. It knows your house, "
     "every measurement, every system, every material our team documented, "
     "and answers in plain language. Adam and the HBC team are one tap away "
     "if you want a human on the line."),
    ("03",
     "Built only on your home. Not on the internet.",
     "Think of it as an operating system for your house. Trained on your home "
     "and your home only, so what it tells you is pulling from what we "
     "actually saw in your walls, not generic remodeling forums."),
]

y = top_y - 0.55 * 72 - 60
for num, head, body in bullets:
    # number
    c.setFillColor(GOLD)
    c.setFont(MONO_SEMI, 9)
    c.drawString(left_x, y, num)
    # gold subhead
    c.setFillColor(GOLD)
    c.setFont(DISPLAY_BOLD, 17)
    # wrap subhead
    head_words = head.split()
    line = ""
    head_lines = []
    for w in head_words:
        trial = (line + " " + w).strip()
        if pdfmetrics.stringWidth(trial, DISPLAY_BOLD, 17) <= left_w - 0.3 * 72:
            line = trial
        else:
            head_lines.append(line)
            line = w
    if line:
        head_lines.append(line)
    hy = y
    for hl in head_lines:
        c.drawString(left_x + 0.3 * 72, hy, hl)
        hy -= 19
    y_after_head = hy - 2
    # body
    y_after_body = draw_wrapped(c, body, left_x + 0.3 * 72, y_after_head,
                                 left_w - 0.3 * 72, BODY, 9.8, 14.5, CREAM_70)
    y = y_after_body - 16

# ----- Right side: phone mockup of the Hub -----
# Phone frame
phone_w = right_w * 0.95
phone_h = phone_w * 2.05
phone_x = right_x + (right_w - phone_w) / 2
phone_y = top_y - 0.55 * 72 - 60 - phone_h + 60  # align top near first bullet

# Recompute: place phone vertically centered in available area
avail_top = top_y - 0.55 * 72 - 30
avail_bottom = MARGIN + 0.6 * 72
avail_h = avail_top - avail_bottom
phone_h = min(avail_h, phone_w * 2.0)
phone_y = avail_bottom + (avail_h - phone_h) / 2

# Outer phone shell
c.setFillColor(HexColor("#0a0a0a"))
c.roundRect(phone_x, phone_y, phone_w, phone_h, 22, fill=1, stroke=0)
# Inner screen
pad = 6
sx = phone_x + pad
sy = phone_y + pad
sw = phone_w - 2 * pad
sh = phone_h - 2 * pad
c.setFillColor(NAVY_DARK)
c.roundRect(sx, sy, sw, sh, 18, fill=1, stroke=0)

# Notch
notch_w = phone_w * 0.32
c.setFillColor(HexColor("#0a0a0a"))
c.roundRect(phone_x + (phone_w - notch_w) / 2, phone_y + phone_h - 14,
            notch_w, 14, 7, fill=1, stroke=0)

# Status bar / app header
hdr_h = 36
hdr_y = sy + sh - hdr_h
c.setFillColor(NAVY)
c.roundRect(sx, hdr_y, sw, hdr_h, 6, fill=1, stroke=0)
# header text
c.setFillColor(GOLD)
c.setFont(MONO_SEMI, 7)
c.drawString(sx + 10, hdr_y + hdr_h - 12, "HOME CLARITY HUB")
c.setFillColor(CREAM)
c.setFont(BODY_SEMI, 9)
c.drawString(sx + 10, hdr_y + 8, "1842 Aurora Hudson Rd")
c.setFillColor(GOLD_30)
c.line(sx + 8, hdr_y, sx + sw - 8, hdr_y)

# Content rows
row_y = hdr_y - 18
row_pad_x = 10

def hub_row(label, value, sub=None, highlight=False):
    global row_y
    row_h = 38 if sub else 28
    if highlight:
        c.setFillColor(Color(184/255, 115/255, 51/255, alpha=0.10))
        c.roundRect(sx + 6, row_y - row_h + 10, sw - 12, row_h, 4, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont(MONO_SEMI, 6.5)
    c.drawString(sx + row_pad_x, row_y, label)
    c.setFillColor(CREAM)
    c.setFont(BODY_SEMI, 8.5)
    c.drawString(sx + row_pad_x, row_y - 11, value)
    if sub:
        c.setFillColor(CREAM_55)
        c.setFont(BODY, 7.3)
        c.drawString(sx + row_pad_x, row_y - 21, sub)
    # divider
    c.setStrokeColor(Color(237/255, 233/255, 225/255, alpha=0.08))
    c.setLineWidth(0.4)
    c.line(sx + 8, row_y - row_h + 8, sx + sw - 8, row_y - row_h + 8)
    row_y -= row_h

hub_row("ROOF", "Replaced 2019", "25-yr arch shingle  ·  6 yrs in")
hub_row("HVAC", "Furnace 2015 · AC 2021", "Lennox  ·  serviced Apr 2025")
hub_row("KITCHEN", "Renovated 2024 by HBC", "Walnut cabinets  ·  quartz")
hub_row("WATER HEATER", "2018  ·  Rheem 50 gal", "Replace window: 2026-2028")
hub_row("ELECTRICAL", "200A panel  ·  2017", "GFCI throughout")
hub_row("PAINT, DEN", "BM Hale Navy HC-154", "Eggshell  ·  2 coats  ·  2024", highlight=True)

# Ask bar at bottom of phone
ask_h = 30
ask_y = sy + 14
c.setFillColor(NAVY)
c.roundRect(sx + 8, ask_y, sw - 16, ask_h, 14, fill=1, stroke=1)
c.setStrokeColor(GOLD)
c.setLineWidth(0.6)
c.roundRect(sx + 8, ask_y, sw - 16, ask_h, 14, fill=0, stroke=1)
c.setFillColor(CREAM_70)
c.setFont(BODY, 8)
c.drawString(sx + 18, ask_y + 11, "Ask the Hub about your home...")
# little send dot
c.setFillColor(GOLD)
c.circle(sx + sw - 22, ask_y + ask_h / 2, 6, fill=1, stroke=0)

# Caption under phone
cap_y = phone_y - 14
c.setFillColor(CREAM_55)
c.setFont(MONO, 7.5)
c.drawCentredString(phone_x + phone_w / 2, cap_y, "YOUR HUB  ·  ILLUSTRATIVE")

# Footer
c.setFillColor(CREAM_55)
c.setFont(MONO, 7.5)
c.drawString(MARGIN, MARGIN - 4, "hometownbuildersclub.com")
c.drawRightString(PAGE_W - MARGIN, MARGIN - 4, "(330) 203-1331  ·  adam@hometownbuildersclub.com")

c.showPage()

# =========================================================
# PAGE 4 — HOW IT WORKS + CTA
# =========================================================
c.setFillColor(CREAM)
c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

# Top label band
c.setFillColor(NAVY)
c.rect(0, PAGE_H - 0.5 * 72, PAGE_W, 0.5 * 72, fill=1, stroke=0)
c.setFillColor(CREAM)
c.setFont(MONO_SEMI, 8.5)
cur = MARGIN
for ch in "HOMETOWN BUILDERS CLUB   ·   THE HOME CLARITY REPORT":
    c.drawString(cur, PAGE_H - 0.32 * 72, ch)
    cur += pdfmetrics.stringWidth(ch, MONO_SEMI, 8.5) + 1.0
c.setFillColor(GOLD)
c.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.32 * 72, "PAGE 04")

# Eyebrow + H1
top_y = PAGE_H - 0.5 * 72 - 0.5 * 72
eyebrow(c, "How it works", MARGIN, top_y)
hairline(c, MARGIN, top_y - 8, MARGIN + 1.6 * 72)

c.setFillColor(NAVY)
c.setFont(DISPLAY_BOLD, 30)
c.drawString(MARGIN, top_y - 0.5 * 72, "From first call to a full plan in 5 business days.")

c.setFillColor(NAVY_72)
c.setFont(DISPLAY_ITALIC, 13)
c.drawString(MARGIN, top_y - 0.5 * 72 - 20,
             "One process. One team. One number to call for as long as you own the house.")

# 4 step cards in a 2x2 grid
steps = [
    ("01", "Discovery call (20 min).",
     "Tell us about your home, your goals, what's keeping you up at night."),
    ("02", "On-site assessment.",
     "Adam and the HBC team spend a full day documenting your home, top to bottom."),
    ("03", "Report delivery.",
     "Within 5 business days, we hand you the floor plans, scope, budgets, and your Home Clarity Hub."),
    ("04", "Forever after.",
     "One call, anytime, for any question about your house. We're your home advisor for as long as you own it."),
]

grid_top = top_y - 0.5 * 72 - 50
grid_bottom = MARGIN + 2.4 * 72  # leave room for CTA strip + footer
grid_h = grid_top - grid_bottom
gap = 14
card_w = (PAGE_W - 2 * MARGIN - gap) / 2
card_h = (grid_h - gap) / 2

positions = [
    (MARGIN,                grid_top - card_h),
    (MARGIN + card_w + gap, grid_top - card_h),
    (MARGIN,                grid_top - 2 * card_h - gap),
    (MARGIN + card_w + gap, grid_top - 2 * card_h - gap),
]

for (num, head, body), (cx_, cy_) in zip(steps, positions):
    # card background
    c.setFillColor(WHITE)
    c.roundRect(cx_, cy_, card_w, card_h, 8, fill=1, stroke=0)
    # gold left rail
    c.setFillColor(GOLD)
    c.rect(cx_, cy_, 4, card_h, fill=1, stroke=0)
    # number
    c.setFillColor(GOLD)
    c.setFont(MONO_SEMI, 10)
    c.drawString(cx_ + 18, cy_ + card_h - 22, num)
    # gold short rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(cx_ + 38, cy_ + card_h - 19, cx_ + 60, cy_ + card_h - 19)
    # heading
    c.setFillColor(NAVY)
    c.setFont(DISPLAY_BOLD, 18)
    c.drawString(cx_ + 18, cy_ + card_h - 44, head)
    # body
    draw_wrapped(c, body, cx_ + 18, cy_ + card_h - 64,
                 card_w - 36, BODY, 10, 14.5, NAVY_72)

# CTA strip
cta_h = 1.3 * 72
cta_y = MARGIN + 0.55 * 72
c.setFillColor(NAVY)
c.roundRect(MARGIN, cta_y, PAGE_W - 2 * MARGIN, cta_h, 10, fill=1, stroke=0)

# Eyebrow inside CTA
c.setFillColor(GOLD)
c.setFont(MONO_SEMI, 9)
cur = MARGIN + 22
for ch in "NEXT STEP":
    c.drawString(cur, cta_y + cta_h - 22, ch)
    cur += pdfmetrics.stringWidth(ch, MONO_SEMI, 9) + 1.3
c.setStrokeColor(GOLD)
c.setLineWidth(0.7)
c.line(MARGIN + 22, cta_y + cta_h - 30, MARGIN + 22 + 0.9 * 72, cta_y + cta_h - 30)

# Big CTA headline
c.setFillColor(CREAM)
c.setFont(DISPLAY_BOLD, 26)
c.drawString(MARGIN + 22, cta_y + cta_h - 56, "Book your discovery call.")

# contact lines
c.setFillColor(CREAM)
c.setFont(MONO_SEMI, 11)
c.drawString(MARGIN + 22, cta_y + 24, "(330) 203-1331")
c.setFillColor(CREAM_70)
c.setFont(BODY, 10.5)
c.drawString(MARGIN + 22 + 1.5 * 72, cta_y + 24, "adam@hometownbuildersclub.com")

# Right side mini panel: price + days
right_block_x = PAGE_W - MARGIN - 1.95 * 72
c.setStrokeColor(GOLD_30)
c.setLineWidth(0.6)
c.line(right_block_x - 14, cta_y + 16, right_block_x - 14, cta_y + cta_h - 16)

c.setFillColor(GOLD)
c.setFont(DISPLAY_BOLD, 26)
c.drawString(right_block_x, cta_y + cta_h - 40, "$4,500")
c.setFillColor(CREAM_70)
c.setFont(MONO, 7.5)
c.drawString(right_block_x, cta_y + cta_h - 54, "FLAT FEE  ·  ALL IN")
c.setFillColor(CREAM)
c.setFont(BODY_SEMI, 10.5)
c.drawString(right_block_x, cta_y + 32, "5 business days")
c.setFillColor(CREAM_70)
c.setFont(BODY, 9)
c.drawString(right_block_x, cta_y + 18, "from on-site to delivery")

# Footer (mono small) — auto-fit by shrinking until it fits inside margins
footer_y = MARGIN + 0.05 * 72
c.setFillColor(NAVY_72)
foot = ("Ohio GC License #GRB130313   ·   EPA Lead Safe Certified Renovator "
        "#R-I-22516-00004   ·   Cuyahoga Falls, OH   ·   © 2026 Hometown Builders Club")
foot_size = 6.6
while pdfmetrics.stringWidth(foot, MONO, foot_size) > PAGE_W - 2 * MARGIN and foot_size > 5.0:
    foot_size -= 0.1
c.setFont(MONO, foot_size)
c.drawCentredString(PAGE_W / 2, footer_y, foot)

c.showPage()
c.save()
print(f"WROTE: {OUT}")
