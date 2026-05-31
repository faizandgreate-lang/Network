#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build complete phrases-all.js: _strings.json atlas keys, _langs txt (KEYS order)."""
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


def main():
    with open(STRINGS_PATH, encoding='utf-8') as f:
        string_keys = json.load(f)
    if len(string_keys) != 160:
        raise SystemExit(f'expected 160 keys, got {len(string_keys)}')
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
        path = os.path.join(LANG_DIR, lang + '.txt')
        if not os.path.isfile(path):
            raise SystemExit(f'missing {path}')
        with open(path, encoding='utf-8') as f:
            trans_lines = [ln.rstrip('\n') for ln in f.readlines()]
        if len(trans_lines) != len(KEYS):
            raise SystemExit(f'{lang}.txt: {len(trans_lines)} lines, need {len(KEYS)}')
        by_key = dict(zip(KEYS, trans_lines))
        lines.append(f"  atlas('{lang}', {{")
        for k in string_keys:
            v = by_key[k]
            if not v:
                raise SystemExit(f'{lang}: empty value for {k!r}')
            lines.append(f'    {jsq(k)}: {jsq(v)},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    text = '\n'.join(lines)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(text)
    print(OUT)
    print(len(lines))


if __name__ == '__main__':
    main()
