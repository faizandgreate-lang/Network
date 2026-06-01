/** Retro terminal + Modern UI themes — persisted in localStorage. */
(function (global) {
  const STORAGE_KEY = 'nm-theme';
  const GREEN = '#33ff66';
  const MODERN_ACCENT = '#2596be';
  const MODERN_OK = '#509591';
  const OFFLINE = '#f43f5e';

  function getStored() {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'retro' ? 'retro' : 'modern';
    } catch (_) {
      return 'modern';
    }
  }

  function isModern() {
    return document.body?.classList.contains('theme-modern');
  }

  function dispatchChange() {
    const modern = isModern();
    const detail = {
      theme: modern ? 'modern' : 'retro',
      modern,
      mono: !modern,
      accent: modern ? MODERN_ACCENT : GREEN,
    };
    document.documentElement.dataset.appTheme = detail.theme;
    global.dispatchEvent(new CustomEvent('retro-theme-change', { detail }));
    global.dispatchEvent(new CustomEvent('app-theme-change', { detail }));
  }

  function applyRetro() {
    document.documentElement.removeAttribute('data-force-modern');
    document.documentElement.dataset.appTheme = 'retro';
    document.documentElement.classList.remove('theme-modern-boot');
    document.body.classList.remove('theme-modern');
    document.body.classList.add('retro-terminal', 'retro-mono');
    document.documentElement.dataset.retroTheme = 'mono';
    if (global.RetroAssets?.applyImages) global.RetroAssets.applyImages(true);
    dispatchChange();
  }

  function applyModern() {
    document.documentElement.removeAttribute('data-force-modern');
    document.documentElement.dataset.appTheme = 'modern';
    document.documentElement.classList.add('theme-modern-boot');
    document.body.classList.remove('retro-terminal', 'retro-mono');
    document.body.classList.add('theme-modern');
    document.documentElement.dataset.retroTheme = 'modern';
    if (global.RetroAssets?.applyModernImages) {
      global.RetroAssets.applyModernImages();
    } else if (global.RetroAssets?.applyImages) {
      global.RetroAssets.applyImages(false);
    }
    dispatchChange();
  }

  function applyTheme(name) {
    const next = name === 'modern' ? 'modern' : 'retro';
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (_) {}
    if (next === 'modern') applyModern();
    else applyRetro();
    updateToggleUi();
  }

  function toggleTheme() {
    applyTheme(isModern() ? 'retro' : 'modern');
  }

  function updateToggleUi() {
    const btn = document.getElementById('theme-toggle');
    const label = btn?.querySelector('.theme-toggle-label');
    if (!btn || !label) return;
    const modern = isModern();
    label.textContent =
      typeof global.t === 'function'
        ? global.t(modern ? 'theme.retro' : 'theme.modern')
        : modern
          ? 'Retro'
          : 'Modern';
    btn.setAttribute(
      'aria-label',
      typeof global.t === 'function'
        ? global.t(modern ? 'theme.ariaToRetro' : 'theme.ariaToModern')
        : modern
          ? 'Switch to retro terminal theme'
          : 'Switch to modern theme',
    );
    btn.classList.toggle('theme-is-modern', modern);
  }

  function ensureThemeToggle() {
    const nav = document.querySelector('.site-nav');
    if (!nav || document.getElementById('theme-toggle')) return;
    const picker = nav.querySelector('.lang-picker');
    const wrap = document.createElement('div');
    wrap.className = 'theme-picker';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn theme-toggle-btn';
    btn.id = 'theme-toggle';
    btn.innerHTML =
      '<span class="theme-toggle-label" data-i18n="theme.modern">Modern</span>';
    btn.setAttribute('data-i18n', '');
    btn.addEventListener('click', toggleTheme);
    wrap.appendChild(btn);
    if (picker) nav.insertBefore(wrap, picker);
    else nav.appendChild(wrap);
    if (global.I18n?.apply) global.I18n.apply(document);
    updateToggleUi();
  }

  function initTheme() {
    if (!document.body) return;
    const stored = getStored();
    if (stored === 'modern') applyModern();
    else {
      if (!document.body.classList.contains('retro-terminal')) {
        document.body.classList.add('retro-terminal', 'retro-mono');
      }
      document.documentElement.dataset.appTheme = 'retro';
      document.documentElement.dataset.retroTheme = 'mono';
      if (global.RetroAssets?.applyImages) global.RetroAssets.applyImages(true);
      dispatchChange();
    }
    ensureThemeToggle();
    updateToggleUi();
  }

  global.AppTheme = {
    get: getStored,
    isModern,
    apply: applyTheme,
    toggle: toggleTheme,
  };

  global.RetroTheme = {
    accent: () => (isModern() ? MODERN_ACCENT : GREEN),
    ok: () => (isModern() ? MODERN_OK : GREEN),
    offlineStroke: () => OFFLINE,
    isMono: () => !isModern() && document.body?.classList.contains('retro-mono'),
    isModern,
    apply: applyTheme,
    init: initTheme,
  };

  global.addEventListener('i18n-applied', updateToggleUi);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }
})(window);
