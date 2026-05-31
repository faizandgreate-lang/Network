/** GitHub Pages (/Network/) vs local server (/) — load first in <head>. */
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

  var RAW = 'https://github.com/faizandgreate-lang/Network/raw/main/';

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

  /** Same layout as localhost; small footer note only on GitHub. */
  function addGitHubFooterNote() {
    if (!global.appIsGitHubPages()) return;
    document.addEventListener('DOMContentLoaded', function () {
      if (document.getElementById('gh-run-note')) return;
      var footer = document.querySelector('.site-footer');
      if (!footer) return;
      var p = document.createElement('p');
      p.id = 'gh-run-note';
      p.className = 'gh-run-note';
      p.innerHTML =
        'This is the same website layout as the desktop app. To <strong>scan Wi‑Fi/LAN</strong> like on localhost: ' +
        '<a class="ext" href="' +
        RAW +
        'zipball/main/">Download ZIP</a> → unzip → double-click <code>START.command</code> (Mac) or <code>START.bat</code> (Windows) → open <code>http://127.0.0.1:5080/</code>.';
      footer.appendChild(p);
    });
  }

  document.addEventListener('DOMContentLoaded', fixDownloadLinks);
  addGitHubFooterNote();
})(window);
