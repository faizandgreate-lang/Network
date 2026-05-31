/** CSV export only works when the local server is running. */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    if (typeof appIsGitHubPages !== 'function' || !appIsGitHubPages()) return;
    var csv = document.getElementById('dl-csv');
    if (!csv) return;
    csv.href = '#start-downloads';
    csv.setAttribute(
      'title',
      typeof window.t === 'function'
        ? window.t('home.s06.csvHint')
        : 'Start the app with START.command or START.bat, then export CSV from Devices.'
    );
  });
})();
