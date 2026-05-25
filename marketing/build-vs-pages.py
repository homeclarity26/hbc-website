#!/usr/bin/env python3
"""
Build /vs-design-build.html and /vs-general-contractor.html using vs-angi.html as a structural template.
Reads vs-angi.html, swaps content via tokenized replacement, writes new files.
Idempotent: re-running overwrites.
"""
from pathlib import Path
import json

ROOT = Path("/home/user/workspace/hbc-website")

# =====================================================================
# Page configurations
# =====================================================================
PAGES = {
    "vs-design-build": {
        "title": "HBC vs. Design-Build Firm: A Different Way to Plan a Remodel in Summit County | Hometown Builders Club",
        "description": "The honest comparison between Hometown Builders Club and a design-build remodeling firm for Summit County, Ohio homeowners planning a kitchen, bathroom, or first-floor renovation.",
        "url_slug": "vs-design-build",
        "competitor": "Design-Build Firm",
        "competitor_short": "Design-Build",
        "competitor_id": "design-build",
        "service_name": "HBC vs Design-Build Firm. Independent Advisor Alternative",
        "service_type": "Independent Home Advisor",
        "service_category": "Alternative to Design-Build Single-Contract Model",
        "service_description": "Why Hometown Builders Club is a stronger first step than a design-build firm for Summit County homeowners. Independent scope and budget before a single firm controls both the design and the construction contract.",
        "audience": "Summit County homeowners considering a design-build firm",
        "h1": "Two different ways to plan a kitchen, bath, or first-floor remodel.",
        "lead_answer_question": "How is Hometown Builders Club different from a design-build firm?",
        "lead_answer": "A design-build firm packages design and construction into one contract you sign with one company. Hometown Builders Club is the step before that. HBC documents your home, writes a scope, and gives you real Summit County pricing so you can hire the right design-build firm, the right general contractor, or no one at all. You stay in control of the budget before any firm owns both halves of the project.",
        "intro": "Both Hometown Builders Club and design-build firms are valid paths for a serious remodel. They serve different moments in the planning process. Here is the honest comparison so you can decide which one fits where you are right now.",
        "table_rows": [
            ("What you sign first", "A flat-fee Home Clarity Report engagement ($4,500)", "A combined design-and-build contract that typically commits 12 to 18 percent of project cost upfront"),
            ("Who owns the design", "You. Floor plans accurate to one-eighth inch are yours to keep, forever.", "The design-build firm, until you sign the construction contract"),
            ("Who builds the project", "A separately contracted trade partner Adam introduces", "The same firm that designed it"),
            ("Independence of the scope", "Independent. HBC has no financial interest in selling you any specific project.", "The firm writing the scope is also the firm bidding the construction"),
            ("Budget transparency", "Written 2026 Summit County pricing per project, before any contractor is selected", "Allowance-driven design until the construction contract is signed"),
            ("Lock-in risk", "Low. The Report is portable. You can walk away with your plans.", "High. Walking away after design typically forfeits the design retainer."),
            ("Best when you have", "Multiple projects, an undefined scope, or want to compare options first", "A single, well-defined project and you want one firm to handle both halves"),
            ("Long-term home documentation", "Yes. 3D scan, equipment registry, and Home OS dashboard for 20 years", "No. Documentation ends at project closeout."),
        ],
        "where_fine_title": "Where design-build firms work well",
        "where_fine_body": [
            "Design-build is a strong model for a single, clearly scoped project when you already know what you want and you value having one point of accountability for both halves. A whole-house renovation that has been sketched out, an addition with a defined footprint, a kitchen where the layout is already final. These are good fits.",
            "If you have an architect's drawings in hand or a clear written scope you can hand to multiple firms, a design-build firm can deliver a polished result without you managing two contracts.",
        ],
        "where_short_title": "Where design-build falls short before you have a plan",
        "where_short_body_intro": "The model gets expensive when you sign before you know what the project actually is.",
        "where_short_body_bullets": [
            ("Scope drift inside one contract.", "When the same firm designs and builds, the scope can grow without a competing bid keeping it honest. Change orders during the design phase are common."),
            ("Design fees that lock you in.", "Most design-build firms charge 8 to 15 percent of estimated project cost as a design retainer. Walking away means you lose that money and your drawings."),
            ("No independent budget reality check.", "The design is built around the firm's own construction pricing. You learn the real number after you have already committed."),
            ("One vendor for two very different jobs.", "Designing a renovation and building a renovation are different skills. Some firms are excellent at one and competent at the other."),
        ],
        "where_short_outro": "For a deeper look at how the pricing model works, read our take on <a href=\"/concierge\">independent advisory</a> or <a href=\"/how-it-works\">how HBC documents a home before any contractor is selected</a>.",
        "what_hbc_does_intro": "The Home Clarity Report is a $4,500 product. Adam scans your home in 3D, walks every system, and produces a written assessment with realistic Summit County 2026 pricing for every project you are considering. The Report includes:",
        "what_hbc_does_bullets": [
            "A complete written scope of work for your specific kitchen, bathroom, or first-floor project",
            "Real local pricing tied to actual recent jobs in Hudson, Bath, Fairlawn, Richfield, and Montrose",
            "Floor plans accurate to one-eighth inch, yours to keep whether you hire HBC, a design-build firm, or no one",
            "A 3D scan and digital twin of your home that lives in your Home OS for 20 years",
            "Adam's direct cell number for questions long after the Report is delivered",
        ],
        "what_hbc_does_close": "If you decide a design-build firm is the right next step, hand them the Report. You walk in with documentation they would normally charge $5,000 to produce, and the firm starts from a clear scope instead of a discovery process.",
        "related_cards": [
            ("How HBC works, step by step", "/how-it-works"),
            ("What the Home Clarity Report includes", "/services"),
            ("Why Summit County renovations are different", "/areas-served"),
            ("HBC concierge membership", "/concierge"),
        ],
        "faq_pairs": [
            ("Is HBC a design-build firm?", "No. HBC is a home advisory service. We write the scope, pricing, and documentation. The actual construction is performed by a separately contracted trade partner we introduce after the Report is delivered."),
            ("Can I use my HBC Report with a design-build firm I already like?", "Yes. The scope, pricing, and 3D scan are yours. Most homeowners who use a design-build firm after the Report find the design phase is faster because the firm starts with documentation already in hand."),
            ("What is the cost difference between HBC and a design-build firm's design phase?", "HBC's Home Clarity Report is a flat $4,500. A design-build design retainer is typically 8 to 15 percent of estimated construction cost, which on a $100,000 project lands between $8,000 and $15,000."),
            ("Do I have to use HBC's trade partner if I commission the Report?", "No. The Report is portable. You can take it to any contractor or design-build firm in Summit County."),
            ("When should I pick a design-build firm over HBC?", "When the project is a single, well-defined renovation, you already know exactly what you want, and you specifically value having one company sign both contracts. HBC is the better starting point when scope is undefined, budgets are uncertain, or you want to compare paths before committing."),
        ],
    },
    "vs-general-contractor": {
        "title": "HBC vs. General Contractor: How to Plan a Remodel Before You Hire | Hometown Builders Club",
        "description": "The honest comparison between Hometown Builders Club and hiring a general contractor directly in Summit County, Ohio. Independent scope and budget before any GC bids your job.",
        "url_slug": "vs-general-contractor",
        "competitor": "General Contractor",
        "competitor_short": "General Contractor",
        "competitor_id": "general-contractor",
        "service_name": "HBC vs General Contractor. Independent Pre-Construction Alternative",
        "service_type": "Independent Pre-Construction Advisory",
        "service_category": "Alternative to Hiring a General Contractor First",
        "service_description": "Why Hometown Builders Club is a stronger first step than calling a general contractor directly for Summit County homeowners. Independent scope, independent budget, and apples-to-apples bids when it is time to hire.",
        "audience": "Summit County homeowners about to hire a general contractor",
        "h1": "Two different ways to start a serious remodel.",
        "lead_answer_question": "How is Hometown Builders Club different from a general contractor?",
        "lead_answer": "A general contractor builds the project. Hometown Builders Club plans it. HBC documents your home, writes the scope, sets a realistic Summit County budget, and only then introduces you to a vetted general contractor to build it. The GC starts the day knowing your home and your project. You start the conversation already on equal footing.",
        "intro": "Hiring a general contractor is the right move for almost every remodel. The question is when you do it, and what you hand them when you do. Here is the honest comparison between starting with HBC and starting with a GC.",
        "table_rows": [
            ("Who you talk to first", "Adam Kilgore, 27-year Summit County remodeler, on a free discovery call", "A general contractor who is also the firm bidding your job"),
            ("Independence of the scope", "Independent. HBC has no financial interest in selling you any specific project.", "The GC writes a scope that matches what they want to build"),
            ("Budget transparency before bidding", "Written 2026 Summit County pricing per project, given to you in writing", "Estimate developed during the GC's own bid process"),
            ("Apples-to-apples bids", "Yes. The Report's scope lets multiple GCs bid the identical project.", "No. Each GC writes their own scope, so the three bids you collect rarely describe the same job."),
            ("Floor plans, photos, equipment registry", "Yes. Yours to keep, accurate to one-eighth inch, in your Home OS for 20 years.", "Sometimes, depending on the GC. Often tied to a signed contract."),
            ("What HBC charges", "$4,500 flat fee for the Home Clarity Report", "$0 to talk. The pricing is built into the bid."),
            ("What the GC charges", "Construction cost only. No marketing markup for the lead.", "Construction cost plus the cost of acquiring and converting your lead."),
            ("Best when you have", "Undefined scope, uncertain budget, or want comparable bids", "A clear scope, a known budget, and a contractor you already trust"),
        ],
        "where_fine_title": "Where calling a general contractor first works well",
        "where_fine_body": [
            "If you already have a complete written scope of work, a realistic budget grounded in current Summit County pricing, and a general contractor you have worked with before or who comes from a strong referral, calling that GC directly is reasonable. You skip an intermediate step.",
            "This works for repeat clients of a trusted local builder, projects where the scope is fully defined by an architect, or follow-up work after a previous remodel went well.",
        ],
        "where_short_title": "Where calling a general contractor first costs you money",
        "where_short_body_intro": "The model breaks down when you do not already have a tight scope, a real budget, and a GC you trust.",
        "where_short_body_bullets": [
            ("Three bids that do not describe the same job.", "Each GC writes a scope that matches their own preferences. You get three numbers that are not comparable, and you have no way to know which GC is including what."),
            ("Allowances that hide the real cost.", "A GC bid often includes generic allowances for cabinets, tile, plumbing fixtures, and lighting. The real number lands during selections, and the change order surprises follow."),
            ("Sales conversations disguised as discovery.", "A GC's first visit is a sales call. They have to decide whether to chase your project. You have to decide whether to hire them. The information flow tilts toward the sale, not the planning."),
            ("Pressure to commit before the project is clear.", "Without an independent scope and budget, the only path forward is to sign with one of the GCs you talked to, often before you have actually decided what you want to build."),
        ],
        "where_short_outro": "For a deeper look at why apples-to-apples bidding matters, read <a href=\"/services\">what the Home Clarity Report includes</a> or <a href=\"/how-it-works\">how HBC documents a home before any contractor walks in</a>.",
        "what_hbc_does_intro": "The Home Clarity Report is a $4,500 product. Adam scans your home in 3D, walks every system, and produces a written assessment with realistic Summit County 2026 pricing for every project you are considering. The Report includes:",
        "what_hbc_does_bullets": [
            "A complete written scope of work for your specific kitchen, bathroom, or first-floor project",
            "Real local pricing tied to actual recent jobs in Hudson, Bath, Fairlawn, Richfield, and Montrose",
            "The waterproofing systems, fixture grades, and finish levels appropriate to your home",
            "A 3D scan and digital twin of your home that you keep for 20 years",
            "Adam's direct cell number for the inevitable mid-project question that comes up six months later",
        ],
        "what_hbc_does_close": "When the Report is done, hand it to any general contractor you want, or to one Adam introduces. The scope is comparable, the budget is honest, and the GC starts the job already knowing your home. Clients save an average of $16,100 on their first major project after receiving the Report.",
        "related_cards": [
            ("How HBC works, step by step", "/how-it-works"),
            ("What the Home Clarity Report includes", "/services"),
            ("Meet Adam", "/meet-adam"),
            ("For trade partners and contractors", "/for-trade-partners"),
        ],
        "faq_pairs": [
            ("Is Adam a general contractor?", "Yes. Adam Kilgore holds Ohio General Contractor License GRB130313 and has been remodeling in Summit County since 1999. HBC is structured separately because the advisory work and the construction work serve different jobs to be done."),
            ("Does HBC compete with general contractors?", "No. HBC introduces clients to general contractors. Every Report eventually hands the scope to a GC we have vetted. We compete with the pre-construction process, not the construction itself."),
            ("Can I take my HBC Report to a general contractor I already know?", "Yes. The scope, pricing, and 3D scan are yours. The GC walks in with documentation they would normally spend six to ten unpaid hours producing, and the bid comes back faster and tighter."),
            ("Why pay $4,500 for an HBC Report if a GC will quote me for free?", "Because the GC quote is not free. It is paid for by the projects they win, recovered as markup on the projects they build. HBC's $4,500 fee buys you an independent scope, independent budget, and apples-to-apples bids that frequently save clients more than ten times the Report cost on the first project alone."),
            ("When should I skip HBC and call a GC directly?", "When you already have a complete written scope, a realistic budget grounded in current local pricing, and a specific GC you trust. If any of those three are missing, the Report pays for itself."),
        ],
    },
}

