# 锚 MindAnchor — v0.2 备考模式回归测试（Playwright + 系统 Chrome）
# 用法：先 `python server.py --host 127.0.0.1 --port 8123`，再 `python scripts/test_v02.py`
"""锚 MindAnchor v0.2 新增功能回归测试"""
from playwright.sync_api import sync_playwright
import time, os

OUT = 'C:/Users/25671/mindanchor/test_shots'
os.makedirs(OUT, exist_ok=True)
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = os.environ.get('MA_URL', 'http://127.0.0.1:8123/index.html')  # 传 MA_URL 可直接验收线上 Pages
errors, fails = [], []


def check(name, cond, extra=''):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")
    if not cond:
        fails.append(name)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=['--no-sandbox', '--no-proxy-server', '--proxy-bypass-list=*'])
    ctx = browser.new_context(viewport={'width': 390, 'height': 844})
    page = ctx.new_page()
    page.on('console', lambda m: errors.append(f'console[{m.type}]: {m.text}') if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(f'pageerror: {e}'))

    page.goto(URL, wait_until='load', timeout=30000)
    page.evaluate("() => localStorage.clear()")
    page.reload(wait_until='load')
    time.sleep(0.8)
    # 加速协议内计时器（10x），只影响 wait()
    page.evaluate("() => { window.wait = (ms) => new Promise(r => setTimeout(r, ms / 10)); }")

    # ================= 底部导航 =================
    check('导航-5 个标签', page.locator('#tabbar button').count() == 5)
    check('导航-首页选中', 'sel' in (page.get_attribute('#tabbar button[data-nav="view-home"]', 'class') or ''))
    page.click('#tabbar button[data-nav="view-triage"]')
    time.sleep(0.3)
    check('导航-切到分流', page.is_visible('#view-triage.active'))
    check('导航-分流高亮', 'sel' in (page.get_attribute('#tabbar button[data-nav="view-triage"]', 'class') or ''))
    check('导航-首页不再高亮', 'sel' not in (page.get_attribute('#tabbar button[data-nav="view-home"]', 'class') or ''))

    # ================= 分流器：走「有动作」出口 =================
    check('分流-第 0 步问句', '脑子里在转的是什么' in page.text_content('#tri-stage'))
    page.fill('#tri-text', '我是不是漏看了哪一条笔记')
    page.click('#tri-stage button:has-text("下一步")')
    time.sleep(0.3)
    check('分流-第 1 问', '今天有具体动作可做吗' in page.text_content('#tri-stage'))
    check('分流-只有两个出口(无第三个「分析」)', page.locator('#tri-stage .tri-choice').count() == 2)
    page.locator('#tri-stage .tri-choice').nth(0).click()
    time.sleep(0.3)
    page.fill('#tri-action', '把第 3 章错题重做一遍')
    page.click('#tri-stage button:has-text("加入待办")')
    time.sleep(0.3)
    check('分流-待办完成页', page.is_visible('#tri-stage .tri-done'))
    check('分流-待办文案', '已经变成一条待办' in page.text_content('#tri-stage'))
    check('分流-写入 ma_todos', page.evaluate("() => JSON.parse(localStorage.getItem('ma_todos')||'[]').length") == 1)
    page.screenshot(path=f'{OUT}/v20_triage_todo.png')

    # ================= 分流器：走「没有动作」→ 寄存 =================
    page.evaluate("() => triReset()")
    time.sleep(0.2)
    page.fill('#tri-text', '我刚才那句话是不是让人不高兴了')
    page.click('#tri-stage button:has-text("下一步")')
    time.sleep(0.2)
    page.locator('#tri-stage .tri-choice').nth(1).click()
    time.sleep(0.2)
    check('分流-第 2 问', '最坏结果是什么' in page.text_content('#tri-stage'))
    page.fill('#tri-worst', '可能真的有人因此讨厌我')
    page.click('#tri-stage button:has-text("下一步")')
    time.sleep(0.2)
    check('分流-承担问句', '你能承担吗' in page.text_content('#tri-stage'))
    page.locator('#tri-stage .tri-choice').nth(1).click()
    time.sleep(0.2)
    check('分流-时间盒', '什么时候处理它' in page.text_content('#tri-stage'))
    check('分流-时间盒有硬提示', '到点必须真的去处理' in page.text_content('#tri-stage'))
    page.screenshot(path=f'{OUT}/v21_triage_schedule.png')
    page.click('#tri-stage button:has-text("寄存")')
    time.sleep(0.3)
    check('分流-寄存完成页', '寄存 ≠ 压制' in page.text_content('#tri-stage'))
    check('分流-写入 ma_parked', page.evaluate("() => JSON.parse(localStorage.getItem('ma_parked')||'[]').length") == 1)
    check('分流-写入 ma_triage', page.evaluate("() => JSON.parse(localStorage.getItem('ma_triage')||'[]').length") == 2)

    # ================= 60 秒紧急版 =================
    page.evaluate("() => showView('view-home')")
    time.sleep(0.2)
    page.click('.hero-actions button:has-text("60 秒版")')
    time.sleep(0.3)
    check('60秒-覆盖层打开', page.is_visible('#overlay60.active'))
    check('60秒-第 1 段是停', '停' in page.text_content('#q60-stage'))
    page.wait_for_selector('#q60-body button:has-text("回到题上")', timeout=20000)
    check('60秒-走到第 4 段', '回到题上' in page.text_content('#q60-stage'))
    check('60秒-进度条 100%', page.evaluate("() => document.getElementById('q60-progress').style.width") == '100%')
    check('60秒-有「不是压制」的关键区分', '压制是它不许出现' in page.text_content('#q60-body'))
    page.screenshot(path=f'{OUT}/v22_quick60.png')
    page.click('#q60-body button:has-text("回到题上")')
    time.sleep(0.3)
    check('60秒-可正常关闭', not page.is_visible('#overlay60.active'))

    # ================= 预期练习 =================
    page.click('#tabbar button[data-nav="view-home"]')
    time.sleep(0.2)
    page.click('button:has-text("🎯 预期练习")')
    time.sleep(0.3)
    check('预期-入口说明', '不是「焦虑降下来」' in page.text_content('#exp-stage'))
    page.click('#exp-stage button:has-text("开始一次练习")')
    time.sleep(0.2)
    page.fill('#ex-task', '检查完一遍就不再检查')
    page.fill('#ex-pred', '会漏掉一处错误，最后丢分')
    page.evaluate("() => { EX.conf = 85; document.getElementById('ex-conf-v').innerHTML = '85<small>%</small>'; }")
    page.screenshot(path=f'{OUT}/v23_expect_before.png')
    page.click('#exp-stage button:has-text("去做它")')
    time.sleep(0.2)
    check('预期-第 2 步显示原预测', '会漏掉一处错误' in page.text_content('#exp-stage'))
    page.fill('#ex-actual', '交上去了，没有出错')
    page.evaluate("() => { EX.post = 25; document.getElementById('ex-post-v').innerHTML = '25<small>%</small>'; }")
    page.click('#exp-stage button:has-text("看看结果")')
    time.sleep(0.3)
    check('预期-违反度计算', '违反度 60' in page.text_content('#exp-stage'), page.text_content('#exp-stage')[:60])
    check('预期-并排对照', page.locator('#exp-stage .ev-box').count() == 2)
    check('预期-写入 ma_expect', page.evaluate("() => JSON.parse(localStorage.getItem('ma_expect')||'[]').length") == 1)
    check('预期-存了 conf/post',
          page.evaluate("() => { const c = JSON.parse(localStorage.getItem('ma_expect'))[0]; return c.conf === 85 && c.post === 25; }"))
    page.screenshot(path=f'{OUT}/v24_expect_result.png')
    page.click('#exp-stage button:has-text("完成")')
    time.sleep(0.3)
    check('预期-进入证据库列表', '证据库' in page.text_content('#exp-stage'))

    # ================= 专注舱 =================
    page.click('#tabbar button[data-nav="view-home"]')
    time.sleep(0.2)
    page.click('#tabbar button[data-nav="view-focus"]')
    time.sleep(0.3)
    check('专注-默认 25 分钟', page.evaluate("() => FOC.total") == 1500)
    page.click('#focus-stage button:has-text("15 分钟")')
    time.sleep(0.2)
    check('专注-选 15 分钟', page.evaluate("() => FOC.total") == 900)
    page.click('#focus-btn')
    time.sleep(1.4)
    check('专注-计时在跑', page.evaluate("() => FOC.sec") >= 1)
    check('专注-按钮变暂停', page.text_content('#focus-btn') == '暂停')
    page.evaluate("() => { focusMark(); focusMark(); }")
    time.sleep(0.2)
    check('专注-标记计数', page.evaluate("() => FOC.marks") == 2)
    check('专注-标记未打断计时', page.evaluate("() => FOC.running") is True)
    check('专注-标记提示非扣分', '这不是扣分' in page.text_content('#focus-note'))
    page.screenshot(path=f'{OUT}/v25_focus.png')
    page.evaluate("() => { FOC.sec = FOC.total; finishFocus(); }")
    time.sleep(0.4)
    check('专注-结束报告', '这一轮结束了' in page.text_content('#focus-stage'))
    check('专注-报告不报扣分', '分心次数不是成绩' in page.text_content('#focus-stage'))
    check('专注-写入 ma_focus', page.evaluate("() => JSON.parse(localStorage.getItem('ma_focus')||'[]').length") == 1)

    # ================= 担忧时间 =================
    page.click('#tabbar button[data-nav="view-home"]')
    time.sleep(0.2)
    page.click('button:has-text("🕘 担忧时间")')
    time.sleep(0.3)
    check('担忧-显示寄存的念头', '我刚才那句话' in page.text_content('#worry-stage'))
    check('担忧-显示最坏结果', '可能真的有人因此讨厌我' in page.text_content('#worry-stage'))
    check('担忧-固定时间说明', '担忧时间：' in page.text_content('#worry-stage'))
    page.click('#worry-stage button:has-text("现在开始担忧时间")')
    time.sleep(0.5)
    check('担忧-计时开始', page.is_visible('#worry-clock'))
    check('担忧-允许带着不确定结束', '允许带着不确定结束' in page.text_content('#worry-stage'))
    page.screenshot(path=f'{OUT}/v26_worry_session.png')
    page.click('#worry-stage button:has-text("没答案，时间到了")')
    time.sleep(0.3)
    check('担忧-可标记为未解决结束',
          page.evaluate("() => JSON.parse(localStorage.getItem('ma_parked'))[0].resolved") == 'unresolved')
    page.click('#worry-stage button:has-text("结束这一轮")')
    time.sleep(0.3)
    check('担忧-回到列表', '待处理' in page.text_content('#worry-stage'))
    check('担忧-已处理分组出现', '已处理' in page.text_content('#worry-stage'))

    # ================= 灾难链 =================
    page.click('#tabbar button[data-nav="view-home"]')
    time.sleep(0.2)
    page.click('button:has-text("🔗 灾难链")')
    time.sleep(0.3)
    for s in ['今天专注不了', '考不上公务员', '这辈子就完了']:
        page.fill('#chain-input', s)
        page.click('#chain-stage button:has-text("加一环")')
        time.sleep(0.15)
    check('灾难链-三环', page.locator('#chain-stage .chain-step').count() == 3)
    check('灾难链-只有第 1 环标为可执行', page.locator('#chain-stage .chain-idx.real').count() == 1)
    check('灾难链-其余标为推测', page.locator('#chain-stage .chain-tag.spec').count() == 2)
    check('灾难链-结论只处理第 1 环', '今天要处理的只有第 1 环' in page.text_content('#chain-stage'))
    page.screenshot(path=f'{OUT}/v27_chain.png')
    page.click('#chain-stage button:has-text("存下来")')
    time.sleep(0.3)
    check('灾难链-写入 ma_chains', page.evaluate("() => JSON.parse(localStorage.getItem('ma_chains')||'[]').length") == 1)

    # ================= 压力期模式 =================
    page.click('#tabbar button[data-nav="view-home"]')
    time.sleep(0.3)
    check('首页-无到期项时不显示提醒', page.locator('#home-quick .ddl-bar').count() == 0)
    # 注入一个已到处理时间的念头，首页应出现「去处理」提醒
    page.evaluate("""() => {
      const all = JSON.parse(localStorage.getItem('ma_parked') || '[]');
      all[0].resolved = null; all[0].dueAt = Date.now() - 60000;
      localStorage.setItem('ma_parked', JSON.stringify(all));
      renderHome();
    }""")
    time.sleep(0.3)
    check('首页-到期提醒出现', page.locator('#home-quick .ddl-bar').count() == 1)
    check('首页-到期提醒说明寄存退化成压制', '退化成压制' in page.text_content('#home-quick'))
    page.evaluate("""() => {
      const all = JSON.parse(localStorage.getItem('ma_parked') || '[]');
      all[0].resolved = 'unresolved';
      localStorage.setItem('ma_parked', JSON.stringify(all));
      renderHome();
    }""")
    time.sleep(0.2)
    check('首页-统计条存在', page.locator('#home-stats > div').count() == 3)
    page.screenshot(path=f'{OUT}/v28_home.png')
    page.evaluate("() => toggleDdl()")
    time.sleep(0.3)
    check('压力期-body 类', page.evaluate("() => document.body.classList.contains('ddl')"))
    check('压力期-统计隐藏', page.is_visible('#home-stats >> visible=true') is False)
    check('压力期-提示条出现', '压力期模式' in page.text_content('#home-ddl'))
    check('压力期-主按钮说明改写', '不用离开你的题' in page.text_content('#home-cta-note'))
    page.evaluate("() => showView('view-practice')")
    time.sleep(0.3)
    check('压力期-连续天数隐藏', page.is_visible('#streak-el >> visible=true') is False)
    page.evaluate("() => showView('view-history')")
    time.sleep(0.4)
    check('压力期-历史统计隐藏', page.is_visible('.stat-grid >> visible=true') is False)
    page.screenshot(path=f'{OUT}/v29_ddl.png')
    page.evaluate("() => { toggleDdl(); showView('view-home'); }")
    time.sleep(0.3)
    check('压力期-可关闭', not page.evaluate("() => document.body.classList.contains('ddl')"))
    check('压力期-统计恢复', page.locator('#home-stats > div').count() == 3)

    # ================= 设置页新项 =================
    page.click('#tabbar button[data-nav="view-settings"]')
    time.sleep(0.3)
    check('设置-备考模式卡片', page.is_visible('#v02-settings'))
    check('设置-担忧时间默认 21:00', page.input_value('#in-worrystart') == '21:00')
    check('设置-担忧时长默认 30', page.input_value('#in-worrymin') == '30')
    page.fill('#in-worrystart', '20:30')
    page.dispatch_event('#in-worrystart', 'change')
    time.sleep(0.2)
    check('设置-担忧时间可保存',
          page.evaluate("() => JSON.parse(localStorage.getItem('ma_settings')).worryStart") == '20:30')
    page.screenshot(path=f'{OUT}/v30_settings.png')

    browser.close()

print('\n=== JS ERRORS ===')
for e in errors[:15]:
    print(e)
print(f'\n=== FAILS: {len(fails)} ===')
for f in fails:
    print(' -', f)
print('DONE')
