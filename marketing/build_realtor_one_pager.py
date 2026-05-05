"""
HBC Realtor Partnership One-Pager.

Fonts (downloaded TTFs at /tmp/fonts/):
  - Cormorant Garamond (Regular, SemiBold, Bold) — display headlines
  - Inter (Regular, Medium, SemiBold, Bold) — body
  - IBM Plex Mono (Regular, Bold) — eyebrows, mono accents

Voice spec compliance:
  - No em dashes (only commas/periods)
  - No banned words: luxury, high-end, delve, leverage, robust,
    seamlessly, moreover, furthermore, navigate
  - No "AI" mention; uses "knows your house", "operating system for your house"
  - Plural team voice ("we", "our team", "the HBC team")

Brand colors: Navy #0A1628, Gold #B87333, Cream #EDE9E1, White #FFFFFF.
"""

from io import BytesIO

import qrcode
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ----- Tokens ---------------------------------------------------------------

NAVY = HexColor("#0A1628")
NAVY_DARK = HexColor("#060e1c")
GOLD = HexColor("#B87333")
CREAM = HexColor("#EDE9E1")
CREAM_DARK = HexColor("#E2DDD4")
WHITE = HexColor("#FFFFFF")
BODY = Color(10/255, 22/255, 40/255, alpha=0.78)
BODY_MUTED = Color(10/255, 22/255, 40/255, alpha=0.62)

PAGE_W, PAGE_H = letter  # 612 x 792
MARGIN = 0.5 * 72  # 36pt

# ----- Fonts ----------------------------------------------------------------

FONT_DIR = "/tmp/fonts"
pdfmetrics.registerFont(TTFont("Cormorant",       f"{FONT_DIR}/CormorantGaramond-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Cormorant-SB",    f"{FONT_DIR}/CormorantGaramond-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Cormorant-Bold",  f"{FONT_DIR}/CormorantGaramond-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Inter",           f"{FONT_DIR}/Inter-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Med",       f"{FONT_DIR}/Inter-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Inter-SB",        f"{FONT_DIR}/Inter-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Bold",      f"{FONT_DIR}/Inter-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono",            f"{FONT_DIR}/IBMPlexMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Bold",       f"{FONT_DIR}/IBMPlexMono-Bold.ttf"))

# ----- Helpers --------------------------------------------------------------

