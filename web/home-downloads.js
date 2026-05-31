/** Step 06 + download links — GitHub Pages and localhost. */
(function () {
  var ZIP = {
    fullMac: 'office-net-monitor by MFK - Mac.zip',
    fullWin: 'office-net-monitor by MFK - Windows.zip',
    macApp: 'office-net-monitor by MFK - Mac app.zip',
  };

  function onGitHub() {
    return typeof appIsGitHubPages === 'function' && appIsGitHubPages();
  }

  function u(path) {
    return typeof appUrl === 'function' ? appUrl(path) : path;
  }

  function dlZip(name) {
    return u('downloads/' + encodeURIComponent(name));
  }

  document.addEventListener('DOMContentLoaded', function () {
    var pairs = [
      ['dl-full-mac', onGitHub() ? dlZip(ZIP.fullMac) : '/api/download/full-mac.zip', ZIP.fullMac],
      ['dl-full-win', onGitHub() ? dlZip(ZIP.fullWin) : '/api/download/full-windows.zip', ZIP.fullWin],
      ['dl-mac-app', onGitHub() ? dlZip(ZIP.macApp) : '/api/download/mac-app.zip', ZIP.macApp],
      ['dl-start-cmd', onGitHub() ? u('downloads/START.command') : '/api/download/start-command', 'START.command'],
      ['dl-start-bat', onGitHub() ? u('downloads/START.bat') : '/api/download/start-bat', 'START.bat'],
    ];

    pairs.forEach(function (row) {
      var el = document.getElementById(row[0]);
      if (!el) return;
      el.href = row[1];
      if (row[2] && row[0].indexOf('dl-full') === 0 || row[0] === 'dl-mac-app') {
        el.setAttribute('download', row[2]);
      }
    });

    var guide = document.getElementById('dl-guide');
    if (guide) {
      guide.href = u('downloads/office-network-monitor-guide.txt');
      guide.setAttribute('download', 'office-network-monitor-guide.txt');
    }

    var gate = document.getElementById('dl-mac-gatekeeper');
    if (gate) {
      gate.href = u('downloads/MAC-GATEKEEPER.txt');
      gate.setAttribute('download', 'MAC-GATEKEEPER.txt');
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
