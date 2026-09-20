/**
 * TRACA Management Service Worker
 * Enhanced caching and offline support for mobile devices
 */

const CACHE_NAME = 'traca-v1';
const STATIC_CACHE = 'traca-static-v1';
const DYNAMIC_CACHE = 'traca-dynamic-v1';

// Files to cache for offline functionality
const STATIC_ASSETS = [
    '/',
    '/static/css/brand.css',
    '/static/css/mobile-enhanced.css',
    '/static/css/admin-custom.css',
    '/static/css/whatsapp-button.css',
    '/static/css/property-comparison.css',
    '/static/css/traca-chatbot.css',
    '/static/js/performance-optimized.js',
    '/static/js/whatsapp-button.js',
    '/static/js/property-comparison.js',
    '/static/js/traca-chatbot.js',
    '/static/js/whatsapp-config.js',
    '/static/js/social-share.js',
    '/static/images/traca-logo-new.png',
    '/static/images/default_property.jpg',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Service Worker: Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('Service Worker: Static assets cached');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('Service Worker: Failed to cache static assets', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== CACHE_NAME) {
                            console.log('Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip external requests (except CDN resources)
    if (url.origin !== location.origin && !url.hostname.includes('cdn.jsdelivr.net')) {
        return;
    }
    
    event.respondWith(
        caches.match(request)
            .then(response => {
                // Return cached version if available
                if (response) {
                    console.log('Service Worker: Serving from cache', request.url);
                    return response;
                }
                
                // Otherwise, fetch from network
                return fetch(request)
                    .then(response => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone response since it can only be consumed once
                        const responseToCache = response.clone();
                        
                        // Cache the response
                        if (shouldCache(request.url)) {
                            caches.open(DYNAMIC_CACHE)
                                .then(cache => {
                                    console.log('Service Worker: Caching dynamic content', request.url);
                                    cache.put(request, responseToCache);
                                });
                        }
                        
                        return response;
                    })
                    .catch(error => {
                        console.log('Service Worker: Network failed, trying offline fallback', error);
                        
                        // Return offline page for navigation requests
                        if (request.mode === 'navigate') {
                            return caches.match('/offline.html') || 
                                   new Response('Offline - Please check your internet connection', {
                                       status: 503,
                                       statusText: 'Service Unavailable'
                                   });
                        }
                        
                        // Return cached image placeholder for image requests
                        if (request.destination === 'image') {
                            return caches.match('/static/images/default_property.jpg');
                        }
                        
                        // Return error for other requests
                        return new Response('Offline', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
            })
    );
});

// Determine if a request should be cached
function shouldCache(url) {
    const urlObj = new URL(url);
    
    // Cache static assets
    if (urlObj.pathname.includes('/static/') || 
        urlObj.pathname.includes('/media/') ||
        urlObj.hostname.includes('cdn.jsdelivr.net')) {
        return true;
    }
    
    // Cache API responses for a short time
    if (urlObj.pathname.includes('/api/')) {
        return true;
    }
    
    // Cache pages
    if (urlObj.pathname.includes('/properties/') || 
        urlObj.pathname.includes('/property/') ||
        urlObj.pathname === '/' ||
        urlObj.pathname === '/about/' ||
        urlObj.pathname === '/contact/' ||
        urlObj.pathname === '/services/') {
        return true;
    }
    
    return false;
}

// Background sync for offline actions
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        console.log('Service Worker: Background sync triggered');
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    // Handle offline actions that need to be synced
    return self.registration.showNotification('TRACA Management', {
        body: 'Your offline actions have been synced',
        icon: '/static/images/traca-logo-new.png',
        badge: '/static/images/traca-logo-new.png'
    });
}

// Push notifications
self.addEventListener('push', event => {
    console.log('Service Worker: Push received');
    
    const options = {
        body: event.data ? event.data.text() : 'You have a new notification from TRACA Management',
        icon: '/static/images/traca-logo-new.png',
        badge: '/static/images/traca-logo-new.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Explore Properties',
                icon: '/static/images/traca-logo-new.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/traca-logo-new.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('TRACA Management', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    console.log('Service Worker: Notification click received');
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/properties/')
        );
    } else if (event.action === 'close') {
        // Just close the notification
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', event => {
    if (event.tag === 'content-sync') {
        console.log('Service Worker: Periodic sync triggered');
        event.waitUntil(syncContent());
    }
});

function syncContent() {
    // Sync dynamic content like property listings
    return caches.open(DYNAMIC_CACHE)
        .then(cache => {
            return cache.add('/properties/');
        });
}

// Message handling from main thread
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_UPDATE') {
        updateCache();
    }
});

function updateCache() {
    // Update cached content
    return caches.open(STATIC_CACHE)
        .then(cache => {
            return cache.addAll(STATIC_ASSETS);
        });
}

// Cache size management
self.addEventListener('message', event => {
    if (event.data.type === 'GET_CACHE_SIZE') {
        getCacheSize().then(size => {
            event.ports[0].postMessage({ size });
        });
    }
});

function getCacheSize() {
    return caches.keys().then(cacheNames => {
        return Promise.all(
            cacheNames.map(cacheName => {
                return caches.open(cacheName).then(cache => {
                    return cache.keys().then(keys => {
                        return keys.length;
                    });
                });
            })
        ).then(sizes => {
            return sizes.reduce((total, size) => total + size, 0);
        });
    });
}

// Performance monitoring
self.addEventListener('fetch', event => {
    const start = performance.now();
    
    event.respondWith(
        (async () => {
            try {
                const response = await fetch(event.request);
                const end = performance.now();
                const duration = end - start;
                
                // Log slow requests
                if (duration > 1000) {
                    console.warn(`Slow request detected: ${event.request.url} took ${duration}ms`);
                }
                
                return response;
            } catch (error) {
                const end = performance.now();
                const duration = end - start;
                
                console.error(`Request failed: ${event.request.url} after ${duration}ms`, error);
                throw error;
            }
        })()
    );
});

console.log('Service Worker: Loaded');
