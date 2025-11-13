/*
 firebase-config.js (clean)
 compat-friendly initializer for PG Tutoring Hub
*/

// Firebase config (project values)
const firebaseConfig = {
    apiKey: "AIzaSyA-ACa0jIx85-akOiGOYLVPpKRPcMgkzq0",
    authDomain: "pg-tutoring-hub.firebaseapp.com",
    projectId: "pg-tutoring-hub",
    storageBucket: "pg-tutoring-hub.firebasestorage.app",
    messagingSenderId: "79088624712",
    appId: "1:79088624712:web:3915324d7c72481003a47d",
    measurementId: "G-GXQ0MER6EP"
};

// For bundlers prefer: npm install firebase and modular imports (see README/notes)

let app = null;
let auth = null;
let db = null;
let messaging = null;

document.addEventListener('DOMContentLoaded', () => {
    if (typeof firebase !== 'undefined' && firebase && firebase.initializeApp) {
        try {
            app = firebase.initializeApp(firebaseConfig);
            if (firebase.analytics) { try { firebase.analytics(); } catch (e) { console.warn('Analytics init failed', e); } }
            if (firebase.auth) auth = firebase.auth();
            if (firebase.firestore) db = firebase.firestore();
            if (firebase.messaging) messaging = firebase.messaging();

            if (messaging && 'serviceWorker' in navigator && 'Notification' in window) setupNotifications();
            console.log('Firebase (compat) initialized');
        } catch (err) { console.error('Firebase init error:', err); }
    } else {
        console.warn('Firebase compat SDK not found. Use npm/modular imports if bundling.');
    }
});

function setupNotifications() {
    if (!messaging) return;
    Notification.requestPermission().then(permission => {
        if (permission !== 'granted') return;
        messaging.getToken({ vapidKey: (window.FIREBASE_VAPID_KEY || '') })
            .then(token => { if (token) sendTokenToServer(token); })
            .catch(e => console.warn('FCM token error', e));
    });
    messaging.onMessage(payload => { if (payload && payload.notification) showNotification(payload.notification); });
}

function sendTokenToServer(token) {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const headers = { 'Content-Type': 'application/json' };
    if (csrfInput && csrfInput.value) headers['X-CSRFToken'] = csrfInput.value;
    fetch('/api/firebase/token/', { method: 'POST', headers, body: JSON.stringify({ token }) })
        .then(r => { if (!r.ok) console.warn('Token registration failed', r.status); })
        .catch(e => console.error('Token registration error', e));
}

function showNotification(notification) {
    if (!notification) return;
    const title = notification.title || 'PG Tutoring Hub';
    const options = { body: notification.body || '', icon: notification.icon || '/static/img/logo.png', badge: notification.badge || '/static/img/badge.png', tag: 'pg-tutoring-notification' };
    if (navigator.serviceWorker && navigator.serviceWorker.ready) navigator.serviceWorker.ready.then(reg => reg.showNotification(title, options));
    else try { new Notification(title, options); } catch (e) { console.warn('Notification display failed', e); }
}

function initializeChat(roomId) { if (!db) return; const messagesRef = db.collection('chats').doc(roomId).collection('messages'); messagesRef.orderBy('timestamp', 'asc').onSnapshot(s => { s.docChanges().forEach(c => { if (c.type === 'added' && window.displayMessage) window.displayMessage(c.doc.data()); }); }); }

function sendFirebaseMessage(roomId, message, userId, userName) { if (!db) return Promise.reject('Firestore not available'); const messagesRef = db.collection('chats').doc(roomId).collection('messages'); return messagesRef.add({ text: message, userId, userName, timestamp: firebase.firestore.FieldValue.serverTimestamp() }); }

function uploadFileToFirebase(file, path) { if (!firebase.storage) return Promise.reject('Storage not available'); const fileRef = firebase.storage().ref().child(path); return fileRef.put(file).then(s => s.ref.getDownloadURL()); }

function trackProgressInFirebase(userId, activityData) { if (!db) return; return db.collection('progress').doc(userId).set(activityData, { merge: true }); }

function listenForAssignmentUpdates(userId) { if (!db) return; const assignmentsRef = db.collection('assignments').where('studentId', '==', userId); assignmentsRef.onSnapshot(s => { s.docChanges().forEach(c => { if (c.type === 'modified') { const assignment = c.doc.data(); showNotification({ title: 'Assignment Updated', body: `Your assignment "${assignment.title}" has been updated.` }); } }); }); }

window.FirebaseHelper = { sendMessage: sendFirebaseMessage, uploadFile: uploadFileToFirebase, trackProgress: trackProgressInFirebase, initializeChat: initializeChat, listenForAssignmentUpdates: listenForAssignmentUpdates };

// Firebase initialization file
// Two supported methods are described below:
// 1) Using npm and a bundler (webpack/Rollup/Parcel) - modular imports (preferred for production):
//    npm install firebase
//    import { initializeApp } from 'firebase/app';
//    import { getAnalytics } from 'firebase/analytics';
//    import { getAuth } from 'firebase/auth';
//    import { getFirestore } from 'firebase/firestore';
//    import { getMessaging } from 'firebase/messaging';
//    const app = initializeApp(firebaseConfig);
//    const analytics = getAnalytics(app);

// 2) Using a <script> tag (no bundler) - global namespace (this file supports this mode):

