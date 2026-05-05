"""Trade Partner One-Pager PDF for Hometown Builders Club."""
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import qrcode

# Brand colors
NAVY = HexColor("#0A1628")
NAVY_DARK = HexColor("#060e1c")
GOLD = HexColor("#B87333")
CREAM = HexColor("#EDE9E1")
CREAM_DARK = HexColor("#E2DDD4")
WHITE = HexColor("#FFFFFF")
BODY = Color(10/255, 22/255, 40/255, alpha=0.78)
MUTED = Color(10/255, 22/255, 40/255, alpha=0.62)

PAGE_W, PAGE_H = letter  # 612 x 792
MARGIN = 0.5 * inch

OUT_PATH = "/home/user/workspace/hbc-website/marketing/trade-partner-one-pager.pdf"

# Use built-in fonts as fallback
SERIF = "Times-Roman"
SERIF_BOLD = "Times-Bold"
SERIF_ITALIC = "Times-Italic"
SANS = "Helvetica"
SANS_BOLD = "Helvetica-Bold"
MONO = "Courier"
MONO_BOLD = "Courier-Bold"


def make_qr_image(url):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0A1628", back_color="#FFFFFF")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def draw_para(c, text, x, y, w, style):
    p = Paragraph(text, style)
    pw, ph = p.wrap(w, 1000)
    p.drawOn(c, x, y - ph)
    return ph  # height drawn


def style_body(font=SANS, size=10, leading=13.5, color=BODY, align=TA_LEFT):
    return ParagraphStyle("body", fontName=font, fontSize=size, leading=leading,
                          textColor=color, alignment=align)


def header_bar(c):
    # Navy bar at top
    bar_h = 0.55 * inch
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
    # Brand name in gold mono uppercase
    c.setFillColor(GOLD)
    c.setFont(MONO_BOLD, 11)
    c.drawString(MARGIN, PAGE_H - bar_h + 0.34 * inch, "HOMETOWN BUILDERS CLUB")
    # Tagline in cream
    c.setFillColor(CREAM)
    c.setFont(MONO, 8.5)
    c.drawString(MARGIN, PAGE_H - bar_h + 0.18 * inch,
                 "TRADE PARTNER NETWORK  ·  SUMMIT COUNTY, OHIO")
    # Right-aligned small mono
    c.setFillColor(CREAM)
    c.setFont(MONO, 8.5)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - bar_h + 0.26 * inch,
                      "(330) 203-1331  ·  hometownbuildersclub.com")


