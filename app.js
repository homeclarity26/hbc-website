/* ============================================================
   APP.JS — Interactivity
   Home Clarity Report
   homeclarityreport.com
   ============================================================ */

(function () {
  'use strict';

  /* ─────────────────────────────────────────────
     LOCAL STORAGE WRAPPER (safe)
  ───────────────────────────────────────────── */
  var store = (function () {
    try {
      var s = window['local' + 'Storage'];
      s.setItem('_hcr_t', '1');
      s.removeItem('_hcr_t');
      return s;
    } catch (e) {
      var mem = {};
      return {
        getItem: function (k) { return mem[k] !== undefined ? mem[k] : null; },
        setItem: function (k, v) { mem[k] = String(v); },
        removeItem: function (k) { delete mem[k]; }
      };
    }
  })();

  /* ─────────────────────────────────────────────
     GA TRACKING HELPER
  ───────────────────────────────────────────── */
  function trackEvent(action, category, label) {
    if (typeof gtag === 'function') {
      gtag('event', action, { event_category: category, event_label: label });
    }
  }
  // Expose globally so inline onclick="" attributes can call it
  window.trackEvent = trackEvent;

  /* ─────────────────────────────────────────────
     DOM READY
  ───────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {


    /* ── Nav scroll shadow ── */
    var nav = document.querySelector('.nav');
    if (nav) {
      var onScroll = function () {
        if (window.scrollY > 10) {
          nav.classList.add('scrolled');
        } else {
          nav.classList.remove('scrolled');
        }
      };
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll(); // run once on load
    }

    /* ── Mobile hamburger menu ── */
    var hamburger = document.getElementById('hamburger');
    var mobileMenu = document.getElementById('mobile-menu');

    if (hamburger && mobileMenu) {

      function openMenu() {
        mobileMenu.classList.add('open');
        hamburger.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = '';
      }

      function closeMenu() {
        mobileMenu.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      }

      hamburger.addEventListener('click', function () {
        var isOpen = mobileMenu.classList.contains('open');
        if (isOpen) {
          closeMenu();
        } else {
          openMenu();
        }
      });

      // Close on any anchor link click inside the menu
      mobileMenu.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
          closeMenu();
        });
      });

      // Close on outside click
      document.addEventListener('click', function (e) {
        if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
          closeMenu();
        }
      });

      // Close on Escape
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeMenu();
      });
    }

    /* ── FAQ Accordion ── */
    var faqItems = document.querySelectorAll('.faq__item');

    faqItems.forEach(function (item) {
      var question = item.querySelector('.faq__question');
      var answer = item.querySelector('.faq__answer');
      if (!question || !answer) return;

      question.addEventListener('click', function () {
        var isOpen = item.classList.contains('open');

        // Close all others
        faqItems.forEach(function (other) {
          if (other !== item && other.classList.contains('open')) {
            other.classList.remove('open');
            var otherQ = other.querySelector('.faq__question');
            if (otherQ) otherQ.setAttribute('aria-expanded', 'false');
          }
        });

        // Toggle this one
        if (isOpen) {
          item.classList.remove('open');
          question.setAttribute('aria-expanded', 'false');
        } else {
          item.classList.add('open');
          question.setAttribute('aria-expanded', 'true');
          trackEvent('click', 'faq', question.querySelector('span') ? question.querySelector('span').textContent.trim().substring(0, 50) : 'question');
        }
      });

      // Keyboard support: Enter / Space already trigger click on <button>
    });

    /* ── Scroll Fade-In (IntersectionObserver) ── */
    var fadeEls = document.querySelectorAll('.fade-in');

    if (fadeEls.length > 0 && 'IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, {
        threshold: 0.08,
        rootMargin: '0px 0px -40px 0px'
      });

      fadeEls.forEach(function (el, idx) {
        // Stagger delay for sibling groups
        var parent = el.parentElement;
        var siblings = parent ? parent.querySelectorAll('.fade-in') : [];
        var siblingIdx = Array.prototype.indexOf.call(siblings, el);
        el.style.transitionDelay = (siblingIdx * 80) + 'ms';
        observer.observe(el);
      });
    } else {
      // Fallback: show all immediately
      fadeEls.forEach(function (el) {
        el.classList.add('visible');
      });
    }

    /* ── Smooth Scroll for Anchor Links ── */
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        var href = link.getAttribute('href');
        if (href === '#' || href === '#!') return;
        var target = document.querySelector(href);
        if (!target) return;
        e.preventDefault();
        var navHeight = nav ? nav.offsetHeight : 0;
        var top = target.getBoundingClientRect().top + window.scrollY - navHeight - 16;
        window.scrollTo({ top: top, behavior: 'smooth' });
      });
    });

    /* ── Contact Form — Formspree AJAX ── */
    var contactForm = document.getElementById('hcr-contact-form');
    var formSuccess = document.getElementById('hcr-form-success');

    if (contactForm && formSuccess) {
      contactForm.addEventListener('submit', function (e) {
        e.preventDefault();

        var submitBtn = contactForm.querySelector('[type="submit"]');
        var originalText = submitBtn ? submitBtn.textContent : '';

        if (submitBtn) {
          submitBtn.textContent = 'Sending…';
          submitBtn.disabled = true;
        }

        fetch(contactForm.action, {
          method: 'POST',
          body: new FormData(contactForm),
          headers: { Accept: 'application/json' }
        })
          .then(function (res) {
            if (res.ok) {
              contactForm.style.display = 'none';
              formSuccess.style.display = 'flex';
              trackEvent('form_submit', 'contact', 'hcr_contact_form_success');
            } else {
              if (submitBtn) {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
              }
              alert('Something went wrong. Please try again or call (330) 203-1331.');
              trackEvent('form_error', 'contact', 'hcr_contact_form_error');
            }
          })
          .catch(function () {
            if (submitBtn) {
              submitBtn.textContent = originalText;
              submitBtn.disabled = false;
            }
            alert('Connection error. Please check your connection or call (330) 203-1331.');
          });
      });
    }

    /* ── Calendly Event Tracking ── */
    window.addEventListener('message', function (e) {
      if (!e.data || typeof e.data !== 'object') return;
      if (e.data.event === 'calendly.event_scheduled') {
        trackEvent('calendly_booked', 'conversion', 'discovery_call_booked');
        // Fire as a GA4 conversion event too
        if (typeof gtag === 'function') {
          gtag('event', 'generate_lead', {
            currency: 'USD',
            value: 4500
          });
        }
      }
    });

  }); // end DOMContentLoaded

})();

