/** GitHub Pages + custom domain — load CSS/JS from the real project URL. */
(function (global) {
  var GITHUB_PAGES_ROOT = 'https://faizandgreate-lang.github.io/Network/';

  function detectAppBase() {
    var host = location.hostname || '';
    if (host === 'localhost' || host === '127.0.0.1') return '/';
    /* Custom domain shows HTML but /static/* 404 — point assets at GitHub project URL */
    if (host === 'network.linux-aios.com') return GITHUB_PAGES_ROOT;
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
  global.__GITHUB_PAGES_ROOT__ = GITHUB_PAGES_ROOT;

  global.appUrl = function (path) {
    if (!path) return base;
    if (/^https?:\/\//i.test(path)) return path;
    var p = path.charAt(0) === '/' ? path.slice(1) : path;
    if (base === '/') return '/' + p;
    if (base.endsWith('/')) return base + p;
    return base + '/' + p;
  };

  global.appIsGitHubPages = function () {
    var h = location.hostname || '';
    return h.endsWith('.github.io') || h === 'network.linux-aios.com';
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
        'Full app (scan Wi‑Fi/LAN): <a class="ext" href="' +
        RAW +
        'zipball/main/">download ZIP</a> → <code>START.command</code> / <code>START.bat</code> → <code>http://127.0.0.1:5080/</code>';
      footer.appendChild(p);
    });
  }

  document.addEventListener('DOMContentLoaded', fixDownloadLinks);
  addGitHubFooterNote();
})(window);
