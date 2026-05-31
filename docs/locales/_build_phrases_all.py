#!/usr/bin/env python3
# Generates phrases-all.js — run: python3 _build_phrases_all.py
import re, os

DIR = os.path.dirname(os.path.abspath(__file__))
EN_PATH = os.path.join(DIR, 'en.js')
OUT_PATH = os.path.join(DIR, 'phrases-all.js')

def parse_unique(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    pat = re.compile(r"'[^']+':\s*'((?:\\'|[^'])*)'")
    vals = [m.group(1).replace("\\'", "'") for m in pat.finditer(content)]
    return list(dict.fromkeys(vals))

def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

LANGS = ['sa','hi','ar','fr','es','zh','ja','de','ru','pt','bn','ur','ne','ml','mr','gu','sw','tl','ko','th','he','el','fa','ta','te','kn','pa','it','id','vi','tr','pl','nl','zu','am','ha','cy','haw']

from _trans_data import KEYS, TRANS  # noqa: E402

def main():
    keys = parse_unique(EN_PATH)
    print(f'Unique keys: {len(keys)} (expected {len(KEYS)})')
    if keys != KEYS:
        for i, (a, b) in enumerate(zip(keys, KEYS)):
            if a != b:
                print(f'  mismatch [{i}] got {a!r} expected {b!r}')
                break
        else:
            if len(keys) != len(KEYS):
                print(f'  length mismatch')
        raise SystemExit('KEYS out of sync with en.js')
    for lang in LANGS:
        if lang not in TRANS:
            raise SystemExit(f'Missing lang {lang}')
        if len(TRANS[lang]) != len(KEYS):
            raise SystemExit(f'{lang}: expected {len(KEYS)}, got {len(TRANS[lang])}')
    keys = KEYS
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
        for k, v in zip(keys, TRANS[lang]):
            lines.append(f'    {jsq(k)}: {jsq(v)},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    text = '\n'.join(lines)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Wrote {OUT_PATH} ({len(lines)} lines)')
    for lang in LANGS:
        for k in keys:
            if k not in TRANS[lang]:
                raise SystemExit(f'{lang} missing key')
    print('Verification OK')

if __name__ == '__main__':
    main()
