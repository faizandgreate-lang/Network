#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble _batch_zh_ja_ko_th_vi.js from _batch_*_block.js.part (no IIFE wrapper)."""
import os

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, '_batch_zh_ja_ko_th_vi.js')
LANGS = ('zh', 'ja', 'ko', 'th', 'vi')

def main():
    parts = []
    for lang in LANGS:
        path = os.path.join(DIR, f'_batch_{lang}_block.js.part')
        with open(path, encoding='utf-8') as f:
            parts.append(f.read().rstrip() + '\n')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(''.join(parts))
    print('Wrote', OUT, len(parts), 'blocks')

if __name__ == '__main__':
    main()
