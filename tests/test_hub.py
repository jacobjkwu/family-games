"""Game Hub tests (Playwright, headless Chrome): TV 1920x1080 with 1/2/4 mocked controllers, iPad touch at
1180x820 and 820x1180, four languages, both sections (our games / community games), corrupt storage.
Run: python3 tests/test_hub.py   (screenshots go to /tmp/hub-shots)"""
import json, sys, threading, functools, http.server, socketserver, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = '/tmp/hub-shots'
os.makedirs(OUT, exist_ok=True)
GAMES = json.load(open(f'{ROOT}/games.json'))['games']
FAMILY = [g for g in GAMES if g.get('category', 'family') == 'family']
COMMUNITY = [g for g in GAMES if g.get('category') == 'community']
PORT = 8767

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{PORT}/'
URL = BASE + 'index.html'
def abs_url(g): return g['url'] if g['url'].startswith('http') else BASE + g['url']

PAD_MOCK = """
(() => {
  const mk = i => ({ index: i, id: 'Xbox Wireless Controller (mock ' + i + ')', mapping: 'standard', connected: true, timestamp: 0,
    buttons: Array.from({length: 17}, () => ({ pressed: false, value: 0, touched: false })), axes: [0, 0, 0, 0],
    vibrationActuator: { playEffect: () => Promise.resolve('complete') } });
  window.__pads = Array.from({length: %d}, (_, i) => mk(i));
  navigator.getGamepads = () => [0, 1, 2, 3].map(i => window.__pads[i] || null);
})();
"""
results = []
def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))
    print(('PASS ' if ok else 'FAIL ') + name + (('  — ' + str(detail)) if detail and not ok else ''))

BTN = {'A': 0, 'B': 1, 'up': 12, 'down': 13, 'left': 14, 'right': 15}
def press(page, b, pad=0):
    page.evaluate(f'(() => {{ const x = window.__pads[{pad}].buttons[{BTN[b]}]; x.pressed = true; x.value = 1; }})()')
    page.wait_for_timeout(60)
    page.evaluate(f'(() => {{ const x = window.__pads[{pad}].buttons[{BTN[b]}]; x.pressed = false; x.value = 0; }})()')
    page.wait_for_timeout(60)
focused = lambda page: page.evaluate("(() => { const e = document.querySelector('.nav.focused'); return e ? (e.dataset.key || e.id) : null; })()")
def walk_to(page, key, pad=0):
    """Drive the focus to [data-key=key] with the D-pad only, one step at a time toward the target."""
    for _ in range(40):
        f = focused(page)
        if f == key: return True
        d = page.evaluate("""(k) => { const a = document.querySelector('.nav.focused'), b = document.querySelector('[data-key="' + k + '"]');
          if (!a || !b) return 'down'; const p = a.getBoundingClientRect(), q = b.getBoundingClientRect();
          const dy = (q.top + q.bottom) / 2 - (p.top + p.bottom) / 2, dx = (q.left + q.right) / 2 - (p.left + p.right) / 2;
          if (Math.abs(dy) > p.height / 2) return dy > 0 ? 'down' : 'up'; return dx > 0 ? 'right' : 'left'; }""", key)
        press(page, d, pad)
    return focused(page) == key

def new_ctx(b, w, h, pads=0, touch=False, lang='zh-CN'):
    ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, locale=lang, device_scale_factor=1)
    if pads: ctx.add_init_script(PAD_MOCK % pads)
    opened = []
    def stub(route):
        opened.append(route.request.url)
        route.fulfill(status=200, content_type='text/html', body='<!DOCTYPE html><title>stub</title>launcher stub')
    ctx.route('https://jacobjkwu.github.io/**', stub)
    ctx.route('**/community/play.html*', stub)
    ctx.route(lambda u: not u.startswith(BASE) and u.startswith('http') and 'jacobjkwu.github.io' not in u, lambda r: r.abort())
    return ctx, opened

