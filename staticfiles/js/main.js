// =========================================================
// Minimal UI handlers — Mostakim Jihad site
// =========================================================
// Mobile menu toggle, smooth anchor scroll, floating CTA
// visibility, scroll progress bar, FAQ accordion, back-to-top,
// and IntersectionObserver-based section reveal.
// NO scroll-driven parallax, NO story-pin, NO tilt, NO cursor
// glow — those were removed in favor of a clean professional UI.
// =========================================================
document.addEventListener('DOMContentLoaded', function () {

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // -----------------------------------------------------------
  // Mobile menu
  // -----------------------------------------------------------
  const btn = document.getElementById('mobile-menu-button');
  const menu = document.getElementById('mobile-menu');
  if (btn && menu) {
    btn.addEventListener('click', () => menu.classList.toggle('hidden'));
  }

  // -----------------------------------------------------------
  // Smooth scroll for in-page anchors
  // -----------------------------------------------------------
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const href = a.getAttribute('href');
      if (href === '#' || href === '#!') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // -----------------------------------------------------------
  // Floating CTA + nav shadow — driven by scroll position only
  // -----------------------------------------------------------
  const floatingCta = document.getElementById('floating-cta');
  const nav = document.getElementById('site-nav');
  const scrollProgress = document.getElementById('scroll-progress');

  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const scrollY = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const nearBottom = scrollY + window.innerHeight > document.documentElement.scrollHeight - 300;

      // Floating CTA — visible after 500px, hidden near bottom
      if (floatingCta) {
        if (scrollY > 500 && !nearBottom) floatingCta.classList.add('is-visible');
        else floatingCta.classList.remove('is-visible');
      }

      // Nav shadow on scroll
      if (nav) {
        if (scrollY > 8) nav.classList.add('is-scrolled');
        else nav.classList.remove('is-scrolled');
      }

      // Top scroll progress bar (if present)
      if (scrollProgress) {
        const pct = docHeight > 0 ? scrollY / docHeight : 0;
        scrollProgress.style.transform = `scaleX(${pct})`;
      }

      ticking = false;
    });
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // -----------------------------------------------------------
  // Reveal-on-scroll (IntersectionObserver)
  // -----------------------------------------------------------
  // Simple opacity fade-in for any element with class `reveal`.
  // Falls back to always-visible if JS fails.
  document.documentElement.classList.add('js-reveals');

  // Map AOS-style data-aos="fade-up" to our .reveal class so legacy
  // markup transfers without rewriting.
  const aosMap = {
    'fade': 'reveal',
    'fade-up': 'reveal',
    'fade-down': 'reveal',
    'fade-left': 'reveal',
    'fade-right': 'reveal',
    'zoom-in': 'reveal',
    'flip-up': 'reveal',
  };
  document.querySelectorAll('[data-aos]').forEach(el => {
    const cls = aosMap[el.getAttribute('data-aos')] || 'reveal';
    if (!el.classList.contains(cls)) el.classList.add(cls);
  });

  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
  }

  // -----------------------------------------------------------
  // FAQ accordion
  // -----------------------------------------------------------
  document.querySelectorAll('[data-faq-item] .faq-q').forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('[data-faq-item]');
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      if (card) card.setAttribute('data-open', String(!expanded));
    });
  });

  // -----------------------------------------------------------
  // Animated number counters — fires when visible
  // -----------------------------------------------------------
  const counters = document.querySelectorAll('[data-counter]');
  if (counters.length) {
    const animateCounter = (el) => {
      if (el.dataset.counterDone === '1') return;
      el.dataset.counterDone = '1';
      const target = parseInt(el.getAttribute('data-counter'), 10) || 0;
      const suffix = el.getAttribute('data-suffix') || '';
      if (reduceMotion) { el.textContent = target + suffix; return; }
      const duration = 1100;
      const startTime = performance.now();
      function tick(now) {
        const elapsed = now - startTime;
        const p = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(eased * target) + suffix;
        if (p < 1) requestAnimationFrame(tick);
        else el.textContent = target + suffix;
      }
      requestAnimationFrame(tick);
    };

    if ('IntersectionObserver' in window) {
      const cio = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            cio.unobserve(entry.target);
          }
        });
      }, { threshold: 0.4 });
      counters.forEach(el => cio.observe(el));
    } else {
      counters.forEach(animateCounter);
    }
  }

  // -----------------------------------------------------------
  // Module showcase tabs
  // -----------------------------------------------------------
  const showcase = document.querySelector('.module-showcase');
  if (showcase) {
    const tabs = showcase.querySelectorAll('.module-tab');
    const panes = showcase.querySelectorAll('.module-pane');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const target = tab.getAttribute('data-tab');
        tabs.forEach(t => t.classList.toggle('active', t === tab));
        panes.forEach(p => p.classList.toggle('active', p.getAttribute('data-tab') === target));
      });
    });
  }

  // -----------------------------------------------------------
  // Hero carousel — auto-rotate every 5s, pause on hover,
  // clickable dots jump to a slide. Respects prefers-reduced-motion
  // (no auto-advance — user clicks dots only).
  // -----------------------------------------------------------
  const carousels = document.querySelectorAll('[data-hero-carousel]');
  carousels.forEach(track => {
    const slides = Array.from(track.querySelectorAll('.hero-carousel-slide'));
    const dots = Array.from(track.parentElement.querySelectorAll('.hero-carousel-dot'));
    if (slides.length < 2) return;
    let current = 0;
    let timer = null;

    const show = (i) => {
      current = (i + slides.length) % slides.length;
      slides.forEach((s, idx) => s.classList.toggle('is-active', idx === current));
      dots.forEach((d, idx) => d.classList.toggle('is-active', idx === current));
    };
    const next = () => show(current + 1);

    const start = () => {
      if (reduceMotion || timer) return;
      timer = setInterval(next, 5000);
    };
    const stop = () => {
      if (timer) { clearInterval(timer); timer = null; }
    };

    // Pause on hover
    track.parentElement.addEventListener('mouseenter', stop);
    track.parentElement.addEventListener('mouseleave', start);
    // Pause when tab not visible
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stop(); else start();
    });

    // Dot navigation
    dots.forEach((dot, i) => {
      dot.addEventListener('click', () => {
        show(i);
        stop();
        start();
      });
    });

    if (!reduceMotion) start();
  });

  // -----------------------------------------------------------
  // Back to top
  // -----------------------------------------------------------
  const backToTop = document.getElementById('back-to-top');
  if (backToTop) {
    let bttTicking = false;
    const updateBtt = () => {
      const visible = window.scrollY > 600;
      backToTop.classList.toggle('visible', visible);
      bttTicking = false;
    };
    window.addEventListener('scroll', () => {
      if (!bttTicking) {
        requestAnimationFrame(updateBtt);
        bttTicking = true;
      }
    }, { passive: true });
    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    updateBtt();
  }

  // -----------------------------------------------------------
  // Mega menu — hover (desktop) / click (touch) / Esc / outside-click
  // Each nav item with `[data-mega]` has a trigger and a sibling
  // panel identified by `[data-mega-panel="<name>"]`.
  // -----------------------------------------------------------
  const isCoarse = window.matchMedia('(hover: none), (pointer: coarse)').matches;
  const triggers = document.querySelectorAll('[data-mega-trigger]');
  const panels = document.querySelectorAll('[data-mega-panel]');
  const wrappers = document.querySelectorAll('[data-mega]');

  if (triggers.length && panels.length) {
    let openName = null;
    let closeTimer = null;

    const panelFor = name => document.querySelector(`[data-mega-panel="${name}"]`);
    const triggerFor = name => document.querySelector(`[data-mega-trigger="${name}"]`);
    const wrapperFor = name => document.querySelector(`[data-mega="${name}"]`);

    const openPanel = (name) => {
      if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
      if (openName === name) return;
      closeAll();
      const panel = panelFor(name);
      const trigger = triggerFor(name);
      const wrapper = wrapperFor(name);
      if (!panel || !trigger) return;
      panel.hidden = false;
      // next frame so the transition can run from hidden → visible
      requestAnimationFrame(() => {
        panel.classList.add('is-open');
      });
      trigger.setAttribute('aria-expanded', 'true');
      wrapper && wrapper.classList.add('is-active');
      openName = name;
    };

    const closeAll = () => {
      panels.forEach(p => {
        p.classList.remove('is-open');
        // restore `hidden` after the fade so screen readers don't see it
        setTimeout(() => { if (!p.classList.contains('is-open')) p.hidden = true; }, 200);
      });
      triggers.forEach(t => t.setAttribute('aria-expanded', 'false'));
      wrappers.forEach(w => w.classList.remove('is-active'));
      openName = null;
    };

    const scheduleClose = () => {
      if (closeTimer) clearTimeout(closeTimer);
      closeTimer = setTimeout(closeAll, 120);
    };

    const cancelClose = () => {
      if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
    };

    triggers.forEach(trigger => {
      const name = trigger.getAttribute('data-mega-trigger');

      if (!isCoarse) {
        // Desktop: open on hover, close when leaving the wrapper
        const wrapper = wrapperFor(name);
        const panel = panelFor(name);
        wrapper && wrapper.addEventListener('mouseenter', () => openPanel(name));
        wrapper && wrapper.addEventListener('mouseleave', scheduleClose);
        panel && panel.addEventListener('mouseenter', cancelClose);
        panel && panel.addEventListener('mouseleave', scheduleClose);
      }

      // Click / keyboard — toggle panel without navigating away
      trigger.addEventListener('click', (e) => {
        // Let users still click through to the parent page if they
        // tap the trigger chevron area or the parent itself; we only
        // intercept when the panel is currently closed.
        if (openName !== name) {
          e.preventDefault();
          openPanel(name);
        } else if (!isCoarse) {
          // Desktop with open panel: keep the link navigable
        }
      });
      trigger.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') { closeAll(); trigger.blur(); }
      });
    });

    // Esc closes any open panel from anywhere on the page
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && openName) closeAll();
    });

    // Click outside the nav closes any open panel
    document.addEventListener('click', (e) => {
      if (!openName) return;
      const wrapper = wrapperFor(openName);
      const panel = panelFor(openName);
      if (wrapper && wrapper.contains(e.target)) return;
      if (panel && panel.contains(e.target)) return;
      closeAll();
    });

    // Resize: collapse any open panel when crossing the desktop break
    window.addEventListener('resize', () => {
      if (window.innerWidth < 1024 && openName) closeAll();
    });
  }
});