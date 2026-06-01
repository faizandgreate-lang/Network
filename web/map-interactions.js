/** Node click — show every field we have from scans (honest: no web browsing history). */
function mapT(key, vars) {
  return typeof window.t === 'function' ? window.t(key, vars) : key;
}

function escHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const DEVICE_FIELDS = [
  ['Device name (best guess)', 'device_name'],
  ['IP address', 'ip'],
  ['Status', 'status'],
  ['MAC address', 'mac'],
  ['Hostname (DNS)', 'hostname'],
  ['IT label (your name)', 'it_label'],
  ['Vendor (OUI)', 'vendor'],
  ['Device type', 'device_type'],
  ['Device fingerprint', 'device_fingerprint'],
  ['Network link', 'link'],
  ['Interface', 'interface_name'],
  ['Subnet scanned', 'subnet'],
  ['Open ports / services', 'services'],
  ['Frequent sites (DNS log)', 'top_domains'],
  ['DNS data source', 'dns_source'],
  ['Ping from this PC (ms)', 'latency_ms'],
  ['First seen (connected)', 'first_seen'],
  ['Last seen (connected)', 'last_seen'],
  ['Session span (our scans)', 'session_duration'],
  ['Times seen in scans', 'scan_count'],
  ['How found', 'source'],
  ['Scan notes', 'notes'],
  ['Device key', 'device_key'],
];

function linkLabel(link) {
  if (link === 'wifi') return 'Wi‑Fi';
  if (link === 'ethernet') return 'LAN (Ethernet)';
  if (link === 'other') return 'Other';
  return link || '—';
}

function fmtVal(key, val) {
  if (val === null || val === undefined || val === '') return '—';
  if (key === 'link') return linkLabel(val);
  if (key === 'status') return val === 'online' ? '● ONLINE' : '○ offline';
  if (key === 'first_seen' || key === 'last_seen') {
    const s = String(val);
    return s.length > 19 ? s.slice(0, 19).replace('T', ' ') : s;
  }
  return String(val);
}

function detailSection(title, rowsHtml) {
  return `<h3 class="detail-section">${escHtml(title)}</h3><table class="detail-table">${rowsHtml}</table>`;
}

function rowsFromObject(obj, fields) {
  return fields
    .map(([label, key]) => {
      const v = fmtVal(key, obj[key]);
      return `<tr><th>${escHtml(label)}</th><td>${escHtml(v)}</td></tr>`;
    })
    .join('');
}

function extractIp(text) {
  const m = String(text || '').match(/\b(\d{1,3}(?:\.\d{1,3}){3})\b/);
  return m ? m[1] : null;
}

async function fetchDeviceBundle(ip) {
  try {
    const res = await fetch(appUrl('/api/devices/by-ip/' + encodeURIComponent(ip)));
    if (res.ok) return await res.json();
  } catch (_) {}
  return null;
}

async function fetchServerInfo() {
  try {
    const res = await fetch(appUrl('/api/info'));
    if (res.ok) return await res.json();
  } catch (_) {}
  return null;
}

function activityHtml(events) {
  if (!events?.length) {
    return '<p class="sub">No activity log entries for this IP yet.</p>';
  }
  return (
    '<ul class="detail-activity">' +
    events
      .map(
        (e) =>
          `<li><b>${escHtml(e.event)}</b> · ${escHtml(e.logged_at || '')}<br>${escHtml(e.detail || '')}</li>`,
      )
      .join('') +
    '</ul>'
  );
}

function networkMeasurementsHtml(nm) {
  if (!nm) return '';
  const gw = nm.gateway_ms != null ? `${nm.gateway_ms} ms` : '—';
  const inet = nm.internet_ms != null ? `${nm.internet_ms} ms` : '—';
  return (
    detailSection(
      'Network latency (measured from this PC)',
      `<tr><th>Gateway ${escHtml(nm.gateway_ip || '')}</th><td>${escHtml(gw)} ping</td></tr>` +
        `<tr><th>Internet (1.1.1.1 / 8.8.8.8)</th><td>${escHtml(inet)} ping</td></tr>` +
        `<tr><th>Measured at</th><td>${escHtml((nm.measured_at || '').slice(0, 19).replace('T', ' '))}</td></tr>`,
    )
  );
}

