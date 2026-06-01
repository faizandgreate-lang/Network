/**
 * Device list — must work on office PCs (no i18n race, no missing appUrl, clear errors).
 */
(function (global) {
  'use strict';

  const $ = function (id) {
    return document.getElementById(id);
  };

  function msg(key, fallback) {
    try {
      if (typeof global.t === 'function') {
        var s = global.t(key);
        if (s && s !== key) return s;
      }
    } catch (e) { /* ignore */ }
    return fallback;
  }

  const TEXT = {
    checking: 'Checking app…',
    refreshing: 'Refreshing…',
    updated: 'Updated',
    scanning: 'Scanning… (30–90 sec)',
    done: 'Scan done',
    scanFailed: 'Scan failed — is START running?',
    offline: 'Start START.bat or START.command → http://127.0.0.1:5080/',
    staticSite: 'Scans need local app: double-click START → http://127.0.0.1:5080/',
    stuck: 'No response — open http://127.0.0.1:5080/ (keep black window open)',
    noDevices: 'No devices yet — click Scan Wi‑Fi + LAN',
  };

  const API_TIMEOUT_MS = 12000;

  function apiPath(path) {
    if (typeof global.appUrl === 'function') return global.appUrl(path);
    if (path.charAt(0) === '/') return path;
    return '/' + path;
  }

  function fetchApi(path, opts) {
    var url = apiPath(path);
    var timeout = new Promise(function (_, reject) {
      setTimeout(function () {
        reject(new Error('timeout'));
      }, API_TIMEOUT_MS);
    });
    var req = fetch(url, opts || {});
    return Promise.race([req, timeout]);
  }

  var filterLink = 'all';
  var lastDevices = [];
  var stuckTimer = null;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function setStatus(text) {
    var chip = $('status-chip');
    if (chip) {
      chip.textContent = text;
      chip.setAttribute('data-i18n-skip', '1');
    }
  }

  function showError(on) {
    var box = $('err-box');
    if (box) box.classList.toggle('show', on);
    var status = $('server-status');
    if (status) status.hidden = !!on;
  }

  function clearStuckTimer() {
    if (stuckTimer) {
      clearTimeout(stuckTimer);
      stuckTimer = null;
    }
  }

  function armStuckTimer() {
    clearStuckTimer();
    stuckTimer = setTimeout(function () {
      setStatus(TEXT.stuck);
      showError(true);
    }, API_TIMEOUT_MS + 2000);
  }

  function isStaticHost() {
    try {
      if (typeof global.appIsGitHubPages === 'function' && global.appIsGitHubPages()) return true;
    } catch (e) { /* ignore */ }
    var h = location.hostname || '';
    return h === 'network.linux-aios.com' || h.endsWith('.github.io');
  }

  function offlineMessage() {
    if (isStaticHost()) return TEXT.staticSite;
    if (location.protocol === 'file:') {
      return 'Do not open the HTML file directly — run START, then http://127.0.0.1:5080/devices.html';
    }
    return TEXT.offline;
  }

  async function loadInfo() {
    var res = await fetchApi('/api/info');
    if (!res.ok) throw new Error('down');
    var info = await res.json();
    showError(false);
    var ifaces = info.interfaces || [];
    var subnet = $('subnet-disp');
    if (subnet) subnet.textContent = ifaces.map(function (i) { return i.link; }).join(' + ') || '—';
    var ifaceList = $('iface-list');
    if (ifaceList) {
      ifaceList.innerHTML = ifaces
        .map(function (i) {
          return (
            '<span class="chip iface-chip"><b>' +
            esc(i.link) +
            '</b> ' +
            esc(i.name) +
            ' <code>' +
            esc(i.ip) +
            '</code></span>'
          );
        })
        .join('');
    }
    var urlList = $('url-list');
    if (urlList) {
      urlList.innerHTML = (info.urls || [])
        .map(function (u) {
          return '<a class="ext" href="' + esc(u) + '">' + esc(u) + '</a>';
        })
        .join('');
    }
    var ws = info.wifi_signal;
    if (ws && ws.rssi_dbm != null && ifaceList) {
      ifaceList.insertAdjacentHTML(
        'afterbegin',
        '<span class="chip iface-chip"><b>Wi‑Fi</b> ' +
          esc(ws.ssid || '') +
          ' · ' +
          esc(ws.rssi_dbm) +
          ' dBm</span>',
      );
    }
  }

  function renderTable(data) {
    lastDevices = data.devices || [];
    var filtered =
      filterLink === 'all' ? lastDevices : lastDevices.filter(function (d) { return d.link === filterLink; });
    var nOn = $('n-on');
    var nOff = $('n-off');
    if (nOn) nOn.textContent = filtered.filter(function (d) { return d.status === 'online'; }).length;
    if (nOff) nOff.textContent = filtered.filter(function (d) { return d.status !== 'online'; }).length;
    var tbody = $('rows');
    if (!tbody) return;
    if (!filtered.length) {
      tbody.innerHTML = '<tr><td colspan="13">' + TEXT.noDevices + '</td></tr>';
      return;
    }
    tbody.innerHTML = filtered
      .map(function (d) {
        var on = d.status === 'online';
        var name = d.device_name || d.hostname || d.vendor || '—';
        var sites = d.top_domains
          ? '<small class="sites-cell">' + esc(d.top_domains) + '</small>'
          : '<small class="sites-cell muted">—</small>';
        return (
          '<tr>' +
          '<td class="' +
          (on ? 'st-on' : 'st-off') +
          '">' +
          (on ? '● ONLINE' : '○ offline') +
          '</td>' +
          '<td>' +
          esc(name) +
          '</td>' +
          '<td><code>' +
          esc(d.ip) +
          '</code></td>' +
          '<td>' +
          sites +
          '</td>' +
          '<td>' +
          esc(d.device_type || '—') +
          '</td>' +
          '<td><small>' +
          esc(d.mac || '—') +
          '</small></td>' +
          '<td>' +
          esc(d.hostname || '—') +
          '</td>' +
          '<td><small>' +
          esc(d.services || '—') +
          '</small></td>' +
          '<td>' +
          (d.latency_ms != null && d.latency_ms !== '' ? esc(d.latency_ms) + ' ms' : '—') +
          '</td>' +
          '<td>' +
          (d.first_seen ? esc(String(d.first_seen).slice(0, 16).replace('T', ' ')) : '—') +
          '</td>' +
          '<td>' +
          (d.last_seen ? esc(String(d.last_seen).slice(0, 16).replace('T', ' ')) : '—') +
          '</td>' +
          '<td><input class="label-in" data-ip="' +
          esc(d.ip) +
          '" value="' +
          esc(d.it_label || '') +
          '" placeholder="Label" /></td>' +
          '<td><a class="btn sec" href="control.html?ip=' +
          encodeURIComponent(d.ip) +
          '">Control</a></td>' +
          '</tr>'
        );
      })
      .join('');
    tbody.querySelectorAll('.label-in').forEach(function (inp) {
      inp.addEventListener('change', function () {
        fetchApi('/api/devices/' + encodeURIComponent(inp.dataset.ip) + '/label', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ label: inp.value }),
        });
      });
    });
  }

  async function loadActivity() {
    try {
      var res = await fetchApi('/api/activity');
      var data = await res.json();
      var events = $('events');
      if (!events) return;
      events.innerHTML = data.events && data.events.length
        ? data.events
            .map(function (e) {
              return '<div class="evt"><b>' + esc(e.event) + '</b> ' + esc(e.ip) + '<br>' + esc(e.detail || '') + '</div>';
            })
            .join('')
        : '—';
    } catch (e) {
      var ev = $('events');
      if (ev) ev.textContent = '—';
    }
  }

  async function refresh(silent) {
    if (isStaticHost() || location.protocol === 'file:') {
      showError(true);
      setStatus(offlineMessage());
      return;
    }
    if (!silent) setStatus(TEXT.refreshing);
    armStuckTimer();
    try {
      var health = await fetchApi('/api/health');
      if (!health.ok) throw new Error('down');
      await loadInfo();
      var devRes = await fetchApi('/api/devices');
      renderTable(await devRes.json());
      await loadActivity();
      clearStuckTimer();
      setStatus(TEXT.updated + ' ' + new Date().toLocaleTimeString());
      showError(false);
    } catch (e) {
      clearStuckTimer();
      showError(true);
      setStatus(offlineMessage());
    }
  }

  function wireControls() {
    var scanBtn = $('scan-btn');
    if (scanBtn) {
      scanBtn.addEventListener('click', function () {
        scanBtn.disabled = true;
        setStatus(TEXT.scanning);
        armStuckTimer();
        fetchApi('/api/scan', { method: 'POST' })
          .then(function (res) {
            return res.json();
          })
          .then(function (data) {
            renderTable(data);
            return loadActivity();
          })
          .then(function () {
            clearStuckTimer();
            setStatus(TEXT.done);
            showError(false);
            var tbl = document.getElementById('devices-table');
            if (tbl) tbl.scrollIntoView({ behavior: 'smooth', block: 'start' });
          })
          .catch(function () {
            clearStuckTimer();
            setStatus(TEXT.scanFailed);
            showError(true);
          })
          .finally(function () {
            scanBtn.disabled = false;
          });
      });
    }

    var refBtn = $('refresh-btn');
    if (refBtn) refBtn.addEventListener('click', function () { refresh(false); });

    var dnsBtn = $('dns-refresh-btn');
    if (dnsBtn) {
      dnsBtn.addEventListener('click', function () {
        dnsBtn.disabled = true;
        setStatus('Loading DNS…');
        fetchApi('/api/dns/refresh', { method: 'POST' })
          .then(function (res) { return res.json(); })
          .then(function (data) {
            renderTable({ devices: data.devices || [] });
            return loadInfo();
          })
          .then(function () {
            setStatus('DNS updated');
          })
          .catch(function () {
            setStatus('DNS refresh failed');
          })
          .finally(function () {
            dnsBtn.disabled = false;
          });
      });
    }

    document.querySelectorAll('[data-filter]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterLink = btn.dataset.filter;
        document.querySelectorAll('[data-filter]').forEach(function (b) {
          b.classList.toggle('active', b === btn);
        });
        renderTable({ devices: lastDevices });
      });
    });
    var allBtn = document.querySelector('[data-filter="all"]');
    if (allBtn) allBtn.classList.add('active');

    document.querySelectorAll('.devices-jump a').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href');
        if (!id || id.charAt(0) !== '#') return;
        var el = document.querySelector(id);
        if (!el) return;
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.replaceState(null, '', id);
      });
    });

    var csv = document.querySelector('a[href="/api/export.csv"]');
    if (csv) csv.setAttribute('href', apiPath('/api/export.csv'));
  }

  function init() {
    setStatus(TEXT.checking);
    showError(true);
    wireControls();
    refresh(false);
  }

  global.addEventListener('error', function () {
    setStatus('Page error — reload after running START');
    showError(true);
  });

  global.addEventListener('locale-change', function () {
    if (lastDevices.length) renderTable({ devices: lastDevices });
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window);