# =====================================================================
# Shared template (head/css/scripts mirrored from vs-angi.html)
# =====================================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index, follow">
  <meta name="author" content="Adam Kilgore">
  <meta name="geo.region" content="US-OH">
  <meta name="geo.placename" content="Summit County, Ohio">
  <link rel="canonical" href="https://www.hometownbuildersclub.com/{slug}">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./brand.css">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 38 38'%3E%3Crect width='38' height='38' rx='9' fill='%230A1628'/%3E%3Cpath d='M8 19.5L19 10L30 19.5' stroke='%23B87333' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3Crect x='11' y='19.5' width='16' height='10.5' rx='1' fill='%23B87333' fill-opacity='0.18' stroke='%23B87333' stroke-width='1.5'/%3E%3Crect x='16.5' y='23.5' width='5' height='6.5' rx='.75' fill='%23B87333'/%3E%3C/svg%3E">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-27C0LKN74Z"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-27C0LKN74Z');</script>
  <script type="application/ld+json">{webpage_schema}</script>
  <meta property="og:image" content="https://www.hometownbuildersclub.com/assets/og-share.jpg">
  <meta property="og:title" content="HBC vs. {competitor_short}">
  <meta property="og:description" content="{description}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://www.hometownbuildersclub.com/assets/og-share.jpg">
  <meta name="twitter:title" content="HBC vs. {competitor_short}">
  <meta name="twitter:description" content="{description}">
  <style>
    .compare-hero {{ background: var(--navy); color: var(--white); padding: 5rem 0 4rem; text-align: center; }}
    .compare-hero h1 {{ font-family: var(--font-display); font-size: clamp(2rem, 4vw, 3rem); font-weight: 600; margin: 0 0 1rem; line-height: 1.15; }}
    .compare-hero .eyebrow {{ font-size: 0.75rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: var(--gold); margin-bottom: 1rem; }}
    .compare-hero p {{ font-size: 1.125rem; color: rgba(255,255,255,0.8); max-width: 640px; margin: 0 auto 2rem; line-height: 1.7; }}
    .compare-table-wrap {{ background: var(--cream); padding: 4rem 0; }}
    .compare-table-wrap h2 {{ font-family: var(--font-display); font-size: 2rem; color: var(--navy); text-align: center; margin: 0 0 2rem; font-weight: 600; }}
    .compare-table {{ width: 100%; max-width: 980px; margin: 0 auto; border-collapse: collapse; background: var(--white); border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(10,22,40,0.08); }}
    .compare-table th, .compare-table td {{ padding: 1.1rem 1.25rem; text-align: left; border-bottom: 1px solid rgba(10,22,40,0.08); font-size: 0.95rem; line-height: 1.6; }}
    .compare-table th {{ background: var(--cream-dark); font-family: var(--font-body); font-weight: 700; color: var(--navy); font-size: 0.8125rem; text-transform: uppercase; letter-spacing: 0.04em; }}
    .compare-table tr td:first-child {{ color: var(--navy); font-weight: 600; width: 28%; }}
    .compare-table tr td:nth-child(2) {{ width: 36%; background: rgba(184,115,51,0.04); color: var(--text-body); }}
    .compare-table tr td:nth-child(3) {{ width: 36%; color: var(--text-body); }}
    .compare-table thead th:nth-child(2) {{ background: var(--gold); color: var(--white); }}
    .compare-section {{ padding: 4rem 0; max-width: 760px; margin: 0 auto; padding-left: 1.5rem; padding-right: 1.5rem; }}
    .compare-section h2 {{ font-family: var(--font-display); font-size: 1.85rem; color: var(--navy); font-weight: 600; margin: 0 0 1.25rem; }}
    .compare-section p {{ font-size: 1.0625rem; line-height: 1.8; color: var(--text-body); margin-bottom: 1.25rem; }}
    .compare-section ul {{ margin: 0 0 1.5rem 1.5rem; }}
    .compare-section li {{ font-size: 1rem; line-height: 1.75; color: var(--text-body); margin-bottom: 0.5rem; }}
    .compare-section strong {{ color: var(--navy); }}
    .compare-section a {{ color: var(--gold); }}
    .compare-cta {{ background: var(--navy); padding: 4rem 0; text-align: center; }}
    .compare-cta h2 {{ font-family: var(--font-display); font-size: clamp(1.75rem, 3vw, 2.5rem); color: var(--white); margin: 0 0 1rem; font-weight: 600; }}
    .compare-cta p {{ color: rgba(255,255,255,0.7); max-width: 540px; margin: 0 auto 1.75rem; line-height: 1.7; font-size: 1rem; }}
    .compare-cta .tel {{ color: rgba(255,255,255,0.55); margin-top: 1rem; font-size: 0.9rem; }}
    .compare-cta .tel a {{ color: var(--gold); font-weight: 600; }}
    .related-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem; max-width: 980px; margin: 2rem auto 0; padding: 0 1.5rem; }}
    .related-card {{ background: var(--cream); padding: 1.5rem; border-radius: 6px; border-left: 3px solid var(--gold); }}
    .related-card h3 {{ font-family: var(--font-body); font-size: 1rem; font-weight: 700; color: var(--navy); margin: 0 0 0.5rem; line-height: 1.35; }}
    .related-card a {{ color: var(--gold); font-size: 0.875rem; font-weight: 600; text-decoration: none; }}
    .faq-block {{ background: var(--white); padding: 4rem 0; }}
    .faq-block .container {{ max-width: 820px; }}
    .faq-block h2 {{ font-family: var(--font-display); font-size: 2rem; color: var(--navy); text-align: center; margin: 0 0 2rem; font-weight: 600; }}
    .faq-item {{ border-bottom: 1px solid rgba(10,22,40,0.08); padding: 1.25rem 0; }}
    .faq-item h3 {{ font-family: var(--font-body); font-size: 1.0625rem; color: var(--navy); margin: 0 0 0.5rem; font-weight: 700; }}
    .faq-item p {{ font-size: 1rem; line-height: 1.7; color: var(--text-body); margin: 0; }}
  </style>
  <script type="application/ld+json">{business_schema}</script>
  <script type="application/ld+json">{service_schema}</script>
  <script type="application/ld+json">{faq_schema}</script>
  <script src="/nav.js" defer></script>
  <script id="schema-ai-website" type="application/ld+json">{ai_website_schema}</script>