function fullDeviceDetailHtml(bundle, meta) {
  const d = bundle.device || (bundle.devices && bundle.devices[0]);
  let html = '';

  if (bundle.devices?.length > 1) {
    html += `<p class="detail-lead">This IP appears on <strong>${bundle.devices.length}</strong> scan paths (Wi‑Fi/LAN).</p>`;
    bundle.devices.forEach((dev, i) => {
      html += detailSection(`Record ${i + 1}`, rowsFromObject(dev, DEVICE_FIELDS));
    });
  } else if (d) {
    html += detailSection('Everything we detected for this device', rowsFromObject(d, DEVICE_FIELDS));
  } else {
    html += `<p class="sub">No database row for <strong>${escHtml(bundle.ip)}</strong>. Run <a class="ext" href="devices.html">Scan Wi‑Fi + LAN</a> first.</p>`;
  }

  if (bundle.interfaces?.length) {
    const ifaceRows = bundle.interfaces
      .map(
        (i) =>
          `<tr><th>${escHtml(linkLabel(i.link))}</th><td>${escHtml(i.name)} · ${escHtml(i.ip)} · ${escHtml(i.subnet || '')}</td></tr>`,
      )
      .join('');
    html += detailSection('Your PC interfaces (this scan)', ifaceRows);
  }

  if (bundle.subnet_info) {
    const si = bundle.subnet_info;
    const sub = typeof si === 'string' ? si : (si.subnets || []).join(' · ') || '—';
    html += detailSection('Network summary', `<tr><th>Subnets</th><td>${escHtml(sub)}</td></tr>`);
  }
  if (bundle.gateway) {
    html += `<table class="detail-table"><tr><th>Default gateway</th><td>${escHtml(bundle.gateway)}</td></tr></table>`;
  }

  html += '<h3 class="detail-section">Activity log (this IP)</h3>' + activityHtml(bundle.activity);

  html += networkMeasurementsHtml(bundle.network_measurements || meta?.network_measurements);
  if (bundle.wifi_signal?.rssi_dbm != null) {
    html += detailSection(
      'Wi‑Fi signal (this monitor Mac only)',
      `<tr><th>SSID</th><td>${escHtml(bundle.wifi_signal.ssid || '—')}</td></tr>` +
        `<tr><th>RSSI</th><td>${escHtml(bundle.wifi_signal.rssi_dbm)} dBm</td></tr>` +
        `<tr><th>Note</th><td>${escHtml(bundle.wifi_signal.note || '')}</td></tr>`,
    );
  }
  html += `<p class="sub"><a class="ext" href="devices.html">Open full device list</a> · <a class="ext" href="devices.html">Download CSV</a></p>`;
  return html;
}

function internetDetailHtml(info, meta, allDevices) {
  const si = info?.subnet_info || {};
  const gw = si.gateway || meta?.gateway || '—';
  const subnets = (si.subnets || []).join(' · ') || '—';
  const ifaces = info?.interfaces || si.interfaces || [];
  let html = detailSection(
    'Internet / WAN (your uplink)',
    `<tr><th>Role</th><td>Connection to the public internet — all LAN devices reach the web through your gateway.</td></tr>` +
      `<tr><th>Default gateway</th><td>${escHtml(gw)}</td></tr>` +
      `<tr><th>Scan subnet(s)</th><td>${escHtml(subnets)}</td></tr>` +
      `<tr><th>Devices online</th><td>${escHtml(meta?.online ?? '—')}</td></tr>` +
      `<tr><th>Devices offline in DB</th><td>${escHtml(meta?.offline ?? '—')}</td></tr>` +
      `<tr><th>This monitor PC</th><td>${escHtml(meta?.monitor_ip || info?.lan_ip || si.this_pc || '—')}</td></tr>` +
      `<tr><th>Dashboard URL</th><td>${escHtml((info?.urls || []).join(' · ') || 'http://127.0.0.1:5080/')}</td></tr>`,
  );

  if (ifaces.length) {
    html += detailSection(
      'Local interfaces on this PC',
      ifaces
        .map(
          (i) =>
            `<tr><th>${escHtml(linkLabel(i.link))}</th><td>${escHtml(i.device)} / ${escHtml(i.name)} — ${escHtml(i.ip)} (${escHtml(i.subnet || '')})</td></tr>`,
        )
        .join(''),
    );
  }

  const online = (allDevices || []).filter((d) => d.status === 'online');
  if (online.length) {
    html += '<h3 class="detail-section">All online devices (from last scan)</h3>';
    html += '<table class="detail-table detail-table-compact"><tr><th>IP</th><th>Info</th></tr>';
    online.forEach((d) => {
      const info = [d.hostname, d.vendor, d.it_label, linkLabel(d.link)].filter(Boolean).join(' · ');
      html += `<tr><th>${escHtml(d.ip)}</th><td>${escHtml(info || '—')}</td></tr>`;
    });
    html += '</table>';
  }

  html += networkMeasurementsHtml(meta?.network_measurements || info?.network_measurements);
  const ws = info?.wifi_signal;
  if (ws?.rssi_dbm != null) {
    html += detailSection(
      'Wi‑Fi signal (this monitor Mac only)',
      `<tr><th>SSID</th><td>${escHtml(ws.ssid || '—')}</td></tr>` +
        `<tr><th>RSSI</th><td>${escHtml(ws.rssi_dbm)} dBm</td></tr>`,
    );
  }
  return html;
}

