/* Drawrassic Park iOS app shell (runs first, before any game script).
   Source: apps/ios/shell/app-shell.js. Copied into www/app/ by scripts/build-www.mjs.
   The game files themselves are never edited.

   What it does
   - window.FamilyNative: one promise API for the native features (Game Center, haptics,
     iCloud saves, save image to Photos, clipboard). Every call resolves, never throws:
     {ok:false, reason:'not-native'|'unavailable'|...} when a feature can't run.
   - Makes the page behave like an app: no links out, no window.open, no text selection or
     callout menus, no microphone, navigator.vibrate -> native haptics,
     <a download> images -> Photos.
   - Launcher page (index.html): only the 🛟 Recover saves tool is used. Any other visit goes
     straight to the game.
   Future game versions can check window.FAMILY_APP (platform, profile, online) to hide
   web-only UI themselves. */
(function () {
  'use strict';
  var APP = window.FAMILY_APP || { platform: 'ios', profile: 'store', online: false, gameFile: 'index.html' };
  var me = document.currentScript;
  var PAGE = (me && me.getAttribute('data-page')) || 'game';
  var html = document.documentElement;
  html.classList.add('family-app', 'app-' + PAGE, 'app-profile-' + APP.profile);
  if (!APP.online) html.classList.add('app-no-online');

  // ---------- launcher: straight to the game unless the rescue tool was asked for ----------
  if (PAGE === 'launcher') {
    if (location.hash !== '#rescue') { location.replace(APP.gameFile); return; }
    html.classList.add('app-rescue-only');
    document.addEventListener('click', function (e) {
      var t = e.target && e.target.closest && e.target.closest('#rClose');
      if (t) { e.preventDefault(); e.stopImmediatePropagation(); location.replace(APP.gameFile); }
    }, true);
  }

  // ---------- native bridge ----------
  var PLUGIN = 'FamilyNative';
  function cap() { var c = window.Capacitor; return c && c.isNativePlatform && c.isNativePlatform() && c.nativePromise ? c : null; }
  function call(method, opts) {
    var c = cap();
    if (!c) return Promise.resolve({ ok: false, reason: 'not-native' });
    try {
      return c.nativePromise(PLUGIN, method, opts || {}).then(
        function (r) { r = r || {}; if (r.ok === undefined) r.ok = true; return r; },
        function (err) { return { ok: false, reason: (err && (err.code || err.message)) || 'error' }; });
    } catch (e) { return Promise.resolve({ ok: false, reason: String(e && e.message || e) }); }
  }
  function blobToDataUrl(blob) {
    return new Promise(function (res, rej) { var r = new FileReader(); r.onload = function () { res(r.result); }; r.onerror = rej; r.readAsDataURL(blob); });
  }
  function toDataUrl(src) {
    if (typeof src === 'string' && src.indexOf('data:') === 0) return Promise.resolve(src);
    if (src && src.toDataURL) return Promise.resolve(src.toDataURL('image/png'));           // canvas
    if (src instanceof Blob) return blobToDataUrl(src);
    if (typeof src === 'string') return fetch(src).then(function (r) { return r.blob(); }).then(blobToDataUrl); // blob: URL
    return Promise.reject(new Error('unsupported image'));
  }

  var FamilyNative = {
    isNative: function () { return !!cap(); },
    app: APP,
    info: function () { return call('info'); },
    haptic: function (style) { return call('haptic', { style: style || 'medium' }); },
    gameCenter: {
      signIn: function () { return call('gcSignIn'); },
      submitScore: function (leaderboardId, score) { return call('gcSubmitScore', { leaderboardId: leaderboardId, score: Math.round(+score || 0) }); },
      reportAchievement: function (achievementId, percent) { return call('gcReportAchievement', { achievementId: achievementId, percent: percent == null ? 100 : +percent }); },
      showDashboard: function (state) { return call('gcShowDashboard', { state: state || 'default' }); },
    },
    cloud: {   // iCloud Drive, app container. key: [a-z0-9._-], data: any string (e.g. a backup code)
      status: function () { return call('cloudStatus'); },
      save: function (key, data) { return call('cloudSave', { key: key, data: String(data) }); },
      load: function (key) { return call('cloudLoad', { key: key }); },
      list: function () { return call('cloudList'); },
    },
    photos: {
      saveImage: function (src) {
        return toDataUrl(src).then(function (d) { return call('saveImage', { dataUrl: d }); },
          function () { return { ok: false, reason: 'bad-image' }; });
      },
    },
    copyText: function (text) { return call('copyText', { text: String(text) }); },
  };
  try { Object.defineProperty(window, 'FamilyNative', { value: Object.freeze(FamilyNative), enumerable: false }); }
  catch (e) { window.FamilyNative = FamilyNative; }

  // ---------- tiny UI strings (4 languages) ----------
  var S = {
    saved: ['Saved to Photos ✅', 'Enregistré dans Photos ✅', '已存到相册 ✅', '已存到照片 ✅'],
    denied: ['Allow Photos in Settings to save pictures.', 'Autorise Photos dans Réglages pour enregistrer les images.', '请在“设置”里允许访问照片，才能存图。', '請在「設定」裡允許取用照片，才能存圖。'],
    failed: ['Could not save the picture.', 'Impossible d’enregistrer l’image.', '图片没能保存。', '圖片沒能儲存。'],
  };
  function langIdx() {
    var l = (html.getAttribute('lang') || navigator.language || 'en').toLowerCase();
    if (l.indexOf('zh') === 0) return /hant|tw|hk|mo/.test(l) ? 3 : 2;
    return l.indexOf('fr') === 0 ? 1 : 0;
  }
  var toastEl = null, toastT = 0;
  function toast(key) {
    if (!document.body) return;
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'family-app-toast'; toastEl.setAttribute('role', 'status'); document.body.appendChild(toastEl); }
    toastEl.textContent = S[key][langIdx()];
    toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('on'); }, 2600);
  }

  // ---------- no links out of the app ----------
  function isAppUrl(href) {
    try { var u = new URL(href, location.href); return u.origin === location.origin || u.protocol === 'data:' || u.protocol === 'blob:' || u.protocol === 'about:'; }
    catch (e) { return false; }
  }
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (a.hasAttribute('download') && /^(data:image|blob:)/.test(href)) {
      e.preventDefault();
      FamilyNative.photos.saveImage(a.href).then(function (r) {
        toast(r.ok ? 'saved' : (r.reason === 'denied' ? 'denied' : 'failed'));
        if (r.ok) FamilyNative.haptic('success');
      });
      return;
    }
    if (!isAppUrl(href) || (a.target && a.target !== '_self')) { e.preventDefault(); e.stopPropagation(); }
  }, true);
  try { window.open = function () { return null; }; } catch (e) {}

  // ---------- haptics instead of navigator.vibrate (WKWebView has none) ----------
  try {
    var vib = function (p) {
      var ms = Array.isArray(p) ? (p[0] || 0) : (+p || 0);
      if (ms > 0) FamilyNative.haptic(ms >= 60 ? 'heavy' : ms >= 25 ? 'medium' : 'light');
      return true;
    };
    Object.defineProperty(navigator, 'vibrate', { value: vib, configurable: true });
  } catch (e) {}

  // ---------- clipboard: keep the web API, fall back to native if WebKit refuses ----------
  try {
    var clip = navigator.clipboard;
    var orig = clip && clip.writeText ? clip.writeText.bind(clip) : null;
    var writeText = function (t) {
      if (!orig) return FamilyNative.copyText(t).then(function (r) { if (!r.ok) throw new Error(r.reason); });
      return orig(t).catch(function () { return FamilyNative.copyText(t).then(function (r) { if (!r.ok) throw new Error(r.reason); }); });
    };
    if (clip) Object.defineProperty(clip, 'writeText', { value: writeText, configurable: true });
    else Object.defineProperty(navigator, 'clipboard', { value: { writeText: writeText }, configurable: true });
  } catch (e) {}

  // ---------- no microphone in the app (voice chat off; see apps/ios/APP-STORE.md) ----------
  try { if (navigator.mediaDevices) Object.defineProperty(navigator.mediaDevices, 'getUserMedia', { value: undefined, configurable: true }); } catch (e) {}

  // ---------- no zoom gestures / selection menus ----------
  document.addEventListener('gesturestart', function (e) { e.preventDefault(); }, { passive: false });
  document.addEventListener('selectstart', function (e) {
    var t = e.target;
    if (t && t.nodeType === 1 && t.closest && t.closest('input,textarea,[contenteditable="true"]')) return;
    e.preventDefault();
  });
})();
