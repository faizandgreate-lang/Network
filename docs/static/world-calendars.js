/** World calendars grid — live dates where computable. */
(function (global) {
  const D = () => new Date();

  function pad(n) {
    return String(n).padStart(2, '0');
  }

  function fmtG(d) {
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }

  function intlCal(calendar) {
    if (global.WorldCalendarMonth?.formatToday) {
      const fake = { intl: calendar };
      const v = global.WorldCalendarMonth.formatToday(fake);
      if (v) return v;
    }
    try {
      return new Intl.DateTimeFormat('en', {
        calendar: calendar === 'korean' ? 'dangi' : calendar,
        weekday: 'short',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }).format(D());
    } catch (_) {
      return null;
    }
  }

  function gregorian() {
    const d = D();
    return fmtG(d) + ' (civil)';
  }

  function julian() {
    if (global.WorldCalendarMonth?.resolveParts) {
      const p = global.WorldCalendarMonth.resolveParts({ fn: 'julian' }, D());
      return `${p.year}-${pad(p.month)}-${pad(p.day)} (Julian)`;
    }
    return fmtG(D()) + ' (Julian)';
  }

  function hijriTabular() {
    const d = D();
    const jd =
      Math.floor((1461 * (d.getFullYear() + 4800 + Math.floor((d.getMonth() - 2) / 12))) / 4) +
      Math.floor((367 * (d.getMonth() - 1 - 12 * Math.floor((d.getMonth() - 2) / 12))) / 12) -
      Math.floor((3 * Math.floor((d.getFullYear() + 4900 + Math.floor((d.getMonth() - 2) / 12)) / 100)) / 4) +
      d.getDate() -
      32075;
    const l = jd - 1948440 + 10632;
    const n = Math.floor((l - 1) / 10631);
    const l2 = l - 10631 * n + 354;
    const j = Math.floor((10985 - l2) / 5316) * Math.floor((50 * l2) / 17719) + Math.floor(l2 / 5670) * Math.floor((43 * l2) / 15238);
    const l3 = l2 - Math.floor((30 - j) / 15) * Math.floor((17719 * j) / 50) - Math.floor(j / 16) * Math.floor((15238 * j) / 43) + 29;
    const m = Math.floor((24 * l3) / 709);
    const day = l3 - Math.floor((709 * m) / 24);
    const y = 30 * n + j - 30;
    const months = ['Muharram', 'Safar', 'Rabi I', 'Rabi II', 'Jumada I', 'Jumada II', 'Rajab', 'Shaʻban', 'Ramadan', 'Shawwal', 'Dhu al-Qiʻdah', 'Dhu al-Hijjah'];
    return `${day} ${months[m - 1]} ${y} AH`;
  }

  function persian() {
    const v = intlCal('persian');
    if (v) return v;
    const g = D();
    const gy = g.getFullYear();
    const days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    let gDayNo =
      365 * (gy - 1600) +
      Math.floor((gy - 1600 + 3) / 4) -
      Math.floor((gy - 1600 + 99) / 100) +
      Math.floor((gy - 1600 + 399) / 400) +
      days[g.getMonth()] +
      g.getDate() -
      79;
    const jy = -979 + 33 * Math.floor(gDayNo / 12053);
    let dNo = gDayNo % 12053;
    jy += 4 * Math.floor(dNo / 1461);
    dNo %= 1461;
    if (dNo >= 366) {
      jy += Math.floor((dNo - 1) / 365);
      dNo = (dNo - 1) % 365;
    }
    const jm = dNo < 186 ? 1 + Math.floor(dNo / 31) : 7 + Math.floor((dNo - 186) / 30);
    const jd = 1 + (dNo < 186 ? dNo % 31 : (dNo - 186) % 30);
    const pm = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar', 'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'];
    return `${jd} ${pm[jm - 1]} ${jy} (Solar Hijri)`;
  }

  function ethiopian() {
    const v = intlCal('ethiopic');
    if (v) return v;
    const g = D();
    const ey = g.getFullYear() - 8;
    return `${g.getDate()} ${g.toLocaleString('en', { month: 'long' })} ${ey} EC (approx.)`;
  }

  function buddhistEra() {
    const g = D();
    return `${fmtG(g)} · BE ${g.getFullYear() + 543}`;
  }

  function holocene() {
    return `Year ${D().getFullYear() + 10000} HE`;
  }

  function unixTime() {
    const ms = Date.now();
    return `${Math.floor(ms / 1000)} s since 1970-01-01 UTC`;
  }

  function isoWeek() {
    const d = new Date(Date.UTC(D().getFullYear(), D().getMonth(), D().getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    const week = Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
    return `${d.getUTCFullYear()}-W${pad(week)} · ${fmtG(D())} Gregorian`;
  }

  function offsetYear(label, delta) {
    const y = D().getFullYear() + delta;
    return `${fmtG(D())} · ${label} year ${y}`;
  }

  function withGregorianNote(label) {
    return `${label}: today aligns with ${fmtG(D())} (Gregorian)`;
  }

  function compute(item) {
    if (global.WorldCalendarMonth?.formatToday) {
      const v = global.WorldCalendarMonth.formatToday(item);
      if (v) return v;
    }
    if (item.intl) {
      const v = intlCal(item.intl);
      if (v) return v;
    }
    if (item.fn && FNS[item.fn]) return FNS[item.fn]();
    if (item.note) return item.note.replace('{g}', fmtG(D()));
    return withGregorianNote('In modern use');
  }

  const FNS = {
    gregorian,
    julian,
    hijriTabular,
    persian,
    ethiopian,
    buddhistEra,
    holocene,
    unixTime,
    isoWeek,
    minguo: () => offsetYear('Minguo', -1911),
    juche: () => offsetYear('Juche', -1911),
    bahai: () => offsetYear('Baháʼí', -1843),
    thai: () => offsetYear('Thai Buddhist', 543),
    frenchRep: () => 'Defunct since 1805 — see Gregorian ' + fmtG(D()),
    soviet: () => 'Defunct (1930–1940) — see Gregorian ' + fmtG(D()),
    discordian: () => {
      const g = D();
      return `YOLD ${g.getFullYear() + 1166} · ${g.toLocaleDateString('en', { weekday: 'long' })}`;
    },
    marsDarian: () => {
      const g = D();
      return `Earth ${fmtG(g)} · Mars sol date ≈ research calendar`;
    },
    historical: () => withGregorianNote('Historical / regional'),
  };

  function item(name, opts = {}) {
    return { name, ...opts };
  }

  /** Candidate calendars; only those whose month/day differ from Gregorian are shown. */
  const CALENDAR_CANDIDATES = [
    {
      items: [
        item('Julian Calendar', { fn: 'julian' }),
        item('Islamic (Hijri) Calendar', { intl: 'islamic', fn: 'hijriTabular' }),
        item('Solar Hijri (Persian/Iranian) Calendar', { intl: 'persian', fn: 'persian' }),
        item('Hebrew Calendar', { intl: 'hebrew' }),
        item('Chinese Calendar', { intl: 'chinese' }),
        item('Hindu Calendar', { intl: 'indian' }),
        item('Ethiopian Calendar', { intl: 'ethiopic', fn: 'ethiopian' }),
        item('Coptic Calendar', { intl: 'coptic' }),
        item('Korean Calendar', { intl: 'dangi' }),
      ],
    },
  ];

  function civilDateKey(item) {
    const p = global.WorldCalendarMonth?.resolveParts(item, D());
    if (!p) return item.name;
    return `${p.year ?? '·'}-${p.month}-${p.day}`;
  }

  function activeCatalog() {
    const differs = global.WorldCalendarMonth?.differsFromGregorianCivil;
    if (!differs) return CALENDAR_CANDIDATES;
    const seen = new Set();
    return CALENDAR_CANDIDATES.map((sec) => ({
      group: sec.group,
      items: sec.items.filter((it) => {
        if (!differs(it)) return false;
        const key = civilDateKey(it);
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      }),
    })).filter((sec) => sec.items.length > 0);
  }

  global.CALENDAR_CATALOG = CALENDAR_CANDIDATES;

  function renderCalendars() {
    const root = document.getElementById('calendar-sections');
    if (!root) return;
    root.innerHTML = '';
    const catalog = activeCatalog();
    if (!catalog.length) {
      root.innerHTML =
        '<p class="sub">No alternate calendars differ from the Gregorian date today in this browser.</p>';
      return;
    }
    catalog.forEach((sec) => {
      const section = document.createElement('section');
      section.className = 'world-section glass-panel';
      const grid = document.createElement('div');
      grid.className = 'world-grid';
      sec.items.forEach((it) => {
        const card = document.createElement('article');
        card.className = 'world-card cal-card cal-card-grid';
        card.dataset.calName = it.name;
        const gridHtml =
          global.WorldCalendarMonth?.buildHtml
            ? global.WorldCalendarMonth.buildHtml(it, { compact: true })
            : '';
        card.innerHTML =
          `<h3 class="world-card-title">${it.name}</h3>` +
          `<p class="world-card-date" data-cal-date>${compute(it)}</p>` +
          gridHtml;
        grid.appendChild(card);
      });
      section.appendChild(grid);
      root.appendChild(section);
    });
  }

  function refreshCardGrid(card, it) {
    const el = card.querySelector('[data-cal-date]');
    if (el) el.textContent = compute(it);
    const embed = card.querySelector('.cal-embed-grid');
    if (embed && global.WorldCalendarMonth?.buildHtml) {
      embed.outerHTML = global.WorldCalendarMonth.buildHtml(it, { compact: true });
    }
  }

  function tick() {
    document.querySelectorAll('.cal-card').forEach((card) => {
      const title = card.querySelector('.world-card-title')?.textContent;
      if (!title) return;
      for (const sec of activeCatalog()) {
        const it = sec.items.find((x) => x.name === title);
        if (it) {
          refreshCardGrid(card, it);
          break;
        }
      }
    });
  }

  global.WorldCalendars = {
    render: renderCalendars,
    tick,
    compute,
    activeCatalog,
    CALENDAR_CATALOG: CALENDAR_CANDIDATES,
  };

  function onLocaleChange() {
    renderCalendars();
  }

  document.addEventListener('DOMContentLoaded', () => {
    const start = () => {
      renderCalendars();
      setInterval(tick, 60000);
      global.addEventListener('locale-change', onLocaleChange);
    };
    if (!global.WorldCalendarMonth?.buildHtml) {
      const s = document.createElement('script');
      s.src = '/static/calendar-month.js';
      s.onload = start;
      document.head.appendChild(s);
      return;
    }
    start();
  });
})(window);
