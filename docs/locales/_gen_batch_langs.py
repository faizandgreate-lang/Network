#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate _batch_zh_ja_ko_th_vi.js atlas blocks (160 keys, fr/en order)."""
import os, re

DIR = os.path.dirname(os.path.abspath(__file__))
EN_PATH = os.path.join(DIR, 'en.js')
FR_PATH = os.path.join(DIR, 'phrases-all.js')
OUT_PATH = os.path.join(DIR, '_batch_zh_ja_ko_th_vi.js')
LANG_DIR = os.path.join(DIR, '_langs')

FN = 'Network Monitor \u2014 empty table cells mean \u201cnot detected\u201d, not guessed.'

def parse_keys_from_fr():
    with open(FR_PATH, encoding='utf-8') as f:
        block = f.read().split("atlas('fr', {")[1].split('});')[0]
    pat = re.compile(r"^\s*'((?:\\'|[^'])*)':", re.M)
    keys = [m.group(1).replace("\\'", "'") for m in pat.finditer(block)]
    if len(keys) != 160:
        raise SystemExit(f'Expected 160 fr keys, got {len(keys)}')
    return keys

def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

def load_txt(lang):
    path = os.path.join(LANG_DIR, lang + '.txt')
    with open(path, encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f.readlines()]
    if len(lines) != 160:
        raise SystemExit(f'{lang}.txt: expected 160 lines, got {len(lines)}')
    return lines

def remap_txt_to_fr_order(txt, lang):
    """_langs/*.txt follow _trans_data order; fr block swaps Start server vs tail."""
    out = txt[:144] + [None] + txt[144:159]
    start = {
        'zh': '启动服务器以加载此指南。',
        'ja': 'このガイドを読み込むにはサーバーを起動してください。',
    }[lang]
    out[144] = start
    fn = {
        'zh': 'Network Monitor — 空表格单元格表示 \u201cnot detected\u201d，而非猜测。',
        'ja': 'Network Monitor — 空のセルは \u201cnot detected\u201d を意味し、推測ではありません。',
    }[lang]
    out[53] = fn
    return out

def emit_block(lang, pairs):
    lines = [f"  atlas('{lang}', {{"]
    for k, v in pairs:
        lines.append(f'    {jsq(k)}: {jsq(v)},')
    lines.append('  });')
    return lines

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
        pairs = list(zip(keys, trans))
        if pairs[53][0] != FN:
            raise SystemExit(f'{lang}: footer key mismatch at 54')
        lines.extend(emit_block(lang, pairs))
    lines.append('})(window);')
    lines.append('')
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {OUT_PATH} ({len(lines)} lines)')

if __name__ == '__main__':
    main()
