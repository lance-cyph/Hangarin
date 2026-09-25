const CACHE_NAME = 'hangarin-cache-v3';
const OFFLINE_URL = '/offline/';

self.addEventListener('install', function(e) {
    e.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll([
                OFFLINE_URL,
                '/static/Palawan_State_University_seal.png',
            ]);
        })
    );
});

self.addEventListener('fetch', function(e) {
    if (e.request.mode === 'navigate') {
        e.respondWith(
            fetch(e.request).catch(function() {
                return caches.match(OFFLINE_URL);
            })
        );
    }
});