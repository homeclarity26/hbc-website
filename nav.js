/* =============================================================
   nav.js — Single source of truth for the HBC site header
   and mobile menu.

   Every page renders <header data-nav></header> and this script
   paints the canonical markup into it. The active link is auto-
   detected from window.location.pathname.

   To change the site nav, change THIS FILE and every page
   updates on next deploy. Do NOT hand-edit nav HTML in page files.

   Footers remain page-owned for now (different pages need
   different footer content). A future pass can canonicalize
   those too.
   ============================================================= */
(function () {
  'use strict';

  // -- Canonical nav config ----------------------------------
  var LINKS = [
    { href: '/how-it-works',       label: 'How It Works' },
    { href: '/start',              label: 'Start Here' },
    { href: '/concierge',          label: 'Concierge' },
    { href: '/for-realtors',       label: 'For Realtors' },
    { href: '/for-trade-partners', label: 'For Trade Partners' },
    { href: '/meet-adam',          label: 'Meet Adam' },
    { href: '/areas-served',       label: 'Areas Served' },
    { href: '/faq',                label: 'FAQ' },
    { href: '/blog',               label: 'Blog' }
  ];

  // -- Helpers -----------------------------------------------
  function currentPath() {
    var p = window.location.pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '');
    if (p.length > 1 && p.slice(-1) === '/') p = p.slice(0, -1);
    return p || '/';
  }
  function isActive(href, path) {
    if (href === '/') return path === '/';
    if (path === href) return true;
    // Section match (e.g. /blog/anything highlights Blog)
    return path.indexOf(href + '/') === 0;
  }
  function isHomepage() {
    return currentPath() === '/';
  }

  // -- Logo variant ------------------------------------------
  // Homepage hero is a photo — use white logo. Other pages have
  // a cream/white body bg with a white-on-navy header strip, so
  // the white logo still reads. We always serve the white logo,
  // but if a page sets <body data-nav-logo="navy"> we switch.
  function logoSrc() {
    var override = document.body && document.body.getAttribute('data-nav-logo');
    if (override === 'navy') return '/assets/hbc-logo-horizontal-navy.png';
    return '/assets/hbc-logo-horizontal-white.png';
  }

  // -- CTA label ---------------------------------------------
  function ctaLabel() {
    var override = document.body && document.body.getAttribute('data-nav-cta');
    if (override) return override;
    return isHomepage() ? 'Get the Report' : 'Book a Call';
  }

  // -- Render header -----------------------------------------
  function renderHeader() {
    var path = currentPath();
    var linksHtml = LINKS.map(function (l) {
      var cls = 'nav__link' + (isActive(l.href, path) ? ' nav__link--active' : '');
      return '<a href="' + l.href + '" class="' + cls + '">' + l.label + '</a>';
    }).join('\n        ');

    var mobileLinksHtml = [].concat(
      ['<a href="/" class="mobile-menu__link' + (path === '/' ? ' mobile-menu__link--active' : '') + '">Home</a>'],
      LINKS.map(function (l) {
        var cls = 'mobile-menu__link' + (isActive(l.href, path) ? ' mobile-menu__link--active' : '');
        return '<a href="' + l.href + '" class="' + cls + '">' + l.label + '</a>';
      })
    ).join('\n      ');

    var cta = ctaLabel();
    return (
      '<nav class="nav" role="navigation" aria-label="Main navigation">' +
      '  <div class="nav__inner">' +
      '    <a href="/" class="nav__brand" aria-label="Hometown Builders Club. Home">' +
      '      <img src="' + logoSrc() + '" alt="Hometown Builders Club" width="160" height="36" loading="eager" decoding="async" style="display:block;height:36px;width:auto;">' +
      '    </a>' +
      '    <div class="nav__links">' +
      '      ' + linksHtml +
      '    </div>' +
      '    <div class="nav__actions">' +
      '      <a href="tel:+13302031331" class="nav__phone">(330) 203-1331</a>' +
      '      <a href="/contact" class="btn btn-primary nav__cta">' + cta + '</a>' +
      '      <button id="hamburger" class="nav__hamburger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>' +
      '    </div>' +
      '  </div>' +
      '</nav>' +
      '<div id="mobile-menu" class="mobile-menu" role="dialog" aria-modal="true" aria-label="Navigation menu">' +
      '  <button id="mobile-close" class="mobile-menu__close" aria-label="Close menu">&times;</button>' +
      '  ' + mobileLinksHtml +
      '  <a href="/contact" class="mobile-menu__cta">' + cta + '</a>' +
      '  <a href="tel:+13302031331" class="mobile-menu__phone">(330) 203-1331</a>' +
      '</div>'
    );
  }

  // -- Mobile menu wiring (event delegation) -----------------
  // We delegate from document so listeners survive any re-render
  // of the header markup and any script timing differences.
  var _menuWired = false;
  function openMenu() {
    var menu = document.getElementById('mobile-menu');
    var hamburger = document.getElementById('hamburger');
    if (!menu) return;
    menu.classList.add('open');
    if (hamburger) hamburger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }
  function shutMenu() {
    var menu = document.getElementById('mobile-menu');
    var hamburger = document.getElementById('hamburger');
    if (!menu) return;
    menu.classList.remove('open');
    if (hamburger) hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
  function wireMobileMenu() {
    if (_menuWired) return;
    _menuWired = true;
    document.addEventListener('click', function (e) {
      var t = e.target;
      if (!t || !t.closest) return;
      if (t.closest('#hamburger')) {
        e.preventDefault();
        openMenu();
        return;
      }
      if (t.closest('#mobile-close')) {
        e.preventDefault();
        shutMenu();
        return;
      }
      // Close when clicking any link inside the mobile menu
      if (t.closest('#mobile-menu a')) {
        shutMenu();
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') shutMenu();
    });
  }

  // -- Mount -------------------------------------------------
  function mount() {
    var header = document.querySelector('header[data-nav]');
    if (header) header.innerHTML = renderHeader();
    wireMobileMenu();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
