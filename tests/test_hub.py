"""Game Hub tests (Playwright, headless Chrome).

Covers: TV 1920x1080 with 1, 2 and 4 mocked controllers (every tile reached by D-pad, A opens it, Y favorites, X search,
LB/RB paging, Menu settings, B back), an Xbox user agent, iPad touch at 1180x820 and 820x1180 (tap, star, arrows, swipe,
rotation), a desktop keyboard, four languages, TV readability (text >= 28px, numbers >= 40px, 5% safe margins),
and bad data (corrupt storage, old keys, broken games.json, storage that throws).
Run: python3 tests/test_hub.py        Screenshots: /tmp/hub-shots
"""
import json, sys, threading, functools, http.server, socketserver, os, re
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = '/tmp/hub-shots'
os.makedirs(OUT, exist_ok=True)
GAMES = json.load(open(f'{ROOT}/games.json'))['games']
BYID = {g['id']: g for g in GAMES}
FAMILY = [g for g in GAMES if g.get('category', 'family') == 'family']
COMMUNITY = [g for g in GAMES if g.get('category') == 'community']
PADOK = [g for g in GAMES if g['input'] in ('controller', 'both')]
KBD = [g for g in COMMUNITY if g['input'] == 'keyboard']
PORT = 8767
LANGS = ['en', 'fr', 'zh-Hans', 'zh-Hant']

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{PORT}/'
URL = BASE + 'index.html'
def abs_url(g): return g['url'] if g['url'].startswith('http') else BASE + g['url']
FAMILY_URLS = {abs_url(g) for g in FAMILY}

PAD_MOCK = """
(() => {
  const mk = i => ({ index: i, id: 'Xbox Wireless Controller (mock ' + i + ')', mapping: 'standard', connected: true, timestamp: 0,
    buttons: Array.from({length: 17}, () => ({ pressed: false, value: 0, touched: false })), axes: [0, 0, 0, 0],
    vibrationActuator: { playEffect: () => Promise.resolve('complete') } });
  window.__pads = Array.from({length: %d}, (_, i) => mk(i));
  navigator.getGamepads = () => [0, 1, 2, 3].map(i => window.__pads[i] || null);
})();
"""
ROWS_JS = """() => [...document.querySelectorAll('#app .navrow')].filter(r => !r.hidden && r.offsetParent)
  .map(r => [...r.querySelectorAll('.nav')].filter(e => e.offsetParent && !e.hidden && !e.disabled).map(e => e.dataset.key)).filter(x => x.length)"""

results = []
def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))
    print(('PASS ' if ok else 'FAIL ') + name + (('  — ' + str(detail)[:600]) if detail and not ok else ''))

BTN = {'A': 0, 'B': 1, 'X': 2, 'Y': 3, 'LB': 4, 'RB': 5, 'menu': 9, 'up': 12, 'down': 13, 'left': 14, 'right': 15}
def press(page, b, pad=0, hold=60):
    page.evaluate(f'(() => {{ const x = window.__pads[{pad}].buttons[{BTN[b]}]; x.pressed = true; x.value = 1; }})()')
    page.wait_for_timeout(hold)
    page.evaluate(f'(() => {{ const x = window.__pads[{pad}].buttons[{BTN[b]}]; x.pressed = false; x.value = 0; }})()')
    page.wait_for_timeout(60)
def focused(page): return page.evaluate("(() => { const e = document.querySelector('.nav.focused'); return e ? (e.dataset.key || e.id) : null; })()")
def rows(page): return page.evaluate(ROWS_JS)
def walk_to(page, key, pad=0, limit=260):
    """Drive the focus to [data-key=key] with the D-pad only (row by row, then along the row)."""
    for _ in range(limit):
        f = focused(page)
        if f == key: return True
        R = rows(page)
        cur = next(((i, r.index(f)) for i, r in enumerate(R) if f in r), None)
        tgt = next(((i, r.index(key)) for i, r in enumerate(R) if key in r), None)
        if not cur or not tgt: press(page, 'down', pad); continue
        if cur[0] != tgt[0]: press(page, 'down' if tgt[0] > cur[0] else 'up', pad)
        else: press(page, 'right' if tgt[1] > cur[1] else 'left', pad)
    return focused(page) == key

