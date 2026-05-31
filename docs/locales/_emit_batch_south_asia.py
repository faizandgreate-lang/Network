#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit _batch_south_asia.js atlas blocks from _south_asia_data.TRANS."""
import os
from _trans_data import KEYS
from _south_asia_data import TRANS

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, '_batch_south_asia.js')
LANGS = ['bn', 'ur', 'ne', 'ml', 'mr', 'gu', 'pa', 'kn', 'te', 'ta']


def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def main():
    lines = []
    for lang in LANGS:
        if lang not in TRANS:
            raise SystemExit(f'missing {lang}')
        trans = TRANS[lang]
        if len(trans) != len(KEYS):
            raise SystemExit(f'{lang}: {len(trans)} vs {len(KEYS)} keys')
        lines.append(f"  atlas('{lang}', {{")
        for k, v in zip(KEYS, trans):
            lines.append(f'    {jsq(k)}: {jsq(v)},')
        lines.append('  });')
        lines.append('')
    text = '\n'.join(lines).rstrip() + '\n'
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Wrote {OUT} ({len(lines)} lines)')


if __name__ == '__main__':
    main()
