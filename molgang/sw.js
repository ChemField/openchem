/* MOLGANG service worker — offline-first app shell (#116).
 *
 * Strategy:
 *   • app CODE (HTML documents + JS)  → NETWORK-FIRST so a deploy always loads
 *     fresh; cache is only the offline fallback (a cache-first code path once
 *     served a stale shell that black-screened after a fix had shipped);
 *   • /api/*                          → network-first with a cached fallback;
 *   • static assets (css/json/icons)  → cache-first + background revalidate.
 *
 * Install is RESILIENT: the shell is warmed with individual, best-effort adds
 * (Promise.allSettled) so a single missing/404 asset can never abort the whole
 * install. A cache.addAll() over a list that included not-yet-published icons
 * used to throw "Failed to execute 'addAll' on 'Cache': Request failed", which
 * left the NEW worker unable to install — so an OLD worker kept serving a stale,
 * broken shell (the bar/game would not open). allSettled removes that deadlock.
 *
 * Versioning: bump CACHE_VERSION on deploy — activate() drops every older cache,
 * so a new shell fully replaces a stale one on the next visit.
 */
"use strict";

const CACHE_VERSION = "v3";
const SHELL_CACHE = `molgang-shell-${CACHE_VERSION}`;
const API_CACHE = `molgang-api-${CACHE_VERSION}`;

// Relative to the SW scope → path-prefix-safe (works at / and /molgang/).
// Only the assets the CURRENT app actually loads. peer.js is the real entry
// module (the legacy app.js/config.js/i18n.js are no longer loaded by
// index.html); the engine wheel + bridge let a warm reload boot offline.
// Icons are best-effort (they may not be published yet) — allSettled tolerates
// any miss.
const SHELL = [
  "./",
  "index.html",
  "style.css",
  "peer.js",
  "manifest.webmanifest",
  "engine/molgang_engine-0.0.0-py3-none-any.whl",
  "engine/serverless_api.py",
  "locales/en.json",
  "locales/nl.json",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/icon-512-maskable.png",
  "icons/apple-touch-icon.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(SHELL_CACHE);
    // best-effort: never let one 404 fail the install (the old addAll deadlock)
    await Promise.allSettled(
      SHELL.map((u) => c.add(new Request(u, { cache: "reload" })).catch(() => null))
    );
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys
        .filter((k) => k !== SHELL_CACHE && k !== API_CACHE)
        .map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;                       // never cache mutations
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;             // same-origin only

  if (url.pathname.includes("/api/")) {
    // network-first: live state when online, last known state when not
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(API_CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // App CODE (HTML documents + JS) → NETWORK-FIRST so a deploy always loads fresh
  // (cache-first here served a stale lab-immersive.html — its heavy GPU path black-
  // screened after a fix had shipped). Cache is only the offline fallback.
  const isCode = req.destination === "document" || url.pathname.endsWith("/") ||
    /\.(html|mjs|js)$/.test(url.pathname);
  if (isCode) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res && res.ok) { const copy = res.clone(); caches.open(SHELL_CACHE).then((c) => c.put(req, copy)); }
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // Static assets (icons/css/json/fonts/wheel) → cache-first + background revalidate.
  e.respondWith(
    caches.match(req).then((hit) => {
      const refresh = fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(SHELL_CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
        .catch(() => hit);
      return hit || refresh;
    })
  );
});
