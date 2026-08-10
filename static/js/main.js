// =========================================================
// Minimal JS — mobile menu, smooth scroll, sliding nav pill,
// animated counters, scroll progress.
// All animations GPU-friendly (transform + opacity only).
// =========================================================
document.addEventListener('DOMContentLoaded', function () {

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
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
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
      const duration = 1200;
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
});