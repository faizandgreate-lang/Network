/** World clock — IANA time zones, digital + analog, DST-aware. */
(function () {
  const t = (k, v) => (typeof window.t === 'function' ? window.t(k, v) : k);
  const ZONES = [
    { tz: 'Etc/GMT+12', label: 'UTC−12:00', places: 'Baker Island' },
    { tz: 'Pacific/Pago_Pago', label: 'UTC−11:00', places: 'American Samoa' },
    { tz: 'Pacific/Honolulu', label: 'UTC−10:00', places: 'Hawaii' },
    { tz: 'Pacific/Marquesas', label: 'UTC−09:30', places: 'Marquesas Islands' },
    { tz: 'America/Anchorage', label: 'UTC−09:00', places: 'Alaska' },
    { tz: 'America/Los_Angeles', label: 'UTC−08:00', places: 'US Pacific' },
    { tz: 'America/Denver', label: 'UTC−07:00', places: 'US Mountain' },
    { tz: 'America/Chicago', label: 'UTC−06:00', places: 'US Central' },
    { tz: 'America/New_York', label: 'UTC−05:00', places: 'US Eastern' },
    { tz: 'America/Caracas', label: 'UTC−04:00', places: 'Venezuela' },
    { tz: 'America/Halifax', label: 'UTC−04:00', places: 'Atlantic Canada' },
    { tz: 'America/St_Johns', label: 'UTC−03:30', places: 'Newfoundland' },
    { tz: 'America/Sao_Paulo', label: 'UTC−03:00', places: 'Brazil' },
    { tz: 'America/Noronha', label: 'UTC−02:00', places: 'Fernando de Noronha' },
    { tz: 'Atlantic/Cape_Verde', label: 'UTC−01:00', places: 'Cape Verde' },
    { tz: 'UTC', label: 'UTC±00:00', places: 'UK, Ghana, Iceland' },
    { tz: 'Europe/London', label: 'UTC±00:00', places: 'London' },
    { tz: 'Europe/Paris', label: 'UTC+01:00', places: 'Central Europe' },
    { tz: 'Europe/Helsinki', label: 'UTC+02:00', places: 'Eastern Europe' },
    { tz: 'Africa/Cairo', label: 'UTC+02:00', places: 'Egypt' },
    { tz: 'Europe/Moscow', label: 'UTC+03:00', places: 'Moscow' },
    { tz: 'Asia/Riyadh', label: 'UTC+03:00', places: 'Arabia' },
    { tz: 'Asia/Tehran', label: 'UTC+03:30', places: 'Iran' },
    { tz: 'Asia/Dubai', label: 'UTC+04:00', places: 'Gulf' },
    { tz: 'Asia/Kabul', label: 'UTC+04:30', places: 'Afghanistan' },
    { tz: 'Asia/Karachi', label: 'UTC+05:00', places: 'Pakistan' },
    { tz: 'Asia/Kolkata', label: 'UTC+05:30', places: 'India' },
    { tz: 'Asia/Kathmandu', label: 'UTC+05:45', places: 'Nepal' },
    { tz: 'Asia/Dhaka', label: 'UTC+06:00', places: 'Bangladesh' },
    { tz: 'Asia/Yangon', label: 'UTC+06:30', places: 'Myanmar' },
    { tz: 'Asia/Bangkok', label: 'UTC+07:00', places: 'Thailand' },
    { tz: 'Asia/Shanghai', label: 'UTC+08:00', places: 'China' },
    { tz: 'Australia/Eucla', label: 'UTC+08:45', places: 'Eucla' },
    { tz: 'Asia/Tokyo', label: 'UTC+09:00', places: 'Japan' },
    { tz: 'Australia/Darwin', label: 'UTC+09:30', places: 'Darwin' },
    { tz: 'Australia/Sydney', label: 'UTC+10:00', places: 'Sydney' },
    { tz: 'Australia/Lord_Howe', label: 'UTC+10:30', places: 'Lord Howe' },
    { tz: 'Pacific/Guadalcanal', label: 'UTC+11:00', places: 'Solomon Islands' },
    { tz: 'Pacific/Auckland', label: 'UTC+12:00', places: 'New Zealand' },
    { tz: 'Pacific/Chatham', label: 'UTC+12:45', places: 'Chatham Islands' },
    { tz: 'Pacific/Tongatapu', label: 'UTC+13:00', places: 'Tonga' },
    { tz: 'Pacific/Kiritimati', label: 'UTC+14:00', places: 'Line Islands' },
  ];

  const STORAGE_KEY = 'nm-clock-view';
  let viewMode = 'both';

  function loadViewMode() {
    try {
      const v = localStorage.getItem(STORAGE_KEY);
      if (v === 'digital' || v === 'analog' || v === 'both') viewMode = v;
    } catch (_) {}
  }

  function saveViewMode() {
    try {
      localStorage.setItem(STORAGE_KEY, viewMode);
    } catch (_) {}
  }

  function partsInZone(tz, now = new Date()) {
    const parts = new Intl.DateTimeFormat('en-GB', {
      timeZone: tz,
      hour: 'numeric',
      minute: 'numeric',
      second: 'numeric',
      hour12: false,
    }).formatToParts(now);
    const g = (t) => parseInt(parts.find((p) => p.type === t)?.value, 10);
    return { h: g('hour'), m: g('minute'), s: g('second') };
  }

  function fmtDigital(tz, now = new Date()) {
    return new Intl.DateTimeFormat('en-GB', {
      timeZone: tz,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).format(now);
  }

  function fmtDate(tz, now = new Date()) {
    return new Intl.DateTimeFormat('en-GB', {
      timeZone: tz,
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    }).format(now);
  }

  function liveOffsetLabel(tz, now = new Date()) {
    try {
      const parts = new Intl.DateTimeFormat('en', {
        timeZone: tz,
        timeZoneName: 'shortOffset',
      }).formatToParts(now);
      return parts.find((p) => p.type === 'timeZoneName')?.value || '';
    } catch (_) {
      return '';
    }
  }

  function analogSvg(h, m, s, size) {
    const sz = size || 76;
    const cx = sz / 2;
    const cy = sz / 2;
    const r = sz / 2 - 5;
    const hand = (deg, len, w) => {
      const rad = ((deg - 90) * Math.PI) / 180;
      const x2 = cx + len * Math.cos(rad);
      const y2 = cy + len * Math.sin(rad);
      return `<line x1="${cx}" y1="${cy}" x2="${x2.toFixed(2)}" y2="${y2.toFixed(2)}" stroke="currentColor" stroke-width="${w}" stroke-linecap="round"/>`;
    };
    const hDeg = (h % 12) * 30 + m * 0.5;
    const mDeg = m * 6 + s * 0.1;
    const sDeg = s * 6;
    let ticks = '';
    for (let i = 0; i < 12; i++) {
      const a = ((i * 30 - 90) * Math.PI) / 180;
      const x1 = cx + (r - 6) * Math.cos(a);
      const y1 = cy + (r - 6) * Math.sin(a);
      const x2 = cx + r * Math.cos(a);
      const y2 = cy + r * Math.sin(a);
      ticks += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="currentColor" stroke-opacity="0.35" stroke-width="1"/>`;
    }
    return (
      `<svg class="clock-analog-svg" viewBox="0 0 ${sz} ${sz}" width="${sz}" height="${sz}" aria-hidden="true">` +
      `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="currentColor" stroke-opacity="0.3"/>` +
      ticks +
      hand(hDeg, r * 0.42, 2.8) +
      hand(mDeg, r * 0.58, 2) +
      hand(sDeg, r * 0.72, 1.2) +
      `<circle cx="${cx}" cy="${cy}" r="2.5" fill="currentColor"/>` +
      '</svg>'
    );
  }

  function applyViewMode() {
    document.body.dataset.clockView = viewMode;
    document.querySelectorAll('.clock-view-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.view === viewMode);
    });
  }

  function cardHtml(z, isLocal, now) {
    const p = partsInZone(z.tz, now);
    const off = liveOffsetLabel(z.tz, now) || z.label;
    const showDigital = viewMode === 'digital' || viewMode === 'both';
    const showAnalog = viewMode === 'analog' || viewMode === 'both';
    return (
      `<h3 class="world-card-title">${esc(z.label)} <span class="clock-tz-offset">${esc(off)}</span></h3>` +
      (showAnalog
        ? `<div class="clock-analog-wrap" data-clock-analog>${analogSvg(p.h, p.m, p.s)}</div>`
        : '') +
      (showDigital ? `<p class="clock-time" data-clock-time>${fmtDigital(z.tz, now)}</p>` : '') +
      `<p class="clock-date sub" data-clock-date>${fmtDate(z.tz, now)}</p>` +
      `<p class="clock-places sub">${esc(z.places)}</p>` +
      `<p class="clock-tz-name sub">${esc(z.tz.replace(/_/g, ' '))}</p>` +
      (isLocal ? '<span class="clock-badge">Your zone</span>' : '')
    );
  }

  function esc(s) {
    return String(s ?? '').replace(/[&<>"']/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  function render() {
    const grid = document.getElementById('clock-grid');
    if (!grid) return;
    const localTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const now = new Date();
    grid.innerHTML = '';
    ZONES.forEach((z) => {
      const isLocal = z.tz === localTz;
      const card = document.createElement('article');
      card.className = 'world-card clock-card' + (isLocal ? ' clock-card-local' : '');
      card.dataset.tz = z.tz;
      card.innerHTML = cardHtml(z, isLocal, now);
      grid.appendChild(card);
    });
    const utcEl = document.getElementById('clock-utc');
    if (utcEl) {
      const time = fmtDigital('UTC', now);
      const date = fmtDate('UTC', now);
      utcEl.textContent =
        typeof t === 'function'
          ? t('clock.utcNow', { time, date })
          : `UTC now: ${time} · ${date}`;
    }
    const localHero = document.getElementById('clock-local-hero');
    if (localHero) {
      const p = partsInZone(localTz, now);
      localHero.innerHTML =
        `<h2 class="clock-hero-title">${
          typeof t === 'function'
            ? esc(t('clock.yourTime', { zone: localTz.replace(/_/g, ' ') }))
            : `Your time — ${esc(localTz.replace(/_/g, ' '))}`
        }</h2>` +
        `<div class="clock-hero-inner">` +
        `<div class="clock-hero-analog">${analogSvg(p.h, p.m, p.s, 120)}</div>` +
        `<div class="clock-hero-digital">` +
        `<p class="clock-hero-time">${fmtDigital(localTz, now)}</p>` +
        `<p class="clock-hero-date sub">${fmtDate(localTz, now)}</p>` +
        `</div></div>`;
    }
    applyViewMode();
  }

  function tick() {
    const now = new Date();
    document.querySelectorAll('.clock-card').forEach((card) => {
      const tz = card.dataset.tz;
      if (!tz) return;
      const p = partsInZone(tz, now);
      const analog = card.querySelector('[data-clock-analog]');
      if (analog) analog.innerHTML = analogSvg(p.h, p.m, p.s);
      const t = card.querySelector('[data-clock-time]');
      const dt = card.querySelector('[data-clock-date]');
      if (t) t.textContent = fmtDigital(tz, now);
      if (dt) dt.textContent = fmtDate(tz, now);
    });
    const utcEl = document.getElementById('clock-utc');
    if (utcEl) {
      const time = fmtDigital('UTC', now);
      const date = fmtDate('UTC', now);
      utcEl.textContent =
        typeof t === 'function'
          ? t('clock.utcNow', { time, date })
          : `UTC now: ${time} · ${date}`;
    }
    const localTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const localHero = document.getElementById('clock-local-hero');
    if (localHero) {
      const p = partsInZone(localTz, now);
      const analog = localHero.querySelector('.clock-hero-analog');
      if (analog) analog.innerHTML = analogSvg(p.h, p.m, p.s, 120);
      const timeEl = localHero.querySelector('.clock-hero-time');
      const dateEl = localHero.querySelector('.clock-hero-date');
      if (timeEl) timeEl.textContent = fmtDigital(localTz, now);
      if (dateEl) dateEl.textContent = fmtDate(localTz, now);
    }
  }

  function wireViewToggle() {
    document.querySelectorAll('.clock-view-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        viewMode = btn.dataset.view || 'both';
        saveViewMode();
        render();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    loadViewMode();
    wireViewToggle();
    render();
    setInterval(tick, 1000);
    window.addEventListener('locale-change', () => {
      if (window.I18n?.apply) window.I18n.apply(document);
      render();
    });
  });
})();
