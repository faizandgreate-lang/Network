#!/usr/bin/env python3
"""Generate phrases-all.js from en.js unique values and translation tables."""
import re
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
EN_PATH = os.path.join(DIR, 'en.js')
OUT_PATH = os.path.join(DIR, 'phrases-all.js')

def parse_en_values(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = re.compile(r"'[^']+':\s*'((?:\\'|[^'])*)'")
    values = []
    for m in pattern.finditer(content):
        values.append(m.group(1).replace("\\'", "'"))
    unique = list(dict.fromkeys(values))
    return values, unique

def js_quote(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n') + "'"

# Load translations from companion JSON (generated alongside this script)
TRANS_PATH = os.path.join(DIR, '_translations_data.json')

def main():
    total, unique = parse_en_values(EN_PATH)
    print(f'Total entries: {len(total)}, unique: {len(unique)}')
    with open(TRANS_PATH, 'r', encoding='utf-8') as f:
        all_trans = json.load(f)
    langs = ['sa','hi','ar','fr','es','zh','ja','de','ru','pt','bn','ur','ne','ml','mr','gu','sw','tl','ko','th','he','el','fa','ta','te','kn','pa','it','id','vi','tr','pl','nl','zu','am','ha','cy','haw']
    missing_langs = [l for l in langs if l not in all_trans]
    if missing_langs:
        raise SystemExit(f'Missing langs: {missing_langs}')
    lines = [
        '(function (g) {',
        "  if (typeof g.registerStringAtlas !== 'function') return;",
        '  function atlas(lang, pairs) {',
        '    g.registerStringAtlas(lang, pairs);',
        '    g.I18N_PHRASES = g.I18N_PHRASES || {};',
        '    g.I18N_PHRASES[lang] = pairs;',
        '  }',
    ]
    for lang in langs:
        trans = all_trans[lang]
        missing = [u for u in unique if u not in trans]
        extra = [k for k in trans if k not in unique]
        if missing:
            raise SystemExit(f'{lang} missing {len(missing)} keys: {missing[:3]}...')
        lines.append(f"  atlas('{lang}', {{")
        for u in unique:
            lines.append(f'    {js_quote(u)}: {js_quote(trans[u])},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {OUT_PATH} ({len(lines)} lines)')
    # verify
    with open(OUT_PATH, 'r', encoding='utf-8') as f:
        out = f.read()
    for lang in langs:
        for u in unique:
            if js_quote(u) + ':' not in out.split(f"atlas('{lang}'")[1].split('});')[0]:
                raise SystemExit(f'verify fail {lang} {u[:40]}')
    print('Verification OK')

if __name__ == '__main__':
    main()