def page_one(c):
    header_bar(c)

    top = PAGE_H - 0.55 * inch  # below header bar
    cursor_y = top - 0.35 * inch

    # Eyebrow
    c.setFillColor(GOLD)
    c.setFont(MONO_BOLD, 9)
    c.drawString(MARGIN, cursor_y, "FOR PARTNER TRADES  ·  PLUMBERS, ELECTRICIANS, HVAC, TILE, CABINETS")
    cursor_y -= 0.32 * inch

    # Hero headline
    headline_style = ParagraphStyle(
        "h1", fontName=SERIF_BOLD, fontSize=30, leading=34,
        textColor=NAVY, alignment=TA_LEFT)
    h = draw_para(
        c,
        "We don\u2019t send you leads.<br/>We send you sold jobs.",
        MARGIN, cursor_y, PAGE_W - 2 * MARGIN, headline_style)
    cursor_y -= h + 0.18 * inch

    # Subhead
    sub_style = ParagraphStyle(
        "sub", fontName=SANS, fontSize=11.5, leading=16,
        textColor=BODY, alignment=TA_LEFT)
    sub_text = ("Pay 15% only when the homeowner signs. No upfront fees. "
                "No subscriptions. No pay-to-play. Here is everything that 15% buys you.")
    h = draw_para(c, sub_text, MARGIN, cursor_y, PAGE_W - 2 * MARGIN, sub_style)
    cursor_y -= h + 0.20 * inch

    # Gold rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(MARGIN, cursor_y, MARGIN + 1.2 * inch, cursor_y)
    cursor_y -= 0.22 * inch

    # 7 numbered bullets
    bullets = [
        ("Sold jobs, not leads.",
         "The homeowner has already decided to do the project. Scope written. Budget approved. They are ready to sign."),
        ("A complete digital briefing before you arrive.",
         "Floor plans accurate to 1/8 inch. 360\u00b0 photos. Full system documentation. Written project scope from a 27-year remodeling expert."),
        ("No competition.",
         "You are the one trade we recommend for that project."),
        ("The pricing is already set. You honor it.",
         "The homeowner has seen and accepted a budget built from your own pricing data. You are not bidding the job. You are delivering it at the number we already quoted. No re-negotiation. No surprises on day one."),
        ("A permanent record of your work.",
         "Every project you complete for an HBC homeowner gets documented in their Home Clarity Hub. Photos, scope, materials, warranty terms, your name."),
        ("Pay only when the job closes.",
         "No upfront fees. No pay-to-play. No monthly subscriptions. 15% of the contract value, billed when the homeowner signs. If a project does not close, you owe nothing."),
        ("A vetted network. Not a free-for-all.",
         "We screen, interview, and reference-check every trade in the network. The homeowner knows that. Your reputation gets a halo from being one of ours."),
    ]

    num_w = 0.55 * inch
    text_x = MARGIN + num_w
    text_w = PAGE_W - 2 * MARGIN - num_w
    head_style = ParagraphStyle("bh", fontName=SANS_BOLD, fontSize=11, leading=14,
                                textColor=NAVY, spaceAfter=2)
    body_style = ParagraphStyle("bb", fontName=SANS, fontSize=9.7, leading=13,
                                textColor=BODY)

    for i, (head, body) in enumerate(bullets, 1):
        # Numeral in gold serif
        c.setFillColor(GOLD)
        c.setFont(SERIF_BOLD, 22)
        c.drawString(MARGIN, cursor_y - 18, f"{i:02d}")

        # Heading
        ph_h = draw_para(c, head, text_x, cursor_y, text_w, head_style)
        # Body
        pb_h = draw_para(c, body, text_x, cursor_y - ph_h - 1, text_w, body_style)
        block_h = max(ph_h + pb_h + 1, 26)
        cursor_y -= block_h + 6

    # Bottom strip on page 1: small note
    cursor_y -= 0.05 * inch
    c.setStrokeColor(CREAM_DARK)
    c.setLineWidth(0.6)
    c.line(MARGIN, cursor_y, PAGE_W - MARGIN, cursor_y)
    cursor_y -= 0.18 * inch
    c.setFillColor(MUTED)
    c.setFont(SANS, 8.5)
    c.drawString(MARGIN, cursor_y, "Built for Summit County trades. 27 years on the ground in Hudson, Bath, Fairlawn, Richfield, Stow, Cuyahoga Falls, and beyond.")
    c.drawRightString(PAGE_W - MARGIN, cursor_y, "Page 1 of 2")


