#!/usr/bin/env python3
"""Build phrases-all.js from _langs/*.txt — run after all 38 lang files exist."""
import re, os, glob

DIR = os.path.dirname(os.path.abspath(__file__))
EN = os.path.join(DIR, 'en.js')
OUT = os.path.join(DIR, 'phrases-all.js')
LANGS = ['sa','hi','ar','fr','es','zh','ja','de','ru','pt','bn','ur','ne','ml','mr','gu','sw','tl','ko','th','he','el','fa','ta','te','kn','pa','it','id','vi','tr','pl','nl','zu','am','ha','cy','haw']

def keys_from_en():
    with open(EN, encoding='utf-8') as f:
        c = f.read()
    p = re.compile(r"'[^']+':\s*'((?:\\'|[^'])*)'")
    v = [m.group(1).replace("\\'", "'") for m in p.finditer(c)]
    return list(dict.fromkeys(v))

def jsq(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

def trans_for_key(lines, key_idx):
    """_langs line 160 maps to key 153 (Start the server); lines 145-159 to keys 154-168."""
    if key_idx <= 152:
        return lines[key_idx - 1]
    if key_idx == 153:
        return lines[159] if len(lines) >= 160 else lines[144]
    return lines[key_idx - 10]

def main():
    keys = keys_from_en()
    assert len(keys) == 160, len(keys)
    lines = ['(function (g) {',
        "  if (typeof g.registerStringAtlas !== 'function') return;",
        '  function atlas(lang, pairs) {',
        '    g.registerStringAtlas(lang, pairs);',
        '    g.I18N_PHRASES = g.I18N_PHRASES || {};',
        '    g.I18N_PHRASES[lang] = pairs;',
        '  }']
    for lang in LANGS:
        path = os.path.join(DIR, '_langs', lang + '.txt')
        with open(path, encoding='utf-8') as f:
            trans = [ln.rstrip('\n') for ln in f]
        if len(trans) == 161:
            trans = trans[:144] + trans[145:]
        assert len(trans) == 160, f'{lang}: {len(trans)}'
        lines.append(f"  atlas('{lang}', {{")
        for i, k in enumerate(keys, 1):
            t = trans_for_key(trans, i)
            lines.append(f'    {jsq(k)}: {jsq(t)},')
        lines.append('  });')
    lines.append('})(window);')
    lines.append('')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(len(lines))

if __name__ == '__main__':
    main()
