# -*- coding: utf-8 -*-
"""Genera const PLANOS: un esquema de orientación por museo y piso.

Origen de las posiciones:
  · AMNH — plano oficial en PDF (© 2026 AMNH): posición de cada etiqueta de sala.
  · MET  — coordenadas geográficas de su mapa oficial (map-api.livingmap.com),
           proyectadas a metros y rotadas 60.6°, que es el ángulo que alinea el
           edificio (da 296 x 180 m, las medidas reales del museo).
  · MoMA — diagrama de pisos: el museo se recorre de arriba hacia abajo y las
           galerías van en secuencia. No hay geometría, y no hace falta.
  · 9/11 — esquema de las dos huellas de las torres y Foundation Hall.
El dibujo es propio. Ninguno es un plano a escala: sirven para orientarse.
"""
import json, math, os

def S(n, x, y, r=None, cerrada=False, w=None, h=None, tenue=False):
    d = {"n": n, "x": round(x), "y": round(y)}
    if r: d["r"] = r if isinstance(r, list) else [r]
    if cerrada: d["c"] = 1
    if w: d["w"] = w
    if h: d["h"] = h
    if tenue: d["g"] = 1
    return d

# ---------------------------------------------------------------- AMNH
AMNH = {
 "titulo": "Museo de Historia Natural",
 "fuente": "Posiciones del plano oficial del museo.",
 "ref": {"t": "Columbus Ave", "b": "Central Park West", "l": "calle 77", "r": "calle 81 · su entrada"},
 "vb": [40, 110, 500, 500],
 "pisos": [
  {"id": "1", "n": "Piso 1", "salas": [
    S("Gemas y minerales", 222, 168, r=4, h=52),
    S("Meteoritos", 102, 190, r=3, w=92),
    S("Insectario", 352, 244, r=8, w=92),
    S("Origen humano", 108, 280, tenue=True, w=88),
    S("Costa del Noroeste", 214, 352, r=6, h=52),
    S("Pantalla gigante", 330, 390, tenue=True, w=88),
    S("Vida marina · la ballena", 192, 444, r=5, h=54),
    S("Mamíferos de Norteamérica", 322, 486, r=7, h=52),
    S("Planetario", 418, 440, cerrada=True, w=82),
    S("Ambiente de Nueva York", 106, 504, tenue=True, w=90),
    S("Biodiversidad", 206, 528, tenue=True, w=88),
    S("Bosques", 96, 560, tenue=True, w=88),
    S("Sala Roosevelt", 318, 562, tenue=True, w=88),
    S("Centro Rose · Planeta Tierra", 462, 556, r=2, h=58, w=92),
  ]},
  {"id": "2", "n": "Piso 2", "salas": [
    S("Pueblos sudamericanos", 222, 172, tenue=True),
    S("Mariposario", 356, 236, cerrada=True),
    S("México y Centroamérica", 105, 270, tenue=True),
    S("Pueblos africanos", 226, 354, tenue=True),
    S("Aves del mundo", 105, 374, tenue=True),
    S("Mamíferos africanos · elefantes", 316, 468, r=9, h=58, w=100),
    S("Pueblos asiáticos", 104, 511, tenue=True),
    S("Mamíferos asiáticos", 212, 548, tenue=True, w=90),
    S("Rotonda Roosevelt", 316, 550, r=10, w=96),
    S("Centro Rose", 462, 534, tenue=True, w=88),
  ]},
  {"id": "4", "n": "Piso 4", "salas": [
    S("Galería 4", 262, 250, cerrada=True, w=86),
    S("Orígenes de los vertebrados", 236, 358, tenue=True, w=96),
    S("Orientación · Titanosaurio", 106, 386, r=11, h=58, w=98),
    S("Saurisquios · T. rex", 314, 474, r=12, h=54, w=96),
    S("Mamíferos avanzados", 104, 492, tenue=True, w=92),
    S("Ornitisquios", 214, 548, r=13, w=92),
    S("Mamíferos primitivos", 100, 566, tenue=True, w=92),
  ]},
 ],
}

# ---------------------------------------------------------------- MET
_MET_M = {   # (este-oeste, norte-sur) en metros, del mapa oficial
 "Great Hall":            ( 54,  -8), "Egipto":            ( 54, 114),
 "Dendur":                ( 12, 127), "Griego y romano":   ( 59,-126),
 "Patio romano":          ( 45,-126), "Armaduras":         ( -6,  69),
 "Engelhard":             (-35,  66), "Ala americana p2":  (-67, 107),
 "Pintura europea":       (-30,  -8), "Van Gogh":          (-10,-133),
 "Astor":                 ( 50, 113), "Moderno":           (-57,-122),
 "Lehman":                (-84,  -8), "Africa":            ( 21,-117),
 "Islamico":              ( 53,  70),
}
def met_xy(k, esc=2.05, cx=250, cy=300):
    e, n = _MET_M[k]
    return (cx + e*esc, cy - n*esc)     # este a la derecha, norte arriba

