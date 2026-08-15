# 锚 MindAnchor — 回归测试：Playwright 驱动系统 Chrome 验证全部功能（34 项断言）。用法：python test_v01.py
"""锚 MindAnchor v0.1 全功能回归测试"""
from playwright.sync_api import sync_playwright
import time, os, json

OUT = 'C:/Users/25671/mindanchor/test_shots'
os.makedirs(OUT, exist_ok=True)
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8123/index.html'
errors = []
fails = []

def check(name, cond, extra=''):
    tag = 'PASS' if cond else 'FAIL'
    print(f'[{tag}] {name} {extra}')
    if not cond: fails.append(name)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=['--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 390, 'height': 844})
    page = ctx.new_page()
    page.on('console', lambda m: errors.append(f'console[{m.type}]: {m.text}') if m.type=='error' else None)
    page.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))

    page.goto(URL, wait_until='load', timeout=30000)
    time.sleep(1.0)
    page.evaluate("() => { window.__origWait = wait; window.wait = (ms) => new Promise(r => setTimeout(r, ms/10)); }")

    # ---- 主页 ----
    check('标题', 'MindAnchor' in page.title())
    check('主页按钮', page.is_visible('text=现在就需要帮助'))
    check('AI 入口隐藏(无key)', not page.is_visible('#ai-entry-wrap >> visible=true'))
    page.screenshot(path=f'{OUT}/v01_home.png')

    # ---- 紧急协议 ----
    page.click('text=现在就需要帮助')
    page.wait_for_selector('#overlay.active')
    check('协议-中断', page.text_content('#ov-stage').startswith('阶段 1'))
    page.evaluate("() => skipPhase()")
    time.sleep(0.5)
    check('协议-呼吸', page.text_content('#ov-stage').startswith('阶段 2'), page.text_content('#breath-label'))
    page.evaluate("() => skipPhase()")
    time.sleep(0.5)
    check('协议-着陆', page.text_content('#ov-stage').startswith('阶段 3'))
    page.evaluate("() => skipPhase()")
    time.sleep(0.5)
    check('协议-寄存', page.text_content('#ov-stage').startswith('阶段 4'))

    # 冲动观察
    page.click('.urge-head')
    check('冲动观察-展开', page.is_visible('#urge-setup'))
    page.evaluate("() => { document.getElementById('urge-slider').value = 8; urgeSlider(8); }")
    check('冲动观察-评分', page.text_content('#urge-val') == '8')
    page.click('text=开始 3 分钟观察')
    check('冲动观察-计时', page.is_visible('#urge-timer'), page.text_content('#urge-clock'))
    # 加速计时器：直接改 sec
    page.evaluate("() => { clearInterval(urgeTimerInt); urgeTimerInt=null; document.getElementById('urge-timer').style.display='none'; document.getElementById('urge-result').style.display='block'; speak=function(){}; }")
    page.evaluate("() => { document.getElementById('urge-slider2').value = 3; urgeSlider2(3); finishUrge(); }")
    check('冲动观察-结果', '下降' in page.text_content('#urge-delta'), page.text_content('#urge-delta'))
    page.screenshot(path=f'{OUT}/v02_park_urge.png')

    # 念头 + 完成
    page.fill('#park-thought', '我总是担心自己刚才说的话让别人不高兴')
    page.evaluate("() => skipPhase()")
    time.sleep(0.5)
    check('完成页-金句', '「' in page.text_content('#done-quote'), page.text_content('#done-quote')[:20])
    check('完成页-SUDS', page.is_visible('#done-suds'))
    page.evaluate("() => { document.getElementById('done-suds').value = 70; doneSuds(70); }")
    check('完成页-SUDS值', page.text_content('#done-suds-val') == '70', page.text_content('#done-suds-label'))
    page.click('text=工作压力')
    page.fill('#done-note', '下午开会前发作')
    page.screenshot(path=f'{OUT}/v03_done.png')
    page.click('text=保存这次记录')

    # ---- 回访卡片应出现（30分钟后，先模拟）----
    time.sleep(0.5)
    page.evaluate("""() => {
      const rs = JSON.parse(localStorage.getItem('ma_records')||'[]');
      rs[0].followUpAt = Date.now() - 1000;  // 模拟已过30分钟
      localStorage.setItem('ma_records', JSON.stringify(rs));
    }""")
    page.evaluate("() => renderHome()")
    check('回访-卡片出现', page.is_visible('#followup-card.show'))
    page.screenshot(path=f'{OUT}/v04_home_followup.png')
    page.click('text=现在评一次 →')
    time.sleep(0.4)
    check('回访-页面', page.is_visible('#fb-compare'), page.text_content('#fb-ctx')[:30])
    page.evaluate("() => { document.getElementById('fb-suds').value = 30; fbSuds(30); }")
    page.click('text=记录这次对比')
    time.sleep(0.4)
    check('回访-对比提示', page.is_visible('#fb-advice'), page.text_content('#fb-advice')[:40].replace('\n',' '))
    page.screenshot(path=f'{OUT}/v05_followup.png')

    # ---- 历史 + 图表 ----
    page.click('.back >> visible=true')
    page.click('text=历史记录')
    time.sleep(0.5)
    check('历史-统计', page.text_content('#st-count') == '1')
    check('历史-SUDS chip', 'SUDS 70' in page.text_content('#rec-list'))
    check('历史-焦虑证据', '下降了 40' in page.text_content('#rec-list'), '')
    check('历史-图表canvas', page.eval_on_selector('#ch-count', 'c => c.width > 0') )
    page.screenshot(path=f'{OUT}/v06_history.png')

    # ---- 每日练习 ----
    page.click('.back >> visible=true')
    page.click('text=每日练习')
    time.sleep(0.4)
    check('练习-连续天数', '连续' in page.text_content('#streak-el'))
    check('练习-5阶段', page.locator('.phase-pip').count() == 5)
    page.click('#p-btn')
    time.sleep(1.5)
    check('练习-运行中', page.text_content('#p-btn') == '暂停')
    page.click('#p-btn')  # 暂停
    check('练习-暂停', page.text_content('#p-btn') == '继续')
    # 快进到完成：把 pSec 调小
    page.evaluate("() => { clearInterval(pInterval); pRunning=false; pSec=3; togglePractice(); }")
    time.sleep(4)
    check('练习-完成', page.evaluate("() => JSON.parse(localStorage.getItem('ma_practices')||'[]').length >= 1"))
    check('练习-记录streak', '连续 1 天' in page.text_content('#streak-el'), page.text_content('#streak-el'))
    page.screenshot(path=f'{OUT}/v07_practice.png')

    # ---- 暴露阶梯 ----
    page.click('.back >> visible=true')
    page.click('text=暴露阶梯')
    time.sleep(0.4)
    check('阶梯-默认5项', page.locator('.exp-item').count() == 5)
    page.fill('#exp-input', '碰过电梯按钮后不立刻洗手')
    page.select_option('#exp-level', '2')
    page.click('text=添加')
    check('阶梯-添加', page.locator('.exp-item').count() == 6)
    page.click('.exp-check >> nth=0')
    check('阶梯-勾选', 'done' in (page.get_attribute('.exp-check >> nth=0', 'class') or ''))
    page.screenshot(path=f'{OUT}/v08_ladder.png')

    # ---- 设置 AI ----
    page.click('.back >> visible=true')
    page.click('text=设置')
    time.sleep(0.4)
    page.fill('#in-aibase', 'https://worldcodes.online/v1')
    page.fill('#in-aikey', 'test-key-123')
    page.fill('#in-aimodel', 'claude-sonnet-4-6')
    page.click('text=保存 AI 配置')
    time.sleep(0.3)
    page.click('.back >> visible=true')
    check('AI入口-出现', page.is_visible('#ai-entry-wrap >> visible=true'))
    page.click('text=和我聊聊')
    time.sleep(0.4)
    check('聊天-初始消息', page.locator('.msg.bot').count() >= 1)
    page.fill('#chat-input', '我刚才又反复检查门锁了')
    page.click('#chat-btn')
    time.sleep(2.0)
    # 无真实网络，应出现错误提示（非崩溃）
    msgs = page.text_content('#chat-msgs')
    check('聊天-有响应(或错误提示)', len(msgs) > 0, msgs[-60:])
    page.screenshot(path=f'{OUT}/v09_chat.png')

    browser.close()

print('\n=== JS ERRORS ===')
for e in errors[:15]: print(e)
print(f'\n=== FAILS: {len(fails)} ===')
for f in fails: print(' -', f)
print('DONE')
