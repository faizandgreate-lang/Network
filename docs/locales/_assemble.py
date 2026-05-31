#!/usr/bin/env python3
"""Assemble phrases-all.js from _langs/*.txt (160 lines each, KEYS order)."""
import os, re

DIR = os.path.dirname(os.path.abspath(__file__))
EN_PATH = os.path.join(DIR, 'en.js')
OUT_PATH = os.path.join(DIR, 'phrases-all.js')
LANG_DIR = os.path.join(DIR, '_langs')
LANGS = ['sa','hi','ar','fr','es','zh','ja','de','ru','pt','bn','ur','ne','ml','mr','gu','sw','tl','ko','th','he','el','fa','ta','te','kn','pa','it','id','vi','tr','pl','nl','zu','am','ha','cy','haw']

def parse_unique(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    pat = re.compile(r"'[^']+':\s*'((?:\\'|[^'])*)'")
    vals = [m.group(1).replace("\\'", "'") for m in pat.finditer(content)]
    return list(dict.fromkeys(vals))

def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

def load_lang(lang):
    path = os.path.join(LANG_DIR, lang + '.txt')
    with open(path, encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f.readlines()]
    if len(lines) != 160:
        raise SystemExit(f'{lang}.txt: expected 160 lines, got {len(lines)}')
    return lines

def main():
    keys = parse_unique(EN_PATH)
    if len(keys) != 160:
        raise SystemExit(f'Expected 160 unique keys, got {len(keys)}')
    missing = [l for l in LANGS if not os.path.isfile(os.path.join(LANG_DIR, l + '.txt'))]
    if missing:
        raise SystemExit(f'Missing lang files: {missing}')
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
        trans = load_lang(lang)
        lines.append(f"  atlas('{lang}', {{")
        for k, v in zip(keys, trans):
            lines.append(f'    {jsq(k)}: {jsq(v)},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    text = '\n'.join(lines)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Wrote {OUT_PATH} ({len(lines)} lines)')
    for lang in LANGS:
        trans = load_lang(lang)
        for k, v in zip(keys, trans):
            if not v:
                raise SystemExit(f'{lang}: empty translation for {k!r}')
    print('OK')

if __name__ == '__main__':
    main()