</head>
<body>
<a href="#main" class="sr-only">Skip to main content</a>

<header data-nav></header>
<main id="main">

  <section class="compare-hero">
    <div class="container">
      <div class="eyebrow">HBC vs. {competitor_short}</div>
      <h1>{h1}</h1>
      <p class="lead-answer" data-answer-for="{lead_answer_question}">{lead_answer}</p>
      <p>{intro}</p>
      <a href="/contact" class="btn btn-primary btn-lg">Book a Discovery Call</a>
    </div>
  </section>

  <section class="compare-table-wrap">
    <div class="container">
      <h2>Side by side</h2>
      <table class="compare-table">
        <thead>
          <tr>
            <th>What you get</th>
            <th>Hometown Builders Club</th>
            <th>{competitor}</th>
          </tr>
        </thead>
        <tbody>
{table_rows_html}
        </tbody>
      </table>
    </div>
  </section>

  <section class="compare-section">
    <h2>{where_fine_title}</h2>
{where_fine_body_html}
  </section>

  <section class="compare-section">
    <h2>{where_short_title}</h2>
    <p>{where_short_body_intro}</p>
    <ul>
{where_short_bullets_html}
    </ul>
    <p>{where_short_outro}</p>
  </section>

  <section class="compare-section">
    <h2>What HBC does instead</h2>
    <p>{what_hbc_does_intro}</p>
    <ul>
{what_hbc_does_bullets_html}
    </ul>
    <p>{what_hbc_does_close}</p>
  </section>

  <section class="faq-block">
    <div class="container">
      <h2>Frequently asked questions</h2>
{faq_html}
    </div>
  </section>

  <section style="background:var(--cream); padding: 3rem 0;">
    <div class="container">
      <h2 style="font-family:var(--font-display); text-align:center; color:var(--navy); font-size:1.75rem; margin: 0 0 0.5rem;">Related reading</h2>
      <div class="related-grid">
{related_cards_html}
      </div>
    </div>
  </section>

  <section class="compare-cta">
    <div class="container">
      <h2>The right project starts with the right plan.</h2>
      <p>A 30-minute discovery call with Adam is free. We will talk through your project, your timeline, and whether the Home Clarity Report is the right next step.</p>
      <a href="/contact" class="btn btn-primary btn-lg">Book a Discovery Call</a>
      <p class="tel">Or call <a href="tel:+13302031331">(330) 203-1331</a></p>
    </div>
  </section>

