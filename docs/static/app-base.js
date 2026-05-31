/** GitHub Pages: same /static/ and /assets/ paths as http://127.0.0.1:5080/ */
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
    if (host === 'network.linux-aios.com') {
      return 'https://faizandgreate-lang.github.io/Network/';
    }
    return '/';
  }

  var base = detectAppBase();
  global.__APP_BASE__ = base;

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

  if (base !== '/' && !/^https?:/i.test(String(base))) {
    var b = document.createElement('base');
    b.href = base;
    var head = document.head;
    if (head) head.insertBefore(b, head.firstChild);
  } else if (/^https?:/i.test(String(base))) {
    var b2 = document.createElement('base');
    b2.href = base;
    var head2 = document.head;
    if (head2) head2.insertBefore(b2, head2.firstChild);
  }
})(window);
