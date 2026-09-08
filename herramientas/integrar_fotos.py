"""Une los fotos*.json, mete las miniaturas en index.html y arma los créditos.

Las fotos vienen de Wikimedia Commons y casi todas son CC BY o CC BY-SA, que
exigen atribuir autor y licencia: por eso se genera `const CREDITOS`, que la
pestaña Info muestra al final. Se puede re-ejecutar cuantas veces haga falta.

    python3 herramientas/integrar_fotos.py herramientas/fotos.json herramientas/fotos3.json
"""
import io, json, re, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(REPO, 'index.html')

fuentes = sys.argv[1:]
if not fuentes:
    sys.exit('uso: integrar_fotos.py <fotos.json> [fotos2.json ...]')

todas = {}
for f in fuentes:
    d = json.load(open(f, encoding='utf-8'))
    for k, v in d.items():
        todas[k] = v
    print(f'{os.path.basename(f)}: {len(d)} fotos')

s = io.open(IDX, encoding='utf-8').read()
DATA = json.loads(re.search(r'^const DATA = (\{.*\});$', s, re.M).group(1))
nombres = {it['name'] for day in DATA['days'] for it in day['items'] if it.get('type') == 'stop'}

huerfanas = [k for k in todas if k not in nombres]
if huerfanas:
    sys.exit(f'ERROR: estas claves no corresponden a ninguna parada: {huerfanas}')

FOTOS = {k: v['b64'] for k, v in todas.items()}
CREDITOS = {}
for k, v in todas.items():
    lic = v.get('licencia', '').strip()
    if v.get('tipo') == 'tematica':
        lic += ' · foto ilustrativa, no es el lugar'
    CREDITOS[k] = lic

def reemplazar(s, nombre, valor):
    pat = re.compile(r'^const ' + nombre + r' = \{.*\};$', re.M)
    linea = f'const {nombre} = ' + json.dumps(valor, ensure_ascii=False, separators=(',', ':')) + ';'
    if pat.search(s):
        return pat.sub(lambda _: linea, s, count=1)
    # insertarla antes de LINECOLOR la primera vez
    return s.replace('const LINECOLOR = ', linea + '\nconst LINECOLOR = ', 1)

s = reemplazar(s, 'FOTOS', FOTOS)
s = reemplazar(s, 'CREDITOS', CREDITOS)
io.open(IDX, 'w', encoding='utf-8').write(s)

tem = [k for k, v in todas.items() if v.get('tipo') == 'tematica']
print(f'\nintegradas: {len(FOTOS)} fotos · {len(nombres)} paradas · {len(nombres)-len(FOTOS)} sin foto')
print(f'temáticas (no son el lugar): {tem if tem else "ninguna"}')
print(f'index.html: {os.path.getsize(IDX)//1024} KB')
