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

`fotos.json` son las 36 miniaturas 160x160 de Wikimedia Commons, indexadas por el
campo `name` de cada parada. Van incrustadas en `index.html` como `const FOTOS`.
Las 9 paradas sin foto llevan un icono de su categoría. Wikimedia tira rate limit
como a las 8 peticiones seguidas: hay que batchear con `titles=A|B|C`.