function segmentDetailHtml(node, allDevices) {
  const link = (node.id || '').replace(/^link_/, '');
  const onLink = (allDevices || []).filter((d) => (d.link || 'unknown') === link);
  let html = `<p class="detail-lead">${escHtml(node.label || link)} — ${onLink.length} device(s) on this link in the database.</p>`;
  if (onLink.length) {
    html += '<table class="detail-table"><tr><th>IP</th><th>Details</th></tr>';
    onLink.forEach((d) => {
      html += `<tr><th>${escHtml(d.ip)}</th><td>${escHtml([d.status, d.hostname, d.mac, d.services].filter(Boolean).join(' · ') || '—')}</td></tr>`;
    });
    html += '</table>';
  }
  html += '<p class="sub">Click a device box on the map for full fields per IP.</p>';
  return html;
}

async function openMapDetail(node, meta) {
  const panel = document.getElementById('map-detail');
  const title = document.getElementById('map-detail-title');
  const body = document.getElementById('map-detail-body');
  if (!panel || !title || !body) return;

  const label = (node.label || node.id || 'Details').replace(/<br\s*\/?>/gi, ' · ');
  title.textContent = label;
  body.innerHTML = '<p class="sub">' + escHtml(mapT('map.detail.loading')) + '</p>';
  panel.classList.add('open');
  panel.setAttribute('aria-hidden', 'false');

  const allDevices = window.mapDeviceCache || [];
  let html = '';

  try {
    if (node.type === 'cloud' || node.id === 'internet') {
      const info = await fetchServerInfo();
      html = internetDetailHtml(info, meta, allDevices);
    } else if (node.type === 'segment' && node.id?.startsWith('link_')) {
      html = segmentDetailHtml(node, allDevices);
    } else if (node.type === 'offline_device' && node.device) {
      html = fullDeviceDetailHtml(
        {
          ip: node.device.ip,
          device: node.device,
          devices: [node.device],
          activity: [],
          network_measurements: meta?.network_measurements,
        },
        meta,
      );
    } else {
      const ip =
        node.device?.ip ||
        node.gateway_ip ||
        extractIp(node.label) ||
        extractIp(node.id);
      if (ip) {
        const bundle = await fetchDeviceBundle(ip);
        if (bundle) {
          bundle.network_measurements = meta?.network_measurements;
          bundle.wifi_signal = bundle.wifi_signal || meta?.wifi_signal;
          title.textContent =
            (bundle.device?.device_name || ip) +
            (bundle.device?.it_label && bundle.device.it_label !== bundle.device?.device_name
              ? ' · ' + bundle.device.it_label
              : '');
          html = fullDeviceDetailHtml(bundle, meta);
        } else if (node.device) {
          html = fullDeviceDetailHtml({ ip, device: node.device, devices: [node.device], activity: [] }, meta);
        } else {
          html = `<p class="sub">Could not load data for ${escHtml(ip)}.</p>`;
        }
      } else if (node.device) {
        html = fullDeviceDetailHtml(
          { ip: node.device.ip, device: node.device, devices: [node.device], activity: [] },
          meta,
        );
      } else if (node.type === 'offline') {
        html = `<p class="sub">${escHtml(node.label)}</p><p class="sub">See <a class="ext" href="devices.html">device list</a> for offline devices.</p>`;
      } else if (node.id === 'more') {
        html =
          '<p class="sub">More devices exist than shown on the map. Open the device list for the full table.</p>' +
          `<p><a class="ext" href="devices.html">Device list</a></p>`;
      } else {
        html = `<p class="sub">${escHtml(node.label || node.id)}</p>`;
      }
    }
  } catch (err) {
    html = `<p class="err-inline">${escHtml(err.message)}</p>`;
  }

  body.innerHTML = html;
}

function closeMapDetail() {
  const panel = document.getElementById('map-detail');
  if (!panel) return;
  panel.classList.remove('open');
  panel.setAttribute('aria-hidden', 'true');
}

