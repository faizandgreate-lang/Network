/** Locale overrides — merged over English. Fun codes use i18n transforms only. */
(function (g) {
  const L = g.I18N_LOCALES || {};
  const e = L.en || {};
  function m(o) {
    return Object.assign({}, e, o);
  }

  L.ar = m({
    'doc.titleHome': 'الرئيسية — مراقب الشبكة',
    'doc.titleDevices': 'قائمة الأجهزة — مراقب الشبكة',
    'doc.titleMap': 'خريطة الشبكة — مراقب الشبكة',
    'app.brand': 'مراقب الشبكة',
    'nav.home': 'الرئيسية',
    'nav.devices': 'الأجهزة',
    'nav.map': 'الخريطة',
    'nav.lang': 'اللغة',
    'hero.lead': 'اعرض كل جهاز على شبكة المكتب أو المنزل. بيانات مسح حقيقية — بدون تخمين.',
    'hero.openDevices': 'فتح قائمة الأجهزة',
    'hero.openMap': 'خريطة الشبكة',
    'devices.title': 'قائمة الأجهزة',
    'devices.scan': 'مسح Wi‑Fi + LAN',
    'devices.refresh': 'تحديث',
    'map.controls': 'تحكم الخريطة',
    'map.scanRedraw': 'مسح وإعادة رسم',
    'theme.green': 'السمة: أخضر',
    'theme.bw': 'السمة: أبيض وأسود',
  });

  L.hi = m({
    'app.brand': 'नेटवर्क मॉनिटर',
    'nav.home': 'होम',
    'nav.devices': 'डिवाइस',
    'nav.map': 'मानचित्र',
    'nav.lang': 'भाषा',
    'hero.lead': 'ऑफिस या घर के Wi‑Fi और LAN पर हर डिवाइस देखें। असली स्कैन डेटा।',
    'hero.openDevices': 'डिवाइस सूची खोलें',
    'hero.openMap': 'नेटवर्क मानचित्र',
    'devices.title': 'डिवाइस सूची',
    'devices.scan': 'Wi‑Fi + LAN स्कैन',
    'devices.refresh': 'रीफ़्रेश',
    'map.controls': 'मानचित्र नियंत्रण',
    'theme.green': 'थीम: हरा',
    'theme.bw': 'थीम: श्याम-श्वेत',
  });

  L.ne = m({
    'app.brand': 'नेटवर्क मनिटर',
    'nav.home': 'गृह',
    'nav.devices': 'यन्त्रहरू',
    'nav.map': 'नक्सा',
    'nav.lang': 'भाषा',
    'hero.lead': 'कार्यालय वा घरको Wi‑Fi र LAN मा सबै यन्त्रहरू हेर्नुहोस्।',
    'devices.scan': 'Wi‑Fi + LAN स्क्यान',
    'theme.green': 'थिम: हरियो',
    'theme.bw': 'थिम: कालो सेतो',
  });

  L.ur = m({
    'app.brand': 'نیٹ ورک مانیٹر',
    'nav.home': 'ہوم',
    'nav.devices': 'آلات',
    'nav.map': 'نقشہ',
    'nav.lang': 'زبان',
    'hero.lead': 'دفتر یا گھر کے Wi‑Fi اور LAN پر ہر ڈیوائس دیکھیں۔',
    'devices.scan': 'Wi‑Fi + LAN سکین',
    'theme.green': 'تھیم: سبز',
    'theme.bw': 'تھیم: سیاہ و سفید',
  });

  L.bn = m({
    'app.brand': 'নেটওয়ার্ক মনিটর',
    'nav.home': 'হোম',
    'nav.devices': 'ডিভাইস',
    'nav.map': 'মানচিত্র',
    'nav.lang': 'ভাষা',
    'hero.lead': 'অফিস বা বাড়ির Wi‑Fi ও LAN-এ সব ডিভাইস দেখুন।',
    'devices.scan': 'Wi‑Fi + LAN স্ক্যান',
    'theme.green': 'থিম: সবুজ',
    'theme.bw': 'থিম: কালো সাদা',
  });

  L.tl = m({
    'app.brand': 'Network Monitor',
    'nav.home': 'Bahay',
    'nav.devices': 'Mga device',
    'nav.map': 'Mapa',
    'nav.lang': 'Wika',
    'hero.lead': 'Tingnan ang bawat device sa Wi‑Fi at LAN. Tunay na scan data.',
    'devices.scan': 'I-scan ang Wi‑Fi + LAN',
    'theme.green': 'TEMA: BERDE',
    'theme.bw': 'TEMA: ITIM AT PUTI',
  });

  L.fr = m({
    'app.brand': 'Moniteur réseau',
    'nav.home': 'Accueil',
    'nav.devices': 'Appareils',
    'nav.map': 'Carte',
    'nav.lang': 'Langue',
    'hero.lead': 'Voir chaque appareil sur le Wi‑Fi et le LAN. Données réelles.',
    'hero.openDevices': 'Liste des appareils',
    'hero.openMap': 'Carte réseau',
    'devices.title': 'Liste des appareils',
    'devices.scan': 'Scanner Wi‑Fi + LAN',
    'devices.refresh': 'Actualiser',
    'map.controls': 'Contrôles carte',
    'theme.green': 'THÈME: VERT',
    'theme.bw': 'THÈME: NOIR ET BLANC',
  });

  L.es = m({
    'app.brand': 'Monitor de red',
    'nav.home': 'Inicio',
    'nav.devices': 'Dispositivos',
    'nav.map': 'Mapa',
    'nav.lang': 'Idioma',
    'hero.lead': 'Vea cada dispositivo en Wi‑Fi y LAN. Datos reales de escaneo.',
    'devices.scan': 'Escanear Wi‑Fi + LAN',
    'theme.green': 'TEMA: VERDE',
    'theme.bw': 'TEMA: BLANCO Y NEGRO',
  });

  L.zh = m({
    'app.brand': '网络监视器',
    'nav.home': '首页',
    'nav.devices': '设备',
    'nav.map': '地图',
    'nav.lang': '语言',
    'hero.lead': '查看办公室或家庭 Wi‑Fi 和局域网上的每台设备。真实扫描数据。',
    'devices.scan': '扫描 Wi‑Fi + 局域网',
    'theme.green': '主题：绿色',
    'theme.bw': '主题：黑白',
  });

  L.ja = m({
    'app.brand': 'ネットワークモニター',
    'nav.home': 'ホーム',
    'nav.devices': 'デバイス',
    'nav.map': 'マップ',
    'nav.lang': '言語',
    'hero.lead': 'オフィスや自宅の Wi‑Fi と LAN の全デバイスを表示。実スキャンデータ。',
    'devices.scan': 'Wi‑Fi + LAN をスキャン',
    'theme.green': 'テーマ: 緑',
    'theme.bw': 'テーマ: 白黒',
  });

  L.ml = m({
    'app.brand': 'നെറ്റ്‌വർക്ക് മോണിറ്റർ',
    'nav.home': 'ഹോം',
    'nav.devices': 'ഉപകരണങ്ങൾ',
    'nav.map': 'മാപ്പ്',
    'nav.lang': 'ഭാഷ',
    'hero.lead': 'ഓഫീസ് അല്ലെങ്കിൽ വീട്ടിലെ Wi‑Fi, LAN ഉപകരണങ്ങൾ കാണുക.',
    'devices.scan': 'Wi‑Fi + LAN സ്കാൻ',
    'theme.green': 'തീം: പച്ച',
    'theme.bw': 'തീം: കറുപ്പ് വെള്ള',
  });

  L.gu = m({
    'app.brand': 'નેટવર્ક મોનિટર',
    'nav.home': 'હોમ',
    'nav.devices': 'ઉપકરણો',
    'nav.map': 'નકશો',
    'nav.lang': 'ભાષા',
    'devices.scan': 'Wi‑Fi + LAN સ્કેન',
    'theme.green': 'થીમ: લીલું',
    'theme.bw': 'થીમ: કાળું સફેદ',
  });

  L.mr = m({
    'app.brand': 'नेटवर्क मॉनिटर',
    'nav.home': 'मुख्यपृष्ठ',
    'nav.devices': 'डिव्हाइस',
    'nav.map': 'नकाशा',
    'nav.lang': 'भाषा',
    'devices.scan': 'Wi‑Fi + LAN स्कॅन',
    'theme.green': 'थीम: हिरवा',
    'theme.bw': 'थीम: काळा पांढरा',
  });

  L.sw = m({
    'app.brand': 'Kifuatilia Mtandao',
    'nav.home': 'Nyumbani',
    'nav.devices': 'Vifaa',
    'nav.map': 'Ramani',
    'nav.lang': 'Lugha',
    'devices.scan': 'Skani Wi‑Fi + LAN',
    'theme.green': 'MANDHARI: KIJANI',
    'theme.bw': 'MANDHARI: Nyeusi na Nyeupe',
  });

  L.zu = m({
    'app.brand': 'Umlindi Wenethiwekhi',
    'nav.home': 'Ikhaya',
    'nav.devices': 'Amadivayisi',
    'nav.map': 'Imephu',
    'nav.lang': 'Ulimi',
    'devices.scan': 'Skena i-Wi‑Fi + LAN',
  });

  L.am = m({
    'app.brand': 'የአውታረ መረብ መቆጣጠሪያ',
    'nav.home': 'መነሻ',
    'nav.devices': 'መሳሪያዎች',
    'nav.map': 'ካርታ',
    'nav.lang': 'ቋንቋ',
    'devices.scan': 'Wi‑Fi + LAN ቃኝ',
  });

  L.ha = m({
    'app.brand': 'Mai Kula Network',
    'nav.home': 'Gida',
    'nav.devices': 'Na\'urori',
    'nav.map': 'Taswira',
    'nav.lang': 'Harshe',
    'devices.scan': 'Duba Wi‑Fi + LAN',
  });

  L.pt = m({
    'nav.home': 'Início',
    'nav.devices': 'Dispositivos',
    'nav.map': 'Mapa',
    'nav.lang': 'Idioma',
    'devices.scan': 'Verificar Wi‑Fi + LAN',
  });

  L.de = m({
    'nav.home': 'Start',
    'nav.devices': 'Geräte',
    'nav.map': 'Karte',
    'nav.lang': 'Sprache',
    'devices.scan': 'Wi‑Fi + LAN scannen',
  });

  L.ru = m({
    'nav.home': 'Главная',
    'nav.devices': 'Устройства',
    'nav.map': 'Карта',
    'nav.lang': 'Язык',
    'devices.scan': 'Сканировать Wi‑Fi + LAN',
  });

  L.ko = m({
    'nav.home': '홈',
    'nav.devices': '장치',
    'nav.map': '지도',
    'nav.lang': '언어',
    'devices.scan': 'Wi‑Fi + LAN 스캔',
  });

  L.th = m({
    'nav.home': 'หน้าแรก',
    'nav.devices': 'อุปกรณ์',
    'nav.map': 'แผนที่',
    'nav.lang': 'ภาษา',
    'devices.scan': 'สแกน Wi‑Fi + LAN',
  });

  L.cy = m({
    'nav.home': 'Hafan',
    'nav.devices': 'Dyfeisiau',
    'nav.map': 'Map',
    'nav.lang': 'Iaith',
  });

  L.haw = m({
    'nav.home': 'Home',
    'nav.devices': 'Mea hana',
    'nav.map': 'Palapala',
    'nav.lang': 'ʻŌlelo',
  });

  g.I18N_LOCALES = L;
})(window);
