# Friends asking to join the family cloud: mocked Firestore that applies the same rules as firestore.rules, mocked EmailJS.
# Run: python3 tests/test_friends.py (prints each step; screenshots in /tmp).
import asyncio, json
from playwright.async_api import async_playwright
import functools, http.server, socketserver, threading, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.ThreadingTCPServer(('127.0.0.1',8769),functools.partial(Q,directory=ROOT)); threading.Thread(target=srv.serve_forever,daemon=True).start()
HUB='http://127.0.0.1:8769/index.html'
STORE={}; MAILS=[]; OPT={'old':False}
FAMILY={'mum@example.com'}
class Deny(Exception): pass
def can(u,op,p,d):
    fam = u and not u.get('anon') and u['email'].lower() in FAMILY
    if OPT['old']:   # the rules live today: family only, no friends collections
        if p.startswith('users/'): return fam and p.split('/')[1]==u['uid']
        return False
    allowed = u and not u.get('anon') and ('allowed/'+u['email'].lower()) in STORE
    parts=p.split('/')
    if parts[0]=='users': return (fam or allowed) and parts[1]==u['uid']
    if parts[0]=='allowed':
        if op in('get','list'): return fam or (len(parts)>1 and u and u['email'].lower()==parts[1])
        return fam
    if parts[0]=='requests':
        if op=='list': return fam
        uid=parts[1]; cur=STORE.get(p)
        if op=='get': return fam or (u and u['uid']==uid)
        if op=='del': return fam or (u and u['uid']==uid and cur and cur.get('status')=='pending')
        if op=='set':
            if cur is not None: return fam
            return bool(u) and u['uid']==uid and set(d)<= {'uid','email','name','at','status','lang'} and d.get('uid')==uid and d.get('email')==u['email'] and d.get('status')=='pending' and isinstance(d.get('name'),str) and 0<len(d['name'])<=40
    return False
def mockdb(source, user, op, p, d):
    u=json.loads(user) if user else None; d=json.loads(d) if d else None
    if not can(u,op,p,d): return json.dumps({'__deny':True})
    if op=='get': return json.dumps(STORE.get(p))
    if op=='set': STORE[p]=d; return 'null'
    if op=='del': STORE.pop(p,None); return 'null'
    if op=='list':
        items=[dict(v,id=k[len(p)+1:]) for k,v in STORE.items() if k.startswith(p+'/') and '/' not in k[len(p)+1:]]
        items.sort(key=lambda x:-x.get('at',0)); return json.dumps(items[:d['n']])
def mail(source, body): MAILS.append(json.loads(body)); return True
MOCK="""(()=>{ const cbs=[]; let user=null; try{ user=JSON.parse(localStorage.getItem('__mockuser')); }catch(e){}
  const call=(op,p,d)=>window.__mockdb(JSON.stringify(user),op,p,d===undefined?null:JSON.stringify(d)).then(r=>{ const o=r==null?null:JSON.parse(r); if(o&&o.__deny){ const e=new Error('Missing or insufficient permissions.'); e.code='permission-denied'; throw e; } return o; });
  window.__CLOUD_MOCK={ onUser(cb){ cbs.push(cb); setTimeout(()=>cb(user),50); },
    async signIn(){ user=JSON.parse(localStorage.getItem('__who')); localStorage.setItem('__mockuser',JSON.stringify(user)); cbs.forEach(c=>c(user)); },
    async signOut(){ user=null; localStorage.removeItem('__mockuser'); cbs.forEach(c=>c(null)); },
    get(p){ return call('get',p); }, set(p,d){ return call('set',p,d); }, list(c,n){ return call('list',c,{n}); }, del(p){ return call('del',p); },
    async mail(b){ await window.__mail(JSON.stringify(b)); return {ok:true}; } }; })();"""
