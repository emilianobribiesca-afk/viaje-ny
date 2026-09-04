const CACHE = 'ny2026-v2';
const ASSETS = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'];

self.addEventListener('install', e=>{
  e.waitUntil(caches.open(CACHE).then(c=>Promise.allSettled(ASSETS.map(a=>c.add(a)))));
  self.skipWaiting();
});
self.addEventListener('activate', e=>{
  e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', e=>{
  if(e.request.method !== 'GET') return;
  if(e.request.url.includes('api.open-meteo.com')) return;
  e.respondWith(
    caches.match(e.request).then(cached=>{
      const network = fetch(e.request).then(res=>{
        if(res.ok && (e.request.url.startsWith(self.location.origin) || e.request.url.includes('cdnjs') || e.request.url.includes('tile.openstreetmap.org'))){
          caches.open(CACHE).then(c=>c.put(e.request, res.clone()));
        }
        return res;
      }).catch(()=>cached);
      return cached || network;
    })
  );
});
