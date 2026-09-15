/*
 * PG Tutoring Hub Firebase client.
 * Chat uses the Django HTTP endpoints; this file only handles notifications.
 */

const firebaseConfig = {
    apiKey: "AIzaSyA-ACa0jIx85-akOiGOYLVPpKRPcMgkzq0",
    authDomain: "pg-tutoring-hub.firebaseapp.com",
    projectId: "pg-tutoring-hub",
    storageBucket: "pg-tutoring-hub.firebasestorage.app",
    messagingSenderId: "79088624712",
    appId: "1:79088624712:web:3915324d7c72481003a47d",
    measurementId: "G-GXQ0MER6EP"
};

let messaging = null;

document.addEventListener("DOMContentLoaded", () => {
    if (typeof firebase === "undefined" || !firebase.initializeApp) {
        console.warn("[FCM] Firebase compat SDK not found.");
        return;
    }

    try {
        firebase.initializeApp(firebaseConfig);
        if (firebase.messaging) {
            messaging = firebase.messaging();
            setupNotifications();
        }
    } catch (error) {
        console.error("[FCM] Firebase initialization failed:", error);
    }
});

function setupNotifications() {
    if (!messaging || !("Notification" in window)) return;

    Notification.requestPermission().then((permission) => {
        if (permission !== "granted") return;
        messaging.getToken({ vapidKey: window.FIREBASE_VAPID_KEY || "" })
            .then((token) => {
                if (token) sendTokenToServer(token);
            })
            .catch((error) => console.warn("[FCM] Token retrieval failed:", error));
    });

    messaging.onMessage((payload) => {
        if (payload && payload.notification) showNotification(payload.notification);
    });
}

function sendTokenToServer(token) {
    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    const headers = { "Content-Type": "application/json" };
    if (csrfInput && csrfInput.value) headers["X-CSRFToken"] = csrfInput.value;

    fetch("/api/firebase/token/", {
        method: "POST",
        headers,
        body: JSON.stringify({ token })
    }).catch((error) => console.error("[FCM] Token registration failed:", error));
}

function showNotification(notification) {
    const title = notification.title || "PG Tutoring Hub";
    const options = {
        body: notification.body || "",
        icon: notification.icon || "/static/img/logo.png",
        badge: notification.badge || "/static/img/badge.png",
        tag: "pg-tutoring-notification"
    };

    if (navigator.serviceWorker && navigator.serviceWorker.ready) {
        navigator.serviceWorker.ready.then((registration) => {
            registration.showNotification(title, options);
        });
    }
}
