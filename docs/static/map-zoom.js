/**
 * Network map: fit view, drag to pan, zoom at cursor (+/− or Ctrl+scroll only).
 * Normal scroll/trackpad does not zoom.
 */
function mapT(key, vars) {
  return typeof window.t === 'function' ? window.t(key, vars) : key;
}

function attachMapZoom(viewportId, innerId, hintId) {
  const viewport = document.getElementById(viewportId);
  const inner = document.getElementById(innerId);
  const hint = hintId ? document.getElementById(hintId) : null;
  const live = document.getElementById('map-zoom-live');
  if (!viewport || !inner) return null;

  let contentBox = null;
  let viewRect = null;
  let scalePct = 100;
  let lastX = 0;
  let lastY = 0;
  let dragging = false;
  let dragStart = null;
  let pointerDown = null;
  const PAN_THRESHOLD = 8;

  const ZOOM_STEP = 1.2;
  const ZOOM_MIN_PCT = 40;
  const ZOOM_MAX_PCT = 400;

  function getSvg() {
    return inner.querySelector('svg');
  }

  function measureBox(svg) {
    try {
      const box = svg.getBBox();
      if (box.width > 2 && box.height > 2) return box;
    } catch {
      /* ignore */
    }
    return null;
  }

  function vpSize() {
    return { w: Math.max(1, viewport.clientWidth), h: Math.max(1, viewport.clientHeight) };
  }

  function fitRectFromContent(box) {
    const { w: vpW, h: vpH } = vpSize();
    const pad = 32;
    const cw = box.width + pad * 2;
    const ch = box.height + pad * 2;
    const arVp = vpW / vpH;
    const arC = cw / ch;
    let w;
    let h;
    if (arC > arVp) {
      w = cw;
      h = cw / arVp;
    } else {
      h = ch;
      w = ch * arVp;
    }
    const cx = box.x + box.width / 2;
    const cy = box.y + box.height / 2;
    return { x: cx - w / 2, y: cy - h / 2, w, h };
  }

  function announce(msg) {
    if (live) live.textContent = msg;
    if (hint) hint.textContent = msg;
  }

  function applyViewRect() {
    const svg = getSvg();
    if (!svg || !viewRect) return;
    svg.setAttribute(
      'viewBox',
      `${viewRect.x} ${viewRect.y} ${viewRect.w} ${viewRect.h}`,
    );
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    if (contentBox) {
      const base = fitRectFromContent(contentBox);
      if (base) {
        scalePct = Math.round((base.w / viewRect.w) * 100);
        scalePct = Math.min(ZOOM_MAX_PCT, Math.max(ZOOM_MIN_PCT, scalePct));
      }
    }
    const pctEl = document.getElementById('zoom-pct');
    if (pctEl) pctEl.textContent = scalePct + '%';
    announce(mapT('map.zoomAnnounce', { pct: scalePct }));
  }

  function setViewState(rect) {
    if (rect?.w > 0 && rect?.h > 0) {
      viewRect = { ...rect };
      applyViewRect();
    }
  }

  function getViewState() {
    return viewRect ? { ...viewRect } : null;
  }

  function pointerInViewport(clientX, clientY) {
    const vp = viewport.getBoundingClientRect();
    return (
      clientX >= vp.left &&
      clientX <= vp.right &&
      clientY >= vp.top &&
      clientY <= vp.bottom
    );
  }

  function zoomAt(clientX, clientY, factor) {
    if (!viewRect || !contentBox) return;
    const vp = viewport.getBoundingClientRect();
    const fx = Math.min(1, Math.max(0, (clientX - vp.left) / vp.width));
    const fy = Math.min(1, Math.max(0, (clientY - vp.top) / vp.height));
    const sx = viewRect.x + fx * viewRect.w;
    const sy = viewRect.y + fy * viewRect.h;
    let newW = viewRect.w / factor;
    let newH = viewRect.h / factor;
    const base = fitRectFromContent(contentBox);
    if (base) {
      const minW = base.w / (ZOOM_MAX_PCT / 100);
      const maxW = base.w / (ZOOM_MIN_PCT / 100);
      newW = Math.min(maxW, Math.max(minW, newW));
      newH = newW * (viewRect.h / viewRect.w);
    }
    viewRect = { x: sx - fx * newW, y: sy - fy * newH, w: newW, h: newH };
    applyViewRect();
  }

  function panByPixels(dx, dy) {
    if (!viewRect) return;
    const { w: vpW, h: vpH } = vpSize();
    viewRect.x -= (dx / vpW) * viewRect.w;
    viewRect.y -= (dy / vpH) * viewRect.h;
    applyViewRect();
  }

  function fitMapToView() {
    const svg = getSvg();
    if (!svg) return;

    inner.style.transform = 'none';
    dragging = false;
    viewport.classList.remove('is-panning');

    const { w: vpW, h: vpH } = vpSize();
    if (vpW < 60 || vpH < 60) {
      requestAnimationFrame(fitMapToView);
      return;
    }

    const box = measureBox(svg);
    if (!box) {
      requestAnimationFrame(fitMapToView);
      return;
    }

    contentBox = { x: box.x, y: box.y, width: box.width, height: box.height };
    viewRect = fitRectFromContent(contentBox);
    if (!viewRect) return;

    svg.style.cssText =
      'display:block;visibility:visible;opacity:1;width:100%;height:100%;background:#000';
    applyViewRect();
  }

  function zoomIn() {
    zoomAt(lastX, lastY, ZOOM_STEP);
  }

  function zoomOut() {
    zoomAt(lastX, lastY, 1 / ZOOM_STEP);
  }

  window.mapFitAll = fitMapToView;
  window.mapAlignLeft = fitMapToView;
  window.mapZoomReset = fitMapToView;
  window.mapZoomIn = zoomIn;
  window.mapZoomOut = zoomOut;
  window.mapGetViewState = getViewState;
  window.mapSetViewState = setViewState;

  viewport.addEventListener('mousemove', (e) => {
    if (pointerInViewport(e.clientX, e.clientY)) {
      lastX = e.clientX;
      lastY = e.clientY;
    }
    if (dragging && dragStart && viewRect) {
      panByPixels(e.clientX - dragStart.mx, e.clientY - dragStart.my);
      dragStart = { mx: e.clientX, my: e.clientY };
      return;
    }
    if (pointerDown && viewRect && !dragging) {
      const dx = e.clientX - pointerDown.mx;
      const dy = e.clientY - pointerDown.my;
      if (Math.hypot(dx, dy) >= PAN_THRESHOLD) {
        dragging = true;
        dragStart = { mx: e.clientX, my: e.clientY };
        viewport.classList.add('is-panning');
      }
    }
  });

  viewport.addEventListener(
    'mousedown',
    (e) => {
      if (e.button !== 0 || !getSvg()) return;
      pointerDown = { mx: e.clientX, my: e.clientY };
      dragging = false;
      dragStart = null;
    },
  );

  window.addEventListener('mouseup', () => {
    dragging = false;
    dragStart = null;
    pointerDown = null;
    viewport.classList.remove('is-panning');
  });

  viewport.addEventListener(
    'wheel',
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.ctrlKey || e.metaKey) {
        lastX = e.clientX;
        lastY = e.clientY;
        zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? ZOOM_STEP : 1 / ZOOM_STEP);
      }
    },
    { passive: false },
  );

  viewport.addEventListener('keydown', (e) => {
    if (e.key === '+' || e.key === '=') {
      e.preventDefault();
      zoomIn();
    } else if (e.key === '-' || e.key === '_') {
      e.preventDefault();
      zoomOut();
    } else if (e.key === '0') {
      e.preventDefault();
      fitMapToView();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      panByPixels(-40, 0);
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      panByPixels(40, 0);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      panByPixels(0, -40);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      panByPixels(0, 40);
    }
  });

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(fitMapToView, 150);
  });

  function refreshAnnounce() {
    if (viewRect) applyViewRect();
    else announce(mapT('map.readyAnnounce'));
  }

  announce(mapT('map.readyAnnounce'));

  return { fitMapToView, getViewState, setViewState, refreshAnnounce };
}

