// Minimal service worker: makes the app installable. Network pass-through only.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) =>
  event.waitUntil(self.clients.claim()),
);
self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request));
});
