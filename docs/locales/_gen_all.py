#!/usr/bin/env python3
"""Generate phrases-all.js from _strings.json keys + _langs/*.txt (KEYS order)."""
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
from _trans_data import KEYS  # noqa: E402

STRINGS_PATH = os.path.join(DIR, '_strings.json')
LANG_DIR = os.path.join(DIR, '_langs')
OUT_PATH = os.path.join(DIR, 'phrases-all.js')
LANGS = [
    'sa', 'hi', 'ar', 'fr', 'es', 'zh', 'ja', 'de', 'ru', 'pt', 'bn', 'ur', 'ne', 'ml',
    'mr', 'gu', 'sw', 'tl', 'ko', 'th', 'he', 'el', 'fa', 'ta', 'te', 'kn', 'pa', 'it',
    'id', 'vi', 'tr', 'pl', 'nl', 'zu', 'am', 'ha', 'cy', 'haw',
]
FN = 'Network Monitor \u2014 empty table cells mean \u201cnot detected\u201d, not guessed.'


def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def load_strings_keys():
    with open(STRINGS_PATH, encoding='utf-8') as f:
        keys = json.load(f)
    if len(keys) != 160:
        raise SystemExit(f'_strings.json: expected 160, got {len(keys)}')
    return keys


def load_txt_by_keys(lang):
    path = os.path.join(LANG_DIR, lang + '.txt')
    if not os.path.isfile(path):
        return None
    with open(path, encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f.readlines()]
    if len(lines) != len(KEYS):
        raise SystemExit(f'{lang}.txt: expected {len(KEYS)}, got {len(lines)}')
    return dict(zip(KEYS, lines))


def main():
    string_keys = load_strings_keys()
    missing = [l for l in LANGS if load_txt_by_keys(l) is None]
    if missing:
        raise SystemExit(f'Missing _langs/*.txt: {missing}')
    if string_keys != KEYS:
        # Atlas uses _strings.json order; txt lines are KEYS order.
        pass
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
            v = by_key[k]
            if not v and k == FN:
                raise SystemExit(f'{lang}: empty footer')
            lines.append(f'    {jsq(k)}: {jsq(v)},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    text = '\n'.join(lines)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print(OUT_PATH)
    print(len(lines))


if __name__ == '__main__':
    main()
