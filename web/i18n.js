/** UI i18n — LANG menu + full phrase atlas (register.js + phrases-all.js). */
(function (global) {
  const LOCALES = global.I18N_LOCALES || {};
  const EN = LOCALES.en || {};
  let lang = 'en';
  let langMenuClickLock = false;

  const MORSE_CODE = {
    A: '.-',
    B: '-...',
    C: '-.-.',
    D: '-..',
    E: '.',
    F: '..-.',
    G: '--.',
    H: '....',
    I: '..',
    J: '.---',
    K: '-.-',
    L: '.-..',
    M: '--',
    N: '-.',
    O: '---',
    P: '.--.',
    Q: '--.-',
    R: '.-.',
    S: '...',
    T: '-',
    U: '..-',
    V: '...-',
    W: '.--',
    X: '-..-',
    Y: '-.--',
    Z: '--..',
    0: '-----',
    1: '.----',
    2: '..---',
    3: '...--',
    4: '....-',
    5: '.....',
    6: '-....',
    7: '--...',
    8: '---..',
    9: '----.',
    '.': '.-.-.-',
    ',': '--..--',
    '?': '..--..',
    '/': '-..-.',
    '@': '.--.-.',
  };

  const NATO = {
    A: 'Alfa',
    B: 'Bravo',
    C: 'Charlie',
    D: 'Delta',
    E: 'Echo',
    F: 'Foxtrot',
    G: 'Golf',
    H: 'Hotel',
    I: 'India',
    J: 'Juliet',
    K: 'Kilo',
    L: 'Lima',
    M: 'Mike',
    N: 'November',
    O: 'Oscar',
    P: 'Papa',
    Q: 'Quebec',
    R: 'Romeo',
    S: 'Sierra',
    T: 'Tango',
    U: 'Uniform',
    V: 'Victor',
    W: 'Whiskey',
    X: 'X-ray',
    Y: 'Yankee',
    Z: 'Zulu',
  };

  const RUNES = 'ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊᛏᛒᛖᛗᛚᛜᛞᛟ';

  function toMorse(s) {
    return s
      .toUpperCase()
      .split('')
      .map((c) => {
        if (c === ' ') return '/';
        return MORSE_CODE[c] || c;
      })
      .join(' ')
      .replace(/\s+\/\s+/g, ' / ')
      .slice(0, 420);
  }

  function rot13(s) {
    return s.replace(/[A-Za-z]/g, (c) => {
      const base = c <= 'Z' ? 65 : 97;
      return String.fromCharCode(((c.charCodeAt(0) - base + 13) % 26) + base);
    });
  }

  function atbash(s) {
    return s.replace(/[A-Za-z]/g, (c) => {
      const base = c <= 'Z' ? 65 : 97;
      return String.fromCharCode(base + 25 - (c.charCodeAt(0) - base));
    });
  }

  function pigLatin(s) {
    return s.replace(/\b([A-Za-z]+)\b/g, (w) => {
      if (/^[aeiou]/i.test(w)) return w + 'way';
      const m = w.match(/^([^aeiou]+)(.*)$/i);
      if (!m) return w;
      return m[2] + m[1] + 'ay';
    });
  }

  function leet(s) {
    const L = { a: '4', e: '3', i: '1', o: '0', s: '5', t: '7', l: '1' };
    return s.replace(/[aeiostl]/gi, (c) => L[c.toLowerCase()] || c);
  }

  function toB64(s) {
    try {
      return btoa(unescape(encodeURIComponent(s.slice(0, 80))));
    } catch (_) {
      return btoa(s.slice(0, 80));
    }
  }

  function toNato(s) {
    return s
      .toUpperCase()
      .split('')
      .map((c) => (c === ' ' ? '·' : NATO[c] || c))
      .join(' ')
      .slice(0, 320);
  }

  function toRunes(s) {
    return s
      .toLowerCase()
      .split('')
      .map((c) => {
        const i = 'abcdefghijklmnopqrstuvwxyz'.indexOf(c);
        return i >= 0 ? RUNES[i % RUNES.length] : c;
      })
      .join('');
  }

  const HIERO = '𓀀𓀁𓀂𓀃𓀄𓀅𓀆𓀇𓀈𓀉𓀊𓀋𓀌𓀍𓀎𓀏';

  function toHiero(s) {
    return (
      '𓂀 ' +
      s
        .toLowerCase()
        .split('')
        .map((c) => {
          const i = 'abcdefghijklmnopqrstuvwxyz'.indexOf(c);
          return i >= 0 ? HIERO[i % HIERO.length] : c;
        })
        .join('') +
      ' 𓂀'
    );
  }

  const TRANSFORM = {
    bin(s) {
      return s
        .split('')
        .slice(0, 120)
        .map((c) => c.charCodeAt(0).toString(2).padStart(8, '0'))
        .join(' ');
    },
    wak(s) {
      return '⟣ ' + s.toUpperCase().replace(/[AEIOU]/g, '◆') + ' ⟢';
    },
    goog(s) {
      return '[Auto] ' + s.replace(/\b(\w{4,})\b/g, 'the $1') + ' (may be wrong)';
    },
    kli(s) {
      return 'tlh: ' + s.replace(/network/gi, 'Hegh').replace(/device/gi, 'Duj');
    },
    pir(s) {
      return s.replace(/Hello/gi, 'Ahoy').replace(/device/gi, 'ship').replace(/network/gi, 'sea');
    },
    morse: toMorse,
    hex(s) {
      return Array.from(s.slice(0, 48))
        .map((c) => c.charCodeAt(0).toString(16))
        .join(' ');
    },
    zalgo(s) {
      return s.slice(0, 60) + '̴̷̸̵̶̷̃';
    },
    upside(s) {
      const map = 'ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz';
      return s
        .toLowerCase()
        .split('')
        .reverse()
        .map((c) => map['abcdefghijklmnopqrstuvwxyz'.indexOf(c)] || c)
        .join('');
    },
    braille(s) {
      return '⠿ ' + s.slice(0, 80) + ' ⠿';
    },
    la(s) {
      return s.replace(/Network/g, 'Rete').replace(/Device/g, 'Instrumentum').replace(/Scan/g, 'Explorare');
    },
    eo(s) {
      return s.replace(/network/gi, 'reto').replace(/device/gi, 'aparato').replace(/Scan/gi, 'Skani');
    },
    rot13,
    atbash,
    piglatin: pigLatin,
    leet,
    b64: toB64,
    nato: toNato,
    rune: toRunes,
    hiero: toHiero,
    classified(s) {
      return '⟨CLASSIFIED⟩ ' + s.split('').reverse().join('');
    },
    cipher(s) {
      return s
        .split('')
        .map((c, i) => String.fromCharCode(c.charCodeAt(0) ^ ((i % 7) + 1)))
        .join('')
        .slice(0, 120);
    },
    vulcan(s) {
      return '⌁ ' + toMorse(s.slice(0, 48)) + ' ⌁';
    },
    aurebesh(s) {
      return '◈ ' + s.toUpperCase().split('').join('·') + ' ◈';
    },
    semaphore(s) {
      return '⚑ ' + s.toUpperCase().replace(/[A-Z]/g, (c) => `/${c}/`) + ' ⚑';
    },
  };

  global.I18N_LANGS = [
    { code: 'en', name: 'English', group: 'Common' },
    { code: 'ar', name: 'العربية (Arabic)', group: 'Common' },
    { code: 'hi', name: 'हिन्दी (Hindi)', group: 'Common' },
    { code: 'ne', name: 'नेपाली (Nepali)', group: 'Common' },
    { code: 'ur', name: 'اردو (Urdu)', group: 'Common' },
    { code: 'bn', name: 'বাংলা (Bengali)', group: 'Common' },
    { code: 'tl', name: 'Tagalog', group: 'Common' },
    { code: 'fr', name: 'Français (French)', group: 'Common' },
    { code: 'es', name: 'Español (Spanish)', group: 'Common' },
    { code: 'zh', name: '中文 (Chinese)', group: 'Common' },
    { code: 'ja', name: '日本語 (Japanese)', group: 'Common' },
    { code: 'sa', name: 'संस्कृतम् (Sanskrit)', group: 'Classical' },
    { code: 'ml', name: 'മലയാളം (Malayalam)', group: 'India' },
    { code: 'gu', name: 'ગુજરાતી (Gujarati)', group: 'India' },
    { code: 'mr', name: 'मराठी (Marathi)', group: 'India' },
    { code: 'sw', name: 'Kiswahili (Swahili)', group: 'Africa' },
    { code: 'zu', name: 'isiZulu (Zulu)', group: 'Africa' },
    { code: 'am', name: 'አማርኛ (Amharic)', group: 'Africa' },
    { code: 'ha', name: 'Hausa', group: 'Africa' },
    { code: 'pt', name: 'Português', group: 'More' },
    { code: 'de', name: 'Deutsch', group: 'More' },
    { code: 'ru', name: 'Русский', group: 'More' },
    { code: 'ko', name: '한국어', group: 'More' },
    { code: 'th', name: 'ไทย', group: 'More' },
    { code: 'morse', name: '·−· Morse code', group: 'Encoding' },
    { code: 'nato', name: 'NATO phonetic', group: 'Encoding' },
    { code: 'rot13', name: 'ROT13', group: 'Encoding' },
    { code: 'atbash', name: 'Atbash', group: 'Encoding' },
    { code: 'classified', name: 'Classified (reversed)', group: 'Encoding' },
    { code: 'b64', name: 'Base64', group: 'Encoding' },
    { code: 'rune', name: 'Elder Futhark runes', group: 'Encoding' },
    { code: 'hiero', name: 'Hieroglyph mask', group: 'Encoding' },
    { code: 'piglatin', name: 'Pig Latin', group: 'Encoding' },
    { code: 'leet', name: 'Leetspeak', group: 'Encoding' },
    { code: 'goog', name: 'Google-ish parody', group: 'Fun' },
    { code: 'bin', name: 'Binary', group: 'Fun' },
    { code: 'pir', name: 'Pirate', group: 'Fun' },
    { code: 'hex', name: 'Hexadecimal', group: 'Fun' },
    { code: 'upside', name: 'Upside down', group: 'Fun' },
    { code: 'zalgo', name: 'Zalgo', group: 'Fun' },
  ];

  function resolveString(key) {
    const enStr = EN[key] || key;
    if (TRANSFORM[lang]) return TRANSFORM[lang](enStr);
    if (lang === 'en') return enStr;
    const loc = LOCALES[lang]?.[key];
    if (loc) return loc;
    const phrases = global.I18N_PHRASES?.[lang];
    if (phrases && phrases[enStr]) return phrases[enStr];
    if (typeof global.translateUiString === 'function') {
      const tr = global.translateUiString(enStr, lang);
      if (tr && tr !== enStr) return tr;
    }
    return enStr;
  }

  function t(key, vars) {
    let str = resolveString(key);
    if (vars) {
      Object.keys(vars).forEach((k) => {
        str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), String(vars[k]));
      });
    }
    return str;
  }

  function apply(root) {
    const r = root || document;
    r.querySelectorAll('[data-i18n]').forEach((el) => {
      if (el.closest('#lang-menu')) return;
      if (el.hasAttribute('data-i18n-skip')) return;
      if (el.id === 'status-chip' || el.id === 'build-tag') return;
      const k = el.getAttribute('data-i18n');
      if (!k) return;
      el.textContent = t(k);
    });
    r.querySelectorAll('[data-i18n-html]').forEach((el) => {
      const k = el.getAttribute('data-i18n-html');
      if (k) el.innerHTML = t(k);
    });
    r.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
      const k = el.getAttribute('data-i18n-placeholder');
      if (k) el.setAttribute('placeholder', t(k));
    });
    r.querySelectorAll('[data-i18n-title]').forEach((el) => {
      const k = el.getAttribute('data-i18n-title');
      if (k) el.setAttribute('title', t(k));
    });
    r.querySelectorAll('[data-i18n-aria]').forEach((el) => {
      const k = el.getAttribute('data-i18n-aria');
      if (k) el.setAttribute('aria-label', t(k));
    });
    const titleKey = document.documentElement.getAttribute('data-i18n-title');
    if (titleKey) document.title = t(titleKey);
    r.querySelectorAll('[data-retro-type]').forEach((el) => {
      const k = el.getAttribute('data-i18n') || 'app.brand';
      el.setAttribute('data-retro-type', t(k));
    });
    document.documentElement.lang = lang === 'en' || lang.length > 3 ? 'en' : lang.slice(0, 2);
    document.documentElement.dataset.langMode = lang;
    document.body.classList.toggle('lang-mode-morse', lang === 'morse');
    document.body.classList.toggle('lang-mode-secret', Boolean(TRANSFORM[lang]));
    if (lang === 'ar' || lang === 'ur') document.documentElement.dir = 'rtl';
    else document.documentElement.dir = 'ltr';
    syncLangToggleLabel();
  }

  function syncLangToggleLabel() {
    const label = document.getElementById('lang-toggle-label');
    if (!label) return;
    if (lang === 'en') {
      label.textContent = 'Language';
      return;
    }
    const current = (global.I18N_LANGS || []).find((L) => L.code === lang);
    label.textContent = current ? current.name : t('nav.lang');
  }

  function syncLangMenuActive() {
    const menu = document.getElementById('lang-menu');
    if (!menu) return;
    menu.querySelectorAll('.lang-menu-item').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
      btn.setAttribute('aria-selected', btn.dataset.lang === lang ? 'true' : 'false');
    });
  }

  function closeLangMenu() {
    const picker = document.getElementById('lang-picker');
    const menu = document.getElementById('lang-menu');
    const toggle = document.getElementById('lang-toggle');
    if (picker) picker.classList.remove('open');
    if (menu) {
      menu.classList.remove('open');
      menu.hidden = true;
    }
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  }

  function openLangMenu() {
    const picker = document.getElementById('lang-picker');
    const menu = document.getElementById('lang-menu');
    const toggle = document.getElementById('lang-toggle');
    if (!picker || !menu) return;
    menu.hidden = false;
    menu.classList.add('open');
    picker.classList.add('open');
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
  }

  function toggleLangMenu() {
    const picker = document.getElementById('lang-picker');
    if (picker && picker.classList.contains('open')) closeLangMenu();
    else openLangMenu();
  }

  function buildLangMenu() {
    const menu = document.getElementById('lang-menu');
    if (!menu) return;
    menu.innerHTML = '';
    let grp = '';
    (global.I18N_LANGS || []).forEach((L) => {
      if (L.group !== grp) {
        grp = L.group;
        const head = document.createElement('div');
        head.className = 'lang-menu-group';
        head.textContent = grp;
        menu.appendChild(head);
      }
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'lang-menu-item';
      btn.dataset.lang = L.code;
      btn.textContent = L.name;
      btn.setAttribute('role', 'option');
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        setLang(L.code);
        closeLangMenu();
      });
      menu.appendChild(btn);
    });
    menu.dataset.wired = '1';
  }

  function wireLangPicker() {
    const toggle = document.getElementById('lang-toggle');
    if (!toggle || toggle.dataset.wired) return;
    toggle.dataset.wired = '1';
    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      langMenuClickLock = true;
      toggleLangMenu();
      setTimeout(() => {
        langMenuClickLock = false;
      }, 0);
    });
    document.addEventListener('click', (e) => {
      if (langMenuClickLock) return;
      const picker = document.getElementById('lang-picker');
      if (!picker || !picker.classList.contains('open')) return;
      if (!picker.contains(e.target)) closeLangMenu();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeLangMenu();
    });
  }

  function setLang(code) {
    lang = code || 'en';
    apply();
    syncLangMenuActive();
    global.dispatchEvent(new CustomEvent('locale-change', { detail: { lang } }));
    global.dispatchEvent(new CustomEvent('i18n-applied', { detail: { lang } }));
  }

  function init() {
    lang = 'en';
    buildLangMenu();
    wireLangPicker();
    apply();
    syncLangMenuActive();
  }

  global.I18n = { t, apply, setLang, getLang: () => lang, init };
  global.t = t;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window);
