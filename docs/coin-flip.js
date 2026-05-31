/**
 * Paired coin flip — nav + hero spin +deg (logo front), creator spins -deg (photo front).
 * All flip together on the same timer / click.
 */
(function () {
  const FLIPS = 3;
  const DEG_PER_FLIP = 180;
  const AUTO_MS = 5000;

  const specs = [
    { id: 'nav-coin', sign: 1 },
    { id: 'hero-coin', sign: 1 },
    { id: 'creator-coin', sign: -1 },
  ];

  const coins = specs
    .map(({ id, sign }) => {
      const el = document.getElementById(id);
      const inner = el?.querySelector('.coin-flip-inner');
      if (!el || !inner) return null;
      return { el, inner, sign };
    })
    .filter(Boolean);

  if (!coins.length) return;

  let busy = false;
  let rotationDeg = 0;
  let intervalId = null;
  let scrolledFlipDone = false;

  const leadInner = coins[0].inner;

  function doPairedFlip() {
    if (busy) return;
    busy = true;
    rotationDeg += FLIPS * DEG_PER_FLIP;
    coins.forEach(({ el, inner, sign }) => {
      el.classList.add('is-flipping');
      inner.style.transform = `rotateY(${sign * rotationDeg}deg)`;
    });
  }

  function onTransitionEnd(e) {
    if (e.propertyName !== 'transform' || e.target !== leadInner) return;
    busy = false;
    coins.forEach(({ el }) => el.classList.remove('is-flipping'));
  }

  leadInner.addEventListener('transitionend', onTransitionEnd);

  function onCoinClick(e) {
    e.preventDefault();
    e.stopPropagation();
    doPairedFlip();
  }

  coins.forEach(({ el }) => el.addEventListener('click', onCoinClick));

  function startAuto() {
    if (intervalId) return;
    intervalId = setInterval(doPairedFlip, AUTO_MS);
  }

  function stopAuto() {
    if (!intervalId) return;
    clearInterval(intervalId);
    intervalId = null;
  }

  const watchRoot =
    document.querySelector('.home-main') ||
    document.querySelector('main') ||
    document.querySelector('.map-page') ||
    document.body;

  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            stopAuto();
            return;
          }
          if (!scrolledFlipDone) {
            scrolledFlipDone = true;
            doPairedFlip();
          }
          startAuto();
        });
      },
      { threshold: 0.08 },
    );
    obs.observe(watchRoot);
  } else {
    setTimeout(doPairedFlip, 600);
    startAuto();
  }
})();