</main>

<footer style="background: var(--navy); color: rgba(255,255,255,0.55); padding: 2rem 0; text-align: center; font-size: 0.85rem;">
  <div class="container" itemscope itemtype="https://schema.org/LocalBusiness">
    <p style="margin:0;">&copy; 2026 <span itemprop="name">Hometown Builders Club</span>. <span itemprop="telephone">(330) 203-1331</span> &middot; <a href="/" style="color:rgba(255,255,255,0.75);">Home</a> &middot; <a href="/blog" style="color:rgba(255,255,255,0.75);">Blog</a> &middot; <a href="/faq" style="color:rgba(255,255,255,0.75);">FAQ</a> &middot; <a href="/contact" style="color:rgba(255,255,255,0.75);">Contact</a></p>
  </div>
</footer>

<div class="mobile-cta-bar" id="mobile-cta-bar" role="region" aria-label="Quick actions">
  <div class="mobile-cta-bar__inner">
    <a href="tel:+13302031331" class="mobile-cta-bar__btn mobile-cta-bar__btn--call" aria-label="Call (330) 203-1331">
      <svg class="mobile-cta-bar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
      <span>Call Adam</span>
    </a>
    <a href="/contact" class="mobile-cta-bar__btn mobile-cta-bar__btn--book" aria-label="Book a discovery call">
      <span>Book a Discovery Call</span>
    </a>
  </div>
