# Pairing success: the owner types a code and a dino pops up “Connected!” (mocked cloud). Run: python3 tests/test_pair_yay.py
import sys; __file__='/home/claude/family-games/tests/test_friends.py'; exec(open(__file__).read().split('\nasync def main')[0])
import time
_can=can
def can(u,op,p,d):
    if p.startswith('pairing/'): return bool(u)
    return _can(u,op,p,d)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for lang in ['zh-Hans','fr']:
            STORE['pairing/ABCDEF']={'anon':'a1','at':int(time.time()*1000)}
            c=await ctx(b,{'uid':'u1','email':'mum@example.com'},lang,820,1180); pg=await c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto(HUB); await pg.wait_for_timeout(1500); await pg.tap('.fc-chip'); await pg.wait_for_timeout(300); await btn(pg,'Google'); await pg.wait_for_timeout(1500); await pg.tap('.fc-chip'); await pg.wait_for_timeout(500)
            await btn(pg,'Appairer un autre' if lang=='fr' else '配对另一台')
            await pg.fill('.fc-box input','ABCDEF'); await btn(pg,'OK' if lang=='fr' else '确定')
            await pg.wait_for_timeout(500); t=await pg.evaluate("[...document.querySelectorAll('[role=status]')].map(e=>e.innerText.replace(/\\n/g,' ')).join('|')")
            await pg.screenshot(path=f'/tmp/yay_{lang}.png'); print(lang,repr(t),'owner set:',(STORE.get('pairing/ABCDEF') or {}).get('owner'),errs[:2]); await c.close()
        await b.close()
asyncio.run(main())