def new_ctx(b, w, h, pads=0, touch=False, lang='zh-CN', ua=None):
    kw = dict(viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, locale=lang, device_scale_factor=1)
    if ua: kw['user_agent'] = ua
    ctx = b.new_context(**kw)
    if pads: ctx.add_init_script(PAD_MOCK % pads)
    opened = []
    def stub(route):
        opened.append(route.request.url)
        route.fulfill(status=200, content_type='text/html', body='<!DOCTYPE html><title>stub</title>game stub')
    ctx.route(lambda u: u.startswith('http') and (not u.startswith(BASE) or u.split('?')[0].split('#')[0] in FAMILY_URLS), stub)    # family launchers (relative URLs) + linked sites
    ctx.route('**/community/play.html*', stub)                                     # sandboxed community games
    ctx.route('**/vendor/firebase-lite.js', lambda r: r.abort())                   # cloud backup: offline here
    return ctx, opened

def open_page(ctx, url=URL):
    page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.goto(url); page.wait_for_selector('#shelves .tile')
    return page, errs

LAYOUT_JS = """(tv) => {
  const iw = innerWidth, ih = innerHeight, bad = [];
  const vis = e => e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden';
  if (document.documentElement.scrollWidth > iw + 1) bad.push('page scrolls sideways ' + document.documentElement.scrollWidth);
  for (const e of document.querySelectorAll('.tb, h1, .shead h2, .play, .inp, .hname, #count')) {
    if (!vis(e)) continue;
    if (e.scrollWidth > e.clientWidth + 1) bad.push('cut: ' + (e.id || e.className) + ' "' + e.textContent.slice(0, 40) + '"');
    const q = e.getBoundingClientRect();
    if (!e.closest('.tiles') && (q.right > iw + 1 || q.left < -1)) bad.push('off-screen: ' + e.textContent.slice(0, 30));
  }
  for (const t of document.querySelectorAll('.tw')) {          // every tile in a shelf has the same width as its siblings
    const sib = t.parentElement.querySelector('.tw' + (t.classList.contains('wide') ? '.wide' : ':not(.wide)'));
    if (Math.abs(t.getBoundingClientRect().width - sib.getBoundingClientRect().width) > 1) { bad.push('uneven tile ' + t.querySelector('a').dataset.key); break; }
  }
  for (const i of document.querySelectorAll('.tile .inp, .tile .ver, .tile .tname')) {     // nothing inside a tile is clipped by its edge
    const t = i.closest('.tile').getBoundingClientRect(), r = i.getBoundingClientRect();
    if (r.right > t.right - 4 || i.scrollWidth > i.clientWidth + 1) { bad.push('clipped in tile: ' + i.textContent.slice(0, 30)); break; }
  }
  for (const b of document.querySelectorAll('.tblurb')) { if (b.scrollHeight > b.clientHeight + 2 && b.getBoundingClientRect().height > parseFloat(getComputedStyle(b).lineHeight) * 2.2) { bad.push('blurb > 2 lines'); break; } }
  const small = [...document.querySelectorAll('.nav, .star, .arr')].filter(e => vis(e) && !e.closest('[hidden]')).filter(e => { const r = e.getBoundingClientRect(); return r.width && (r.height < 43.5 || r.width < 43.5); }).map(e => e.dataset.key || e.className);
  if (small.length) bad.push('tap target <44px: ' + small.slice(0, 5).join(','));
  let m = null;
  if (tv) {
    const fs = e => parseFloat(getComputedStyle(e).fontSize);
    const textEls = [...document.querySelectorAll('.tname, .tblurb, .credit, .inp, .shead h2, .shead small, .divider, .kicker, .hblurb, .tb, #count, .dline, .dname, .keys span')].filter(vis);
    const minText = Math.min(...textEls.map(fs)), minEl = textEls.find(e => fs(e) === minText);
    const nums = [...document.querySelectorAll('.ver b')].filter(vis).map(fs);
    const mx = iw * 0.05, my = ih * 0.05, out = [];
    for (const e of document.querySelectorAll('header .nav, h1, #hero, .shead h2, #detail, .nav.focused')) {
      if (!vis(e)) continue; const q = e.getBoundingClientRect();
      if (q.bottom < 0 || q.top > ih) continue;   // shelf headings scroll: one peeking past the top or bottom edge is the next row, not fixed UI
      const tol = e.classList.contains('focused') ? 12 : 1;      // the 4.5% lift of a focused tile
      if (q.left < mx - tol || q.right > iw - mx + tol || q.top < my - tol && q.bottom > 0 && e.tagName !== 'H2' || q.bottom > ih - my + tol && e.tagName !== 'H2') out.push((e.dataset.key || e.id || e.tagName) + ' ' + JSON.stringify([q.left|0, q.top|0, q.right|0, q.bottom|0]));
    }
    m = { minText, minEl: minEl && (minEl.className || minEl.tagName) + ' ' + minEl.textContent.slice(0, 20), minNum: nums.length ? Math.min(...nums) : 99, out };
  }
  return { bad, m };
}"""
def layout_checks(page, tag, tv=False):
    r = page.evaluate(LAYOUT_JS, tv)
    check(f'{tag}: nothing cut off or off-screen, tiles even, tap targets ≥44px', not r['bad'], r['bad'])
    if tv:
        m = r['m']
        check(f'{tag}: all text ≥28px (smallest {m["minText"]:.1f}px)', m['minText'] >= 27.9, m['minEl'])
        check(f'{tag}: version numbers ≥40px ({m["minNum"]:.1f}px)', m['minNum'] >= 40)
        check(f'{tag}: important UI inside the 5% safe area', not m['out'], m['out'])

