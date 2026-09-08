# El mapa offline

`ny.pmtiles` (20 MB) es el mapa vectorial de Nueva York: Protomaps sobre datos de
OpenStreetMap. Sin llaves de API y sin depender de ningún servidor de tiles.

## Cómo se regenera

```bash
# la CLI: https://github.com/protomaps/go-pmtiles/releases (Darwin_arm64)
pmtiles extract https://build.protomaps.com/AAAAMMDD.pmtiles ny.pmtiles \
  --bbox=-74.06,40.66,-73.90,40.80 --maxzoom=15
```

- El bbox cubre Manhattan, Liberty Island, Ellis y DUMBO. **JFK queda fuera a
  propósito**: incluirlo subía el archivo de 20 a 43 MB, y ahí van en Uber y hay wifi.
- `--maxzoom=15` es el máximo real de los datos: pedir 16 da el mismo archivo.
- `--dry-run` estima el tamaño antes de bajar nada. Úsalo para tantear el bbox.

## Cosas que costaron y no hay que volver a descubrir

- La librería es `protomaps-leaflet` (v5, `pml.js`, self-hosteada para que funcione
  sin red). La opción del tema se llama **`flavor`**, no `theme`, y acepta el string
  `"light"`. Pasarle un objeto de `@protomaps/basemaps` truena con "Flavor not found";
  ese paquete no hace falta.
- **v3 de la librería no sirve** con estos datos: el basemap v4 renombró las
  propiedades y ninguna regla de pintado coincide. El síntoma es cruel — los datos
  cargan bien (se pueden listar las capas y contar features) pero el canvas queda
  transparente, sin un solo error en consola.
- El archivo se lee por **rangos de bytes**. Cache Storage no admite respuestas 206,
  así que `sw.js` guarda el archivo entero y corta el pedazo pedido con `blob.slice()`.
- El mapa vive en su propio caché (`ny-map-v1`) para que actualizar la app no borre
  los 20 MB.
- Para probar en local hace falta un servidor **con soporte de Range**;
  `python3 -m http.server` no lo tiene y devuelve 200 con el archivo completo.

## Las fotos del itinerario

Las miniaturas 160x160 vienen de Wikimedia Commons, indexadas por el campo `name` de
cada parada, y se integran con:

```bash
python3 herramientas/integrar_fotos.py herramientas/fotos*.json
```

Eso regenera `const FOTOS` y `const CREDITOS` en `index.html`, y **falla** si alguna
clave no corresponde a ninguna parada (así se detecta un nombre mal escrito).
Van 44 de 50 paradas; las otras 6 llevan un icono de su categoría.

- **Las licencias obligan a atribuir.** Casi todo es CC BY o CC BY-SA, así que la
  pestaña Info muestra autor y licencia de cada foto. Si agregas fotos, el crédito
  se genera solo desde el campo `licencia` del JSON.
- Una foto marcada `"tipo":"tematica"` **no es el lugar**, es ilustrativa (ramen para
  Tonchin, nigiri para Shiro, café turco para Kahve, porque no existe foto libre de
  esos locales). El integrador les agrega "foto ilustrativa, no es el lugar" en el
  crédito; no quitar esa marca.
- **El hotel no tiene foto a propósito.** En el acervo libre no hay ninguna del Romer
  Hell's Kitchen; lo único que aparece de esa cuadra es la Octava Avenida sin hotel
  visible. Si quieres una real, tiene que ser una foto propia.
- Wikimedia tira rate limit como a las 8 peticiones seguidas: batchear con
  `titles=A|B|C`. Openverse funciona pero tarda 30-90 s por consulta y falla a ratos.

## Las rutas dentro de los museos

`const MUSEOS` en `index.html` guarda las cuatro rutas internas (9/11, MET, AMNH, MoMA):
paradas en orden de recorrido, piso y galería, minutos, avisos y qué recortar. Se editan
con un script (es una línea gigante). El generador vive en el scratchpad de la sesión;
si hay que rehacerlo, la estructura es:

```python
{"n11": {"nombre", "parada", "cuando", "min", "color", "tip",
         "stops":[{"q","d","m","por", "fuera": True}], "avisos":[], "cortar":[]}}
```

- `parada` debe coincidir **exactamente** con el `name` de la parada del itinerario: de ahí
  saca la foto del encabezado y ahí aparece el botón "Qué ver adentro".
- `"fuera": True` marca una parada que no consume el tiempo de adentro (las fuentes del
  Memorial del 9/11, que son exteriores y gratis).
- **Los minutos se suman en el render, no a mano** (`sumaMin` / `holgura`). Se hizo así
  porque el total reportado para el MET no cuadraba con la suma de sus propias paradas.

### Datos con fecha de caducidad — revisar la semana del viaje

- **MET**: rota obras entre galerías. Los números son del 8-sep-2026, de la API oficial de
  la colección (`collectionapi.metmuseum.org`, filtrando `isOnView=true`) y del mapa
  `maps.metmuseum.org`. Revisar `metmuseum.org/plan-your-visit/gallery-closures`.
- **AMNH**: su lista de cierres solo cubre dos semanas y se actualiza cada lunes. El
  mariposario está cerrado del 8 al 18 de septiembre. Revisar `amnh.org/plan-your-visit/hours`.
- **MoMA**: rota la colección permanente cada pocos meses. El buscador de `moma.org` dice
  si una obra está "on view" y en qué galería; el Pollock famoso y la Drowning Girl no lo
  están.
- Ni el MET ni el AMNH publican ya un itinerario oficial de "si solo tienes 2 horas": los
  minutos por parada son estimación, no dato oficial.
