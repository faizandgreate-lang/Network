import re, json, sys
path = sys.argv[1]
with open(path, encoding='utf-8') as f:
    content = f.read()
pattern = re.compile(r"'[^']+':\s*'((?:\\'|[^'])*)'")
values = [m.group(1).replace("\\'", "'") for m in pattern.finditer(content)]
unique = list(dict.fromkeys(values))
print(len(values), len(unique))
json.dump(unique, open('/tmp/en-unique.json','w'), ensure_ascii=False, indent=2)
