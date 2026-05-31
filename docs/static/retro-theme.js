/** @deprecated — use /static/app-theme.js */
(function (global) {
  if (global.AppTheme) return;
  var el = document.createElement('script');
  el.src = typeof appUrl === 'function' ? appUrl('/static/app-theme.js') : 'static/app-theme.js';
  el.async = false;
  (document.head || document.documentElement).appendChild(el);
})();
