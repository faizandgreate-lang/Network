/** Apply saved theme on <html> before first paint (avoids flash). */
(function () {
  var modern = true;
  try {
    modern = localStorage.getItem('nm-theme') !== 'retro';
  } catch (_) {}

  document.documentElement.setAttribute('data-app-theme', modern ? 'modern' : 'retro');
  document.documentElement.classList.toggle('theme-modern-boot', modern);
  document.documentElement.style.backgroundColor = modern ? '#ffffff' : '#000000';

  function applyBodyThemeEarly() {
    if (!document.body) return;
    if (modern) {
      document.body.classList.add('theme-modern');
      document.body.classList.remove('retro-terminal', 'retro-mono');
    } else {
      document.body.classList.remove('theme-modern');
      document.body.classList.add('retro-terminal', 'retro-mono');
    }
  }

  if (document.body) applyBodyThemeEarly();
  else document.addEventListener('DOMContentLoaded', applyBodyThemeEarly);
})();
