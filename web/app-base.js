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
      return '/';
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

  /* No <base> tag — it breaks #anchors (step 06 “Mac / PC starters”) on GitHub Pages. */
})(window);