function styleMapSvg(container) {
  const svg = container.querySelector('svg');
  if (!svg) return;

  const accent =
    typeof RetroTheme !== 'undefined' && RetroTheme.accent ? RetroTheme.accent() : '#33ff66';

  svg.setAttribute('role', 'group');
  svg.setAttribute('aria-label', 'Network topology diagram');

  svg.style.display = 'block';
  svg.style.visibility = 'visible';
  svg.style.opacity = '1';
  svg.style.background = '#000000';
  svg.style.width = '100%';
  svg.style.height = '100%';

  svg.querySelectorAll('text, tspan, .nodeLabel').forEach((t) => {
    t.setAttribute('fill', '#ffffff');
  });

  svg.querySelectorAll('.node rect, .node polygon, .node circle').forEach((el) => {
    el.setAttribute('fill', '#000000');
    el.setAttribute('stroke', accent);
    el.setAttribute('stroke-width', '2');
  });

  svg.querySelectorAll('.edgePath .path, .flowchart-link, path.flowchart-link').forEach((el) => {
    el.setAttribute('stroke', accent);
    el.setAttribute('fill', 'none');
  });

  svg.querySelectorAll('marker path').forEach((el) => {
    el.setAttribute('fill', accent);
    el.setAttribute('stroke', accent);
  });
}

window.addEventListener('retro-theme-change', () => {
  const el = document.getElementById('map-diagram');
  if (el) styleMapSvg(el);
});

window.addEventListener('locale-change', () => {
  const api = window.mapZoomApi;
  if (api && typeof api.refreshAnnounce === 'function') api.refreshAnnounce();
});
