/** Head-only SEO: meta tags + JSON-LD (creator Mohammad Faizan Khan). */
(function () {
  const cfg = window.SEO_CONFIG;
  if (!cfg) return;

  function pageKeyFromPath() {
    const p = (location.pathname || '/').toLowerCase();
    if (p.includes('devices')) return 'devices';
    if (p.includes('map')) return 'map';
    if (p.includes('calendar')) return 'calendar';
    if (p.includes('clock')) return 'clock';
    if (p.includes('about')) return 'about';
    return 'home';
  }

  const pageKey =
    document.documentElement.getAttribute('data-seo-page') || pageKeyFromPath();
  const page = cfg.pages[pageKey] || cfg.pages.home;
  const origin = cfg.siteOrigin.replace(/\/$/, '');
  const canonical = origin + page.path.replace(/\/$/, page.path === '/' ? '/' : page.path);
  const portfolio = cfg.portfolioUrl.replace(/\/$/, '');
  const title = page.title;
  const description = page.description;
  const image = cfg.defaultImage;
  const logoImage = cfg.logoImage || image;
  const noindex = Boolean(page.noindex);
  const keywords = [page.keywords, ...(cfg.keywords || [])].filter(Boolean).join(', ');
  const creatorLine = cfg.creatorStatement || 'I am the creator Mohammad Faizan Khan';

  function setMeta(name, content, prop) {
    if (!content) return;
    const attr = prop ? 'property' : 'name';
    const sel = prop ? `meta[property="${name}"]` : `meta[name="${name}"]`;
    let el = document.querySelector(sel);
    if (!el) {
      el = document.createElement('meta');
      el.setAttribute(attr, name);
      document.head.appendChild(el);
    }
    el.setAttribute('content', content);
  }

  function setLink(rel, href, extra) {
    if (!href) return;
    let el = document.querySelector(`link[rel="${rel}"]`);
    if (!el) {
      el = document.createElement('link');
      el.rel = rel;
      document.head.appendChild(el);
    }
    el.href = href;
    if (extra) Object.keys(extra).forEach((k) => el.setAttribute(k, extra[k]));
  }

  document.title = title;
  setMeta('description', description);
  setMeta('keywords', keywords);
  setMeta('robots', noindex ? 'noindex, nofollow' : 'index, follow, max-image-preview:large');
  setMeta('googlebot', noindex ? 'noindex, nofollow' : 'index, follow');
  setMeta('google-site-verification', cfg.googleVerification);
  setMeta('application-name', cfg.siteName);
  setMeta('author', cfg.creator);
  setMeta('creator', cfg.creator);
  setMeta('publisher', cfg.creator);
  setMeta('theme-color', cfg.themeColor || '#2596be');

  setMeta('og:type', 'website', true);
  setMeta('og:locale', cfg.locale || 'en_US', true);
  setMeta('og:site_name', cfg.siteName + ' — ' + cfg.creator, true);
  setMeta('og:title', title, true);
  setMeta('og:description', description, true);
  setMeta('og:url', canonical, true);
  setMeta('og:image', image, true);
  setMeta('og:image:alt', cfg.creator + ' — creator of ' + cfg.siteName, true);

  setMeta('twitter:card', 'summary_large_image');
  setMeta('twitter:title', title);
  setMeta('twitter:description', description);
  setMeta('twitter:image', image);
  setMeta('twitter:image:alt', cfg.creator + ' — creator of Network Monitor');

  setLink('canonical', canonical);
  setLink('sitemap', origin + '/sitemap.xml', { type: 'application/xml', title: 'Sitemap' });
  setLink('me', cfg.linkedIn);
  setLink('author', portfolio);

  const graph = [
    {
      '@context': 'https://schema.org',
      '@type': 'Person',
      '@id': portfolio + '/#person',
      name: cfg.creator,
      alternateName: cfg.alternateNames,
      description: creatorLine + '. ' + (cfg.jobTitle || '') + ', ' + (cfg.location || ''),
      url: portfolio,
      image: image,
      jobTitle: cfg.jobTitle,
      email: cfg.email,
      telephone: cfg.phone,
      homeLocation: cfg.location,
      sameAs: [cfg.linkedIn, cfg.instagram, cfg.parentBrandUrl, cfg.creatorUrl],
      knowsAbout: [
        'Network Monitor',
        'Wi-Fi scanning',
        'LAN device inventory',
        'Network operations',
        'Project management',
      ],
      creator: [
        { '@type': 'SoftwareApplication', '@id': origin + '/#software' },
        { '@type': 'WebSite', '@id': origin + '/#website' },
      ],
    },
    {
      '@context': 'https://schema.org',
      '@type': 'ProfilePage',
      '@id': canonical + '#profile',
      url: canonical,
      name: cfg.creator + ' — ' + cfg.siteName,
      description: description,
      mainEntity: { '@id': portfolio + '/#person' },
      isPartOf: { '@id': origin + '/#website' },
    },
    {
      '@context': 'https://schema.org',
      '@type': 'Organization',
      '@id': origin + '/#organization',
      name: cfg.brand,
      url: cfg.parentBrandUrl,
      logo: logoImage,
      founder: { '@id': portfolio + '/#person' },
    },
    {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      '@id': origin + '/#website',
      url: origin + '/',
      name: cfg.siteName,
      description: cfg.pages.home.description,
      inLanguage: 'en',
      publisher: { '@id': origin + '/#organization' },
      author: { '@id': portfolio + '/#person' },
      creator: { '@id': portfolio + '/#person' },
      keywords: keywords,
    },
    {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      '@id': canonical + '#webpage',
      url: canonical,
      name: title,
      description: description,
      isPartOf: { '@id': origin + '/#website' },
      about: { '@id': portfolio + '/#person' },
      author: { '@id': portfolio + '/#person' },
      inLanguage: 'en',
    },
    {
      '@context': 'https://schema.org',
      '@type': 'SoftwareApplication',
      '@id': origin + '/#software',
      name: cfg.siteName,
      url: origin + '/',
      applicationCategory: 'BusinessApplication',
      operatingSystem: 'Windows, macOS, Linux',
      description: cfg.pages.home.description,
      featureList: cfg.appFeatures,
      keywords: keywords,
      image: logoImage,
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
      author: { '@id': portfolio + '/#person' },
      creator: { '@id': portfolio + '/#person' },
      publisher: { '@id': origin + '/#organization' },
    },
  ];

  if (pageKey === 'home' && cfg.faq?.length) {
    graph.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: cfg.faq.map((item) => ({
        '@type': 'Question',
        name: item.q,
        acceptedAnswer: { '@type': 'Answer', text: item.a },
      })),
    });
  }

  const old = document.getElementById('seo-jsonld');
  if (old) old.remove();
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.id = 'seo-jsonld';
  script.textContent = JSON.stringify(graph);
  document.head.appendChild(script);
})();
