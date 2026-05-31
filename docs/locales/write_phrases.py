# -*- coding: utf-8 -*-
"""Generate phrases-all.js from _strings.json keys + _langs/*.txt (KEYS order)."""
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
from _trans_data import KEYS  # noqa: E402

STRINGS_PATH = os.path.join(DIR, '_strings.json')
LANG_DIR = os.path.join(DIR, '_langs')
OUT = os.path.join(DIR, 'phrases-all.js')
LANGS = [
    'sa', 'hi', 'ar', 'fr', 'es', 'zh', 'ja', 'de', 'ru', 'pt', 'bn', 'ur', 'ne', 'ml',
    'mr', 'gu', 'sw', 'tl', 'ko', 'th', 'he', 'el', 'fa', 'ta', 'te', 'kn', 'pa', 'it',
    'id', 'vi', 'tr', 'pl', 'nl', 'zu', 'am', 'ha', 'cy', 'haw',
]


def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def load_strings_keys():
    with open(STRINGS_PATH, encoding='utf-8') as f:
        keys = json.load(f)
    if len(keys) != 160:
        raise ValueError(f'_strings.json: expected 160, got {len(keys)}')
    return keys


def load_txt_by_keys(lang):
    path = os.path.join(LANG_DIR, lang + '.txt')
    with open(path, encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f.readlines()]
    if len(lines) != len(KEYS):
        raise ValueError(f'{lang}.txt: expected {len(KEYS)}, got {len(lines)}')
    return dict(zip(KEYS, lines))


def write_phrases():
    string_keys = load_strings_keys()
    missing = [l for l in LANGS if not os.path.isfile(os.path.join(LANG_DIR, l + '.txt'))]
    if missing:
        raise ValueError(f'Missing _langs/*.txt: {missing}')
    lines = [
        '(function (g) {',
        "  if (typeof g.registerStringAtlas !== 'function') return;",
        '  function atlas(lang, pairs) {',
        '    g.registerStringAtlas(lang, pairs);',
        '    g.I18N_PHRASES = g.I18N_PHRASES || {};',
        '    g.I18N_PHRASES[lang] = pairs;',
        '  }',
    ]
    for lang in LANGS:
        by_key = load_txt_by_keys(lang)
        lines.append(f"  atlas('{lang}', {{")
        for k in string_keys:
            lines.append(f'    {jsq(k)}: {jsq(by_key[k])},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    text = '\n'.join(lines)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(text)
    return len(lines)


if __name__ == '__main__':
    n = write_phrases()
    print(f'Wrote {OUT} ({n} lines)')
