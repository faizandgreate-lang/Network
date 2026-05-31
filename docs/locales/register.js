/** Merge full string atlas entries into I18N_LOCALES by key. */
(function (g) {
  g.I18N_STRING_ATLAS = g.I18N_STRING_ATLAS || {};
  g.registerStringAtlas = function (lang, map) {
    g.I18N_STRING_ATLAS[lang] = Object.assign(g.I18N_STRING_ATLAS[lang] || {}, map);
    const L = g.I18N_LOCALES || {};
    const en = L.en || {};
    if (!L[lang]) L[lang] = Object.assign({}, en);
    Object.keys(en).forEach((k) => {
      const src = en[k];
      if (map[src]) L[lang][k] = map[src];
    });
  };
  g.translateUiString = function (str, lang) {
    if (!str || lang === 'en') return str;
    const atlas = g.I18N_STRING_ATLAS[lang];
    if (atlas && atlas[str]) return atlas[str];
    const phrases = g.I18N_PHRASES && g.I18N_PHRASES[lang];
    if (!phrases) return str;
    let out = str;
    Object.keys(phrases)
      .sort((a, b) => b.length - a.length)
      .forEach((enPhrase) => {
        out = out.split(enPhrase).join(phrases[enPhrase]);
      });
    return out;
  };
})(window);
