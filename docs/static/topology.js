/** Map from scanned device rows only — no guessed groups. */
function escM(s) {
  return String(s ?? '').replace(/"/g, "'").replace(/\[/g, '(').replace(/\]/g, ')');
}

function deviceLabel(d) {
  const parts = [d.ip];
  if (d.hostname) parts.push(String(d.hostname).slice(0, 20));
  else if (d.vendor) parts.push(String(d.vendor).slice(0, 16));
  if (d.latency_ms != null && d.latency_ms !== '') parts.push(d.latency_ms + 'ms');
  return parts.join(' ').slice(0, 48);
}

function buildMermaidFromScan(devices, info) {
  const online = (devices || []).filter((d) => d.status === 'online');
  const offline = (devices || []).length - online.length;
  const gateway = info?.subnet_info?.gateway || info?.gateway || null;

  const stroke =
    typeof RetroTheme !== 'undefined' && RetroTheme.accent ? RetroTheme.accent() : '#33ff66';
  const offStroke =
    typeof RetroTheme !== 'undefined' && RetroTheme.offlineStroke
      ? RetroTheme.offlineStroke()
      : '#ff5555';

  const lines = [
    "%%{init: {'flowchart': {'rankSpacing': 65, 'nodeSpacing': 45}, 'themeVariables': {'fontSize': '16px'}}}%%",
    'flowchart LR',
    `  classDef cloud fill:#000,stroke:${stroke},color:#fff`,
    `  classDef router fill:#000,stroke:${stroke},color:#fff`,
    `  classDef segment fill:#000,stroke:${stroke},color:#fff`,
    '  classDef device fill:#000,stroke:#fff,color:#fff',
    `  classDef offline fill:#000,stroke:${offStroke},color:#fff`,
    '  internet(["Internet"])',
    '  class internet cloud',
  ];

  let root = 'lan';
  if (gateway) {
    const gw = online.find((d) => d.ip === gateway);
    let gl = `Gateway ${gateway}`;
    if (gw?.hostname) gl = `${escM(gw.hostname)} ${gateway}`;
    else if (gw?.vendor) gl = `${escM(gw.vendor)} ${gateway}`;
    lines.push(`  gateway{"${gl}"}`);
    lines.push('  class gateway router');
    lines.push('  internet --> gateway');
    root = 'gateway';
  } else {
    lines.push('  lan["LAN — gateway not detected"]');
    lines.push('  class lan segment');
    lines.push('  internet --> lan');
  }

  const byLink = {};
  online.forEach((d) => {
    if (gateway && d.ip === gateway) return;
    const lk = d.link || 'unknown';
    if (!byLink[lk]) byLink[lk] = [];
    byLink[lk].push(d);
  });

  const linkNames = { wifi: 'Wi‑Fi', ethernet: 'LAN cable', other: 'Other', unknown: 'Unknown link' };
  let n = 0;
  const cap = 24;
  const maxOnMap = 60;
  let shown = 0;
  Object.keys(byLink).forEach((link) => {
    if (shown >= maxOnMap) return;
    const devs = byLink[link];
    const lid = 'link_' + link.replace(/\W/g, '_');
    lines.push(`  ${lid}["${escM(linkNames[link] || link)} (${devs.length})"]`);
    lines.push(`  class ${lid} segment`);
    lines.push(`  ${root} --> ${lid}`);
    const room = Math.min(cap, maxOnMap - shown);
    devs.slice(0, room).forEach((d, i) => {
      const did = `d_${link}_${i}`;
      lines.push(`  ${did}["${escM(deviceLabel(d))}"]`);
      lines.push(`  class ${did} device`);
      lines.push(`  ${lid} --> ${did}`);
      n++;
      shown++;
    });
  });

  if (offline > 0) {
    lines.push(`  offl["Offline in DB: ${offline}"]`);
    lines.push('  class offl offline');
    lines.push(`  ${root} --> offl`);
  }
  const mon = info?.lan_ip;
  if (mon) {
    lines.push(`  mon["This PC ${escM(mon)}"]`);
    lines.push('  class mon device');
    lines.push(`  ${root} -.-> mon`);
  }
  return lines.join('\n');
}

async function fetchTopologyMermaid() {
  try {
    const res = await fetch(appUrl('/api/topology'));
    if (res.ok) {
      const data = await res.json();
      return { mermaid: data.mermaid, meta: data };
    }
  } catch (_) {}
  const [devRes, infoRes] = await Promise.all([
    fetch(appUrl('/api/devices')),
    fetch(appUrl('/api/info')),
  ]);
  if (!devRes.ok) throw new Error('no server');
  const devData = await devRes.json();
  const info = infoRes.ok ? await infoRes.json() : {};
  return {
    mermaid: buildMermaidFromScan(devData.devices || [], info),
      meta: {
      online: devData.online,
      offline: devData.offline,
      total_in_db: (devData.devices || []).length,
      main_router: { ip: info.subnet_info?.gateway },
      monitor_ip: info.lan_ip,
      network_measurements: info.network_measurements,
      scan_error: info.scan_error,
      needs_scan: devData.online === 0 && !(devData.devices || []).length,
      updated_note: 'From last scan only.',
      nodes: [],
    },
  };
}
