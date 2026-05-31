#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit _batch_zh_ja_ko_th_vi.js — run from locales dir: python3 _emit_batch.py"""
import os, re, sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
from _gen_batch_langs import parse_keys_from_fr, jsq, load_txt, remap_txt_to_fr_order, emit_block

OUT = os.path.join(DIR, '_batch_zh_ja_ko_th_vi.js')

def main():
    keys = parse_keys_from_fr()
    lines = ['(function (g) {', "  if (typeof g.registerStringAtlas !== 'function') return;",
             '  function atlas(lang, pairs) {', '    g.registerStringAtlas(lang, pairs);',
             '    g.I18N_PHRASES = g.I18N_PHRASES || {};', '    g.I18N_PHRASES[lang] = pairs;',
             '  }']
    for lang in ('zh', 'ja', 'ko', 'th', 'vi'):
        if lang in ('zh', 'ja'):
            trans = remap_txt_to_fr_order(load_txt(lang), lang)
        else:
            trans = load_txt(lang)
        lines.extend(emit_block(lang, list(zip(keys, trans))))
    lines.append('})(window);')
    lines.append('')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('Wrote', OUT, len(lines), 'lines')

if __name__ == '__main__':
    main()
