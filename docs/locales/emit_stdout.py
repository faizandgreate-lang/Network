#!/usr/bin/env python3
"""Emit phrases-all.js to stdout — redirect: python3 emit_stdout.py > phrases-all.js"""
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
from _trans_data import KEYS  # noqa: E402

STRINGS_PATH = os.path.join(DIR, '_strings.json')
LANGS = [
    'sa', 'hi', 'ar', 'fr', 'es', 'zh', 'ja', 'de', 'ru', 'pt', 'bn', 'ur', 'ne', 'ml',
    'mr', 'gu', 'sw', 'tl', 'ko', 'th', 'he', 'el', 'fa', 'ta', 'te', 'kn', 'pa', 'it',
    'id', 'vi', 'tr', 'pl', 'nl', 'zu', 'am', 'ha', 'cy', 'haw',
]


def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


with open(STRINGS_PATH, encoding='utf-8') as f:
    string_keys = json.load(f)

out = [
    '(function (g) {',
    "  if (typeof g.registerStringAtlas !== 'function') return;",
    '  function atlas(lang, pairs) {',
    '    g.registerStringAtlas(lang, pairs);',
    '    g.I18N_PHRASES = g.I18N_PHRASES || {};',
    '    g.I18N_PHRASES[lang] = pairs;',
    '  }',
]
for lang in LANGS:
    p = os.path.join(DIR, '_langs', lang + '.txt')
    with open(p, encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f]
    if len(lines) != len(KEYS):
        sys.stderr.write(f'ERROR {lang}: {len(lines)} vs {len(KEYS)}\n')
        sys.exit(1)
    by_key = dict(zip(KEYS, lines))
    out.append(f"  atlas('{lang}', {{")
    for k in string_keys:
        out.append(f'    {jsq(k)}: {jsq(by_key[k])},')
    out.append('  });')
out.append('})(window);')
out.append('')
sys.stdout.write('\n'.join(out))
sys.stderr.write(f'keys={len(string_keys)} langs={len(LANGS)} lines={len(out)}\n')
