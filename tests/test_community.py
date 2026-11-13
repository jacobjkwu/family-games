"""Community games tests (Playwright, headless Chrome with SwiftShader WebGL).
Checks every community game through community/play.html at both iPad sizes, the sandbox isolation from the
family games' storage, the save round trip, reloads, corrupt/foreign/oversized data, direct opening, the
controller "hold B" exit and the bar in four languages.
The local server adds Access-Control-Allow-Origin: * like GitHub Pages does (needed by module scripts in the
sandbox). Run: python3 tests/test_community.py   (screenshots go to /tmp/community-shots)"""
import json, sys, threading, functools, http.server, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = '/tmp/community-shots'
os.makedirs(OUT, exist_ok=True)
ALL = [g for g in json.load(open(f'{ROOT}/games.json'))['games'] if g.get('category') == 'community']
GAMES = [g for g in ALL if 'entry' in g]            # copied into community/
EMBED = [g for g in ALL if 'external' in g]         # official site shown inside play.html
PORT = 8768

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*'); self.send_header('Cache-Control', 'no-store'); super().end_headers()
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer.allow_reuse_address = True
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(H, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{PORT}/'
UA = 'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
PAD_MOCK = """(() => { const mk = i => ({ index: i, id: 'mock', mapping: 'standard', connected: true, timestamp: 0,
  buttons: Array.from({length: 17}, () => ({ pressed: false, value: 0 })), axes: [0, 0, 0, 0] });
  window.__pads = [mk(0)]; navigator.getGamepads = () => [window.__pads[0], null, null, null]; })();"""

results = []
def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))
    print(('PASS ' if ok else 'FAIL ') + name + (('  — ' + str(detail)) if detail and not ok else ''))

def ctx_for(b, w=1180, h=820, pads=False, locale='en-US'):
    c = b.new_context(viewport={'width': w, 'height': h}, has_touch=True, device_scale_factor=1, user_agent=UA, locale=locale)
    c.route(lambda u: u.startswith('http') and not u.startswith(BASE), lambda r: r.abort())   # offline except our site
    if pads: c.add_init_script(PAD_MOCK)
    return c
def frame(page):
    for _ in range(100):
        fr = [f for f in page.frames if f != page.main_frame and '/community/' in f.url]
        if fr: return fr[0]
        page.wait_for_timeout(100)
    return None
