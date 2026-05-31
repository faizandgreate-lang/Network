#!/usr/bin/env python3
"""Write phrases-all.js from embedded TRANSLATIONS (160 keys × 38 langs)."""
import re, os, json

DIR = os.path.dirname(os.path.abspath(__file__))
EN_PATH = os.path.join(DIR, 'en.js')
OUT_PATH = os.path.join(DIR, 'phrases-all.js')
DATA_PATH = os.path.join(DIR, '_translations.json')
LANGS = ['sa','hi','ar','fr','es','zh','ja','de','ru','pt','bn','ur','ne','ml','mr','gu','sw','tl','ko','th','he','el','fa','ta','te','kn','pa','it','id','vi','tr','pl','nl','zu','am','ha','cy','haw']

def parse_unique(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    pat = re.compile(r"'[^']+':\s*'((?:\\'|[^'])*)'")
    vals = [m.group(1).replace("\\'", "'") for m in pat.finditer(content)]
    return list(dict.fromkeys(vals))

def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

def build_js(keys, data):
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
        if lang not in data:
            raise SystemExit(f'missing {lang}')
        trans = data[lang]
        if len(trans) != len(keys):
            raise SystemExit(f'{lang}: {len(trans)} vs {len(keys)}')
        lines.append(f"  atlas('{lang}', {{")
        for k, v in zip(keys, trans):
            lines.append(f'    {jsq(k)}: {jsq(v)},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    return '\n'.join(lines)

def main():
    keys = parse_unique(EN_PATH)
    with open(DATA_PATH, encoding='utf-8') as f:
        data = json.load(f)
    if len(keys) != 160:
        print('warn: keys', len(keys))
    js = build_js(keys, data)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f'Wrote {OUT_PATH} ({js.count(chr(10))+1} lines)')
    for lang in LANGS:
        for k in keys:
            if k not in dict(zip(keys, data[lang])):
                pass
        if len(data[lang]) != len(keys):
            raise SystemExit(f'{lang} count')
    print('OK')

if __name__ == '__main__':
    main()
