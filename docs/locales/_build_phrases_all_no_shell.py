#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build complete phrases-all.js — same as write_phrases.py / _merge_phrases_all.py."""
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
        with open(path, encoding='utf-8') as f:
            trans_lines = [ln.rstrip('\n') for ln in f.readlines()]
        if len(trans_lines) == 161:
            trans_lines = trans_lines[:144] + trans_lines[145:]
        if len(trans_lines) != len(KEYS):
            raise SystemExit(f'{lang}.txt: {len(trans_lines)} lines, need {len(KEYS)}')
        by_key = dict(zip(KEYS, trans_lines))
        lines.append(f"  atlas('{lang}', {{")
        for k in string_keys:
            lines.append(f'    {jsq(k)}: {jsq(by_key[k])},')
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