def open_game(page, gid, wait=5000):
    page.goto(BASE + 'community/play.html?g=' + gid, wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(wait)
    return frame(page)
LS = lambda page: page.evaluate("(() => { const o = {}; for (const k of Object.keys(localStorage)) o[k] = localStorage.getItem(k); return o; })()")

FAMILY_KEYS = {'dragon-gems/save/s2': '{"v":2,"gems":42}', 'crab-castle/save/s3': '{"wave":7}', 'game-hub/settings': '{"lang":"en"}',
               'family-cloud/state': '{"owner":null}', 'drawrassic-park/settings': '{"lang":"en"}'}

with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])

    # ---------- 1. every game, both iPad sizes ----------
    for (w, h) in [(1180, 820), (820, 1180)]:
        for g in GAMES:
            c = ctx_for(b, w, h); page = c.new_page(); errs = []
            page.on('pageerror', lambda e: errs.append(str(e)[:160]))
            f = open_game(page, g['id'])
            info = f.evaluate("({o: self.origin, shim: !!window.__FAMILY_COMMUNITY__, body: document.body ? document.body.innerText.length + document.querySelectorAll('canvas').length : 0})") if f else {}
            page.touchscreen.tap(w // 2, h // 2 + 30); page.wait_for_timeout(1200)
            page.screenshot(path=f'{OUT}/{g["id"]}-{w}x{h}.png')
            fe = page.evaluate("document.querySelectorAll('#stage iframe').length === 1 && document.getElementById('msg').hidden")
            check(f'{w}x{h} {g["id"]}: runs sandboxed (origin null, shim on, frame shown)', info.get('o') == 'null' and info.get('shim') and fe and info.get('body', 0) > 0, info)
            check(f'{w}x{h} {g["id"]}: no page errors', not errs, errs)
            bar = page.evaluate("(() => { const b = document.getElementById('bar').getBoundingClientRect(); return [b.height, document.documentElement.scrollWidth <= innerWidth + 1]; })()")
            check(f'{w}x{h} {g["id"]}: bar fits (≥44px, no sideways scroll)', bar[0] >= 44 and bar[1], bar)
            c.close()

    # ---------- 2. isolation from the family games ----------
    g0 = 'sudoku'
    c = ctx_for(b); page = c.new_page()
    page.goto(BASE + 'index.html', wait_until='domcontentloaded')
    page.evaluate("(o) => { for (const k in o) localStorage.setItem(k, o[k]); document.cookie = 'fam=1; path=/'; }", FAMILY_KEYS)
    f = open_game(page, g0, 2500)
    r = f.evaluate("""(() => { const out = {};
      localStorage.clear(); localStorage.setItem('dragon-gems/save/s2', 'HACKED'); localStorage.highscore = '99';
      out.keys = Object.keys(localStorage); out.cookie = document.cookie;
      try { out.parentLS = typeof parent.localStorage.getItem; } catch (e) { out.parentLS = 'blocked'; }
      try { out.parentDoc = parent.document.title; } catch (e) { out.parentDoc = 'blocked'; }
      try { out.idb = typeof indexedDB.open('x'); } catch (e) { out.idb = 'blocked'; }
      try { top.location.href = 'https://example.com/'; out.topNav = 'allowed'; } catch (e) { out.topNav = 'blocked'; }
      return out; })()""")
    page.wait_for_timeout(500)
    ls = LS(page)
    check('Isolation: family keys untouched after the game calls clear() and writes a family key name', all(ls.get(k) == v for k, v in FAMILY_KEYS.items()), {k: ls.get(k) for k in FAMILY_KEYS})
    check('Isolation: the game cannot read the hub page, its storage or navigate the top page', r['parentLS'] == 'blocked' and r['parentDoc'] == 'blocked' and r['topNav'] == 'blocked' and page.url.startswith(BASE), r)
    check('Isolation: the game sees no family cookie', r['cookie'] == '', r['cookie'])
    saved = json.loads(ls.get('community/sudoku/save', '{}'))
    check('Isolation: the game\'s own writes land under community/sudoku/save only', (saved.get('data') or {}).get('dragon-gems/save/s2') == 'HACKED' and saved['data'].get('highscore') == '99', saved)
    # ---------- 3. round trip, reload of the hub page and of the game itself ----------
    page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(2500); f = frame(page)
    v = f.evaluate("[localStorage.getItem('highscore'), localStorage.length, Object.keys(localStorage).sort().join(',')]")
    check('Round trip: after reloading play.html the game sees its saved data', v[0] == '99' and 'dragon-gems/save/s2' in v[2], v)
    f.evaluate("localStorage.setItem('afterReload', 'yes')"); page.wait_for_timeout(300)
    f.evaluate("location.reload()"); page.wait_for_timeout(2500); f = frame(page)
    v = f.evaluate("[localStorage.getItem('afterReload'), localStorage.getItem('highscore')]")
    check('Reload inside the game keeps the latest data (window.name)', v == ['yes', '99'], v)
    ls = LS(page)
    check('Backups: /bak and a daily /bak-d copy were written', 'community/sudoku/save/bak' in ls and any(k.startswith('community/sudoku/save/bak-d') for k in ls), [k for k in ls if k.startswith('community/')])
    # oversized write
    r = f.evaluate("(() => { try { localStorage.setItem('big', 'x'.repeat(4600000)); return 'stored'; } catch (e) { return e.name; } })()")
    check('Oversized write: the game gets QuotaExceededError, nothing breaks', r == 'QuotaExceededError', r)
    # conflict: something else changes the save (another tab or a cloud restore) -> saving pauses instead of overwriting
    page.evaluate("localStorage.setItem('community/sudoku/save', JSON.stringify({v:1, g:'sudoku', at:1, data:{fromCloud:'1'}}))")
    f.evaluate("localStorage.setItem('late', '1')"); page.wait_for_timeout(500)
    ls = LS(page)
    check('Conflict: an outside change is not overwritten; saving pauses with a message', json.loads(ls['community/sudoku/save'])['data'] == {'fromCloud': '1'} and page.locator('#msg').is_visible(), page.locator('#msgText').text_content())
    c.close()

    # ---------- 4. corrupt save, empty storage, quota full, unknown game ----------
    c = ctx_for(b); page = c.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    page.goto(BASE + 'index.html', wait_until='domcontentloaded')
    page.evaluate("""localStorage.setItem('community/sudoku/save', '{broken'); localStorage.setItem('community/sudoku/save/bak', JSON.stringify({v:1, g:'sudoku', at:1, data:{fromBak:'1'}}))""")
    f = open_game(page, 'sudoku', 2500)
    v = f.evaluate("localStorage.getItem('fromBak')"); ls = LS(page)
    check('Corrupt save: game starts from /bak, the bad data is kept under /broken-…', v == '1' and any(k.startswith('community/sudoku/save/broken-') and ls[k] == '{broken' for k in ls) and not errs, (v, errs))
    page.evaluate("localStorage.clear()")
    f = open_game(page, 'karagoz', 4000)
    check('Empty storage: game starts fresh without errors', f is not None and not errs, errs)
    page.evaluate("""(() => { const s = Storage.prototype.setItem; Storage.prototype.setItem = function (k, v) { if (String(k).startsWith('community/')) throw new DOMException('full', 'QuotaExceededError'); return s.call(this, k, v); }; })()""")
    f.evaluate("localStorage.setItem('q', '1')"); page.wait_for_timeout(400)
    check('Quota full on the hub page: the game keeps running, no errors', f.evaluate("localStorage.getItem('q')") == '1' and not errs, errs)
    page.goto(BASE + 'community/play.html?g=not-a-game', wait_until='domcontentloaded'); page.wait_for_timeout(800)
    check('Unknown game id: message and a way back to the hub', page.locator('#msg').is_visible() and page.locator('#msgHome').is_visible())
    page.goto(BASE + 'community/play.html?g=../games', wait_until='domcontentloaded'); page.wait_for_timeout(500)
    check('Bad game id: refused', page.locator('#msg').is_visible() and page.locator('#stage iframe').count() == 0)
    c.close()

    # ---------- 5. opening a game page directly never runs it on the family origin ----------
    for g in GAMES:
        c = ctx_for(b); page = c.new_page()
        page.goto(BASE + 'index.html', wait_until='domcontentloaded')
        page.evaluate("(o) => { localStorage.clear(); for (const k in o) localStorage.setItem(k, o[k]); }", FAMILY_KEYS)
        page.goto(BASE + 'community/' + g['entry'], wait_until='domcontentloaded'); page.wait_for_timeout(1500)
        ls = LS(page)
        stray = [k for k in ls if k not in FAMILY_KEYS and not k.startswith('community/') and not k.startswith('game-hub/') and not k.startswith('family-cloud/')]
        check(f'Direct open {g["id"]}: redirected to play.html, no game script touched the family storage', page.url.startswith(BASE + 'community/play.html?g=' + g['id']) and not stray, (page.url, stray))
        c.close()

    # ---------- 6. controller: hold B to leave, a short B press stays ----------
    c = ctx_for(b, 1920, 1080, pads=True); page = c.new_page()
    open_game(page, 'puffling-flight', 2500)
    check('Controller: "Hold B" hint shows when a controller is connected', page.locator('#padHint').is_visible())
    page.evaluate("window.__pads[0].buttons[1].pressed = true"); page.wait_for_timeout(500)
    page.evaluate("window.__pads[0].buttons[1].pressed = false"); page.wait_for_timeout(300)
    check('Controller: a short B press stays in the game', '/community/play.html' in page.url)
    page.evaluate("window.__pads[0].buttons[1].pressed = true"); page.wait_for_timeout(2200)
    check('Controller: holding B for 1.5 s goes back to the hub', page.url.rstrip('/').endswith('/index.html'), page.url)
    c.close()

    # ---------- 6b. embedded external sites (stubbed: this sandbox can't reach them) ----------
    STUB = '<!DOCTYPE html><title>stub</title><body>external game stub<script>try{localStorage.setItem("x","1")}catch(e){document.title="nostorage"}; parent.postMessage({__fgshim:1,type:"save",g:location.hostname,data:{evil:"1"}},"*");</script>'
    for g in EMBED:
        c = ctx_for(b, 820, 1180)
        c.route(g['external'].split('?')[0] + '*', lambda r: r.fulfill(status=200, content_type='text/html', body=STUB))
        page = c.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        page.goto(BASE + 'index.html', wait_until='domcontentloaded')
        page.evaluate("(o) => { for (const k in o) localStorage.setItem(k, o[k]); }", FAMILY_KEYS)
        page.goto(BASE + 'community/play.html?g=' + g['id'], wait_until='domcontentloaded'); page.wait_for_timeout(900)
        fr = page.locator('#stage iframe')
        info = page.evaluate("(() => { const f = document.querySelector('#stage iframe'); return f ? {src: f.src, sb: f.getAttribute('sandbox'), name: f.name} : null; })()")
        nt = page.locator('#newtab')
        ls = LS(page)
        ok = info and info['src'] == g['external'] and 'allow-same-origin' in info['sb'] and 'allow-top-navigation' not in info['sb'] and not info['name']
        check(f'Embed {g["id"]}: official site in the frame, no top navigation, no shim data passed', ok, info)
        check(f'Embed {g["id"]}: "open in new tab" shown, cloud button hidden, msg hidden', nt.is_visible() and nt.get_attribute('href') == g['external'] and page.locator('#cloud').is_hidden() and page.locator('#msg').is_hidden())
        check(f'Embed {g["id"]}: its messages can\'t write our storage', all(ls.get(k) == v for k, v in FAMILY_KEYS.items()) and not any(k.startswith('community/') for k in ls) and not errs, (errs, [k for k in ls if k.startswith('community/')]))
        bad = page.evaluate("[...document.querySelectorAll('#bar .btn')].filter(e => !e.hidden && (e.getBoundingClientRect().right > innerWidth + 1 || e.getBoundingClientRect().height < 44)).map(e => e.textContent)")
        check(f'Embed {g["id"]}: bar fits in portrait', not bad, bad)
        c.close()
    # bad external urls are refused
    c = ctx_for(b); page = c.new_page()
    for badurl in ['javascript:alert(1)', 'http://example.com/', BASE + 'index.html']:
        body = json.dumps({'games': [{'id': 'x', 'category': 'community', 'url': 'community/play.html?g=x', 'external': badurl}]})
        page.route('**/games.json', (lambda body: (lambda r: r.fulfill(status=200, content_type='application/json', body=body)))(body))
        page.goto(BASE + 'community/play.html?g=x', wait_until='domcontentloaded'); page.wait_for_timeout(500)
        check(f'Embed: refuses external url {badurl[:30]}', page.locator('#stage iframe').count() == 0 and page.locator('#msg').is_visible())
        page.unroute('**/games.json')
    c.close()

    # ---------- 7. the bar in four languages, portrait ----------
    for lg in ['en', 'fr', 'zh-Hans', 'zh-Hant']:
        c = ctx_for(b, 820, 1180); page = c.new_page()
        page.goto(BASE + 'index.html', wait_until='domcontentloaded')
        page.evaluate(f"localStorage.setItem('game-hub/settings', JSON.stringify({{lang:'{lg}'}}))")
        open_game(page, 'kapadokya-balonu', 3000)
        bad = page.evaluate("""[...document.querySelectorAll('#bar .btn')].filter(e => !e.hidden && (e.scrollWidth > e.clientWidth + 1 || e.getBoundingClientRect().right > innerWidth + 1 || e.getBoundingClientRect().height < 44)).map(e => e.textContent)""")
        home = page.locator('#home').text_content()
        check(f'Bar {lg}: translated, buttons fit and are ≥44px', not bad and home != '', (home, bad))
        page.screenshot(path=f'{OUT}/bar-{lg}.png')
        c.close()
    b.close()

srv.shutdown()
fails = [r for r in results if not r[1]]
print(f'\n{len(results) - len(fails)}/{len(results)} passed')
sys.exit(1 if fails else 0)
