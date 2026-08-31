// Cache the shell so the app opens offline; always try the network for data.json
// first, so the morning's build replaces yesterday's reading as soon as it exists.
const CACHE = "qultura-v1";
const SHELL = ["./", "./index.html", "./app.webmanifest", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const fresh = fetch(e.request)
    .then((res) => {
      const copy = res.clone();
      caches.open(CACHE).then((c) => c.put(e.request, copy));
      return res;
    })
    .catch(() => caches.match(e.request));
  // Shell files can come from cache instantly; data.json must try the network first.
  e.respondWith(e.request.url.includes("data.json")
    ? fresh
    : caches.match(e.request).then((hit) => hit || fresh));
});
