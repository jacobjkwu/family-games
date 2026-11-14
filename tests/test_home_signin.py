# Home Screen (standalone) sign-in help: the Google pop-up can't report back there, so the hub explains it and offers the pairing code.
# Run: python3 tests/test_home_signin.py
import asyncio, sys, json
sys.path.insert(0,'/home/claude/family-games/tests'); sys.argv=['x']
src=open('/home/claude/family-games/tests/test_friends.py').read(); src=src[:src.index('async def chip(pg)')+200].split('\nasync def',1)
__file__='/home/claude/family-games/tests/test_friends.py'; exec(open(__file__).read().split('\nasync def main')[0])
FAIL="""(()=>{ const t=setInterval(()=>{ if(window.__CLOUD_MOCK){ clearInterval(t); window.__CLOUD_MOCK.signIn=async()=>{ window.__tries=(window.__tries||0)+1; const e=new Error('closed'); e.code='auth/popup-closed-by-user'; throw e; }; } },5); })();"""
STAND="Object.defineProperty(navigator,'standalone',{get:()=>true});"
async def run(b,stand,lang,w,h):
    c=await ctx(b,{'uid':'u1','email':'mum@example.com'},lang,w,h); await c.add_init_script(FAIL)
    if stand: await c.add_init_script(STAND)
    pg=await c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(HUB); await pg.wait_for_timeout(1500)
    await pg.tap('.fc-chip'); await pg.wait_for_timeout(500)
    t1=await box(pg); labels=await pg.evaluate("[...document.querySelectorAll('.fc-box .fc-btn')].map(b=>b.textContent)")
    over=await pg.evaluate("[...document.querySelectorAll('.fc-box .fc-btn')].some(b=>b.scrollWidth>b.clientWidth+1||b.getBoundingClientRect().right>innerWidth)")
    await pg.screenshot(path=f'/tmp/home_{int(stand)}_{lang}_{w}.png')
    gl=[l for l in labels if 'Google' in l][0]
    await btn(pg,gl); await pg.wait_for_timeout(600); t2=await box(pg)
    await c.close(); return t1,labels,t2,over,errs
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for lang in ['en','fr','zh-Hans','zh-Hant']:
            for w,h in [(1180,820),(820,1180)]:
                t1,l,t2,o,e=await run(b,True,lang,w,h)
                ok = ('Safari' in t1) and ('📺' in l[0]) and ('Safari' in t2) and not o and not e
                print('stand',lang,w,'OK' if ok else 'FAIL',l[:2],o,e)
        t1,l,t2,o,e=await run(b,False,'zh-Hans',1180,820)
        print('browser', 'OK' if ('Safari' not in t1 and 'Google' in l[0] and t2=='' and not e) else 'FAIL', l[:2], repr(t2[:40]), e)
        await b.close()
asyncio.run(main())