</div>
<script>
(function(){{var bar=document.getElementById('mobile-cta-bar');if(!bar)return;var threshold=600;var shown=false;function check(){{var y=window.scrollY||window.pageYOffset;if(y>threshold&&!shown){{bar.classList.add('is-visible');document.body.classList.add('has-mobile-cta');shown=true;}}else if(y<=threshold&&shown){{bar.classList.remove('is-visible');document.body.classList.remove('has-mobile-cta');shown=false;}}}}window.addEventListener('scroll',check,{{passive:true}});check();}})();
</script>

</body>
</html>
'''

# Shared schemas
BUSINESS_SCHEMA = {"@context":"https://schema.org","@type":["LocalBusiness","HomeAndConstructionBusiness"],"@id":"https://www.hometownbuildersclub.com/#business","name":"Hometown Builders Club","alternateName":"HBC","url":"https://www.hometownbuildersclub.com","telephone":"+13302031331","email":"adam@hometownbuildersclub.com","foundingDate":"1999","address":{"@type":"PostalAddress","addressLocality":"Cuyahoga Falls","addressRegion":"OH","postalCode":"44223","addressCountry":"US"},"geo":{"@type":"GeoCoordinates","latitude":41.1334,"longitude":-81.4843},"areaServed":{"@type":"AdministrativeArea","name":"Summit County, Ohio"},"serviceArea":{"@type":"GeoCircle","geoMidpoint":{"@type":"GeoCoordinates","latitude":41.1334,"longitude":-81.4843},"geoRadius":"48280","description":"30-mile service radius from Cuyahoga Falls, Ohio. Covers Summit County and adjacent communities in Medina, Portage, southern Cuyahoga, and northern Stark counties."},"hasCredential":[{"@type":"EducationalOccupationalCredential","name":"Ohio General Contractor License","credentialCategory":"license","recognizedBy":{"@type":"Organization","name":"Summit County, Ohio"},"identifier":"GRB130313"},{"@type":"EducationalOccupationalCredential","name":"EPA Lead Safe Certified Renovator","credentialCategory":"certification","recognizedBy":{"@type":"Organization","name":"U.S. Environmental Protection Agency"},"identifier":"R-I-22516-00004"}],"aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","bestRating":"5","worstRating":"1","ratingCount":"3","reviewCount":"3"},"founder":{"@id":"https://www.hometownbuildersclub.com/#adam"},"sameAs":["https://www.homeclarityreport.com","https://akrenovationsohio.com"]}

AI_WEBSITE_SCHEMA = {"@context":"https://schema.org","@graph":[{"@type":"WebSite","@id":"https://www.hometownbuildersclub.com/#website","url":"https://www.hometownbuildersclub.com/","name":"Hometown Builders Club","publisher":{"@id":"https://www.hometownbuildersclub.com/#business"},"potentialAction":[{"@type":"SearchAction","target":{"@type":"EntryPoint","urlTemplate":"https://www.hometownbuildersclub.com/?q={search_term_string}"},"query-input":"required name=search_term_string"},{"@type":"ReserveAction","name":"Book a discovery call","target":{"@type":"EntryPoint","urlTemplate":"https://calendly.com/homeclarityreport/30min","actionPlatform":["https://schema.org/DesktopWebPlatform","https://schema.org/MobileWebPlatform"]},"result":{"@type":"Reservation","name":"30-minute discovery call with Hometown Builders Club","provider":{"@id":"https://www.hometownbuildersclub.com/#business"}}}]},{"@type":"Organization","@id":"https://www.hometownbuildersclub.com/#org-contact","name":"Hometown Builders Club","url":"https://www.hometownbuildersclub.com/","contactPoint":[{"@type":"ContactPoint","contactType":"customer service","telephone":"+13302031331","availableLanguage":["en"],"areaServed":"US-OH","url":"https://www.hometownbuildersclub.com/contact"},{"@type":"ContactPoint","contactType":"reservations","url":"https://calendly.com/homeclarityreport/30min","availableLanguage":["en"]}]}]}

def html_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build_page(slug, cfg):
    url = f"https://www.hometownbuildersclub.com/{slug}"

    # WebPage breadcrumb schema
    webpage_schema = {"@context":"https://schema.org","@type":"WebPage","name":f"HBC vs. {cfg['competitor_short']}","url":url,"breadcrumb":{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://www.hometownbuildersclub.com/"},{"@type":"ListItem","position":2,"name":f"HBC vs. {cfg['competitor_short']}","item":url}]}}

    # Service schema
    service_schema = {"@context":"https://schema.org","@type":"Service","@id":f"{url}#service","name":cfg["service_name"],"serviceType":cfg["service_type"],"category":cfg["service_category"],"url":url,"provider":{"@id":"https://www.hometownbuildersclub.com/#business"},"areaServed":[{"@type":"AdministrativeArea","name":"Summit County, Ohio"},{"@type":"AdministrativeArea","name":"Medina County, Ohio"},{"@type":"AdministrativeArea","name":"Portage County, Ohio"}],"audience":{"@type":"Audience","audienceType":cfg["audience"]},"description":cfg["service_description"]}

    # FAQ schema
    faq_schema = {"@context":"https://schema.org","@type":"FAQPage","@id":f"{url}#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in cfg["faq_pairs"]]}

    # Table rows HTML
    table_rows_html = "\n".join(
        f"          <tr>\n            <td>{html_escape(label)}</td>\n            <td>{html_escape(hbc)}</td>\n            <td>{html_escape(other)}</td>\n          </tr>"
        for label, hbc, other in cfg["table_rows"]
    )

    # Where-fine body
    where_fine_body_html = "\n".join(f"    <p>{html_escape(p)}</p>" for p in cfg["where_fine_body"])

    # Where-short bullets
    where_short_bullets_html = "\n".join(
        f"      <li><strong>{html_escape(strong)}</strong> {html_escape(rest)}</li>"
        for strong, rest in cfg["where_short_body_bullets"]
    )

    # What HBC does bullets
    what_hbc_does_bullets_html = "\n".join(f"      <li>{html_escape(b)}</li>" for b in cfg["what_hbc_does_bullets"])

    # FAQ HTML
    faq_html = "\n".join(
        f'      <div class="faq-item">\n        <h3>{html_escape(q)}</h3>\n        <p>{html_escape(a)}</p>\n      </div>'
        for q, a in cfg["faq_pairs"]
    )

    # Related cards
    related_cards_html = "\n".join(
        f'        <div class="related-card">\n          <h3>{html_escape(title)}</h3>\n          <a href="{href}">Read more &rarr;</a>\n        </div>'
        for title, href in cfg["related_cards"]
    )

    html = HTML_TEMPLATE.format(
        slug=slug,
        title=cfg["title"],
        description=cfg["description"],
        competitor=cfg["competitor"],
        competitor_short=cfg["competitor_short"],
        h1=cfg["h1"],
        lead_answer_question=cfg["lead_answer_question"],
        lead_answer=cfg["lead_answer"],
        intro=cfg["intro"],
        where_fine_title=cfg["where_fine_title"],
        where_fine_body_html=where_fine_body_html,
        where_short_title=cfg["where_short_title"],
        where_short_body_intro=cfg["where_short_body_intro"],
        where_short_bullets_html=where_short_bullets_html,
        where_short_outro=cfg["where_short_outro"],
        what_hbc_does_intro=cfg["what_hbc_does_intro"],
        what_hbc_does_bullets_html=what_hbc_does_bullets_html,
        what_hbc_does_close=cfg["what_hbc_does_close"],
        faq_html=faq_html,
        table_rows_html=table_rows_html,
        related_cards_html=related_cards_html,
        webpage_schema=json.dumps(webpage_schema, separators=(",", ":")),
        business_schema=json.dumps(BUSINESS_SCHEMA, separators=(",", ":")),
        service_schema=json.dumps(service_schema, separators=(",", ":")),
        faq_schema=json.dumps(faq_schema, separators=(",", ":")),
        ai_website_schema=json.dumps(AI_WEBSITE_SCHEMA, separators=(",", ":")),
    )

    out = ROOT / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)} ({len(html):,} bytes)")

def main():
    for slug, cfg in PAGES.items():
        build_page(slug, cfg)

if __name__ == "__main__":
    main()
