"""Offline checks for apps/ios/www (the bundle that goes into the iOS app).

Runs the built www/ in Chrome with every non-local request blocked and a mocked
Capacitor bridge, at iPad sizes 1180x820 and 820x1180. It does NOT run WKWebView or
the Swift code: those need a Mac (see README.md).

    npm run build:web            # or: node scripts/build-www.mjs --profile family
    python3 tests/test_www.py [--shots DIR]
"""
import hashlib, http.server, json, os, socketserver, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

APP = Path(__file__).resolve().parent.parent
WWW = APP / 'www'
REPO = APP.parent.parent
INFO = json.loads((WWW / 'app/build-info.json').read_text())
SHOTS = Path(sys.argv[sys.argv.index('--shots') + 1]) if '--shots' in sys.argv else None
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')

MOCK = """
window.__calls = [];
window.Capacitor = { isNativePlatform: () => true, getPlatform: () => 'ios',
  nativePromise: (p, m, o) => { window.__calls.push([p, m, o]);
    return Promise.resolve(m === 'saveImage' ? {ok: true} : {ok: true}); } };
"""

fails = []
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(WWW), **k)
    def log_message(self, *a): pass

def main():
    src = (REPO / 'drawrassic-park' / INFO['gameFile']).read_bytes()
    check(hashlib.sha256(src).hexdigest()[:16] == INFO['sourceSha256'], 'original game file unchanged since the build')
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Quiet); srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_address[1]}/'
    game_url = base + INFO['gameFile']
    online = INFO['online']
    print(f"profile={INFO['profile']} game v{INFO['gameVersion']} online={online}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        for (w, h) in [(1180, 820), (820, 1180)]:
            tag = f'{w}x{h}'
            ctx = browser.new_context(viewport={'width': w, 'height': h}, has_touch=True, device_scale_factor=2,
                                      locale='en-US')
            outside, errors = [], []
            def route(r):
                if r.request.url.startswith(base) or r.request.url.startswith(('data:', 'blob:')): return r.continue_()
                outside.append(r.request.url); return r.abort()
            ctx.route('**/*', route)
            ctx.add_init_script(MOCK)
            page = ctx.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            popups = []
            page.on('popup', lambda p: popups.append(p.url))

            # 1. launcher -> game
            page.goto(base, wait_until='load')
            page.wait_for_url(game_url, timeout=15000)
            check(page.url == game_url, f'[{tag}] app start page opens the game directly')
            page.wait_for_function("document.querySelector('canvas') && document.querySelectorAll('#tools button').length > 3", timeout=30000)
            page.wait_for_timeout(2500)
            check(page.evaluate("!!window.FamilyNative && FamilyNative.isNative()"), f'[{tag}] FamilyNative bridge present')
            check(page.evaluate("document.fonts.check('600 20px Fredoka')"), f'[{tag}] Fredoka font bundled and loaded')
            if SHOTS:
                SHOTS.mkdir(parents=True, exist_ok=True); page.screenshot(path=str(SHOTS / f"{INFO['profile']}-{tag}-start.png"))

            # 2. web-only UI hidden
            disp = lambda sel: page.evaluate(f"(()=>{{const e=document.querySelector({json.dumps(sel)}); return e?getComputedStyle(e).display:'missing'}})()")
            for sel in ['#switchVer', '#cloudBox', '#verBadge']:
                check(disp(sel) in ('none', 'missing'), f'[{tag}] {sel} hidden ({disp(sel)})')
            if online:
                check(disp('#netOpen') != 'none', f'[{tag}] family build keeps 🌐 online battle button')
            else:
                check(disp('#netOpen') in ('none', 'missing'), f'[{tag}] store build hides 🌐 online battle button')
                vis = page.evaluate("[...document.querySelectorAll('#tools [data-qa=online],#tools [data-qa=together],#tools [data-qa=players]')].filter(e=>getComputedStyle(e).display!=='none').length")
                check(vis == 0, f'[{tag}] store build: no online/together/players quick-bar buttons visible ({vis})')

            # 3. native hooks
            page.evaluate("window.__calls.length=0; navigator.vibrate(30)")
            page.wait_for_timeout(100)
            calls = page.evaluate("window.__calls")
            check(calls and calls[0][:2] == ['FamilyNative', 'haptic'], f'[{tag}] navigator.vibrate -> native haptic {calls}')
            check(page.evaluate("window.open('https://example.com') === null"), f'[{tag}] window.open blocked')
            check(page.evaluate("navigator.mediaDevices ? navigator.mediaDevices.getUserMedia === undefined : true"), f'[{tag}] microphone API removed')

            # 4. links out of the app do nothing
            page.evaluate("""(()=>{ for (const [id,href,t] of [['x1','https://example.com/',''],['x2','https://example.com/','_blank'],['x3','mailto:a@b.c','']]) {
                const a=document.createElement('a'); a.id=id; a.href=href; if(t) a.target=t; a.textContent=id;
                a.style.cssText='position:fixed;left:10px;top:'+(10+30*+id[1])+'px;z-index:99999;font-size:20px;background:#fff'; document.body.appendChild(a); } })()""")
            for i in (1, 2, 3):
                page.locator(f'#x{i}').tap()
            page.wait_for_timeout(500)
            check(page.url == game_url and not popups, f'[{tag}] external links blocked (url={page.url}, popups={popups})')

            # 5. <a download> image -> Photos
            page.evaluate("""(()=>{ const c=document.createElement('canvas'); c.width=c.height=8; const a=document.createElement('a');
                a.id='dl'; a.href=c.toDataURL('image/png'); a.download='my-dino.png'; a.textContent='PNG';
                a.style.cssText='position:fixed;left:200px;top:10px;z-index:99999;font-size:20px;background:#fff'; document.body.appendChild(a); window.__calls.length=0; })()""")
            page.locator('#dl').tap(); page.wait_for_timeout(300)
            calls = page.evaluate("window.__calls")
            check(any(c[1] == 'saveImage' for c in calls), f'[{tag}] download link -> native saveImage')
            toast = page.evaluate("(document.querySelector('.family-app-toast')||{}).textContent||''")
            check('Photos' in toast, f'[{tag}] photo toast shown ({toast})')
            for lang, want in [('fr', 'Photos'), ('zh-Hans', '相册'), ('zh-Hant', '照片')]:
                page.evaluate(f"document.documentElement.lang={json.dumps(lang)}")
                page.locator('#dl').tap(); page.wait_for_timeout(150)
                t = page.evaluate("document.querySelector('.family-app-toast').textContent")
                check(want in t, f'[{tag}] toast in {lang}: {t}')

            # 6. rescue tool via the launcher copy
            page.goto(base + 'index.html#rescue', wait_until='load')
            page.wait_for_timeout(1500)
            check(page.url.endswith('index.html#rescue'), f'[{tag}] #rescue stays on the recover tool')
            check(disp('#rescue') != 'none', f'[{tag}] recover dialog visible')
            shown = page.evaluate("(()=>{const e=document.querySelector('#list'); return !!e && e.getClientRects().length>0})()")
            check(not shown, f'[{tag}] version list hidden in the app')
            if SHOTS: page.screenshot(path=str(SHOTS / f"{INFO['profile']}-{tag}-rescue.png"))
            page.locator('#rClose').tap()
            page.wait_for_url(game_url, timeout=10000)
            check(page.url == game_url, f'[{tag}] closing the recover tool returns to the game')
            page.wait_for_timeout(1500)

            check(not outside, f'[{tag}] no request left the device ({outside[:5]})')
            real_errors = [e for e in errors if 'firebase' not in e.lower()]
            check(not real_errors, f'[{tag}] no page errors ({real_errors[:3]})')
            ctx.close()
        browser.close()
    srv.shutdown()
    print(f"\n{'ALL PASSED' if not fails else str(len(fails)) + ' FAILED'}")
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
