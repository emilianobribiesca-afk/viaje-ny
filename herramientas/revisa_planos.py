"""Revisa que ningún bloque del plano se solape ni se salga del marco.

    python3 herramientas/revisa_planos.py

Correrlo siempre después de mover una sala en gen_planos.py: a ojo no se ven
los solapes de 3 px, y en el celular sí.
"""
import re, json, os, sys

s = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html'), encoding='utf-8').read()
P = json.loads(re.search(r'^const PLANOS = (\{.*\});$', s, re.M).group(1))
malos = 0
for k, pl in P.items():
    for f in pl['pisos']:
        cs = [(sa['x']-sa.get('w',96)/2, sa['y']-sa.get('h',46)/2, sa.get('w',96), sa.get('h',46), sa['n'])
              for sa in f['salas']]
        bad = []
        for i in range(len(cs)):
            for j in range(i+1, len(cs)):
                a, b = cs[i], cs[j]
                ox = min(a[0]+a[2], b[0]+b[2]) - max(a[0], b[0])
                oy = min(a[1]+a[3], b[1]+b[3]) - max(a[1], b[1])
                if ox > 2 and oy > 2: bad.append(f'{a[4]} / {b[4]} ({ox:.0f}x{oy:.0f})')
        vx, vy, vw, vh = pl['vb']
        fuera = [c[4] for c in cs if c[0] < vx or c[1] < vy or c[0]+c[2] > vx+vw or c[1]+c[3] > vy+vh]
        print(f"{k:5} {f['n'][:24]:26} {'OK' if not bad and not fuera else 'REVISAR'}")
        for x in bad:   print('        solape:', x); malos += 1
        for x in fuera: print('        fuera del marco:', x); malos += 1
sys.exit(1 if malos else 0)
