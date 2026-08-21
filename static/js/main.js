// =========================================================
// Minimal JS — mobile menu, smooth scroll, sliding nav pill,
// scroll progress, animated counters, tabs, FAQ, reveal,
// back-to-top. All animations GPU-friendly (transform + opacity).
// =========================================================
document.addEventListener('DOMContentLoaded', function () {

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ----- Mobile menu -----
  const btn = document.getElementById('mobile-menu-button');
  const menu = document.getElementById('mobile-menu');
  if (btn && menu) {
    btn.addEventListener('click', () => menu.classList.toggle('hidden'));
  }

  // ----- Smooth scroll for in-page anchors -----
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

  // ----- Floating CTA: show after scrolling past the hero -----
  const floatingCta = document.getElementById('floating-cta');
  if (floatingCta) {
    let ticking = false;
    const updateFloatingCta = () => {
      // Show once the user has scrolled ~500px (past hero), hide near footer
      const scrollY = window.scrollY;
      const docHeight = document.documentElement.scrollHeight;
      const winHeight = window.innerHeight;
      const nearBottom = scrollY + winHeight > docHeight - 300;
      if (scrollY > 500 && !nearBottom) {
        floatingCta.classList.add('is-visible');
      } else {
        floatingCta.classList.remove('is-visible');
      }
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateFloatingCta);
        ticking = true;
      }
    }, { passive: true });
  }

  // ----- Scroll progress bar -----
  const progress = document.getElementById('scroll-progress');
  if (progress) {
    let ticking = false;
    function updateProgress() {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const pct = docHeight > 0 ? scrollTop / docHeight : 0;
      progress.style.transform = `scaleX(${pct})`;
      ticking = false;
    }
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateProgress);
        ticking = true;
      }
    }, { passive: true });
    updateProgress();
  }

  // ----- Sliding nav pill -----
  const nav = document.getElementById('primary-nav');
  const pill = document.getElementById('nav-pill');
  if (nav && pill) {
    const links = nav.querySelectorAll('.nav-link');
    if (links.length) {
      const moveTo = (link) => {
        if (!link) return;
        const navRect = nav.getBoundingClientRect();
        const linkRect = link.getBoundingClientRect();
        const x = linkRect.left - navRect.left;
        pill.style.width = linkRect.width + 'px';
        pill.style.transform = `translate3d(${x}px, -50%, 0)`;
      };
      let active = nav.querySelector('.nav-link.is-active');
      if (!active) {
        const path = window.location.pathname.replace(/\/+$/, '') || '/';
        links.forEach(l => {
          const href = (l.getAttribute('href') || '').replace(/\/+$/, '') || '/';
          if (href === path || (href !== '/' && path.startsWith(href))) active = l;
        });
      }
      if (active) active.classList.add('is-active');

      const place = () => moveTo(active);
      requestAnimationFrame(() => {
        pill.classList.add('ready');
        place();
      });
      window.addEventListener('resize', place);

      links.forEach(l => {
        l.addEventListener('mouseenter', () => moveTo(l));
        l.addEventListener('mouseleave', () => moveTo(active));
        l.addEventListener('click', () => {
          links.forEach(x => x.classList.remove('is-active'));
          l.classList.add('is-active');
          active = l;
        });
      });
    }
  }

  // ----- Animated number counters -----
  const counters = document.querySelectorAll('[data-counter]');
  if (counters.length) {
    counters.forEach(el => {
      const target = parseInt(el.getAttribute('data-counter'), 10) || 0;
      const suffix = el.getAttribute('data-suffix') || '';
      if (reduceMotion) {
        el.textContent = target + suffix;
        return;
      }
      let current = 0;
      const duration = 1100;
      const startTime = performance.now();
      function tick(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        current = Math.round(eased * target);
        el.textContent = current + suffix;
        if (progress < 1) requestAnimationFrame(tick);
        else el.textContent = target + suffix;
      }
      requestAnimationFrame(tick);
    });
  }

  // ----- Module showcase tabs -----
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

  // ----- Services board tabs (sidebar + pane) -----
  const svcBoard = document.querySelector('.svc-board');
  if (svcBoard) {
    const tabs = svcBoard.querySelectorAll('.svc-tab');
    const panes = svcBoard.querySelectorAll('.svc-pane');
    const navBtns = svcBoard.querySelectorAll('.svc-nav-btn');

    const activate = (key) => {
      tabs.forEach(t => {
        const isActive = t.getAttribute('data-tab') === key;
        t.classList.toggle('active', isActive);
        t.setAttribute('aria-selected', isActive ? 'true' : 'false');
      });
      panes.forEach(p => p.classList.toggle('active', p.getAttribute('data-pane') === key));
      // Keep the active tab visible on mobile (horizontal scroll)
      const activeTab = svcBoard.querySelector(`.svc-tab[data-tab="${key}"]`);
      if (activeTab && activeTab.scrollIntoView) {
        activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
      }
    };

    tabs.forEach(tab => {
      tab.addEventListener('click', () => activate(tab.getAttribute('data-tab')));
    });

    navBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-go');
        if (target) activate(String(target).padStart(2, '0'));
      });
    });

    // Keyboard arrows (when a tab is focused)
    tabs.forEach((tab, i) => {
      tab.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
          e.preventDefault();
          const next = tabs[(i + 1) % tabs.length];
          next.focus(); activate(next.getAttribute('data-tab'));
        } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
          e.preventDefault();
          const prev = tabs[(i - 1 + tabs.length) % tabs.length];
          prev.focus(); activate(prev.getAttribute('data-tab'));
        }
      });
    });
  }

  // ----- FAQ accordion -----
  document.querySelectorAll('.faq-item').forEach(item => {
    const q = item.querySelector('.faq-q');
    if (!q) return;
    q.addEventListener('click', () => {
      const wasOpen = item.classList.contains('open');
      // Close siblings (single-open accordion)
      item.parentElement.querySelectorAll('.faq-item.open').forEach(other => {
        if (other !== item) other.classList.remove('open');
      });
      item.classList.toggle('open', !wasOpen);
    });
  });

  // ----- Scroll reveal (IntersectionObserver) -----
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
  }

  // ----- Back to top -----
  const backToTop = document.getElementById('back-to-top');
  if (backToTop) {
    let bttTicking = false;
    function updateBtt() {
      const visible = window.scrollY > 600;
      backToTop.classList.toggle('visible', visible);
      bttTicking = false;
    }
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
});