def wrap(text, font, size, max_width):
    """Greedy word wrap returning list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(test, font, size) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(c, text, x, y, font, size, max_width, leading=None,
                 color=BODY, align="left"):
    """Draws wrapped text top-down. Returns y after last line."""
    if leading is None:
        leading = size * 1.35
    c.setFillColor(color)
    c.setFont(font, size)
    lines = wrap(text, font, size, max_width)
    cur_y = y
    for line in lines:
        if align == "left":
            c.drawString(x, cur_y, line)
        elif align == "center":
            c.drawCentredString(x, cur_y, line)
        elif align == "right":
            c.drawRightString(x, cur_y, line)
        cur_y -= leading
    return cur_y + leading  # baseline of last drawn line


def draw_eyebrow(c, text, x, y, color=GOLD, size=8.5, font="Mono-Bold", tracking=1.8):
    """Small uppercase tracked eyebrow text using a text object.

    Important: ReportLab's text-state Tc (character spacing) persists across
    text objects within a page. We must reset it to 0 before ending so it
    doesn't bleed into later body text.
    """
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(tracking)
    t.textOut(text.upper())
    t.setCharSpace(0)  # reset so subsequent text on the page is normal
    c.drawText(t)


def make_qr_image(url):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


# ----- Page 1 ---------------------------------------------------------------

def draw_header(c):
    """Top navy bar with HBC wordmark and tagline."""
    bar_h = 70
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
    # Gold thin line under bar
    c.setFillColor(GOLD)
    c.rect(0, PAGE_H - bar_h - 3, PAGE_W, 3, fill=1, stroke=0)

    # Logo image (navy variant: white type on navy background)
    try:
        logo = ImageReader("/home/user/workspace/hbc-website/assets/hbc-logo-horizontal-navy.png")
        logo_h = 40
        logo_w = logo_h * (2048/408)
        c.drawImage(logo,
                    MARGIN, PAGE_H - bar_h + (bar_h - logo_h)/2,
                    width=logo_w, height=logo_h,
                    mask='auto')
    except Exception:
        c.setFillColor(GOLD)
        c.setFont("Mono-Bold", 13)
        c.drawString(MARGIN, PAGE_H - bar_h/2 - 4, "HOMETOWN BUILDERS CLUB")

    # Tagline right-aligned
    c.setFillColor(CREAM)
    c.setFont("Inter", 9.5)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h/2 + 4,
                      "Find HBC first.")
    c.setFillColor(CREAM_DARK)
    c.setFont("Inter", 9.5)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h/2 - 8,
                      "Before you hire anyone.")


def draw_page1(c):
    draw_header(c)
    bar_h = 70
    content_top = PAGE_H - bar_h - 3
    content_w = PAGE_W - 2 * MARGIN

    # Eyebrow
    eb_y = content_top - 36
    draw_eyebrow(c, "Realtor partnership program", MARGIN, eb_y, tracking=2.0)

    # Hero headline (Cormorant Bold ~32pt)
    hero_text = "We make you the hero to your past clients."
    headline_size = 30
    headline_lead = headline_size * 1.08
    hero_y = eb_y - 30
    end_y = draw_wrapped(c, hero_text, MARGIN, hero_y,
                         "Cormorant-Bold", headline_size, content_w,
                         leading=headline_lead, color=NAVY)

    # Subhead (Inter)
    sub_text = ("When a homeowner you closed a deal with calls you six "
                "months later about a roof leak, an HVAC issue, or a "
                "kitchen they want to gut, you have one number to give "
                "them. Ours.")
    sub_y = end_y - 22
    end_y = draw_wrapped(c, sub_text, MARGIN, sub_y,
                         "Inter", 11.5, content_w,
                         leading=16, color=BODY)

    # Three benefit cards
    cards = [
        {
            "title": "The stamp travels with the house.",
            "body": ("Two stamps, Hometown Builders Club and Home "
                     "Clarity Report, appear in listings, lift home "
                     "value, and give buyers a documented reason to "
                     "pick that house."),
        },
        {
            "title": "You stay the hero forever.",
            "body": ("Even if the homeowner never buys a Report, we "
                     "still help. The realtor wins the relationship. "
                     "We become your one tool for every question your "
                     "past clients have about their house."),
        },
        {
            "title": "Either door, both win.",
            "body": ("If your client comes to us, you stay in the "
                     "loop. If a homeowner finds us first without a "
                     "realtor, we send them to a partner from our "
                     "trusted list. We never recommend another "
                     "realtor to a homeowner who already has one."),
        },
    ]

    cards_top = end_y - 36
    gutter = 14
    card_w = (content_w - 2 * gutter) / 3
    card_h = 230  # taller to allow for body breathing
    card_y = cards_top - card_h

    for i, card in enumerate(cards):
        cx = MARGIN + i * (card_w + gutter)
        # Card background (cream)
        c.setFillColor(CREAM)
        c.rect(cx, card_y, card_w, card_h, fill=1, stroke=0)
        # Gold top border
        c.setFillColor(GOLD)
        c.rect(cx, card_y + card_h - 3, card_w, 3, fill=1, stroke=0)
        # Number eyebrow
        draw_eyebrow(c, f"0{i+1}", cx + 14, card_y + card_h - 22, size=9, tracking=1.6)
        # Title (Cormorant SemiBold)
        title_y = card_y + card_h - 44
        title_lines = wrap(card["title"], "Cormorant-Bold", 17, card_w - 28)
        c.setFillColor(NAVY)
        c.setFont("Cormorant-Bold", 17)
        for line in title_lines:
            c.drawString(cx + 14, title_y, line)
            title_y -= 19
        # Body
        body_y = title_y - 10
        draw_wrapped(c, card["body"], cx + 14, body_y,
                     "Inter", 9.5, card_w - 28,
                     leading=14, color=BODY)

    # Footer-ish quote band (Adam's North Star, in cream)
    quote_y = card_y - 30
    c.setFillColor(NAVY)
    c.setFont("Cormorant-SB", 13)
    quote = ("\u201CFind HBC first. Before you hire a realtor, a "
             "general contractor, an architect, a designer, anyone.\u201D")
    qlines = wrap(quote, "Cormorant-SB", 13, content_w - 80)
    qy = quote_y
    for line in qlines:
        c.drawCentredString(PAGE_W/2, qy, line)
        qy -= 17
    c.setFillColor(BODY_MUTED)
    c.setFont("Mono", 8.5)
    c.drawCentredString(PAGE_W/2, qy - 6, "Adam Kilgore, founder")

    # Page number / mini footer
    c.setFillColor(BODY_MUTED)
    c.setFont("Mono", 7.5)
    c.drawString(MARGIN, MARGIN/2,
                 "hometownbuildersclub.com  ·  (330) 203-1331")
    c.drawRightString(PAGE_W - MARGIN, MARGIN/2, "1 / 2")


# ----- Page 2 ---------------------------------------------------------------

def draw_check(c, x, y, size=7, color=GOLD):
    """Draw a small filled check-disc with white check."""
    c.setFillColor(color)
    c.circle(x, y, size, fill=1, stroke=0)
    c.setStrokeColor(WHITE)
    c.setLineWidth(1.4)
    c.setLineCap(1)
    c.line(x - size*0.45, y - size*0.05,
           x - size*0.10, y - size*0.40)
    c.line(x - size*0.10, y - size*0.40,
           x + size*0.50, y + size*0.35)


def draw_page2(c):
    draw_header(c)
    bar_h = 70
    content_top = PAGE_H - bar_h - 3
    content_w = PAGE_W - 2 * MARGIN

    # Section eyebrow
    draw_eyebrow(c, "What your client gets", MARGIN, content_top - 36, tracking=2.0)

    # Section H2
    c.setFillColor(NAVY)
    c.setFont("Cormorant-Bold", 24)
    c.drawString(MARGIN, content_top - 64,
                 "Inside a Home Clarity Report.")

    # Two-column checklist
    items = [
        "5-business-day expert assessment of the home, conducted by Adam Kilgore personally.",
        "Interior floor plans accurate to 1/8 inch, every level.",
        "Full exterior 3D model with measurements (roof, siding, windows).",
        "360\u00b0 photography of every room and mechanical space.",
        "Written project scope and Summit County budget ranges for every priority area.",
        "Vetted trade network already briefed on the home, plus a lifetime advisor relationship.",
    ]
    list_top = content_top - 84
    col_gap = 24
    col_w = (content_w - col_gap) / 2
    line_height = 38

    for i, item in enumerate(items):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (col_w + col_gap)
        y = list_top - row * line_height
        draw_check(c, x + 7, y - 4, size=7, color=GOLD)
        draw_wrapped(c, item, x + 22, y - 1,
                     "Inter", 9.5, col_w - 22,
                     leading=13.5, color=BODY)

    # ---- Hub callout box ----
    callout_top = list_top - 3 * line_height + 4
    callout_h = 175
    callout_y = callout_top - callout_h - 14

    c.setFillColor(CREAM)
    c.rect(MARGIN, callout_y, content_w, callout_h, fill=1, stroke=0)
    # Gold left border
    c.setFillColor(GOLD)
    c.rect(MARGIN, callout_y, 4, callout_h, fill=1, stroke=0)

    pad = 18
    cy = callout_y + callout_h - pad - 4
    draw_eyebrow(c, "What lives in their Home Clarity Hub",
                 MARGIN + pad + 4, cy, tracking=2.0)

    cy -= 22
    c.setFillColor(NAVY)
    c.setFont("Cormorant-Bold", 18)
    c.drawString(MARGIN + pad + 4, cy, "An operating system for the house.")

    bullets = [
        ("Their house, on call. Forever.",
         "The Hub lives on any phone, any time. Every detail of their home is in there."),
        ("A second opinion before they say yes to anyone.",
         "Ask the Hub. It knows their house, every measurement, every system, every material we documented."),
        ("Built only on their home.",
         "An operating system for the house, not generic remodeling advice."),
    ]
    cy -= 18
    bullet_x = MARGIN + pad + 4
    avail_w = content_w - pad * 2 - 4
    for title, body in bullets:
        # gold dot
        c.setFillColor(GOLD)
        c.circle(bullet_x + 3, cy - 3, 2.2, fill=1, stroke=0)
        # title bold
        c.setFillColor(NAVY)
        c.setFont("Inter-SB", 9.5)
        c.drawString(bullet_x + 12, cy - 5, title)
        title_w = pdfmetrics.stringWidth(title, "Inter-SB", 9.5)
        # body inline
        c.setFillColor(BODY)
        c.setFont("Inter", 9.5)
        body_x = bullet_x + 12 + title_w + 6
        body_lines = wrap(body, "Inter", 9.5, avail_w - (body_x - bullet_x))
        if body_lines:
            c.drawString(body_x, cy - 5, body_lines[0])
            for extra in body_lines[1:]:
                cy -= 13
                c.drawString(bullet_x + 12, cy - 5, extra)
        cy -= 18

    # ---- Meet the team ----
    team_top = callout_y - 28
    draw_eyebrow(c, "Meet the team behind HBC", MARGIN, team_top, tracking=2.0)

    c.setFillColor(NAVY)
    c.setFont("Cormorant-Bold", 22)
    c.drawString(MARGIN, team_top - 26, "27 years. About 400 homes.")

    bio = ("Adam Kilgore founded Hometown Builders Club after 27 years "
           "remodeling, building, and rebuilding about 400 homes in "
           "Summit County. The HBC team brings the same craftsmanship "
           "and the same answer-every-call standard to every homeowner "
           "they work with.")
    draw_wrapped(c, bio, MARGIN, team_top - 50,
                 "Inter", 10.5, content_w - 30,
                 leading=15.5, color=BODY)

    # ---- Bottom CTA strip ----
    cta_h = 110
    cta_y = MARGIN + 16  # leave room for footer line
    c.setFillColor(NAVY)
    c.rect(0, cta_y, PAGE_W, cta_h, fill=1, stroke=0)
    # Gold thin top border
    c.setFillColor(GOLD)
    c.rect(0, cta_y + cta_h, PAGE_W, 2, fill=1, stroke=0)

    # Layout: left column "Refer your first client", middle "Become a partner", right QR
    inner_pad = MARGIN
    qr_size = 70
    qr_x = PAGE_W - inner_pad - qr_size
    qr_y = cta_y + (cta_h - qr_size) / 2

    # QR
    try:
        qr_img = make_qr_image("https://www.hometownbuildersclub.com/for-realtors")
        # White backing
        c.setFillColor(WHITE)
        c.rect(qr_x - 6, qr_y - 6, qr_size + 12, qr_size + 12, fill=1, stroke=0)
        c.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size)
    except Exception:
        c.setStrokeColor(WHITE); c.setFillColor(WHITE)
        c.rect(qr_x, qr_y, qr_size, qr_size, fill=0, stroke=1)
        c.setFillColor(WHITE); c.setFont("Mono", 7)
        c.drawCentredString(qr_x + qr_size/2, qr_y + qr_size/2,
                            "Scan to learn more")
    # QR caption
    c.setFillColor(CREAM_DARK)
    c.setFont("Mono", 7)
    c.drawCentredString(qr_x + qr_size/2, qr_y - 12, "for-realtors")

    # Two CTA blocks (split remaining width)
    cta_block_w = (qr_x - 18 - inner_pad) / 2
    block_x1 = inner_pad
    block_x2 = inner_pad + cta_block_w + 14

    # Block 1
    draw_eyebrow(c, "Refer your first client",
                 block_x1, cta_y + cta_h - 26, tracking=1.8)
    c.setFillColor(WHITE)
    c.setFont("Cormorant-Bold", 16)
    c.drawString(block_x1, cta_y + cta_h - 50, "Email Adam directly.")
    c.setFillColor(CREAM)
    c.setFont("Mono", 10)
    email = "adam@hometownbuildersclub.com"
    c.drawString(block_x1, cta_y + cta_h - 70, email)
    c.linkURL(f"mailto:{email}",
              (block_x1, cta_y + cta_h - 76, block_x1 + 200, cta_y + cta_h - 60),
              relative=0)

    # Block 2
    draw_eyebrow(c, "Become an HBC realtor partner",
                 block_x2, cta_y + cta_h - 26, tracking=1.8)
    c.setFillColor(WHITE)
    c.setFont("Cormorant-Bold", 16)
    c.drawString(block_x2, cta_y + cta_h - 50, "Book a 20-minute call.")
    c.setFillColor(CREAM)
    c.setFont("Mono", 10)
    phone = "(330) 203-1331"
    c.drawString(block_x2, cta_y + cta_h - 70, phone)

    # Footer line
    c.setFillColor(BODY_MUTED)
    c.setFont("Mono", 7)
    footer = ("Ohio GC License #GRB130313  ·  EPA Lead Safe Certified "
              "Renovator #R-I-22516-00004  ·  Cuyahoga Falls, OH  ·  "
              "\u00a9 2026 Hometown Builders Club")
    c.drawCentredString(PAGE_W/2, MARGIN/2 - 2, footer)

    # Page indicator
    c.setFillColor(BODY_MUTED)
    c.setFont("Mono", 7.5)
    c.drawRightString(PAGE_W - MARGIN, MARGIN/2 + 8, "2 / 2")


# ----- Build ----------------------------------------------------------------

def build(out_path):
    c = canvas.Canvas(out_path, pagesize=letter)
    c.setTitle("HBC Realtor Partnership One-Pager")
    c.setAuthor("Perplexity Computer")
    c.setSubject("Hometown Builders Club Realtor Partnership leave-behind")

    draw_page1(c)
    c.showPage()
    draw_page2(c)
    c.showPage()
    c.save()


if __name__ == "__main__":
    build("/home/user/workspace/hbc-website/marketing/realtor-one-pager.pdf")
    print("OK")
