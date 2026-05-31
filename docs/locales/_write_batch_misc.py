#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate _batch_misc.js — run: python3 _write_batch_misc.py"""
import re
import os
from _trans_data import KEYS
from _batch_misc_data import ALL

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, '_batch_misc.js')
LANGS = ['he', 'el', 'fa', 'sw', 'zu', 'am', 'ha', 'cy', 'haw']

def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

def phrase_keys():
    """160 keys in phrases-all.js order (Start server before Loading all available data)."""
    keys = list(KEYS)
    if keys[-1] == 'Start the server to load this guide.':
        keys.pop()
    idx = keys.index('Loading all available data\u2026')
    keys.insert(idx, 'Start the server to load this guide.')
    assert len(keys) == 160, len(keys)
    return keys

def main():
    keys = phrase_keys()
    for lang in LANGS:
        trans = ALL[lang]
        if len(trans) != 160:
            raise SystemExit(f'{lang}: expected 160 translations, got {len(trans)}')
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
        lines.append(f"  atlas('{lang}', {{")
        for k, v in zip(keys, ALL[lang]):
            lines.append(f'    {jsq(k)}: {jsq(v)},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {OUT} ({len(lines)} lines, {len(keys)} keys × {len(LANGS)} langs)')

if __name__ == '__main__':
    main()
