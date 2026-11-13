/* community/shim.js — loaded first by every page of a community game.
   Community games run in a sandboxed iframe (opaque origin) inside community/play.html, so they can never read or
   change the family games' saves, cloud sign-in or settings on this website. In that sandbox the browser's own
   localStorage is unavailable, so this file gives the game an in-memory localStorage/sessionStorage:
   - it starts from the snapshot play.html puts in window.name,
   - every change goes back to play.html (postMessage), which saves it under community/<id>/save,
   - window.name is kept up to date, so a reload inside the game keeps its progress.
   If a community page is opened directly (not sandboxed), the page stops here and goes to play.html instead. */
(function () {
  'use strict';
  var TAG = '{"__fgshim":';
  var MAX_CHARS = 4500000;

  // Which community game is this? community/<id>/... in the path.
  var m = /\/community\/([a-z0-9-]+)\//.exec(location.pathname);
  var gameId = m ? m[1] : '';

  // 1. Never run unsandboxed on the family origin.
  var sandboxed = false;
  try { sandboxed = self.origin === 'null'; } catch (e) {}
  if (!sandboxed) {
    var to = location.pathname.slice(0, location.pathname.indexOf('/community/') + 11) + 'play.html' + (gameId ? '?g=' + gameId : '');
    try { document.write('<plaintext style="display:none">'); } catch (e) {}   // stop parsing: no other script on this page runs
    location.replace(to);
    return;
  }

  // 2. Initial data from play.html (or from our own last write, after a reload).
  var data = Object.create(null);
  try {
    var n = window.name;
    if (n && n.indexOf(TAG) === 0) {
      var o = JSON.parse(n);
      if (o && o.g === gameId && o.data && typeof o.data === 'object') for (var k in o.data) if (typeof o.data[k] === 'string') data[k] = o.data[k];
    }
  } catch (e) {}

  function size() { var t = 0; for (var k in data) t += k.length + data[k].length; return t; }
  var pending = false;
  function flush() {
    pending = false;
    var copy = {}; for (var k in data) copy[k] = data[k];
    try { window.name = JSON.stringify({ __fgshim: 1, g: gameId, data: copy }); } catch (e) {}
    try { parent.postMessage({ __fgshim: 1, type: 'save', g: gameId, data: copy }, '*'); } catch (e) {}
  }
  function changed() { if (!pending) { pending = true; setTimeout(flush, 0); } }
  addEventListener('pagehide', function () { if (pending) flush(); });

  function quota() { var e; try { e = new DOMException('Storage is full', 'QuotaExceededError'); } catch (x) { e = new Error('QuotaExceededError'); e.name = 'QuotaExceededError'; } return e; }
  function makeStorage(map, persist) {
    var api = {
      getItem: function (k) { k = String(k); return Object.prototype.hasOwnProperty.call(map, k) ? map[k] : null; },
      setItem: function (k, v) {
        k = String(k); v = String(v);
        var old = Object.prototype.hasOwnProperty.call(map, k) ? map[k] : null;
        if (persist && size() - (old == null ? 0 : k.length + old.length) + k.length + v.length > MAX_CHARS) throw quota();
        map[k] = v; if (persist) changed();
      },
      removeItem: function (k) { k = String(k); if (Object.prototype.hasOwnProperty.call(map, k)) { delete map[k]; if (persist) changed(); } },
      clear: function () { var any = false; for (var k in map) { delete map[k]; any = true; } if (any && persist) changed(); },
      key: function (i) { var ks = Object.keys(map); i = Number(i) | 0; return i >= 0 && i < ks.length ? ks[i] : null; }
    };
    Object.defineProperty(api, 'length', { get: function () { return Object.keys(map).length; }, enumerable: false, configurable: true });
    if (typeof Proxy !== 'function') return api;
    return new Proxy(api, {
      get: function (t, p) { if (p in t) return t[p]; if (typeof p === 'string' && Object.prototype.hasOwnProperty.call(map, p)) return map[p]; return undefined; },
      set: function (t, p, v) { if (typeof p === 'string' && !(p in t)) t.setItem(p, v); return true; },
      deleteProperty: function (t, p) { if (typeof p === 'string' && !(p in t)) t.removeItem(p); return true; },
      has: function (t, p) { return (p in t) || (typeof p === 'string' && Object.prototype.hasOwnProperty.call(map, p)); },
      ownKeys: function () { return Object.keys(map); },
      getOwnPropertyDescriptor: function (t, p) {
        if (typeof p === 'string' && Object.prototype.hasOwnProperty.call(map, p)) return { value: map[p], writable: true, enumerable: true, configurable: true };
        return undefined;
      }
    });
  }

  var local = makeStorage(data, true), session = makeStorage(Object.create(null), false);
  function define(obj, name, value) {
    try { Object.defineProperty(obj, name, { get: function () { return value; }, configurable: true, enumerable: true }); } catch (e) {}
  }
  define(window, 'localStorage', local);
  define(window, 'sessionStorage', session);
  // document.cookie throws in a sandbox; give games a harmless empty cookie jar instead.
  try { Object.defineProperty(document, 'cookie', { get: function () { return ''; }, set: function () {}, configurable: true }); } catch (e) {}
  // In the sandbox the game's own images count as cross-origin, so a canvas that draws them can't be read back
  // (getImageData). Load the game's own images with CORS (GitHub Pages answers Access-Control-Allow-Origin: *).
  try {
    var home = location.protocol + '//' + location.host;
    var d = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src');
    if (d && d.set) Object.defineProperty(HTMLImageElement.prototype, 'src', {
      configurable: true, enumerable: d.enumerable, get: d.get,
      set: function (v) {
        try { if (this.crossOrigin == null && new URL(String(v), document.baseURI).origin === home) this.crossOrigin = 'anonymous'; } catch (e) {}
        d.set.call(this, v);
      }
    });
  } catch (e) {}
  window.__FAMILY_COMMUNITY__ = { id: gameId, shim: 1 };
})();
