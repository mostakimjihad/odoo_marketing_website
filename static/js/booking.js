/* =====================================================================
   Booking modal — vanilla JS, no dependencies.
   Triggered by any element with [data-book-trigger].
   Flow:  calendar -> time slots -> form -> success.
   ===================================================================== */
(function () {
  'use strict';

  const dlg = document.getElementById('booking-modal');
  if (!dlg) return;

  // ---------- State ----------
  const state = {
    viewYear: 0,
    viewMonth: 0, // 1-12
    today: null,
    horizon: null,
    availableDays: new Set(),
    blockedDays: new Set(),
    selectedDate: null,           // 'YYYY-MM-DD'
    selectedSlot: null,           // ISO string in project TZ
    visitorTz: 'Asia/Dhaka',
  };

  // ---------- Helpers ----------
  // `$` and `$$` default to document so global lookups (CTAs anywhere on
  // the page) work without having to pass `document` every time.
  // Pass an explicit root when you need to scope to the dialog.
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function csrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  async function fetchJSON(url) {
    const r = await fetch(url, { credentials: 'same-origin', headers: { 'Accept': 'application/json' } });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }

  async function postJSON(url, body) {
    const r = await fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf(),
        'Accept': 'application/json',
      },
      body: JSON.stringify(body),
    });
    let data = {};
    try { data = await r.json(); } catch (_) {}
    if (!r.ok) {
      const err = new Error(data.error || ('HTTP ' + r.status));
      err.data = data;
      err.status = r.status;
      throw err;
    }
    return data;
  }

  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const fmtDate = (iso) => {
    const [y, m, d] = iso.split('-').map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d));
    return dt.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
  };
  const fmtTime = (iso) => {
    const d = new Date(iso);
    return d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  };

  // ---------- Steps ----------
  function showStep(name) {
    $$('.booking-step').forEach(s => { s.hidden = s.dataset.step !== name; });
  }

  function clearErrors() {
    $$('[data-error]', dlg).forEach(e => { e.hidden = true; e.textContent = ''; });
    const formErr = $('[data-book-error]');
    if (formErr) { formErr.hidden = true; formErr.textContent = ''; }
  }

  // ---------- Calendar ----------
  function renderCalendar() {
    const label = $('[data-cal-label]');
    label.textContent = `${MONTHS[state.viewMonth - 1]} ${state.viewYear}`;
    const grid = $('[data-cal-grid]');
    grid.innerHTML = '';

    const first = new Date(Date.UTC(state.viewYear, state.viewMonth - 1, 1));
    const startWeekday = first.getUTCDay(); // 0 = Sunday
    const daysInMonth = new Date(Date.UTC(state.viewYear, state.viewMonth, 0)).getUTCDate();

    // Leading blanks
    for (let i = 0; i < startWeekday; i++) {
      const blank = document.createElement('div');
      blank.className = 'booking-cal__day booking-cal__day--blank';
      blank.setAttribute('aria-hidden', 'true');
      grid.appendChild(blank);
    }

    const todayISO = state.today;
    const horizonISO = state.horizon;

    for (let day = 1; day <= daysInMonth; day++) {
      const iso = `${state.viewYear}-${String(state.viewMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const cell = document.createElement('button');
      cell.type = 'button';
      cell.className = 'booking-cal__day';
      cell.textContent = String(day);
      cell.dataset.date = iso;

      const isAvailable = state.availableDays.has(iso);
      const isBlocked = state.blockedDays.has(iso);
      const isPast = iso < todayISO;
      const isFuture = iso > horizonISO;
      const isToday = iso === todayISO;
      const isSelected = iso === state.selectedDate;

      if (isPast || isFuture || isBlocked) {
        cell.disabled = true;
        cell.classList.add('is-disabled');
      } else if (isAvailable) {
        cell.classList.add('is-available');
      } else {
        cell.disabled = true;
        cell.classList.add('is-disabled');
      }
      if (isToday) cell.classList.add('is-today');
      if (isSelected) cell.classList.add('is-selected');

      cell.addEventListener('click', () => {
        state.selectedDate = iso;
        renderCalendar();
        loadSlots(iso);
      });
      grid.appendChild(cell);
    }
  }

  async function loadCalendar(year, month) {
    state.viewYear = year;
    state.viewMonth = month;
    try {
      const data = await fetchJSON(`/booking/calendar/?year=${year}&month=${month}`);
      state.today = data.today;
      state.horizon = data.horizon;
      state.availableDays = new Set(data.days);
      state.blockedDays = new Set(data.blocked);
    } catch (e) {
      console.error('calendar load failed', e);
      // Show empty calendar with a friendly note
      state.availableDays = new Set();
      state.blockedDays = new Set();
      const grid = $('[data-cal-grid]');
      grid.innerHTML = '<div class="booking-cal__error">Could not load availability. Please refresh and try again.</div>';
      return;
    }
    renderCalendar();
  }

  // ---------- Slots ----------
  async function loadSlots(dateISO) {
    showStep('slots');
    const list = $('[data-slots-list]');
    const empty = $('[data-slots-empty]');
    const label = $('[data-slots-date]');
    label.textContent = fmtDate(dateISO);

    list.innerHTML = '<div class="booking-loading">Loading times…</div>';
    empty.hidden = true;

    try {
      const data = await fetchJSON(`/booking/slots/?date=${dateISO}`);
      const slots = data.slots || [];
      list.innerHTML = '';
      if (!slots.length) {
        empty.hidden = false;
        return;
      }
      slots.forEach(iso => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'booking-slot';
        btn.dataset.slot = iso;
        btn.textContent = fmtTime(iso);
        btn.addEventListener('click', () => {
          state.selectedSlot = iso;
          $$('.booking-slot', list).forEach(b => b.classList.remove('is-selected'));
          btn.classList.add('is-selected');
          // brief beat before transitioning so the user sees the selection
          setTimeout(() => showFormSummary(), 120);
        });
        list.appendChild(btn);
      });
    } catch (e) {
      list.innerHTML = '<div class="booking-cal__error">Could not load times. Please try again.</div>';
    }
  }

  function showFormSummary() {
    if (!state.selectedDate || !state.selectedSlot) return;
    const summary = $('[data-form-summary]');
    summary.textContent = `${fmtDate(state.selectedDate)} · ${fmtTime(state.selectedSlot)} (${state.visitorTz})`;
    showStep('form');
    setTimeout(() => $('#bk-name') && $('#bk-name').focus(), 80);
  }

  // ---------- Submit ----------
  async function submitForm(ev) {
    ev.preventDefault();
    clearErrors();

    const submit = $('[data-book-submit]');
    const label = $('[data-book-submit-label]');
    const form = ev.currentTarget;
    const formErr = $('[data-book-error]');

    const data = {
      name: (form.elements.name.value || '').trim(),
      email: (form.elements.email.value || '').trim(),
      phone: (form.elements.phone.value || '').trim(),
      company: (form.elements.company.value || '').trim(),
      notes: (form.elements.notes.value || '').trim(),
      start_iso: state.selectedSlot,
      slot_minutes: 30,
      timezone: state.visitorTz,
    };

    // Quick client-side validation
    const fieldErrors = {};
    if (!data.name) fieldErrors.name = 'Name is required.';
    if (!data.email) fieldErrors.email = 'Email is required.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) fieldErrors.email = 'Enter a valid email.';
    if (!data.start_iso) fieldErrors.start_iso = 'Please pick a time slot.';
    if (Object.keys(fieldErrors).length) {
      Object.entries(fieldErrors).forEach(([k, msg]) => {
        const el = dlg.querySelector(`[data-error="${k}"]`);
        if (el) { el.hidden = false; el.textContent = msg; }
      });
      return;
    }

    submit.disabled = true;
    const originalLabel = label.textContent;
    label.textContent = 'Booking…';

    try {
      const res = await postJSON('/booking/create/', data);

      $('[data-done-email]').textContent = data.email;
      $('[data-done-time]').textContent = `${fmtDate(state.selectedDate)} · ${fmtTime(state.selectedSlot)} (${state.visitorTz})`;
      const confirmLink = $('[data-done-confirm]');
      if (confirmLink && res.confirm_url) confirmLink.href = res.confirm_url;
      showStep('done');
      // refresh calendar so this slot disappears from the picker
      loadCalendar(state.viewYear, state.viewMonth);
    } catch (e) {
      const data = e.data || {};
      if (data.errors && typeof data.errors === 'object') {
        Object.entries(data.errors).forEach(([k, msg]) => {
          const el = dlg.querySelector(`[data-error="${k}"]`);
          if (el) { el.hidden = false; el.textContent = msg; }
        });
      } else {
        formErr.hidden = false;
        formErr.textContent = e.message || 'Could not complete the booking. Please try again.';
      }
    } finally {
      submit.disabled = false;
      label.textContent = originalLabel;
    }
  }

  // ---------- Open / close ----------
  function open() {
    // Reset form errors and inputs
    clearErrors();
    const form = $('[data-book-form]');
    if (form) form.reset();
    state.selectedSlot = null;

    // Visitor TZ
    try {
      state.visitorTz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Dhaka';
    } catch (_) {
      state.visitorTz = 'Asia/Dhaka';
    }
    const tzEl = $('[data-book-tz]');
    if (tzEl) tzEl.textContent = state.visitorTz;

    // Initial month = today
    const now = new Date();
    const y = now.getFullYear();
    const m = now.getMonth() + 1;

    try {
      if (typeof dlg.showModal === 'function') dlg.showModal();
      else dlg.setAttribute('open', '');
    } catch (err) {
      console.error('Booking modal failed to open:', err);
    }

    document.body.style.overflow = 'hidden';
    loadCalendar(y, m).then(() => showStep('calendar'));
  }

  function close() {
    if (typeof dlg.close === 'function') dlg.close();
    else dlg.removeAttribute('open');
    document.body.style.overflow = '';
  }

  // ---------- Wire up ----------
  function init() {
    $$('[data-book-trigger]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        open();
      });
    });

    $$('[data-book-close]').forEach(el => el.addEventListener('click', close));
    dlg.addEventListener('click', (e) => { if (e.target === dlg) close(); });
    dlg.addEventListener('cancel', (e) => { e.preventDefault(); close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && dlg.open) close(); });

    $$('[data-cal-prev]').forEach(b => b.addEventListener('click', () => {
      let m = state.viewMonth - 1, y = state.viewYear;
      if (m < 1) { m = 12; y -= 1; }
      loadCalendar(y, m);
    }));
    $$('[data-cal-next]').forEach(b => b.addEventListener('click', () => {
      let m = state.viewMonth + 1, y = state.viewYear;
      if (m > 12) { m = 1; y += 1; }
      loadCalendar(y, m);
    }));

    $$('[data-step-back]').forEach(b => b.addEventListener('click', () => {
      showStep(b.dataset.stepBack);
    }));

    const form = $('[data-book-form]');
    if (form) form.addEventListener('submit', submitForm);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
