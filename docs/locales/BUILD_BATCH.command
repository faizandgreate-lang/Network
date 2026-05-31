#!/bin/bash
cd "$(dirname "$0")"
/usr/bin/python3 _assemble_batch.py
wc -l _batch_zh_ja_ko_th_vi.js
grep -c "atlas('" _batch_zh_ja_ko_th_vi.js
