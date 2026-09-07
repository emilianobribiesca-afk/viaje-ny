import json, re, os, sys, shutil, base64

new = json.load(open('TIX_new.json'))
targets = [os.path.expanduser('~/Downloads/nueva-york-app.html'),
           os.path.expanduser('~/viaje-ny/index.html')]

for path in targets:
    shutil.copy2(path, path + '.bak')
    lines = open(path, encoding='utf-8').read().split('\n')
    iT = next(i for i,l in enumerate(lines) if l.startswith('const TIX = '))
    iD = next(i for i,l in enumerate(lines) if l.startswith('const DATA = '))

    old = json.loads(re.match(r'const TIX = (\{.*\});?$', lines[iT]).group(1))
    tix = dict(new)
    tix['cecc'] = old['cecc']                       # la única que sigue siendo captura
    lines[iT] = 'const TIX = ' + json.dumps(tix, separators=(',',':')) + ';'

    D = json.loads(re.match(r'const DATA = (\{.*\});?$', lines[iD]).group(1))
    D['tickets']['summit']['imgs'] = 'summit'
    D['tickets']['summit']['code'] = 'Boletos 1002011050359… · orden 49431400'
    lines[iD] = 'const DATA = ' + json.dumps(D, ensure_ascii=False, separators=(',',':')) + ';'

    open(path,'w',encoding='utf-8').write('\n'.join(lines))
    print(f'{path}: TIX línea {iT+1}, DATA línea {iD+1} · {sum(len(v) for v in tix.values())} imágenes · {os.path.getsize(path)//1024} KB')
