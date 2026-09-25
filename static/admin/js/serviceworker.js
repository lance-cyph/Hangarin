const CACHE_NAME = 'hangarin-cache-v4'; // Bumped to v4 to trigger the update
const OFFLINE_URL = '/offline/';

// 1. Install Phase
self.addEventListener('install', function(e) {
    self.skipWaiting();
    e.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll([
                OFFLINE_URL,
                '/static/Palawan_State_University_seal.png',
            ]);
        })
    );
});

self.addEventListener('activate', function(e) {
    e.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(function() {
            return self.clients.claim();
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