function resolveMapNode(el, nodes, allDevices) {
  const text = (el.textContent || '').replace(/\s+/g, ' ').trim();
  if (!text) return null;
  if (/^Internet$/i.test(text) || (text.includes('Internet') && text.length < 24)) {
    return nodes.find((n) => n.id === 'internet');
  }
  if (/^Offline in DB/i.test(text)) return nodes.find((n) => n.id === 'offline');
  if (/more \(device list\)/i.test(text)) return nodes.find((n) => n.id === 'more');
  if (/^This PC /i.test(text)) return nodes.find((n) => n.id === 'monitor');
  if (/^Gateway /i.test(text)) {
    return nodes.find((n) => n.id === 'gateway');
  }
  const ip = extractIp(text);
  if (ip) {
    let n = nodes.find((n) => n.device?.ip === ip || n.gateway_ip === ip);
    if (n) return n;
    n = nodes.find((n) => extractIp(n.label) === ip);
    if (n) return n;
    const dev = (allDevices || []).find((d) => d.ip === ip);
    if (dev) return { id: `ip_${ip}`, label: text, type: 'device', device: dev };
  }
  for (const n of nodes) {
    if (n.type === 'segment' && n.label && text.startsWith(String(n.label).split(' (')[0])) {
      return n;
    }
  }
  return nodes.find((n) => n.label === text) || null;
}

function wireMapNodeClicks(container, meta) {
  const svg = container.querySelector('svg');
  if (!svg || !meta?.nodes?.length) return;
  const nodes = meta.nodes;
  const allDevices = window.mapDeviceCache || [];
  svg.querySelectorAll('g.node').forEach((el) => {
    const n = resolveMapNode(el, nodes, allDevices);
    if (!n) return;
    el.style.cursor = 'pointer';
    el.setAttribute('data-map-node', n.id || '');
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      openMapDetail(n, meta);
    });
  });
}

window.mapLoadDeviceCache = async function () {
  try {
    const res = await fetch(appUrl('/api/devices'));
    if (res.ok) {
      const data = await res.json();
      window.mapDeviceCache = data.devices || [];
    }
  } catch (_) {
    window.mapDeviceCache = [];
  }
};

function toggleMapExpand() {
  const page = document.querySelector('.map-page');
  const btn = document.getElementById('map-expand-btn');
  if (!page) return;
  const on = page.classList.toggle('map-expanded');
  if (btn) btn.textContent = on ? mapT('map.exitExpand') : mapT('map.expand');
  const runFit = () => window.mapFitAll && window.mapFitAll();
  requestAnimationFrame(() => {
    runFit();
    setTimeout(runFit, 150);
  });
}

async function downloadMapPdf() {
  const svg = document.querySelector('#map-diagram svg');
  const status = document.getElementById('map-status');
  if (!svg) {
    if (status) status.textContent = mapT('map.pdf.none');
    return;
  }
  if (!window.jspdf?.jsPDF) {
    if (status) status.textContent = mapT('map.pdf.lib');
    return;
  }
  try {
    if (status) status.textContent = mapT('map.pdf.creating');
    const clone = svg.cloneNode(true);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    const box = svg.getBBox();
    const w = Math.max(box.width + 40, 800);
    const h = Math.max(box.height + 40, 500);
    const { jsPDF } = window.jspdf;
    const landscape = w > h;
    const doc = new jsPDF({
      orientation: landscape ? 'landscape' : 'portrait',
      unit: 'pt',
      format: 'a4',
    });
    const pageW = doc.internal.pageSize.getWidth();
    const pageH = doc.internal.pageSize.getHeight();
    const margin = 24;
    const scale = Math.min((pageW - margin * 2) / w, (pageH - margin * 2) / h);
    if (typeof doc.svg === 'function') {
      await doc.svg(clone, {
        x: margin,
        y: margin,
        width: w * scale,
        height: h * scale,
      });
    } else if (window.svg2pdf) {
      await window.svg2pdf(clone, doc, {
        x: margin,
        y: margin,
        width: w * scale,
        height: h * scale,
      });
    } else {
      throw new Error('svg2pdf not loaded');
    }
    doc.save('office-network-map.pdf');
    if (status) status.textContent = mapT('map.pdf.done');
  } catch (err) {
    if (status) status.textContent = mapT('map.pdf.fail');
    console.error(err);
  }
}

function syncMapExpandLabel() {
  const page = document.querySelector('.map-page');
  const btn = document.getElementById('map-expand-btn');
  if (!btn || !page) return;
  const on = page.classList.contains('map-expanded');
  btn.textContent = on ? mapT('map.exitExpand') : mapT('map.expand');
}

function initMapUi() {
  document.getElementById('map-detail-close')?.addEventListener('click', closeMapDetail);
  document.getElementById('map-expand-btn')?.addEventListener('click', toggleMapExpand);
  document.getElementById('map-fit-btn')?.addEventListener('click', () => window.mapFitAll?.());
  document.getElementById('map-pdf-btn')?.addEventListener('click', downloadMapPdf);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMapDetail();
  });
  window.addEventListener('locale-change', syncMapExpandLabel);
}

document.addEventListener('DOMContentLoaded', initMapUi);
