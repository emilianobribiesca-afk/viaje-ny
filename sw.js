const CACHE = 'ny2026-v7';
const MAPCACHE = 'ny-map-v1';          // el mapa de 20 MB vive aparte: no se borra al actualizar la app
const MAPFILE = 'ny.pmtiles';
const ASSETS = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png', './pml.js',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'];

self.addEventListener('install', e=>{
  e.waitUntil(caches.open(CACHE).then(c=>Promise.allSettled(ASSETS.map(a=>c.add(a)))));
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

self.addEventListener('fetch', e=>{
  if(e.request.method !== 'GET') return;
  const url = e.request.url;
  if(url.includes('api.open-meteo.com')) return;
  if(url.includes(MAPFILE)){ e.respondWith(serveMap(e.request)); return; }
  e.respondWith(
    caches.match(e.request).then(cached=>{
      const network = fetch(e.request).then(res=>{
        if(res.ok && (url.startsWith(self.location.origin) || url.includes('cdnjs'))){
          caches.open(CACHE).then(c=>c.put(e.request, res.clone()));
        }
        return res;
      }).catch(()=>cached);
      return cached || network;
    })
  );
});
