#!/usr/bin/env python3
"""Revisa el maestro antes de publicar. Lo corre el CI en cada push.

No valida estilo: valida las cosas que ya se rompieron alguna vez —
JSON de las constantes gigantes, archivos que el service worker promete
cachear, boletos referenciados que no existen y coordenadas fuera de NY.
"""
import json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_CONSTS = ["DATA", "TIX", "FOTOS", "CREDITOS", "MUSEOS", "PLANOS"]
# Estas dos son objetos JS con las claves sin comillas: se normalizan para leerlas.
JS_CONSTS = ["DAYDATE", "HOTEL"]
# Nueva York con holgura: cualquier parada fuera de aquí es un typo de coordenada.
BBOX = (40.45, 41.00, -74.30, -73.60)

fallas = []
def falla(m): fallas.append(m)

html = open(os.path.join(RAIZ, "index.html"), encoding="utf-8").read()

def const(nombre):
    m = re.search(r"^const %s\s*=\s*(.*?);\s*$" % nombre, html, re.M)
    if not m:
        falla("no encuentro `const %s` en index.html" % nombre)
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        falla("%s no es JSON válido: %s" % (nombre, e))
        return None

def const_js(nombre):
    m = re.search(r"^const %s\s*=\s*(.*?);\s*$" % nombre, html, re.M)
    if not m:
        falla("no encuentro `const %s` en index.html" % nombre)
        return None
    crudo = re.sub(r"([{,])\s*([A-Za-z_]\w*)\s*:", r'\1"\2":', m.group(1))
    try:
        return json.loads(crudo)
    except json.JSONDecodeError as e:
        falla("%s no se pudo leer: %s" % (nombre, e))
        return None

C = {n: const(n) for n in JSON_CONSTS}
C.update({n: const_js(n) for n in JS_CONSTS})

# --- Los días del itinerario y sus fechas tienen que coincidir ---
if C["DATA"] and C["DAYDATE"]:
    ids = [d.get("id") for d in C["DATA"].get("days", [])]
    faltan = [i for i in ids if i not in C["DAYDATE"]]
    if faltan:
        falla("DAYDATE no trae fecha para: %s (el clima queda en blanco)" % ", ".join(faltan))
    fuera = [f for f in C["DAYDATE"].values() if not "2026-09-16" <= f <= "2026-09-20"]
    if fuera:
        falla("DAYDATE tiene fechas fuera del viaje: %s" % ", ".join(fuera))

# --- El service worker no puede prometer archivos que no existen ---
sw = open(os.path.join(RAIZ, "sw.js"), encoding="utf-8").read()
m = re.search(r"const ASSETS = \[(.*?)\];", sw, re.S)
if not m:
    falla("no encuentro ASSETS en sw.js")
else:
    for a in re.findall(r"'([^']+)'", m.group(1)):
        if a.startswith("http") or a == "./":
            continue
        if not os.path.exists(os.path.join(RAIZ, a)):
            falla("sw.js cachea %s y ese archivo no está en el repo" % a)
if not re.search(r"const CACHE = 'ny2026-v(\d+)'", sw):
    falla("la versión de CACHE en sw.js no tiene la forma ny2026-vN")

# --- Boletos, fotos y coordenadas ---
data, tix, fotos = C["DATA"], C["TIX"], C["FOTOS"]
if data and tix:
    paradas = [s for d in data.get("days", []) for s in d.get("items", []) if s.get("type") == "stop"]
    if not paradas:
        falla("DATA no trae ninguna parada: cambió la forma del objeto")
    for s in paradas:
        t = s.get("ticket")
        if t and t not in tix:
            falla("la parada «%s» apunta al boleto «%s» que no está en TIX" % (s["name"], t))
        if s.get("status") == "pagado" and not t:
            falla("«%s» está pagado pero no tiene boleto en el wallet" % s["name"])
        la, ln = s.get("lat"), s.get("lng")
        if la is None or ln is None:
            falla("«%s» no tiene coordenadas" % s["name"])
        elif not (BBOX[0] <= la <= BBOX[1] and BBOX[2] <= ln <= BBOX[3]):
            falla("«%s» tiene coordenadas fuera de Nueva York: %s, %s" % (s["name"], la, ln))
    if fotos:
        creditos = C["CREDITOS"] or {}
        for n in fotos:
            if n not in creditos:
                falla("la foto de «%s» no tiene crédito: las licencias CC obligan a atribuir" % n)

# --- Basura que no debe llegar al repo ---
for d, _, fs in os.walk(RAIZ):
    if ".git" in d or "__pycache__" in d:
        continue
    for f in fs:
        if f.endswith((".bak", ".orig", ".rej")):
            falla("sobra un archivo temporal: %s" % os.path.relpath(os.path.join(d, f), RAIZ))

if fallas:
    print("FALLA la validación (%d):" % len(fallas))
    for f in fallas:
        print("  ·", f)
    sys.exit(1)

n = len([s for d in (data or {}).get("days", []) for s in d.get("items", []) if s.get("type") == "stop"])
print("OK · %d paradas, %d boletos, %d fotos con crédito" % (n, len(tix or {}), len(fotos or {})))
