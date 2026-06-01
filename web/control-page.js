(function (global) {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var currentIp = '';
  var API_MS = 15000;

  function api(path, opts) {
    var url = typeof appUrl === 'function' ? appUrl(path) : path;
    var t = new Promise(function (_, rej) {
      setTimeout(function () { rej(new Error('timeout')); }, API_MS);
    });
    return Promise.race([fetch(url, opts || {}), t]);
  }

  function log(obj) {
    var el = $('log-out');
    if (!el) return;
    el.textContent = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
  }

  function setStatus(t) {
    var c = $('status-chip');
    if (c) c.textContent = t;
  }

  function showErr(on) {
    var b = $('err-box');
    if (b) b.classList.toggle('show', on);
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function getIp() {
    return ($('ip-input') && $('ip-input').value.trim()) || '';
  }

  function applyQueryIp() {
    var m = /[?&]ip=([^&]+)/.exec(location.search);
    if (m) {
      try {
        $('ip-input').value = decodeURIComponent(m[1]);
      } catch (e) {
        $('ip-input').value = m[1];
      }
    }
  }

  function fillDetail(dev, links) {
    var title = $('detail-title');
    var meta = $('detail-meta');
    var svc = $('services-text');
    if (!dev) {
      if (title) title.textContent = 'IP ' + getIp();
      if (meta) meta.textContent = 'Not in scan database — you can still ping / wake / HTTP.';
      if (svc) svc.textContent = '—';
    } else {
      var name = dev.it_label || dev.device_name || dev.hostname || dev.vendor || dev.ip;
      if (title) title.textContent = name;
      if (meta) {
        meta.textContent =
          dev.ip +
          (dev.mac ? ' · ' + dev.mac : '') +
          (dev.device_type ? ' · ' + dev.device_type : '') +
          (dev.link ? ' · ' + dev.link : '');
      }
      if (svc) svc.textContent = dev.services || '—';
      if ($('mac-input') && dev.mac && !$('mac-input').value) $('mac-input').value = dev.mac;
    }
    var box = $('quick-links');
    if (!box) return;
    box.innerHTML = (links || []).map(function (l) {
      return '<a class="btn sec" href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label) + '</a>';
    }).join('');
  }

  function loadDevice() {
    var ip = getIp();
    if (!ip) {
      setStatus('Enter an IP');
      return;
    }
    currentIp = ip;
    setStatus('Loading…');
    api('/api/control/device/' + encodeURIComponent(ip))
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        showErr(false);
        fillDetail(data.device, data.links);
        setStatus('Ready — ' + ip);
      })
      .catch(function (e) {
        showErr(true);
        setStatus('Server offline');
        log(String(e));
      });
  }

  function postJson(path, body) {
    return api(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) throw new Error(j.detail || j.error || 'Request failed');
        return j;
      });
    });
  }

  function actionPing() {
    var ip = getIp();
    if (!ip) return;
    setStatus('Pinging…');
    postJson('/api/control/ping', { ip: ip })
      .then(function (d) {
        log(d);
        setStatus(d.online ? 'Online — ' + d.latency_ms + ' ms' : 'Offline');
      })
      .catch(function (e) {
        log(e.message);
        setStatus('Failed');
      });
  }

  function actionWake() {
    var ip = getIp();
    var mac = $('mac-input') && $('mac-input').value.trim();
    if (!ip) return;
    setStatus('Sending Wake-on-LAN…');
    postJson('/api/control/wake', { ip: ip, mac: mac || null })
      .then(function (d) {
        log(d);
        setStatus(d.ok ? 'Wake sent' : 'Wake failed');
      })
      .catch(function (e) {
        log(e.message);
        setStatus('Failed');
      });
  }

  function actionProbe() {
    var ip = getIp();
    if (!ip) return;
    setStatus('Checking ports…');
    postJson('/api/control/probe', { ip: ip })
      .then(function (d) {
        log(d);
        if ($('services-text')) $('services-text').textContent = d.services || '—';
        setStatus('Ports checked');
      })
      .catch(function (e) {
        log(e.message);
        setStatus('Failed');
      });
  }

  function actionHttp() {
    var ip = getIp();
    if (!ip) return;
    setStatus('HTTP…');
    postJson('/api/control/http', {
      ip: ip,
      port: parseInt($('http-port').value, 10) || 80,
      method: $('http-method').value,
      path: $('http-path').value || '/',
      use_https: $('http-https') && $('http-https').checked,
    })
      .then(function (d) {
        log(d);
        setStatus('HTTP done');
      })
      .catch(function (e) {
        log(e.message);
        setStatus('Failed');
      });
  }

  function loadDeviceList() {
    api('/api/devices')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        showErr(false);
        var sel = $('device-select');
        if (!sel) return;
        var devs = data.devices || [];
        sel.innerHTML = '<option value="">— Select device —</option>';
        devs.forEach(function (d) {
          var opt = document.createElement('option');
          opt.value = d.ip;
          var label = (d.it_label || d.hostname || d.vendor || d.ip) + ' (' + d.ip + ')';
          opt.textContent = label;
          sel.appendChild(opt);
        });
      })
      .catch(function () {
        showErr(true);
      });
  }

  function init() {
    applyQueryIp();
    loadDeviceList();
    if (getIp()) loadDevice();

    $('load-btn') && $('load-btn').addEventListener('click', loadDevice);
    $('device-select') &&
      $('device-select').addEventListener('change', function () {
        if ($('device-select').value) {
          $('ip-input').value = $('device-select').value;
          loadDevice();
        }
      });
    $('btn-ping') && $('btn-ping').addEventListener('click', actionPing);
    $('btn-wake') && $('btn-wake').addEventListener('click', actionWake);
    $('btn-probe') && $('btn-probe').addEventListener('click', actionProbe);
    $('btn-http') && $('btn-http').addEventListener('click', actionHttp);

    api('/api/health')
      .then(function (r) {
        if (r.ok) showErr(false);
        else showErr(true);
      })
      .catch(function () { showErr(true); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window);
