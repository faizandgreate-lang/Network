/** Apply saved theme on <html> before first paint (avoids flash). */
(function () {
  var path = (location.pathname || '').toLowerCase();
  var forceModernPage = /calendar\.html|clock\.html|devices\.html|map\.html|\/calendar|\/clock|\/devices|\/map/.test(path);

  if (forceModernPage) {
    document.documentElement.setAttribute('data-force-modern', '1');
    document.documentElement.setAttribute('data-app-theme', 'modern');
    document.documentElement.classList.add('theme-modern-boot');
    document.documentElement.style.backgroundColor = '#ffffff';
  }

  try {
    var t = forceModernPage ? 'modern' : localStorage.getItem('nm-theme');
    if (t === 'retro') {
      document.documentElement.setAttribute('data-app-theme', 'retro');
      document.documentElement.classList.remove('theme-modern-boot');
      document.documentElement.style.backgroundColor = '#000000';
    } else {
      document.documentElement.setAttribute('data-app-theme', 'modern');
      document.documentElement.classList.add('theme-modern-boot');
      document.documentElement.style.backgroundColor = '#ffffff';
    }
  } catch (_) {
    document.documentElement.setAttribute('data-app-theme', 'modern');
    document.documentElement.classList.add('theme-modern-boot');
    document.documentElement.style.backgroundColor = '#ffffff';
  }

  function applyBodyThemeEarly() {
    if (!document.body) return;
    var modern = document.documentElement.getAttribute('data-app-theme') === 'modern';
    if (modern) {
      document.body.classList.add('theme-modern');
      document.body.classList.remove('retro-terminal', 'retro-mono');
    }
  }

  if (document.body) applyBodyThemeEarly();
  else document.addEventListener('DOMContentLoaded', applyBodyThemeEarly);
})();
