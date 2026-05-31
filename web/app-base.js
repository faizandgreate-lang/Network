/** GitHub Pages base path (/Network/) vs local server (/) — must load first in <head>. */
(function (global) {
  function detectAppBase() {
    var host = location.hostname || '';
    if (host === 'localhost' || host === '127.0.0.1') return '/';
    if (host.endsWith('.github.io')) {
      var parts = location.pathname.split('/').filter(Boolean);
      if (parts.length && !/\.html?$/i.test(parts[0])) {
        return '/' + parts[0] + '/';
      }
    }
    return '/';
  }

  var base = detectAppBase();
  global.__APP_BASE__ = base;

  global.appUrl = function (path) {
    if (!path) return base;
    if (/^https?:\/\//i.test(path)) return path;
    var p = path.charAt(0) === '/' ? path.slice(1) : path;
    return base === '/' ? '/' + p : base + p;
  };

  global.appIsGitHubPages = function () {
    return (location.hostname || '').endsWith('.github.io');
  };

  if (base !== '/') {
    var b = document.createElement('base');
    b.setAttribute('data-app-base', '1');
    b.href = base;
    var head = document.head || document.getElementsByTagName('head')[0];
    if (head) head.insertBefore(b, head.firstChild);
  }

  function showGitHubBanner() {
    if (!global.appIsGitHubPages()) return;
    document.addEventListener('DOMContentLoaded', function () {
      if (document.getElementById('github-pages-banner')) return;
      var el = document.createElement('div');
      el.id = 'github-pages-banner';
      el.className = 'github-pages-banner';
      el.setAttribute('role', 'status');
      el.innerHTML =
        '<strong>GitHub preview</strong> — layout and pages work here. ' +
        '<strong>Wi‑Fi scan, device list, and downloads</strong> need the app on your computer: ' +
        'clone this repo and double‑click <code>START.command</code> (Mac) or <code>START.bat</code> (Windows), ' +
        'then open <code>http://127.0.0.1:5080/</code>.';
      if (document.body) document.body.insertBefore(el, document.body.firstChild);
    });
  }

  var RAW =
    'https://github.com/faizandgreate-lang/Network/raw/main/';

  function fixDownloadLinks() {
    if (!global.appIsGitHubPages()) return;
    var map = {
      '/api/download/full-mac.zip': RAW + 'data/Network-Monitor-Full-Mac.zip',
      '/api/download/full-windows.zip': RAW + 'data/Network-Monitor-Full-Windows.zip',
      '/api/download/start-command': RAW + 'START.command',
      '/api/download/start-bat': RAW + 'START.bat',
      '/api/download/mac-app.zip': RAW + 'data/Network-Monitor-Full-Mac.zip',
      '/api/download/guide.txt': RAW + 'web/guide.txt',
      '/api/export.csv': '#',
    };
    document.querySelectorAll('a[href^="/api/"]').forEach(function (a) {
      var key = a.getAttribute('href').split('?')[0];
      if (map[key]) a.setAttribute('href', map[key]);
    });
  }

  document.addEventListener('DOMContentLoaded', fixDownloadLinks);
  showGitHubBanner();
})(window);