UA='Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
async def ctx(b,who,lang='zh-Hans',w=1180,h=820):
    c=await b.new_context(viewport={'width':w,'height':h},has_touch=True,is_mobile=True,user_agent=UA)
    await c.expose_binding('__mockdb',mockdb); await c.expose_binding('__mail',mail); await c.add_init_script(MOCK)
    await c.add_init_script(f"localStorage.setItem('__who',{json.dumps(json.dumps(who))}); if(!localStorage.getItem('game-hub/settings')) localStorage.setItem('game-hub/settings',JSON.stringify({{lang:'{lang}'}}));")
    return c
async def box(pg): return await pg.evaluate("(document.querySelector('.fc-box')||{}).innerText||''")
async def btn(pg,t): await pg.locator('.fc-btn',has_text=t).first.tap(); await pg.wait_for_timeout(400)
async def chip(pg): return await pg.evaluate("(document.querySelector('.fc-chip')||{}).textContent||''")
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']); errs=[]
        # 0. today's rules: the family keeps backing up (no friends collections yet)
        OPT['old']=True
        M=await ctx(b,{'uid':'m1','email':'mum@example.com'}); pm=await M.new_page(); pm.on('pageerror',lambda e: errs.append('M:'+str(e)))
        await pm.goto(HUB); await pm.wait_for_timeout(1500); await pm.tap('.fc-chip'); await pm.wait_for_timeout(300); await btn(pm,'用 Google 登录'); await pm.wait_for_timeout(1500)
        print('0 old rules: family role',await pm.evaluate("FamilyCloud.role()"),'| chip',await chip(pm),'| uploaded',any(k.startswith('users/m1/ls/') for k in STORE))
        OPT['old']=False
        # 1. a friend signs in and asks to join
        F=await ctx(b,{'uid':'f1','email':'friend@example.com'}); pf=await F.new_page(); pf.on('pageerror',lambda e: errs.append('F:'+str(e)))
        await pf.goto(HUB); await pf.wait_for_timeout(1500); await pf.tap('.fc-chip'); await pf.wait_for_timeout(300); await btn(pf,'用 Google 登录'); await pf.wait_for_timeout(1200)
        print('1 friend role',await pf.evaluate("FamilyCloud.role()"),'| dialog:',(await box(pf))[:80].replace('\n',' '))
        await pf.screenshot(path='/tmp/f1_guest.png')
        await btn(pf,'发送申请'); await btn(pf,'发送申请'); await pf.wait_for_timeout(300)
        print('  empty name -> dialog again:', '你的名字' in await pf.evaluate("(document.querySelector('.fc-box input')||{}).placeholder||''"))
        await pf.fill('.fc-box input','小明 Xiaoming'); await pf.screenshot(path='/tmp/f2_apply.png'); await btn(pf,'发送申请'); await pf.wait_for_timeout(800)
        print('  request',STORE.get('requests/f1'),'| mails',len(MAILS), MAILS[-1]['template_params'] if MAILS else None, MAILS[-1]['service_id'] if MAILS else None)
        print('  chip',await chip(pf),'| uploaded?',any(k.startswith('users/f1/') for k in STORE))
        # cannot ask twice / no second email
        r=await pf.evaluate("""(async()=>{ try{ await window.__CLOUD_MOCK.set('requests/f1',{uid:'f1',email:'friend@example.com',name:'x',at:1,status:'pending'}); return 'allowed'; }catch(e){ return e.code; } })()""")
        print('  second request by friend:',r,'| forged email:',await pf.evaluate("""(async()=>{ try{ await window.__CLOUD_MOCK.set('requests/zz',{uid:'zz',email:'x@y',name:'x',at:1,status:'pending'}); return 'allowed'; }catch(e){ return e.code; } })()"""),
              '| self-approve:',await pf.evaluate("""(async()=>{ try{ await window.__CLOUD_MOCK.set('allowed/friend@example.com',{}); return 'allowed'; }catch(e){ return e.code; } })()"""))
        await pf.tap('.fc-chip'); await pf.wait_for_timeout(300); print('  pending dialog:',(await box(pf)).replace('\n',' ')[:90]); await pf.screenshot(path='/tmp/f3_pending.png'); await btn(pf,'关闭')
        # 2. family sees the bell and approves
        await pm.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await pm.wait_for_timeout(800)
        print('2 family chip',await chip(pm)); await pm.screenshot(path='/tmp/f4_bell.png')
        await pm.tap('.fc-chip'); await pm.wait_for_timeout(300); await btn(pm,'等待批准的朋友'); await pm.wait_for_timeout(300)
        print('  request card:',(await box(pm)).replace('\n',' ')[:100]); await pm.screenshot(path='/tmp/f5_card.png'); await btn(pm,'✅ 同意'); await pm.wait_for_timeout(500)
        print('  allowed doc',STORE.get('allowed/friend@example.com'),'| request status',STORE['requests/f1']['status'],'| chip',await chip(pm))
        # 3. the friend becomes a member and backs up
        await pf.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await pf.wait_for_timeout(1500)
        print('3 friend role',await pf.evaluate("FamilyCloud.role()"),'| uploaded',[k for k in STORE if k.startswith('users/f1/')][:3],'| chip',await chip(pf))
        # 4. a second friend is not approved
        F2=await ctx(b,{'uid':'f2','email':'other@example.com'},'en'); p2=await F2.new_page(); p2.on('pageerror',lambda e: errs.append('F2:'+str(e)))
        await p2.goto(HUB); await p2.wait_for_timeout(1500); await p2.tap('.fc-chip'); await p2.wait_for_timeout(300); await btn(p2,'Sign in with Google'); await p2.wait_for_timeout(1200)
        await btn(p2,'Send request'); await p2.fill('.fc-box input','Stranger'); await btn(p2,'Send request'); await p2.wait_for_timeout(600)
        await pm.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await pm.wait_for_timeout(800); await pm.tap('.fc-chip'); await pm.wait_for_timeout(300); await btn(pm,'等待批准的朋友'); await btn(pm,'不同意'); await pm.wait_for_timeout(400)
        await p2.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await p2.wait_for_timeout(1000); await p2.tap('.fc-chip'); await p2.wait_for_timeout(300)
        print('4 denied friend:',(await box(p2)).replace('\n',' ')[:110],'| role',await p2.evaluate("FamilyCloud.role()"),'| mails',len(MAILS)); await btn(p2,'Close')
        # 5. family removes friend 1 -> friend may ask again
        await pm.tap('.fc-chip'); await pm.wait_for_timeout(300); await btn(pm,'已批准的朋友'); await pm.screenshot(path='/tmp/f6_members.png'); await btn(pm,'小明'); await btn(pm,'移除'); await pm.wait_for_timeout(400)
        await pf.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); await pf.wait_for_timeout(1000)
        print('5 removed: allowed',('allowed/friend@example.com' in STORE),'| request',('requests/f1' in STORE),'| friend role',await pf.evaluate("FamilyCloud.role()"),'| friend data kept',any(k.startswith('users/f1/') for k in STORE))
        # 6. all four languages: the apply dialog, portrait
        for lg in ['en','fr','zh-Hans','zh-Hant']:
            X=await ctx(b,{'uid':'g'+lg,'email':lg+'@example.com'},lg,820,1180); px=await X.new_page(); px.on('pageerror',lambda e: errs.append('X:'+str(e)))
            await px.goto(HUB); await px.wait_for_timeout(1300); await px.tap('.fc-chip'); await px.wait_for_timeout(300); await px.locator('.fc-btn').first.tap(); await px.wait_for_timeout(1200)
            await px.locator('.fc-btn').first.tap(); await px.wait_for_timeout(400); await px.screenshot(path=f'/tmp/f7_{lg}.png'); print('6',lg,(await box(px)).replace('\n',' ')[:70]); await X.close()
        print('errors',errs); await b.close()
asyncio.run(main())
