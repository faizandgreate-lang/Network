/** Month grid + accurate dates via Intl calendar API (ICU). */
(function (global) {
  const WEEKDAYS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  const WEEKDAYS_FULL = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const CAL_ALIAS = {
    korean: 'dangi',
  };

  function calId(item) {
    const raw = item.intl;
    if (!raw) return null;
    return CAL_ALIAS[raw] || raw;
  }

  function supportsIntlCalendar(id) {
    if (!id) return false;
    try {
      new Intl.DateTimeFormat('en', { calendar: id }).format(new Date());
      return true;
    } catch (_) {
      return false;
    }
  }

  function sameDay(a, b) {
    return a.year === b.year && a.month === b.month && a.day === b.day;
  }

  function intlParts(calendar, date) {
    if (!calendar || !supportsIntlCalendar(calendar)) return null;
    try {
      const parts = new Intl.DateTimeFormat('en', {
        calendar,
        day: 'numeric',
        month: 'numeric',
        year: 'numeric',
      }).formatToParts(date);
      const get = (t) => parts.find((p) => p.type === t)?.value;
      const day = parseInt(get('day'), 10);
      const month = parseInt(get('month'), 10);
      const year = parseInt(get('year'), 10);
      if (Number.isNaN(day) || Number.isNaN(month) || Number.isNaN(year)) return null;
      return { day, month, year };
    } catch (_) {
      return null;
    }
  }

  function intlFormat(calendar, date, opts) {
    if (!calendar || !supportsIntlCalendar(calendar)) return null;
    try {
      return new Intl.DateTimeFormat('en', { calendar, ...opts }).format(date);
    } catch (_) {
      return null;
    }
  }

  function monthBucket(item, date) {
    const id = calId(item);
    if (id) {
      try {
        const parts = new Intl.DateTimeFormat('en', {
          calendar: id,
          year: 'numeric',
          month: 'numeric',
        }).formatToParts(date);
        const y = parts.find((p) => p.type === 'year')?.value;
        const m = parts.find((p) => p.type === 'month')?.value;
        if (y != null && m != null) return `${y}-${m}`;
      } catch (_) {}
    }
    const p = resolveParts(item, date);
    return `${p.year}-${p.month}`;
  }

  function gregorianParts(date) {
    return { day: date.getDate(), month: date.getMonth() + 1, year: date.getFullYear() };
  }

  function gregorianJulianDayGap(year) {
    if (year >= 2101) return 14;
    if (year >= 1901) return 13;
    if (year >= 1801) return 12;
    if (year >= 1701) return 11;
    return 10;
  }

  function julianParts(date) {
    const g = gregorianParts(date);
    const probe = new Date(g.year, g.month - 1, g.day);
    probe.setDate(probe.getDate() - gregorianJulianDayGap(g.year));
    return { day: probe.getDate(), month: probe.getMonth() + 1, year: probe.getFullYear() };
  }

  function eraParts(date, yearDelta) {
    const g = gregorianParts(date);
    return { day: g.day, month: g.month, year: g.year + yearDelta };
  }

  function eraYearDelta(item) {
    if (item.fn === 'minguo' || item.fn === 'juche') return -1911;
    if (item.fn === 'bahai') return -1843;
    if (item.fn === 'thai' || item.fn === 'buddhistEra') return 543;
    return 0;
  }

  function resolveParts(item, date) {
    const id = calId(item);
    if (id) {
      const p = intlParts(id, date);
      if (p) return p;
    }
    if (item.fn === 'gregorian') return gregorianParts(date);
    if (item.fn === 'julian') return julianParts(date);
    if (item.fn === 'persian') return intlParts('persian', date) || gregorianParts(date);
    if (item.fn === 'hijriTabular') return intlParts('islamic', date) || gregorianParts(date);
    if (item.fn === 'minguo') return intlParts('roc', date) || eraParts(date, -1911);
    if (item.fn === 'juche') return eraParts(date, -1911);
    if (item.fn === 'bahai') return eraParts(date, -1843);
    if (item.fn === 'thai' || item.fn === 'buddhistEra') {
      return intlParts('buddhist', date) || eraParts(date, 543);
    }
    return gregorianParts(date);
  }

  function usesGregorianGrid(item) {
    if (calId(item)) return false;
    if (item.fn === 'julian') return false;
    return true;
  }

  function collectGregorianMonthDays(gregYear, gregMonth) {
    const days = [];
    const cursor = new Date(gregYear, gregMonth - 1, 1);
    while (cursor.getMonth() === gregMonth - 1) {
      days.push({
        date: new Date(cursor),
        parts: gregorianParts(cursor),
        weekday: cursor.getDay(),
      });
      cursor.setDate(cursor.getDate() + 1);
    }
    return days;
  }

  function collectMonthDaysForBucket(item, bucketKey) {
    const today = new Date();
    let probe = new Date(today);
    for (let i = 0; i < 450; i++) {
      if (monthBucket(item, probe) === bucketKey) break;
      probe.setDate(probe.getDate() - 1);
    }
    for (let i = 0; i < 450; i++) {
      const prev = new Date(probe);
      prev.setDate(prev.getDate() - 1);
      if (monthBucket(item, prev) !== bucketKey) break;
      probe = prev;
    }
    const days = [];
    const cursor = new Date(probe);
    for (let i = 0; i < 45; i++) {
      if (monthBucket(item, cursor) !== bucketKey) break;
      days.push({
        date: new Date(cursor),
        parts: resolveParts(item, cursor),
        weekday: cursor.getDay(),
      });
      cursor.setDate(cursor.getDate() + 1);
    }
    return days;
  }

  function collectMonthDays(item, calYear, calMonth) {
    const id = calId(item);
    const delta = eraYearDelta(item);

    if (id) {
      const bucketKey = `${calYear}-${calMonth}`;
      return collectMonthDaysForBucket(item, bucketKey);
    }

    if (item.fn === 'julian') {
      const bucketKey = `${calYear}-${calMonth}`;
      return collectMonthDaysForBucket(item, bucketKey);
    }

    if (delta && usesGregorianGrid(item)) {
      const gregYear = calYear - delta;
      return collectGregorianMonthDays(gregYear, calMonth).map((d) => ({
        date: d.date,
        weekday: d.weekday,
        parts: {
          day: d.parts.day,
          month: d.parts.month,
          year: d.date.getFullYear() + delta,
        },
      }));
    }

    return collectGregorianMonthDays(calYear, calMonth);
  }

  function buildWeeks(days) {
    if (!days.length) return [];
    const weeks = [];
    let week = new Array(7).fill(null);
    const first = days[0].weekday;
    for (let i = 0; i < first; i++) week[i] = null;
    days.forEach((d) => {
      week[d.weekday] = d;
      if (d.weekday === 6) {
        weeks.push(week);
        week = new Array(7).fill(null);
      }
    });
    if (week.some(Boolean)) weeks.push(week);
    while (weeks.length < 6) weeks.push(new Array(7).fill(null));
    return weeks.slice(0, 6);
  }

  function monthTitle(item, calYear, calMonth, sampleDate) {
    const id = calId(item);
    if (id && sampleDate) {
      const t = intlFormat(id, sampleDate, { month: 'long', year: 'numeric' });
      if (t) return t;
    }
    if (item.note && !id && usesGregorianGrid(item)) {
      const names = [
        '',
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December',
      ];
      return `Gregorian ${names[calMonth] || calMonth} ${calYear}`;
    }
    const names = [
      '',
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];
    return `${names[calMonth] || 'Month ' + calMonth} ${calYear}`;
  }

  function formatToday(item) {
    const id = calId(item);
    if (id) {
      const s = intlFormat(id, new Date(), {
        weekday: 'short',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
      if (s) return s;
    }
    return null;
  }

  function buildMonthGridHtml(item, opts = {}) {
    const compact = Boolean(opts.compact);
    const todayParts = resolveParts(item, new Date());
    const calYear = opts.year ?? todayParts.year;
    const calMonth = opts.month ?? todayParts.month;
    const days = collectMonthDays(item, calYear, calMonth);
    const weeks = buildWeeks(days);
    const sample = days[Math.floor(days.length / 2)]?.date || new Date();
    const dow = compact ? WEEKDAYS : WEEKDAYS_FULL;
    const wrapClass = compact ? 'cal-embed-grid cal-month-grid' : 'cal-month-grid';

    let html = `<div class="${wrapClass}" role="grid" aria-label="Month view">`;
    if (compact) {
      html += `<p class="cal-embed-month">${monthTitle(item, calYear, calMonth, sample)}</p>`;
    }
    html += '<div class="cal-month-dow">';
    dow.forEach((w, i) => {
      html += `<span class="cal-dow" aria-label="${WEEKDAYS_FULL[i]}">${w}</span>`;
    });
    html += '</div><div class="cal-month-weeks">';

    weeks.forEach((week) => {
      html += '<div class="cal-month-row">';
      week.forEach((cell) => {
        if (!cell) {
          html += '<span class="cal-day cal-day-empty" aria-hidden="true"></span>';
          return;
        }
        const isToday = sameDay(cell.parts, todayParts);
        html +=
          `<span class="cal-day${isToday ? ' cal-day-today' : ''}"` +
          ` role="gridcell" aria-current="${isToday ? 'date' : 'false'}"` +
          ` title="${cell.date.toDateString()}">` +
          `<span class="cal-day-num">${cell.parts.day}</span></span>`;
      });
      html += '</div>';
    });
    html += '</div></div>';
    return html;
  }

  /** True when this calendar's month/day today differ from the Gregorian civil date. */
  function differsFromGregorianCivil(item, date = new Date()) {
    if (!item || item.fn === 'gregorian') return false;
    const g = gregorianParts(date);
    const p = resolveParts(item, date);
    if (Number.isNaN(p.day) || Number.isNaN(p.month)) return true;
    return p.day !== g.day || p.month !== g.month;
  }

  global.WorldCalendarMonth = {
    buildHtml: buildMonthGridHtml,
    formatToday,
    resolveParts,
    calId,
    gregorianParts,
    differsFromGregorianCivil,
  };

  document.addEventListener('DOMContentLoaded', () => {});
})(window);
