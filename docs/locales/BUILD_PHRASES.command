#!/bin/bash
cd "$(dirname "$0")" || exit 1
python3 _merge_phrases_all.py
wc -l phrases-all.js