MET = {
 "titulo": "MET",
 "fuente": "Posiciones del mapa oficial del museo, proyectadas y alineadas (el edificio mide 296 x 180 m).",
 "ref": {"t": "calle 84", "b": "calle 80", "l": "Central Park", "r": "5th Avenue · su entrada"},
 "vb": [55, 20, 390, 580],
 "pisos": [
  {"id": "1", "n": "Piso 1", "salas": [
    S("Ala egipcia · Perneb y Dendur", 300, 62, r=[3, 4], w=104, h=56),
    S("Armaduras", *met_xy("Armaduras"), r=7, w=88),
    S("Patio Engelhard", 150, 158, r=8, w=92),
    S("Great Hall · entrada", *met_xy("Great Hall"), r=[1, 2], w=100, h=54),
    S("Arte islámico", 372, 158, tenue=True, w=84),
    S("Griego y romano · Kouros y patio", 300, 480, r=[5, 6], w=104, h=56),
    S("Arte de África", 170, 500, tenue=True, w=88),
    S("Colección Lehman", 250, 555, tenue=True, w=92),
    S("Arte moderno", 132, 420, cerrada=True, w=88),
  ]},
  {"id": "2", "n": "Piso 2", "salas": [
    S("Patio chino Astor", 356, 68, r=14, w=96),
    S("Ala americana", 160, 92, r=[9, 10], w=92, h=54),
    S("Pintura europea", *met_xy("Pintura europea"), r=[11, 12], w=96, h=54),
    S("Van Gogh e impresionistas", 190, 470, r=13, w=100, h=56),
    S("Arte moderno", 132, 545, cerrada=True, w=88),
  ]},
 ],
}

# ---------------------------------------------------------------- MoMA
def _banda(y, salas, x0=90, paso=112):
    return [S(n, x0 + i*paso, y, r=r, w=100, h=r and 50 or 44, tenue=(r is None))
            for i, (n, r) in enumerate(salas)]
MOMA = {
 "titulo": "MoMA",
 "fuente": "Diagrama de pisos: el museo se baja del 5 a la planta baja y las galerías van en secuencia.",
 "ref": {"t": "se empieza arriba", "b": "se sale por la planta baja", "l": "", "r": ""},
 "vb": [20, 60, 460, 420],
 "pisos": [
  {"id": "todo", "n": "Los 4 niveles", "salas":
    _banda(110, [("501 · Noche estrellada", 2), ("502 · Aviñón", 3), ("506 · Matisse", 4)]) +
    _banda(190, [("515 · Nenúfares", 5), ("517 · Dalí", 6)]) +
    _banda(290, [("403 · Rothko", 7), ("405 · Pollock", 8), ("412 · Warhol", 9)]) +
    _banda(380, [("3 North · Frida", 10)]) +
    _banda(450, [("Jardín de esculturas", 11)]),
   "bandas": [
     {"y": 150, "n": "PISO 5 · pintura y escultura 1880-1940"},
     {"y": 290, "n": "PISO 4 · 1940-1970"},
     {"y": 380, "n": "PISO 3 · fotografía y dibujo"},
     {"y": 450, "n": "PLANTA BAJA"},
   ]},
 ],
}

# ---------------------------------------------------------------- 9/11
N11 = {
 "titulo": "Museo del 9/11",
 "fuente": "Esquema de las dos huellas de las torres y Foundation Hall. Casi todo está en el nivel del lecho de roca.",
 "ref": {"t": "calle Vesey", "b": "calle Liberty", "l": "West Street", "r": "Greenwich St · su entrada"},
 "vb": [30, 30, 440, 440],
 "pisos": [
  {"id": "plaza", "n": "Plaza (exterior)", "salas": [
    S("One World Trade", 200, 80, tenue=True, w=120),
    S("Fuente norte", 200, 180, r=1, w=120, h=86),
    S("Fuente sur", 200, 330, r=1, w=120, h=86),
    S("Pabellón de entrada", 372, 255, r=2, w=92, h=56),
  ]},
  {"id": "bedrock", "n": "Lecho de roca (-21 m)", "salas": [
    S("Huella Torre Norte · exposición del día", 240, 145, r=[7, 8], w=170, h=86),
    S("Memorial Hall · las acuarelas", 240, 240, r=6, w=170, h=44),
    S("Huella Torre Sur · In Memoriam", 240, 335, r=9, w=170, h=86),
    S("Foundation Hall · Slurry Wall y Last Column", 106, 240, r=[4, 5], w=72, h=170),
    S("Rampa · Survivors' Stairs", 386, 150, r=3, w=76, h=76),
    S("Ladder 3 y la antena", 386, 330, r=10, w=76, h=62),
  ]},
 ],
}

PLANOS = {"n11": N11, "met": MET, "amnh": AMNH, "moma": MOMA}

p = os.path.expanduser('~/viaje-ny/index.html')
s = open(p, encoding='utf-8').read()
import re
linea = 'const PLANOS = ' + json.dumps(PLANOS, ensure_ascii=False, separators=(',', ':')) + ';'
pat = re.compile(r'^const PLANOS = \{.*\};$', re.M)
s = pat.sub(lambda _: linea, s, count=1) if pat.search(s) else s.replace('const LINECOLOR = ', linea + '\nconst LINECOLOR = ', 1)
open(p, 'w', encoding='utf-8').write(s)

for k, v in PLANOS.items():
    tot = sum(len(f['salas']) for f in v['pisos'])
    ruta = sum(len([x for x in f['salas'] if 'r' in x]) for f in v['pisos'])
    print(f"  {k:5} {v['titulo'][:28]:30} {len(v['pisos'])} niveles · {tot:2} salas · {ruta:2} con parada")
print(f"\npeso: {len(linea)//1024} KB")
