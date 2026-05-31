/** Apply saved theme on <html> before first paint (avoids flash). */
(function () {
  try {
    var t = localStorage.getItem('nm-theme');
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
})();
