/** Logo + creator — original colors on transparent PNG (no filters). */
(function (global) {
  const LOGO = 'assets/logo.png';
  const CREATOR = 'assets/creator.png';
  const LOGO_FB = 'assets/logo-display.png';
  const CREATOR_FB = 'assets/creator-display.png';
  const CACHE = 'logo-19';

  const PLACEHOLDER_LOGO =
    'data:image/svg+xml,' +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">' +
        '<text x="60" y="72" text-anchor="middle" font-family="system-ui,sans-serif" font-size="32" font-weight="700" fill="#2596be">MFK</text></svg>',
    );

  const PLACEHOLDER_PHOTO =
    'data:image/svg+xml,' +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">' +
        '<circle cx="60" cy="44" r="22" fill="#2596be" opacity="0.9"/>' +
        '<ellipse cx="60" cy="98" rx="34" ry="26" fill="#509591" opacity="0.85"/></svg>',
    );

  function styleImg(img) {
    img.style.backgroundColor = 'transparent';
    img.style.background = 'transparent';
    img.style.border = 'none';
    img.style.outline = 'none';
    img.style.boxShadow = 'none';
    img.style.filter = 'none';
    img.style.webkitFilter = 'none';
    img.style.opacity = '1';
    img.style.mixBlendMode = 'normal';
    img.style.visibility = 'visible';
    img.style.objectFit = 'contain';
    img.style.display = 'block';
    img.style.width = '100%';
    img.style.height = '100%';
  }

  function setSrc(img, url) {
    styleImg(img);
    img.src = `${url}?v=${CACHE}`;
  }

  function loadImage(img, primary, fallback, placeholder) {
    styleImg(img);
    let triedFallback = false;
    img.onerror = () => {
      if (!triedFallback && fallback && img.src.indexOf(fallback) === -1) {
        triedFallback = true;
        setSrc(img, fallback);
        return;
      }
      img.onerror = null;
      img.src = placeholder;
      styleImg(img);
    };
    img.onload = () => styleImg(img);
    setSrc(img, primary);
  }

  function applyImages() {
    document.querySelectorAll('.coin-flip-logo, .logo-img').forEach((img) => {
      loadImage(img, LOGO, LOGO_FB, PLACEHOLDER_LOGO);
    });
    document.querySelectorAll('.coin-flip-photo').forEach((img) => {
      loadImage(img, CREATOR, CREATOR_FB, PLACEHOLDER_PHOTO);
    });
  }

  global.RetroAssets = {
    applyImages,
    applyModernImages: applyImages,
  };

  global.addEventListener('retro-theme-change', applyImages);

  function init() {
    document.querySelectorAll('.logo-img').forEach((img) => {
      if (img.closest('.coin-flip')) return;
      styleImg(img);
      img.classList.add('logo-ready');
    });
    applyImages();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window);