def page_two(c):
    header_bar(c)
    top = PAGE_H - 0.55 * inch
    cursor_y = top - 0.30 * inch

    # Section: Inside the briefing package
    c.setFillColor(GOLD)
    c.setFont(MONO_BOLD, 9)
    c.drawString(MARGIN, cursor_y, "INSIDE THE BRIEFING PACKAGE")
    cursor_y -= 0.10 * inch
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.line(MARGIN, cursor_y, MARGIN + 1.4 * inch, cursor_y)
    cursor_y -= 0.22 * inch

    section_h = ParagraphStyle("sh", fontName=SERIF_BOLD, fontSize=20, leading=24,
                               textColor=NAVY)
    h = draw_para(c, "Every job arrives fully documented.", MARGIN, cursor_y,
                  PAGE_W - 2 * MARGIN, section_h)
    cursor_y -= h + 0.15 * inch

    checks = [
        "Interior floor plans accurate to 1/8 inch, every level",
        "Full exterior 3D model with precise measurements",
        "360\u00b0 photography of every room and mechanical space",
        "Written project scope from a 27-year remodeling expert",
        "Realistic Summit County budget the homeowner has accepted",
        "System ages and condition ratings for every mechanical",
        "The homeowner\u2019s goals, priorities, and timeline",
    ]

    # Two-column checks
    col_w = (PAGE_W - 2 * MARGIN - 0.25 * inch) / 2
    col1_x = MARGIN
    col2_x = MARGIN + col_w + 0.25 * inch
    check_style = ParagraphStyle("ck", fontName=SANS, fontSize=10, leading=13.5,
                                 textColor=BODY, leftIndent=14)
    start_y = cursor_y
    half = (len(checks) + 1) // 2  # 4 in left col, 3 in right
    left_y = start_y
    right_y = start_y
    for i, item in enumerate(checks):
        if i < half:
            x = col1_x
            y = left_y
        else:
            x = col2_x
            y = right_y
        # checkmark
        c.setFillColor(GOLD)
        c.setFont(SANS_BOLD, 11)
        c.drawString(x, y - 11, "\u2713")
        ph = draw_para(c, item, x + 14, y, col_w - 14, check_style)
        if i < half:
            left_y -= max(ph, 14) + 6
        else:
            right_y -= max(ph, 14) + 6
    cursor_y = min(left_y, right_y) - 0.10 * inch

    # Divider
    c.setStrokeColor(CREAM_DARK)
    c.setLineWidth(0.6)
    c.line(MARGIN, cursor_y, PAGE_W - MARGIN, cursor_y)
    cursor_y -= 0.22 * inch

    # How partner trades earn the work
    c.setFillColor(GOLD)
    c.setFont(MONO_BOLD, 9)
    c.drawString(MARGIN, cursor_y, "HOW PARTNER TRADES EARN THE WORK")
    cursor_y -= 0.10 * inch
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.line(MARGIN, cursor_y, MARGIN + 1.4 * inch, cursor_y)
    cursor_y -= 0.30 * inch

    steps = [
        ("01", "Apply", "Ten minute online form."),
        ("02", "20-min call", "Talk it through with Adam and the HBC team."),
        ("03", "Reference check", "Two or three past clients, or trades you have worked with."),
        ("04", "Welcome to the network", "Your first briefing follows."),
    ]
    step_w = (PAGE_W - 2 * MARGIN) / 4
    for i, (num, head, body) in enumerate(steps):
        x = MARGIN + i * step_w
        # Big numeral gold
        c.setFillColor(GOLD)
        c.setFont(SERIF_BOLD, 26)
        c.drawString(x, cursor_y - 22, num)
        # Heading
        c.setFillColor(NAVY)
        c.setFont(SANS_BOLD, 10.5)
        c.drawString(x, cursor_y - 38, head)
        # body, wrapped
        bs = ParagraphStyle("st", fontName=SANS, fontSize=9, leading=12, textColor=BODY)
        draw_para(c, body, x, cursor_y - 42, step_w - 0.15 * inch, bs)
    cursor_y -= 1.05 * inch

    # Cream callout box
    box_h = 1.05 * inch
    c.setFillColor(CREAM)
    c.rect(MARGIN, cursor_y - box_h, PAGE_W - 2 * MARGIN, box_h, fill=1, stroke=0)
    # Gold left bar
    c.setFillColor(GOLD)
    c.rect(MARGIN, cursor_y - box_h, 4, box_h, fill=1, stroke=0)
    # Title
    inner_x = MARGIN + 0.22 * inch
    inner_w = PAGE_W - 2 * MARGIN - 0.40 * inch
    title_style = ParagraphStyle("ct", fontName=SERIF_BOLD, fontSize=14, leading=17,
                                 textColor=NAVY)
    body_style = ParagraphStyle("cb", fontName=SANS, fontSize=9.7, leading=13.2,
                                textColor=BODY)
    ty = cursor_y - 0.18 * inch
    th = draw_para(c, "Your work, documented for life.", inner_x, ty, inner_w, title_style)
    callout_body = ("Every project you complete for an HBC homeowner gets logged in "
                    "their Home Clarity Hub. Photos, scope, materials, warranty, your name. "
                    "When they sell the house in 12 years, your craftsmanship is part of "
                    "what makes it more valuable.")
    draw_para(c, callout_body, inner_x, ty - th - 4, inner_w, body_style)
    cursor_y -= box_h + 0.22 * inch

    # Bottom CTA strip, navy
    cta_h = 1.20 * inch
    c.setFillColor(NAVY)
    c.rect(0, 0.55 * inch, PAGE_W, cta_h, fill=1, stroke=0)

    # CTA contents
    cta_top = 0.55 * inch + cta_h - 0.22 * inch
    c.setFillColor(GOLD)
    c.setFont(MONO_BOLD, 9)
    c.drawString(MARGIN, cta_top, "APPLY FOR TRADE PARTNER MEMBERSHIP")

    c.setFillColor(WHITE)
    c.setFont(SERIF_BOLD, 17)
    c.drawString(MARGIN, cta_top - 0.30 * inch, "Ready to stop chasing leads?")

    c.setFillColor(CREAM)
    c.setFont(SANS, 10)
    c.drawString(MARGIN, cta_top - 0.50 * inch, "Email   ")
    c.setFillColor(WHITE)
    c.setFont(SANS_BOLD, 10)
    c.drawString(MARGIN + 0.42 * inch, cta_top - 0.50 * inch, "adam@hometownbuildersclub.com")

    c.setFillColor(CREAM)
    c.setFont(SANS, 10)
    c.drawString(MARGIN, cta_top - 0.68 * inch, "Call    ")
    c.setFillColor(WHITE)
    c.setFont(SANS_BOLD, 10)
    c.drawString(MARGIN + 0.42 * inch, cta_top - 0.68 * inch, "(330) 203-1331")

    c.setFillColor(CREAM)
    c.setFont(SANS, 10)
    c.drawString(MARGIN, cta_top - 0.86 * inch, "Web     ")
    c.setFillColor(WHITE)
    c.setFont(SANS_BOLD, 10)
    c.drawString(MARGIN + 0.42 * inch, cta_top - 0.86 * inch,
                 "hometownbuildersclub.com/for-trade-partners")

    # QR code on right
    qr_buf = make_qr_image("https://www.hometownbuildersclub.com/for-trade-partners")
    from reportlab.lib.utils import ImageReader
    qr_img = ImageReader(qr_buf)
    qr_size = 0.85 * inch
    qr_x = PAGE_W - MARGIN - qr_size
    qr_y = 0.55 * inch + (cta_h - qr_size) / 2 + 0.06 * inch
    # White card behind QR
    c.setFillColor(WHITE)
    c.rect(qr_x - 5, qr_y - 5, qr_size + 10, qr_size + 10, fill=1, stroke=0)
    c.drawImage(qr_img, qr_x, qr_y, qr_size, qr_size, mask='auto')
    # Label
    c.setFillColor(CREAM)
    c.setFont(MONO_BOLD, 7.2)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 14, "SCAN TO APPLY")

    # Footer line below CTA
    c.setFillColor(NAVY)
    c.setFont(MONO, 7.2)
    footer_y = 0.32 * inch
    c.setFillColor(HexColor("#0A1628"))
    footer_text = ("Ohio GC License #GRB130313  \u00b7  EPA Lead Safe Certified Renovator "
                   "#R-I-22516-00004  \u00b7  Cuyahoga Falls, OH  \u00b7  "
                   "\u00a9 2026 Hometown Builders Club")
    c.drawCentredString(PAGE_W / 2, footer_y, footer_text)


def main():
    c = canvas.Canvas(OUT_PATH, pagesize=letter)
    c.setTitle("Hometown Builders Club Trade Partner One-Pager")
    c.setAuthor("Perplexity Computer")
    c.setSubject("Trade Partner recruiting leave-behind")

    page_one(c)
    c.showPage()
    page_two(c)
    c.showPage()
    c.save()
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
