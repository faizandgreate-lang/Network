/** Retro terminal typing + boot line (respects reduced motion). */
(function () {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function typeInto(el, text, ms) {
    return new Promise((resolve) => {
      if (!el) return resolve();
      if (reduced) {
        el.textContent = text;
        return resolve();
      }
      el.textContent = '';
      let i = 0;
      const tick = () => {
        if (i < text.length) {
          el.textContent += text[i];
          i += 1;
          setTimeout(tick, ms);
        } else {
          resolve();
        }
      };
      tick();
    });
  }

  async function runBoot() {
    const boot = document.getElementById('retro-boot');
    if (!boot) return;
    const tt = (k, fb) => (typeof window.t === 'function' ? window.t(k) : fb);
    const lines = [
      tt('boot.init', '> INITIALIZING NETWORK MONITOR...'),
      tt('boot.load', '> LOADING INTERFACE OK'),
      tt('boot.ready', '> READY'),
    ];
    if (reduced) {
      boot.textContent = lines.join(' ');
      return;
    }
    boot.textContent = '';
    for (const line of lines) {
      const row = document.createElement('div');
      row.className = 'retro-boot-line';
      boot.appendChild(row);
      await typeInto(row, line, 22);
      await new Promise((r) => setTimeout(r, 120));
    }
  }

  async function runTitles() {
    const nodes = document.querySelectorAll('[data-retro-type]');
    for (const el of nodes) {
      const text = el.getAttribute('data-retro-type') || el.textContent.trim();
      el.setAttribute('aria-label', text);
      await typeInto(el, text, 38);
    }
  }

  function wireCursors() {
    document.querySelectorAll('.retro-title-wrap').forEach((wrap) => {
      if (wrap.querySelector('.retro-cursor')) return;
      const cur = document.createElement('span');
      cur.className = 'retro-cursor';
      cur.setAttribute('aria-hidden', 'true');
      wrap.appendChild(cur);
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (document.body?.classList.contains('theme-modern')) return;
    wireCursors();
    runBoot().then(runTitles);
  });
})();