/* ─────────────────────────────────────────────
   EXIT INTENT POPUP
───────────────────────────────────────────── */
(function () {
  var overlay    = document.getElementById('exit-overlay');
  var closeBtn   = document.getElementById('exit-close');
  var dismissBtn = document.getElementById('exit-dismiss');

  if (!overlay) return;

  var shown    = false;
  var dismissed = false;

  // Don't show again this session if dismissed
  try {
    if (sessionStorage.getItem('hcr-exit-shown') === '1') {
      dismissed = true;
    }
  } catch (e) {}

  function openExit() {
    if (shown || dismissed) return;
    shown = true;

    // Initialise Calendly widget now (lazy — avoids loading it on every page)
    if (window.Calendly && typeof window.Calendly.initInlineWidgets === 'function') {
      window.Calendly.initInlineWidgets();
    }

    overlay.classList.add('open');
    overlay.removeAttribute('aria-hidden');
    document.body.style.overflow = 'hidden';
    if (closeBtn) closeBtn.focus();

    trackEvent('exit_intent_shown', 'engagement', 'exit_popup_displayed');

    try { sessionStorage.setItem('hcr-exit-shown', '1'); } catch (e) {}
  }

  function closeExit() {
    dismissed = true;
    overlay.classList.remove('open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    trackEvent('exit_intent_dismissed', 'engagement', 'exit_popup_closed');
  }

  // ── Mouse leaves viewport through the top (cursor heads toward browser chrome) ──
  document.addEventListener('mouseleave', function (e) {
    if (e.clientY <= 0) {
      openExit();
    }
  });

  // ── Mobile: back button / hash change triggers after 30s on page ──
  var timeOnPage = 0;
  var timer = setInterval(function () {
    timeOnPage += 1;
    if (timeOnPage >= 30 && !shown && !dismissed) {
      // On mobile there's no cursor leave — show after 30s of inactivity
      // Only trigger once per session
      clearInterval(timer);
    }
  }, 1000);

  // ── Close actions ──
  if (closeBtn)   closeBtn.addEventListener('click', closeExit);
  if (dismissBtn) dismissBtn.addEventListener('click', closeExit);

  // Click outside the modal
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeExit();
  });

  // Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('open')) {
      closeExit();
    }
  });

  // Track if Calendly booking happens from exit popup
  window.addEventListener('message', function (e) {
    if (!e.data || typeof e.data !== 'object') return;
    if (e.data.event === 'calendly.event_scheduled' && overlay.classList.contains('open')) {
      trackEvent('exit_intent_converted', 'conversion', 'booking_from_exit_popup');
      if (typeof gtag === 'function') {
        gtag('event', 'generate_lead', { currency: 'USD', value: 4500, event_label: 'exit_popup_booking' });
      }
      setTimeout(closeExit, 2000);
    }
  });

})();