// Your web app's Firebase configuration (provided)
const firebaseConfig = {
  apiKey: "AIzaSyA-ACa0jIx85-akOiGOYLVPpKRPcMgkzq0",
  authDomain: "pg-tutoring-hub.firebaseapp.com",
  projectId: "pg-tutoring-hub",
  storageBucket: "pg-tutoring-hub.firebasestorage.app",
  messagingSenderId: "79088624712",
  appId: "1:79088624712:web:3915324d7c72481003a47d",
  measurementId: "G-GXQ0MER6EP"
};

// Global handles
let app = null;
let auth = null;
let db = null;
let messaging = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // If using the <script> tag that provides the compat API
    if (typeof firebase !== 'undefined' && firebase && firebase.initializeApp) {
        try {
            app = firebase.initializeApp(firebaseConfig);
            // Analytics (if available)
            if (firebase.analytics) {
                try { firebase.analytics(); } catch (e) { console.warn('Analytics init failed', e); }
            }

            // Initialize services (compat)
            if (firebase.auth) auth = firebase.auth();
            if (firebase.firestore) db = firebase.firestore();
            if (firebase.messaging) messaging = firebase.messaging();

            if (messaging && 'serviceWorker' in navigator && 'Notification' in window) {
                setupNotifications();
            }

            console.log('Firebase (compat) initialized');
        } catch (error) {
            console.error('Firebase initialization error:', error);
        }
        return;
    }

    // If firebase is not present (e.g., using npm modular builds), the app should initialize via bundler imports.
    console.warn('Firebase global not found. If you are using a bundler, import and initialize Firebase via npm as shown in comments.');
});

// Notification setup (compat)
function setupNotifications() {
    if (!messaging) return;

    Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
            messaging.getToken({ vapidKey: (window.FIREBASE_VAPID_KEY || '') }).then((currentToken) => {
                if (currentToken) {
                    console.log('FCM registration token:', currentToken);
                    sendTokenToServer(currentToken);
                } else {
                    console.log('No registration token available.');
                }
            }).catch((err) => {
                console.warn('Error retrieving token:', err);
            });
        } else {
            console.log('Notifications permission denied.');
        }
    });

    // Foreground message handler
    messaging.onMessage((payload) => {
        console.log('Foreground message:', payload);
        if (payload && payload.notification) showNotification(payload.notification);
    });
}

// Send token to Django backend (uses CSRF token when present)
function sendTokenToServer(token) {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const headers = { 'Content-Type': 'application/json' };
    if (csrfInput && csrfInput.value) headers['X-CSRFToken'] = csrfInput.value;

    fetch('/api/firebase/token/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ token: token })
    }).then(res => {
        if (!res.ok) console.warn('Failed to register token on server', res.status);
    }).catch(err => console.error('Error sending token to server:', err));
}

function showNotification(notification) {
    if (!notification) return;
    const title = notification.title || 'PG Tutoring Hub';
    const options = {
        body: notification.body || '',
        icon: notification.icon || '/static/img/logo.png',
        badge: notification.badge || '/static/img/badge.png',
        tag: 'pg-tutoring-notification'
    };

    if (navigator.serviceWorker && navigator.serviceWorker.ready) {
        navigator.serviceWorker.ready.then(reg => reg.showNotification(title, options));
    } else {
        // Fallback: regular Notification
        try { new Notification(title, options); } catch (e) { console.warn('Notification failed', e); }
    }
}

// Simple Firestore-based chat helpers (compat)
function initializeChat(roomId) {
    if (!db) return console.warn('Firestore not available');
    const messagesRef = db.collection('chats').doc(roomId).collection('messages');
    messagesRef.orderBy('timestamp', 'asc').onSnapshot(snapshot => {
        snapshot.docChanges().forEach(change => {
            if (change.type === 'added') {
                if (window.displayMessage) window.displayMessage(change.doc.data());
            }
        });
    });
}

function sendFirebaseMessage(roomId, message, userId, userName) {
    if (!db) return Promise.reject('Firestore not available');
    const messagesRef = db.collection('chats').doc(roomId).collection('messages');
    return messagesRef.add({ text: message, userId, userName, timestamp: firebase.firestore.FieldValue.serverTimestamp() });
}

function uploadFileToFirebase(file, path) {
    if (!firebase.storage) return Promise.reject('Storage not available');
    const fileRef = firebase.storage().ref().child(path);
    return fileRef.put(file).then(s => s.ref.getDownloadURL());
}

function trackProgressInFirebase(userId, activityData) {
    if (!db) return;
    db.collection('progress').doc(userId).set(activityData, { merge: true }).catch(e => console.warn(e));
}

function listenForAssignmentUpdates(userId) {
    if (!db) return;
    const assignmentsRef = db.collection('assignments').where('studentId', '==', userId);
    assignmentsRef.onSnapshot(snapshot => {
        snapshot.docChanges().forEach(change => {
            if (change.type === 'modified') {
                const assignment = change.doc.data();
                showNotification({ title: 'Assignment Updated', body: `Your assignment "${assignment.title}" has been updated.` });
            }
        });
    });
}

window.FirebaseHelper = {
    sendMessage: sendFirebaseMessage,
    uploadFile: uploadFileToFirebase,
    trackProgress: trackProgressInFirebase,
    initializeChat: initializeChat,
    listenForAssignmentUpdates: listenForAssignmentUpdates
};