def touch_swipe(page, x0, y0, x1, y1, steps=8):
    cdp = page.context.new_cdp_session(page)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y0}]})
    for i in range(1, steps + 1):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + (x1 - x0) * i / steps, 'y': y0 + (y1 - y0) * i / steps}]})
        page.wait_for_timeout(16)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    page.wait_for_timeout(500)

with sync_playwright() as p:
    b = p.chromium.launch()

    # =============== 1. TV 1920x1080, one controller, controller only ===============
    ctx, opened = new_ctx(b, 1920, 1080, pads=1)
    page, errs = open_page(ctx)
    check('TV: hero shows today\'s pick (one of our games) before anything was played',
          page.locator('#hero').is_visible() and page.locator('#hero').get_attribute('data-id') in [g['id'] for g in FAMILY])
    check('TV: header shows the game count', page.locator('#count').text_content() == f'{len(GAMES)} 个游戏', page.locator('#count').text_content())
    check('TV: no controller shelf before a controller is used (not an Xbox)', page.locator('[data-shelf="pad"]').count() == 0)
    page.screenshot(path=f'{OUT}/tv-start.png')
    # --- cover art: every game has a 16:9 picture; the ones on screen have loaded and fill their tile ---
    from PIL import Image as _Im
    bad_art = []
    for g in GAMES:
        f = os.path.join(ROOT, g.get('art', '') or '-')
        try:
            w_, h_ = _Im.open(f).size
            if abs(w_ / h_ - 16 / 9) > 0.01 or w_ < 960: bad_art.append((g['id'], w_, h_))
        except Exception as e: bad_art.append((g['id'], 'missing'))
    check(f'Art: all {len(GAMES)} games have a 16:9 cover file ≥960px wide', not bad_art, bad_art)
    page.wait_for_timeout(600)
    art = page.evaluate("""() => {
      const vis = [...document.querySelectorAll('#shelves .tile')].filter(t => { const r = t.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth; });
      const noImg = vis.filter(t => !t.querySelector('.art img.kimg')).map(t => t.dataset.id);
      const notLoaded = vis.filter(t => { const i = t.querySelector('img.kimg'); return i && !(i.complete && i.naturalWidth); }).map(t => t.dataset.id);
      const ratio = vis.filter(t => { const r = t.querySelector('.art').getBoundingClientRect(); return Math.abs(r.width / r.height - 16 / 9) > 0.03; }).map(t => t.dataset.id);
      const named = vis.filter(t => !t.classList.contains('key') && !t.querySelector('.tname').offsetHeight).map(t => t.dataset.id);
      const lazy = [...document.querySelectorAll('#shelves img.kimg')].every(i => i.loading === 'lazy');
      const hero = document.querySelector('#hero .hbg img');
      return { n: vis.length, noImg, notLoaded, ratio, named, lazy, hero: !!(hero && hero.complete && hero.naturalWidth) };
    }""")
    check('Art: tiles on screen show their cover picture, loaded, at 16:9', art['n'] > 3 and not art['noImg'] and not art['notLoaded'] and not art['ratio'], art)
    check('Art: community tiles keep the (translated) name under the picture; shelf pictures load lazily', not art['named'] and art['lazy'], art)
    check('Art: the hero shows the game\'s cover picture', art['hero'], art)
    press(page, 'A')
    check('TV: first A press only shows the focus ring (opens nothing)', not opened and focused(page) == 'cont', focused(page))
    check('TV: controller shelf appears once a controller is used, with every controller game',
          sorted(page.eval_on_selector_all('[data-shelf="pad"] .tile', 'e => e.map(x => x.dataset.id)')) == sorted(g['id'] for g in PADOK))
    shelf_ids = page.eval_on_selector_all('.shelf', 'e => e.map(x => x.dataset.shelf)')
    check('TV: shelves in order: ours, controller, genres…, keyboard last', shelf_ids[0] == 'family' and shelf_ids[1] == 'pad' and shelf_ids[-1] == 'kbd' and all(s.startswith('g-') for s in shelf_ids[2:-1]), shelf_ids)
    kb_ids = page.eval_on_selector_all('[data-shelf="kbd"] .tile', 'e => e.map(x => x.dataset.id)')
    check('TV: keyboard-only games are all in the last shelf, and only there', sorted(kb_ids) == sorted(g['id'] for g in KBD)
          and not page.eval_on_selector_all('[data-shelf^="g-"] .tile', f'e => e.filter(x => {json.dumps([g["id"] for g in KBD])}.includes(x.dataset.id)).length'))
    genre_ok = page.evaluate("""(G) => [...document.querySelectorAll('[data-shelf^="g-"]')].every(s => [...s.querySelectorAll('.tile')].every(t => 'g-' + G[t.dataset.id] === s.dataset.shelf))""", {g['id']: g.get('genre') for g in GAMES})
    check('TV: every genre shelf only holds games of that genre', genre_ok)
    shown = set(page.eval_on_selector_all('#shelves .tile', 'e => e.map(x => x.dataset.id)'))
    check(f'TV: all {len(GAMES)} games are on a shelf', shown == set(BYID), sorted(set(BYID) - shown))
    ext = page.eval_on_selector_all('#shelves .tile', 'e => e.filter(x => x.querySelector(".extb")).map(x => x.dataset.id)')
    check('TV: embedded and linked games carry the ↗ external mark', set(ext) == {g['id'] for g in GAMES if 'external' in g or g.get('link')})

    # --- every tile is reachable with the D-pad; focus stays fully visible; per-shelf memory ---
    press(page, 'down')              # hero → first shelf
    seen, hidden_tiles, R = [], [], rows(page)
    tile_rows = [r for r in R if r and ':' in r[0]]
    for ri, want in enumerate(tile_rows):
        if ri: press(page, 'down')
        keys = [focused(page)]
        for _ in range(len(want) - 1):
            press(page, 'right'); keys.append(focused(page)); page.wait_for_timeout(450)
            vis = page.evaluate("""() => { const f = document.querySelector('.nav.focused'), r = f.getBoundingClientRect(), row = f.closest('.tiles').getBoundingClientRect(), d = document.getElementById('detail').getBoundingClientRect();
                return r.left >= row.left - 2 && r.right <= row.right + 2 && r.bottom <= d.top + 1 && r.top >= 0; }""")
            if not vis: hidden_tiles.append(keys[-1])
        press(page, 'right')
        if focused(page) != want[-1]: keys.append('moved past end')
        seen.append(keys == want)
        if ri == 2:                                   # remembered position: down then up comes back to the same tile
            press(page, 'down'); press(page, 'up')
            check('TV pad: up/down returns to the remembered tile in a shelf', focused(page) == want[-1], focused(page))
    check(f'TV pad: D-pad walks every tile of all {len(tile_rows)} shelves in order and stops at the end', all(seen) and len(seen) == len(tile_rows), seen)
    check('TV pad: the focused tile is always fully visible (inside its shelf, above the detail bar)', not hidden_tiles, hidden_tiles[:5])
    page.screenshot(path=f'{OUT}/tv-pad-deep.png')

    # --- B steps back: start of shelf, then the hero ---
    press(page, 'B'); f1 = focused(page)
    press(page, 'B'); f2 = focused(page)
    check('TV pad: B goes to the start of the shelf, then back to the hero', f1 == tile_rows[-1][0] and f2 == 'cont', (f1, f2))

    # --- LB / RB page through a long shelf ---
    long_row = max(tile_rows, key=len)
    walk_to(page, long_row[0]); press(page, 'RB'); i1 = long_row.index(focused(page)); press(page, 'LB'); i2 = long_row.index(focused(page))
    check('TV pad: RB jumps a page right in a shelf and LB jumps back', i1 >= 2 and i2 == 0, (i1, i2))

    # --- detail bar shows the focused game ---
    walk_to(page, 'family:' + FAMILY[0]['id'])
    dname = page.locator('#detail .dname').text_content()
    check('TV pad: detail bar names the focused game and shows A/Y/X/B hints', dname == FAMILY[0]['name']['zh-Hans'] and page.locator('#detail .k.a').count() == 1 and page.locator('#detail .k.y').count() == 1, dname)

    # --- A opens games (family, community, external link, keyboard), hero/recent/return focus ---
    sample = [FAMILY[0], FAMILY[1], next(g for g in COMMUNITY if g.get('link')), next(g for g in COMMUNITY if 'entry' in g), KBD[0]]
    for n, g in enumerate(sample):
        key = page.evaluate("(id) => { const t = document.querySelector('#shelves .tile[data-id=\"' + id + '\"]'); return t && t.dataset.key; }", g['id'])
        ok = walk_to(page, key)
        n0 = len(opened); press(page, 'A'); page.wait_for_timeout(500)
        check(f'TV pad: A opens {g["id"]}', ok and len(opened) > n0 and opened[-1] == abs_url(g), (ok, opened[-1:]))
        page.go_back(); page.wait_for_selector('#shelves .tile'); page.wait_for_timeout(700)
        check(f'TV: back on the hub, focus returns to the {g["id"]} tile', focused(page) == key, (focused(page), key))
        check(f'TV: hero now says Continue {g["id"]}', page.locator('#hero').get_attribute('data-id') == g['id'] and page.locator('#cont span').text_content() == '继续玩')
        if not page.evaluate("document.body.classList.contains('show-focus')"): press(page, 'A')   # first press after a reload only re-shows the focus ring
    rec = page.eval_on_selector_all('[data-shelf="recent"] .tile', 'e => e.map(x => x.dataset.id)')
    check('TV: "recently played" shelf lists the games newest first', rec == [g['id'] for g in reversed(sample)], rec)
    n0 = len(opened); walk_to(page, 'cont'); press(page, 'A'); page.wait_for_timeout(400)
    check('TV pad: A on Continue opens the last game played', len(opened) > n0 and opened[-1] == abs_url(sample[-1]))
    page.go_back(); page.wait_for_selector('#shelves .tile')
    if not page.evaluate("document.body.classList.contains('show-focus')"): press(page, 'A')

    # --- Y favorites ---
    fav_g = next(g for g in COMMUNITY[3:] if g['input'] != 'keyboard' and g['id'] not in [x['id'] for x in sample])
    key = page.evaluate("(id) => document.querySelector('[data-shelf^=\"g-\"] .tile[data-id=\"' + id + '\"]').dataset.key", fav_g['id'])
    walk_to(page, key); press(page, 'Y'); page.wait_for_timeout(200)
    favs = page.eval_on_selector_all('[data-shelf="fav"] .tile', 'e => e.map(x => x.dataset.id)')
    stored = page.evaluate("JSON.parse(localStorage.getItem('game-hub/favs')).ids")
    check('TV pad: Y adds the focused game to "My favorites" and saves it', favs == [fav_g['id']] and stored == [fav_g['id']], (favs, stored))
    check('TV pad: focus stays on the same tile after Y', focused(page) == key, focused(page))
    check('TV: a toast confirms the favorite', page.locator('#toast').is_visible() and '收藏' in page.locator('#toast').text_content())
    press(page, 'Y'); page.wait_for_timeout(200)
    check('TV pad: Y again removes it', page.locator('[data-shelf="fav"]').count() == 0 and page.evaluate("JSON.parse(localStorage.getItem('game-hub/favs')).ids") == [])
    walk_to(page, 'hfav'); press(page, 'A'); page.wait_for_timeout(200)
    hid = page.locator('#hero').get_attribute('data-id')
    check('TV pad: the hero ☆ button favorites the hero game', page.eval_on_selector_all('[data-shelf="fav"] .tile', 'e => e.map(x => x.dataset.id)') == [hid] and page.locator('#hfav').get_attribute('aria-pressed') == 'true')

    # --- X search ---
    press(page, 'X'); page.wait_for_timeout(200)
    check('TV pad: X opens search and puts the cursor in the box', page.locator('#sbar').is_visible() and page.evaluate("document.activeElement.id") == 'q')
    page.keyboard.type('sudoku'); page.wait_for_timeout(200)
    res = page.eval_on_selector_all('[data-shelf="results"] .tile', 'e => e.map(x => x.dataset.id)')
    check('Search: typing filters to one results shelf', 'sudoku' in res and page.locator('.shelf').count() == 1 and page.locator('#hero').is_hidden(), res)
    page.keyboard.press('Enter'); page.wait_for_timeout(150)
    check('Search: Enter moves focus to the first result', focused(page) == 'results:' + res[0] and page.evaluate("document.activeElement.id") != 'q', focused(page))
    page.fill('#q', '恐龙'); page.wait_for_timeout(150)
    res = page.eval_on_selector_all('[data-shelf="results"] .tile', 'e => e.map(x => x.dataset.id)')
    check('Search: Chinese words match (恐龙 → Drawrassic Park)', 'drawrassic-park' in res, res)
    page.fill('#q', 'zzzqqq'); page.wait_for_timeout(150)
    check('Search: no match shows a message', page.locator('#none').is_visible() and page.locator('#shelves .tile').count() == 0)
    page.fill('#q', ''); page.locator('#q').blur(); walk_to(page, 'q'); press(page, 'B'); page.wait_for_timeout(150)
    check('Search: B closes search and every shelf comes back', page.locator('#sbar').is_hidden() and page.locator('#shelves .tile').count() > len(GAMES))

    # --- Menu: language & settings dialog, controller only ---
    press(page, 'menu'); page.wait_for_timeout(150)
    check('TV pad: Menu opens "language & settings"', page.locator('#dlg').is_visible() and page.locator('#dlg .dnav').count() == 7)
    names = page.eval_on_selector_all('#dlg .dnav', 'e => e.slice(0, 4).map(x => x.textContent)')
    check('Settings: languages listed in their own names', names == ['English', 'Français', '简体中文', '繁體中文'], names)
    for _ in range(3): press(page, 'up')
    press(page, 'A'); page.wait_for_timeout(150)
    check('TV pad: picking English switches the whole hub at once', page.locator('h1').text_content() == '🎮 Game Hub' and page.locator('.shead h2').first.text_content() == '🕹️ Recently played' and page.locator('.shead h2').nth(1).text_content() == '⭐ My favorites')
    for _ in range(4): press(page, 'down')
    snd0 = page.evaluate("JSON.parse(localStorage.getItem('game-hub/settings')).sound")
    press(page, 'A'); page.wait_for_timeout(100)
    snd1 = page.evaluate("JSON.parse(localStorage.getItem('game-hub/settings')).sound")
    check('Settings: the sound switch toggles and is saved', snd0 is not False and snd1 is False, (snd0, snd1))
    press(page, 'B'); page.wait_for_timeout(100)
    check('TV pad: B closes the dialog', page.locator('#dlg').is_hidden())
    page.reload(); page.wait_for_selector('#shelves .tile')
    check('Settings: language kept after reload', page.locator('h1').text_content() == '🎮 Game Hub')
    check('TV: no page errors', not errs, errs)

    # --- TV readability in four languages (controller mode, focus on a deep tile) ---
    for lg in LANGS:
        page.evaluate(f"localStorage.setItem('game-hub/settings', JSON.stringify({{lang:'{lg}', sound:false}}))")
        page.reload(); page.wait_for_selector('#shelves .tile'); press(page, 'down'); page.wait_for_timeout(150)
        layout_checks(page, f'TV 1920x1080 {lg} (top)', tv=True)
        page.screenshot(path=f'{OUT}/tv-{lg}-top.png')
        for _ in range(5): press(page, 'down')
        press(page, 'right'); page.wait_for_timeout(500)
        layout_checks(page, f'TV 1920x1080 {lg} (deep, detail bar)', tv=True)
        page.screenshot(path=f'{OUT}/tv-{lg}-deep.png')
    ctx.close()

    # =============== 2. Two and four controllers: any controller drives the hub ===============
    for n in (2, 4):
        ctx, opened = new_ctx(b, 1920, 1080, pads=n)
        page, errs = open_page(ctx)
        last = n - 1
        press(page, 'down', last); press(page, 'down', last); press(page, 'right', last)
        check(f'{n} pads: header shows {n} controllers', page.locator('#pads').text_content() == f'🎮 ×{n}', page.locator('#pads').text_content())
        press(page, 'A', last); page.wait_for_timeout(400)
        check(f'{n} pads: controller #{n} alone opens the second family game', opened and opened[-1] == abs_url(FAMILY[1]), opened)
        ctx.close()

    # =============== 3. Xbox user agent ===============
    XUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox Series X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
    ctx, opened = new_ctx(b, 1920, 1080, ua=XUA)
    page, errs = open_page(ctx)
    check('Xbox: controller shelf shown right away', page.locator('[data-shelf="pad"]').count() == 1)
    check('Xbox: "press A once to wake the page" hint shown', '按一次 A' in page.locator('#foot').text_content())
    first_genre = page.eval_on_selector_all('[data-shelf="g-racing"] .tile', 'e => e.map(x => x.dataset.id)')
    racing = [g for g in COMMUNITY if g.get('genre') == 'racing' and g['input'] != 'keyboard']
    want = [g['id'] for g in racing if g['input'] in ('controller', 'both')] + [g['id'] for g in racing if g['input'] not in ('controller', 'both')]
    check('Xbox: controller games come first inside each genre shelf', first_genre == want, (first_genre[:6], want[:6]))
    check('Xbox: no page errors', not errs, errs)
    ctx.close()

    # =============== 4. iPad touch, both orientations ===============
    for (w, h) in [(1180, 820), (820, 1180)]:
        ctx, opened = new_ctx(b, w, h, touch=True)
        page, errs = open_page(ctx)
        tag = f'iPad {w}x{h}'
        g = COMMUNITY[0]
        t = page.locator(f'[data-shelf^="g-"] .tile[data-id="{g["id"]}"]').first
        t.scroll_into_view_if_needed(); t.tap(); page.wait_for_timeout(500)
        check(f'{tag}: tap a tile opens the game', opened and opened[-1] == abs_url(g))
        page.go_back(); page.wait_for_selector('#shelves .tile')
        check(f'{tag}: no focus ring or detail bar for touch', not page.evaluate("document.body.classList.contains('show-focus')") and page.locator('#detail').is_hidden())
        star = page.locator('[data-shelf="family"] .star').nth(1)
        n0 = len(opened); star.tap(); page.wait_for_timeout(300)
        check(f'{tag}: tap ☆ favorites the game without opening it', len(opened) == n0 and page.eval_on_selector_all('[data-shelf="fav"] .tile', 'e => e.map(x => x.dataset.id)') == [FAMILY[1]['id']])
        page.locator('[data-shelf="fav"] .star').first.tap(); page.wait_for_timeout(300)
        check(f'{tag}: tap ★ again removes it', page.locator('[data-shelf="fav"]').count() == 0)
        sec = page.locator('[data-shelf="g-arcade"]'); sec.scroll_into_view_if_needed()
        row = sec.locator('.tiles')
        x0 = row.evaluate('e => e.scrollLeft'); sec.locator('.arr').nth(1).tap(); page.wait_for_timeout(700)
        x1 = row.evaluate('e => e.scrollLeft')
        check(f'{tag}: › arrow scrolls the shelf', x1 > x0 + 50, (x0, x1))
        bb = row.bounding_box(); touch_swipe(page, bb['x'] + bb['width'] * 0.8, bb['y'] + bb['height'] / 2, bb['x'] + bb['width'] * 0.2, bb['y'] + bb['height'] / 2)
        x2 = row.evaluate('e => e.scrollLeft')
        check(f'{tag}: swiping a shelf sideways scrolls it', x2 > x1 + 50, (x1, x2))
        y0 = page.evaluate('scrollY'); touch_swipe(page, bb['x'] + 40, min(h - 60, bb['y'] + bb['height'] - 20), bb['x'] + 40, 80); y1 = page.evaluate('scrollY')
        check(f'{tag}: swiping up on a shelf still scrolls the page', y1 > y0 + 50, (y0, y1))
        ta = page.evaluate("[getComputedStyle(document.body).touchAction, getComputedStyle(document.querySelector('.tiles')).touchAction]")
        check(f'{tag}: pinch/double-tap zoom blocked (touch-action {ta})', ta == ['pan-y', 'pan-x pan-y'])
        page.evaluate('scrollTo(0,0)'); page.locator('#bLang').tap(); page.wait_for_timeout(150)
        page.locator('#dlg .dnav', has_text='繁體中文').tap(); page.wait_for_timeout(150)
        check(f'{tag}: 🌐 → 繁體中文 switches the language', page.locator('h1').text_content() == '🎮 遊戲大廳')
        page.locator('#dlg').tap(position={'x': 5, 'y': 5}); page.wait_for_timeout(150)
        check(f'{tag}: tapping outside closes the dialog', page.locator('#dlg').is_hidden())
        page.locator('#bSearch').tap(); page.wait_for_timeout(150)
        check(f'{tag}: 🔍 opens search with the keyboard ready', page.evaluate("document.activeElement.id") == 'q')
        fs = page.evaluate("parseFloat(getComputedStyle(document.getElementById('q')).fontSize)")
        check(f'{tag}: search box font ≥16px (no iOS zoom)', fs >= 16, fs)
        page.keyboard.type('bloom'); page.wait_for_timeout(150)
        page.locator('[data-shelf="results"] .tile').first.tap(); page.wait_for_timeout(400)
        check(f'{tag}: tap a search result opens it', opened[-1] == abs_url(BYID['bloom-hop']))
        page.go_back(); page.wait_for_selector('#shelves .tile')
        for lg in LANGS:
            page.evaluate(f"localStorage.setItem('game-hub/settings', JSON.stringify({{lang:'{lg}'}}))")
            page.reload(); page.wait_for_selector('#shelves .tile')
            layout_checks(page, f'{tag} {lg}')
            page.screenshot(path=f'{OUT}/ipad-{w}x{h}-{lg}.png')
        page.set_viewport_size({'width': h, 'height': w}); page.wait_for_timeout(400)
        layout_checks(page, f'{tag} rotated to {h}x{w}')
        check(f'{tag}: no page errors', not errs, errs)
        ctx.close()

    # =============== 5. Desktop keyboard ===============
    ctx, opened = new_ctx(b, 1440, 900)
    page, errs = open_page(ctx)
    page.keyboard.press('ArrowDown')
    check('Keyboard: first arrow only shows the focus ring', focused(page) == 'cont' and not opened)
    page.keyboard.press('ArrowDown'); page.keyboard.press('ArrowRight'); page.keyboard.press('Enter'); page.wait_for_timeout(400)
    check('Keyboard: arrows + Enter open a game', opened and opened[-1] == abs_url(FAMILY[1]))
    page.go_back(); page.wait_for_selector('#shelves .tile')
    page.keyboard.press('/'); page.wait_for_timeout(150)
    check('Keyboard: "/" opens search', page.evaluate("document.activeElement.id") == 'q')
    page.keyboard.press('Escape'); page.keyboard.press('Escape'); page.wait_for_timeout(150)
    check('Keyboard: Escape leaves and closes search', page.locator('#sbar').is_hidden())
    check('Keyboard: no page errors', not errs, errs)
    ctx.close()

    # =============== 6. Bad data and old data ===============
    ctx, opened = new_ctx(b, 1920, 1080, pads=1)
    page, errs = open_page(ctx)
    page.evaluate("""localStorage.setItem('game-hub/settings', '{bad json'); localStorage.setItem('game-hub/recent', '[1,2'); localStorage.setItem('game-hub/favs', '{"ids": [5, null, "sudoku", "sudoku", "no-such-game"]}')""")
    page.reload(); page.wait_for_selector('#shelves .tile')
    check('Corrupt storage: page loads, bad values ignored, valid favorite kept once',
          page.eval_on_selector_all('[data-shelf="fav"] .tile', 'e => e.map(x => x.dataset.id)') == ['sudoku'] and not errs, errs)
    page.evaluate("localStorage.removeItem('game-hub/recent'); localStorage.setItem('game-hub/last', JSON.stringify({id: 'crab-castle', at: 5}))")
    page.reload(); page.wait_for_selector('#shelves .tile')
    check('Old hub data: game-hub/last still becomes "Continue"', page.locator('#hero').get_attribute('data-id') == 'crab-castle' and page.locator('#cont span').text_content() == '继续玩')
    page.evaluate("localStorage.setItem('game-hub/last', JSON.stringify({id: 'deleted-game'})); localStorage.removeItem('game-hub/recent')")
    page.reload(); page.wait_for_selector('#shelves .tile')
    check('Old hub data: a removed game falls back to today\'s pick', page.locator('#hero').get_attribute('data-id') in [g['id'] for g in FAMILY])
    state = {'mode': 'fail'}
    def gj(route):
        if state['mode'] == 'fail': route.fulfill(status=500, body='x')
        elif state['mode'] == 'weird':
            bad = {'games': [{'id': 'a', 'url': 'javascript:alert(1)'}, {'id': 'b', 'url': 'https://example.org/b', 'icon': '<img src=x onerror=alert(1)>', 'color': 'red;background:url(x)'},
                             {'id': 'b', 'url': 'https://example.org/dup'}, {'nope': 1}]}
            route.fulfill(status=200, content_type='application/json', body=json.dumps(bad))
        else: route.continue_()
    page.route('**/games.json', gj)
    page.reload(); page.wait_for_selector('#msg:not([hidden])')
    check('games.json fails: message and Retry button', page.locator('#retry').is_visible())
    press(page, 'down'); f = focused(page)
    check('games.json fails: the controller lands on Retry', f == 'retry', f)
    state['mode'] = 'ok'; press(page, 'A'); page.wait_for_selector('#shelves .tile')
    check('Retry by controller loads the games', page.locator('#shelves .tile').count() > len(GAMES))
    state['mode'] = 'weird'; page.reload(); page.wait_for_timeout(800)
    info = page.evaluate("[document.querySelectorAll('#shelves .tile').length, document.querySelectorAll('#shelves img').length, document.querySelector('#shelves .tile') && document.querySelector('#shelves .tile').href]")
    check('Bad entries in games.json: unsafe URL, injected icon, duplicate id and junk are dropped', info[0] >= 1 and info[1] == 0 and info[2] == 'https://example.org/b', info)
    state['mode'] = 'ok'; page.reload(); page.wait_for_selector('#shelves .tile')
    page.evaluate("Object.defineProperty(window, 'localStorage', { get() { throw new Error('denied'); } })")
    page.evaluate("document.querySelector('[data-shelf=\"family\"] .star').click()")
    page.evaluate("document.getElementById('bLang').click()"); page.evaluate("document.querySelector('[data-key=\"d-lang-en\"]').click()")
    check('Storage that throws: favorites and language switch don\'t crash', page.locator('h1').text_content() == '🎮 Game Hub' and not errs, errs)
    ctx.close()
    b.close()

srv.shutdown()
fails = [r for r in results if not r[1]]
print(f'\n{len(results) - len(fails)}/{len(results)} passed')
sys.exit(1 if fails else 0)
