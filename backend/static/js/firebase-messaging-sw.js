// Service Worker for Firebase Cloud Messaging
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

// Firebase configuration (project values)
const firebaseConfig = {
    apiKey: "AIzaSyA-ACa0jIx85-akOiGOYLVPpKRPcMgkzq0",
    authDomain: "pg-tutoring-hub.firebaseapp.com",
    projectId: "pg-tutoring-hub",
    storageBucket: "pg-tutoring-hub.firebasestorage.app",
    messagingSenderId: "79088624712",
    appId: "1:79088624712:web:3915324d7c72481003a47d"
};

// Initialize Firebase in service worker
firebase.initializeApp(firebaseConfig);

// Retrieve an instance of Firebase Messaging
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage(function(payload) {
    console.log('[firebase-messaging-sw.js] Received background message ', payload);
    
    const notificationTitle = payload.notification.title || 'PG Tutoring Hub';
    const notificationOptions = {
        body: payload.notification.body || 'You have a new message',
        icon: '/static/img/logo.png',
        badge: '/static/img/badge.png',
        tag: 'pg-tutoring-notification',
        requireInteraction: true,
        data: payload.data,
        actions: [
            {
                action: 'view',
                title: 'View',
                icon: '/static/img/view-icon.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/img/dismiss-icon.png'
            }
        ]
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification clicks
self.addEventListener('notificationclick', function(event) {
    console.log('[firebase-messaging-sw.js] Notification click received.');

    event.notification.close();

    if (event.action === 'view') {
        // Open the app when notification is clicked
        event.waitUntil(
            clients.openWindow('/')
        );
    } else if (event.action === 'dismiss') {
        // Just close the notification
        console.log('Notification dismissed');
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Handle push events
self.addEventListener('push', function(event) {
    console.log('[firebase-messaging-sw.js] Push event received.');
    
    if (event.data) {
        const data = event.data.json();
        const notificationTitle = data.notification.title || 'PG Tutoring Hub';
        const notificationOptions = {
            body: data.notification.body || 'You have a new message',
            icon: '/static/img/logo.png',
            badge: '/static/img/badge.png',
            tag: 'pg-tutoring-notification',
            requireInteraction: true,
            data: data.data
        };

        event.waitUntil(
            self.registration.showNotification(notificationTitle, notificationOptions)
        );
    }
});

// Cache management for offline functionality
const CACHE_NAME = 'pg-tutoring-hub-v1';
const urlsToCache = [
    '/',
    '/static/css/kids_theme.css',
    '/static/css/bootstrap.min.css',
    '/static/js/firebase-config.js',
    '/static/img/logo.png',
    '/offline.html'
];

// Install event - cache resources
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});