def layout_checks(page, tag, tv=False):
    r = page.evaluate("""(() => {
      const iw = innerWidth, bad = [];
      if (document.documentElement.scrollWidth > iw + 1) bad.push('page scrolls sideways ' + document.documentElement.scrollWidth);
      for (const e of document.querySelectorAll('.btn, #cont .tx, .card .name, .card .blurb, .card .credit, .tag, .ver, h1, h2.sec')) {
        if (e.offsetParent === null) continue;
        if (e.scrollWidth > e.clientWidth + 1) bad.push('overflow: ' + (e.className || e.tagName) + ' "' + e.textContent.slice(0, 30) + '"');
        const q = e.getBoundingClientRect();
        if (q.right > iw + 1 || q.left < -1) bad.push('off-screen: ' + e.textContent.slice(0, 30));
      }
      const small = [...document.querySelectorAll('.nav')].filter(e => e.offsetParent && (e.getBoundingClientRect().height < 44 || e.getBoundingClientRect().width < 44)).map(e => e.textContent.slice(0, 20));
      if (small.length) bad.push('tap target <44px: ' + small.join(','));
      return bad;
    })()""")
    check(f'{tag}: no overflow / cut-off, tap targets ≥44px', not r, r)
    if tv:
        m = page.evaluate("""(() => {
          const fs = e => parseFloat(getComputedStyle(e).fontSize);
          const body = fs(document.body), num = Math.min(...[...document.querySelectorAll('.ver b')].map(fs));
          const text = Math.min(...[...document.querySelectorAll('.card .blurb, .card .credit, .tag, footer, .btn, h2.sec small')].filter(e => e.offsetParent).map(fs));
          const mx = innerWidth * 0.05, out = [];
          for (const e of document.querySelectorAll('.nav, h1, h2.sec, footer, .ver b')) {
            if (e.offsetParent === null) continue; const q = e.getBoundingClientRect();
            if (q.left < mx - 1 || q.right > innerWidth - mx + 1) out.push((e.dataset.key || e.id || e.tagName) + ' ' + JSON.stringify([q.left|0, q.right|0]));
          }
          return { body, num, text, out };
        })()""")
        check(f'{tag}: body text ≥28px (body {m["body"]:.1f}, smallest text {m["text"]:.1f})', m['body'] >= 28 and m['text'] >= 27.9)
        check(f'{tag}: version numbers ≥40px ({m["num"]:.1f})', m['num'] >= 40)
        check(f'{tag}: UI inside the 5% side margins', not m['out'], m['out'])

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------- 1. TV 1920x1080, one controller only ----------
    ctx, opened = new_ctx(b, 1920, 1080, pads=1)
    page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    page.goto(URL); page.wait_for_selector('#games .card')
    check(f'TV: all {len(GAMES)} cards loaded from games.json', page.locator('#games .card').count() == len(GAMES))
    secs = page.locator('h2.sec').all_text_contents()
    check('TV: two sections, ours first, community second', len(secs) == 2 and '自己开发的游戏' in secs[0] and '社区游戏' in secs[1], secs)
    order = page.evaluate("[...document.querySelectorAll('#games .card')].map(a => a.dataset.id)")
    check('TV: section order matches the categories', order == [g['id'] for g in FAMILY] + [g['id'] for g in COMMUNITY], order)
    credit = page.locator(f'[data-key="game-{COMMUNITY[0]["id"]}"] .credit').text_content()
    check('TV: community card shows author and AI tool', COMMUNITY[0]['credit']['author'] in credit and COMMUNITY[0]['credit']['made'] in credit, credit)
    check('TV: no "Continue" before any game was opened', page.locator('#cont').is_hidden())
    press(page, 'A')
    check('TV: first A press only shows the focus ring (opens nothing)', not opened and focused(page) == 'game-' + FAMILY[0]['id'], focused(page))
    for g in GAMES:
        page.goto(URL); page.wait_for_selector('#games .card')
        press(page, 'down')
        ok = walk_to(page, 'game-' + g['id'])
        check(f'TV pad: D-pad reaches {g["id"]}', ok, focused(page))
        n0 = len(opened); press(page, 'A'); page.wait_for_timeout(400)
        check(f'TV pad: A opens {g["id"]}', len(opened) > n0 and opened[-1] == abs_url(g), opened[-1:])
        page.go_back(); page.wait_for_selector('#games .card')
        txt = page.locator('#cont .tx').text_content() if page.locator('#cont').is_visible() else None
        check(f'TV: Continue now shows {g["name"]["zh-Hans"]}', txt == f'继续玩：{g["name"]["zh-Hans"]}', txt)
    press(page, 'down')
    check('TV: default focus is Continue when present', focused(page) == 'cont', focused(page))
    n0 = len(opened); press(page, 'A'); page.wait_for_timeout(400)
    check('TV pad: A on Continue opens the last game (a community game)', len(opened) > n0 and opened[-1] == abs_url(GAMES[-1]))
    page.go_back(); page.wait_for_selector('#games .card')
    press(page, 'down'); ok = walk_to(page, 'lang-en'); press(page, 'A'); page.wait_for_timeout(100)
    check('TV pad: language switch to English by controller', ok and page.locator('h1').text_content() == '🎮 Game Hub')
    check('TV pad: section titles follow the language', page.locator('h2.sec').first.text_content().startswith('🏠 Our own games'))
    press(page, 'B'); page.wait_for_timeout(100)
    check('TV pad: B goes back to Continue', focused(page) == 'cont', focused(page))
    check('TV: no page errors', not errs, errs)
    for lg in ['en', 'fr', 'zh-Hans', 'zh-Hant']:
        page.evaluate(f"localStorage.setItem('game-hub/settings', JSON.stringify({{lang:'{lg}'}})); localStorage.setItem('game-hub/last', JSON.stringify({{id:'crab-castle'}}))")
        page.reload(); page.wait_for_selector('#games .card'); press(page, 'down')
        layout_checks(page, f'TV 1920x1080 {lg}', tv=True)
        page.screenshot(path=f'{OUT}/tv-{lg}.png', full_page=True)
    ctx.close()

    # ---------- 2. 2 and 4 controllers: any controller can drive ----------
    for n in (2, 4):
        ctx, opened = new_ctx(b, 1920, 1080, pads=n)
        page = ctx.new_page(); page.goto(URL); page.wait_for_selector('#games .card')
        last = n - 1
        press(page, 'down', last); walk_to(page, 'game-' + COMMUNITY[1]['id'], last); press(page, 'A', last); page.wait_for_timeout(400)
        check(f'{n} pads: controller #{n} alone opens a community game', opened and opened[-1] == abs_url(COMMUNITY[1]), opened)
        ctx.close()

    # ---------- 3. iPad sizes, touch only ----------
    for (w, h) in [(1180, 820), (820, 1180)]:
        ctx, opened = new_ctx(b, w, h, touch=True)
        page = ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        page.goto(URL); page.wait_for_selector('#games .card')
        for i, g in enumerate(GAMES):
            page.goto(URL); page.wait_for_selector('#games .card')
            c = page.locator('#games .card').nth(i); c.scroll_into_view_if_needed(); c.tap(); page.wait_for_timeout(300)
            check(f'iPad {w}x{h}: tap opens {g["id"]}', opened and opened[-1] == abs_url(g))
            page.go_back(); page.wait_for_selector('#games .card')
        page.get_by_text('繁體中文').tap(); page.wait_for_timeout(100)
        check(f'iPad {w}x{h}: tap 繁體中文 switches language', page.locator('h1').text_content() == '🎮 遊戲大廳')
        check(f'iPad {w}x{h}: no focus ring shown for touch', not page.evaluate("document.body.classList.contains('show-focus')"))
        for lg in ['en', 'fr', 'zh-Hans', 'zh-Hant']:
            page.evaluate(f"localStorage.setItem('game-hub/settings', JSON.stringify({{lang:'{lg}'}}))")
            page.reload(); page.wait_for_selector('#games .card')
            layout_checks(page, f'iPad {w}x{h} {lg}')
            page.screenshot(path=f'{OUT}/ipad-{w}x{h}-{lg}.png', full_page=True)
        check(f'iPad {w}x{h}: no page errors', not errs, errs)
        ctx.close()

    # ---------- 4. Robustness ----------
    ctx, opened = new_ctx(b, 1920, 1080, pads=1)
    page = ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    page.goto(URL); page.wait_for_selector('#games .card')
    page.evaluate("localStorage.setItem('game-hub/settings', '{bad json'); localStorage.setItem('game-hub/last', '\"nope');")
    page.reload(); page.wait_for_selector('#games .card')
    check('Corrupt localStorage: page still loads, no Continue', page.locator('#cont').is_hidden() and not errs, errs)
    page.route('**/games.json', lambda r: r.fulfill(status=200, content_type='application/json', body=json.dumps({'games': FAMILY[:1] + [{'id': 'x', 'url': 'javascript:alert(1)'}]})))
    page.reload(); page.wait_for_selector('#games .card')
    check('Bad url in games.json is dropped; one section only shows no headings', page.locator('#games .card').count() == 1 and page.locator('h2.sec').count() == 0)
    ctx.close()
    b.close()

srv.shutdown()
fails = [r for r in results if not r[1]]
print(f'\n{len(results) - len(fails)}/{len(results)} passed')
sys.exit(1 if fails else 0)
