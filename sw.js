const CACHE = 'ny2026-v12';
const MAPCACHE = 'ny-map-v1';          // el mapa de 20 MB vive aparte: no se borra al actualizar la app
const MAPFILE = 'ny.pmtiles';
const ASSETS = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png', './pml.js',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'];

/* cache:'reload' es obligatorio: sin él, al instalar una versión nueva el
   navegador rellena el caché con lo que ya tenía guardado y la actualización
   nunca llega. */
self.addEventListener('install', e=>{
  e.waitUntil(caches.open(CACHE).then(c=>Promise.allSettled(
    ASSETS.map(a=>c.add(new Request(a, {cache:'reload'})))
  )));
  self.skipWaiting();
});
self.addEventListener('activate', e=>{
  e.waitUntil(caches.keys().then(keys=>Promise.all(
    keys.filter(k=>k!==CACHE && k!==MAPCACHE).map(k=>caches.delete(k))
  )));
  self.clients.claim();
});

/* El mapa se lee por rangos de bytes. Cache Storage no guarda respuestas 206,
   así que el archivo se guarda entero y aquí se corta el pedazo pedido. */
async function serveMap(req){
  const c = await caches.open(MAPCACHE);
  const full = await c.match(MAPFILE);
  if(!full) return fetch(req);                       // aún no descargado: va a la red
  const range = req.headers.get('range');
  const blob = await full.blob();
  if(!range) return new Response(blob, {status:200, headers:{'Content-Type':'application/octet-stream','Content-Length':String(blob.size)}});
  const m = /bytes=(\d*)-(\d*)/.exec(range);
  if(!m) return new Response(blob, {status:200});
  const start = m[1] ? parseInt(m[1],10) : 0;
  const end   = m[2] ? parseInt(m[2],10) : blob.size - 1;
  if(start >= blob.size) return new Response(null, {status:416, headers:{'Content-Range':`bytes */${blob.size}`}});
  const part = blob.slice(start, end + 1);
  return new Response(part, {status:206, headers:{
    'Content-Type':'application/octet-stream',
    'Content-Length': String(part.size),
    'Content-Range': `bytes ${start}-${end}/${blob.size}`,
    'Accept-Ranges':'bytes'
  }});
}

/* La app se sirve del caché (instantánea y sin datos) y se refresca por detrás,
   así una versión nueva entra sola en la siguiente apertura. */
async function staleWhileRevalidate(req){
  const c = await caches.open(CACHE);
  const cached = await c.match(req, {ignoreSearch:true});
  const fresh = fetch(new Request(req.url, {cache:'reload'}))
    .then(res=>{ if(res.ok) c.put(req, res.clone()); return res; })
    .catch(()=>null);
  return cached || (await fresh) || fetch(req);
}

self.addEventListener('fetch', e=>{
  const req = e.request;
  if(req.method !== 'GET') return;
  const url = req.url;
  if(url.includes('api.open-meteo.com')) return;
  if(url.includes(MAPFILE)){ e.respondWith(serveMap(req)); return; }
  if(req.mode === 'navigate' || url.endsWith('/') || url.includes('index.html') || url.includes('pml.js')){
    e.respondWith(staleWhileRevalidate(req)); return;
  }
  e.respondWith(
    caches.match(req).then(cached=>{
      const network = fetch(req).then(res=>{
        if(res.ok && (url.startsWith(self.location.origin) || url.includes('cdnjs'))){
          caches.open(CACHE).then(c=>c.put(req, res.clone()));
        }
        return res;
      }).catch(()=>cached);
      return cached || network;
    })
  );
});
