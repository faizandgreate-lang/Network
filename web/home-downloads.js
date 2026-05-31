/** Step 06 + report links — work on GitHub Pages and localhost. */
(function () {
  function onGitHub() {
    return typeof appIsGitHubPages === 'function' && appIsGitHubPages();
  }

  function u(path) {
    return typeof appUrl === 'function' ? appUrl(path) : path;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var guide = document.getElementById('dl-guide');
    if (guide) {
      guide.href = u('downloads/office-network-monitor-guide.txt');
      guide.setAttribute('download', 'office-network-monitor-guide.txt');
    }

    document.querySelectorAll('a[href="/api/export.csv"], #dl-csv').forEach(function (a) {
      if (onGitHub()) {
        a.href = u('downloads/devices-sample.csv');
        a.setAttribute('download', 'devices-sample.csv');
        a.setAttribute(
          'title',
          typeof window.t === 'function'
            ? window.t('home.s06.csvHint')
            : 'Sample CSV. Start the app and scan, then export real data from Devices.'
        );
      } else {
        a.href = '/api/export.csv';
        a.removeAttribute('download');
      }
    });

    document.querySelectorAll('a[href="#start-downloads"]').forEach(function (a) {
      a.href = 'index.html#start-downloads';
    });

    var hint = document.getElementById('dl-csv-hint');
    if (hint && onGitHub()) hint.hidden = false;
  });
})();
