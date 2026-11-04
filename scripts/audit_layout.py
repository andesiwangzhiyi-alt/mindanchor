# 布局审计：检查横向溢出、元素越界、被底部导航遮挡、零尺寸等真实渲染问题
from playwright.sync_api import sync_playwright
import time, json, os

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8123/index.html'
OUT = 'C:/Users/25671/mindanchor/test_shots'
os.makedirs(OUT, exist_ok=True)

VIEWPORTS = [(320, 568), (360, 640), (390, 844), (430, 932)]
SCREENS = [
    ('home', "() => showView('view-home')"),
    ('triage0', "() => { triReset(); showView('view-triage'); }"),
    ('triage1', "() => { TRI.text='测试'; TRI.step=1; renderTriage(); }"),
    ('triage5', "() => { TRI.text='测试'; TRI.worst='最坏结果'; TRI.burden='hard'; TRI.step=5; renderTriage(); }"),
    ('expect_list', "() => { EX=null; showView('view-expect'); }"),
    ('expect_a', "() => { expNew(); }"),
    ('focus', "() => showView('view-focus')"),
    ('worry', "() => showView('view-worry')"),
    ('chain', "() => showView('view-chain')"),
    ('practice', "() => showView('view-practice')"),
    ('ladder', "() => showView('view-ladder')"),
    ('history', "() => showView('view-history')"),
    ('settings', "() => showView('view-settings')"),
]

problems = []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=['--no-sandbox'])
    for (w, h) in VIEWPORTS:
        ctx = browser.new_context(viewport={'width': w, 'height': h})
        page = ctx.new_page()
        page.goto(URL, wait_until='load', timeout=30000)
        time.sleep(0.6)
        # 预置数据，让各页面有内容
        page.evaluate("""() => {
          localStorage.setItem('ma_parked', JSON.stringify([{id:'p1',text:'我是不是漏看了哪一条笔记，导致最后丢分',worst:'可能真的丢分',burden:'hard',at:Date.now(),dueAt:Date.now()-1000,dueKind:'worry',resolved:null}]));
          localStorage.setItem('ma_expect', JSON.stringify([{id:'e1',task:'检查完一遍就不再检查',pred:'会漏掉一处错误',conf:85,actual:'交上去了，没有出错',post:25,at:Date.now()}]));
          localStorage.setItem('ma_triage', JSON.stringify([{id:'t1',text:'念头',exit:'park',at:Date.now()}]));
          localStorage.setItem('ma_records', JSON.stringify([{t:Date.now(),suds:70,thought:'测试念头',tags:['工作压力'],followUpSuds:30}]));
          localStorage.setItem('ma_focus', JSON.stringify([{id:'f1',min:15,marks:3,at:Date.now()}]));
        }""")
        page.reload(wait_until='load')
        time.sleep(0.6)
        for name, js in SCREENS:
            page.evaluate(js)
            time.sleep(0.35)
            res = page.evaluate("""() => {
              const vw = window.innerWidth, vh = window.innerHeight;
              const bar = document.getElementById('tabbar').getBoundingClientRect();
              const out = { docW: document.documentElement.scrollWidth, vw,
                            over: [], zero: [], underBar: [] };
              // 横向溢出
              document.querySelectorAll('.view.active *').forEach(el => {
                if (!el.offsetParent && el.offsetWidth === 0) return;
                const r = el.getBoundingClientRect();
                if (r.width === 0 && r.height === 0) return;
                if (r.right > vw + 1.5 || r.left < -1.5) {
                  out.over.push(el.tagName + '.' + (el.className||'').toString().slice(0,28) + ' L' + Math.round(r.left) + ' R' + Math.round(r.right));
                }
              });
              // 可见但零高/零宽的可交互元素（跳过隐藏元素）
              document.querySelectorAll('.view.active button, .view.active input, .view.active textarea').forEach(el => {
                if (!el.offsetParent && el.offsetWidth === 0) return;
                const cs = getComputedStyle(el);
                if (cs.display === 'none' || cs.visibility === 'hidden') return;
                const r = el.getBoundingClientRect();
                if (r.height === 0 || r.width === 0) out.zero.push(el.tagName + '.' + (el.className||'').toString().slice(0,28));
              });
              // 被底部导航遮住的最后一批内容（只查 .wrap 的最后一个直接子元素）
              const wrap = document.querySelector('.view.active .wrap');
              if (wrap && wrap.lastElementChild) {
                const r = wrap.lastElementChild.getBoundingClientRect();
                if (r.bottom > bar.top + 1 && r.top < bar.top) out.underBar.push('last child bottom=' + Math.round(r.bottom) + ' barTop=' + Math.round(bar.top));
              }
              return out;
            }""")
            if res['docW'] > res['vw'] + 1:
                problems.append(f'{w}x{h} {name}: 横向溢出 docW={res["docW"]} vw={res["vw"]}')
            for o in res['over']:
                problems.append(f'{w}x{h} {name}: 元素越界 {o}')
            for z in res['zero']:
                problems.append(f'{w}x{h} {name}: 零尺寸可交互元素 {z}')
            if name in ('home', 'focus', 'worry', 'settings', 'history'):
                page.screenshot(path=f'{OUT}/layout_{w}_{name}.png', full_page=False)
        ctx.close()
    browser.close()

print(f'PROBLEMS: {len(problems)}')
for x in problems[:60]:
    print(' -', x)
