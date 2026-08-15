#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""锚 MindAnchor — GitHub 上传（Playwright Chrome 网络栈，绕过 TLS 指纹封锁）
用 page.request（Chromium 网络栈，走 Chrome 的代理链路）调 GitHub REST API：
建仓 -> 逐文件上传(Contents API) -> topics -> release -> 验证
"""
import json, base64, os, re, subprocess, sys
from playwright.sync_api import sync_playwright

# ---------- 提取 token / 用户名 ----------
remote = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                        capture_output=True, text=True).stdout.strip()
m = re.match(r'https://([^:]+):([^@]+)@github\.com/([^/]+)/(.+)\.git', remote)
if not m:
    print('❌ 无法从 git remote 提取凭据'); sys.exit(1)
USER, TOKEN, REPO = m.group(1), m.group(2), m.group(4)
print(f'账号: {USER}  仓库: {REPO}')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH = f'token {TOKEN}'
API = 'https://api.github.com'

def api(page, method, path, data=None):
    kwargs = dict(headers={'Authorization': AUTH, 'Accept': 'application/vnd.github+json',
                           'User-Agent': 'mindanchor-upload'})
    if data is not None:
        kwargs['data'] = json.dumps(data)
        kwargs['headers']['Content-Type'] = 'application/json'
    fn = getattr(page.request, method.lower())  # post / put / get / patch / delete
    r = fn(f'{API}{path}', timeout=60000, **kwargs)
    try:
        body = r.json() if r.text() else {}
    except Exception:
        body = {'raw': r.text()[:200]}
    return r.status, body

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        headless=True, args=['--no-sandbox'])
    page = browser.new_page()

    # ---------- 1. 创建公开仓库 ----------
    st, d = api(page, 'POST', '/user/repos', {
        'name': REPO,
        'description': '锚 MindAnchor — 思维强迫(OCD)发作时的应急引导PWA: 打断回路/降焦虑/拉回现实。纯前端,本地存储,离线可用,含每日微训练/暴露阶梯/焦虑回访/AI引导。',
        'private': False, 'has_issues': True, 'has_wiki': False,
    })
    if st in (200, 201):
        print(f'✅ 建仓: {d.get("html_url")}')
    elif st == 422 and 'already exists' in str(d.get('message', '')):
        print(f'ℹ️ 仓库已存在: https://github.com/{USER}/{REPO}')
    else:
        print(f'❌ 建仓失败 [{st}]: {d.get("message")}'); sys.exit(1)

    # ---------- 2. 逐文件上传（Contents API） ----------
    EXCLUDE_DIRS = ('.git', 'ocd_repos', 'test_shots', '__pycache__')
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [x for x in dirnames if x not in EXCLUDE_DIRS]
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, ROOT).replace('\\', '/')
            if rel == 'scripts/upload_v2.sh':  # 不上传失败的中间脚本
                continue
            files.append((rel, fp))
    files.sort()

    print(f'共 {len(files)} 个文件，开始上传...')
    ok, fail = 0, []
    for rel, fp in files:
        with open(fp, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
        st, d = api(page, 'PUT', f'/repos/{USER}/{REPO}/contents/{rel}', {
            'message': f'Add {rel}',
            'content': content,
            'branch': 'main',
        })
        if st in (200, 201):
            ok += 1
        else:
            fail.append((rel, st, d.get('message', d.get('raw', ''))[:100]))
        print(f'  [{ok+fail.__len__()}/{len(files)}] {"✅" if st in (200,201) else "❌"} {rel}')

    if fail:
        print(f'\n⚠️ {len(fail)} 个文件失败:')
        for f_ in fail: print('   ', f_)
    else:
        print(f'\n✅ 全部 {ok} 个文件上传完成')

    # ---------- 3. topics ----------
    st, d = api(page, 'PUT', f'/repos/{USER}/{REPO}/topics', {
        'names': ['ocd', 'mental-health', 'pwa', 'cbt', 'erp',
                  'self-help', 'obsessive-compulsive-disorder', 'offline-first']
    })
    print(f'{"✅" if st == 200 else "❌"} topics: {st}')

    # ---------- 4. Release v0.1 ----------
    st, d = api(page, 'POST', f'/repos/{USER}/{REPO}/releases', {
        'tag_name': 'v0.1', 'name': 'v0.1', 'draft': False, 'prerelease': False,
        'body': ('**锚 MindAnchor v0.1** — 思维强迫应急引导 PWA\n\n'
                 '- 紧急协议: 中断→呼吸→着陆→寄存(含冲动观察)\n'
                 '- SUDS 0-100 量表 + 焦虑证据回访\n'
                 '- 每日5分钟微训练 + 暴露阶梯\n'
                 '- 7天趋势图 + AI对话引导(可选)\n'
                 '- 全本地存储, 离线可用, PWA可安装'),
    })
    print(f'{"✅" if st in (200, 201) else "❌"} release: {d.get("html_url", d.get("message"))}')

    # ---------- 5. 验证 ----------
    st, d = api(page, 'GET', f'/repos/{USER}/{REPO}')
    if st == 200:
        print(f'\n🎉 完成! https://github.com/{USER}/{REPO}  (分支: {d.get("default_branch")})')
    else:
        print('⚠️ 验证失败:', d.get('message'))
    browser.close()
