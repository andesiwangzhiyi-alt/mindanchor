#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""锚 MindAnchor — GitHub 上传（Python 实现，避免 Windows curl 中文编码问题）
步骤: 提取token -> 建仓 -> git push -> topics -> release -> 验证
"""
import json, re, subprocess, sys, urllib.request, urllib.error

# 走 Clash 代理（本机直连被 TLS 指纹拦截，代理已修复可用）
_proxy = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897',
})
urllib.request.install_opener(urllib.request.build_opener(_proxy))

# ---------- 1. 从 git remote 提取 token / 用户名 ----------
remote = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                        capture_output=True, text=True).stdout.strip()
m = re.match(r'https://([^:]+):([^@]+)@github\.com/([^/]+)/(.+)\.git', remote)
if not m:
    print('❌ 无法从 git remote 提取凭据'); sys.exit(1)
USER, TOKEN, REPO = m.group(1), m.group(2), m.group(4)
print(f'账号: {USER}  仓库: {REPO}')

# ---------- API 封装（Python 默认 UTF-8，中文安全） ----------
def api(method, path, data=None):
    req = urllib.request.Request(f'https://api.github.com{path}', method=method)
    req.add_header('Authorization', f'token {TOKEN}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('User-Agent', 'mindanchor-upload')
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, body, timeout=40) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try: err = json.loads(raw)
        except Exception: err = {'message': raw[:200].decode('utf-8', 'replace')}
        return e.code, err

# ---------- 2. 创建公开仓库 ----------
DESC = ('锚 MindAnchor — 思维强迫(OCD)发作时的应急引导PWA: 打断回路/降焦虑/拉回现实。'
        '纯前端,本地存储,离线可用,含每日微训练/暴露阶梯/焦虑回访/AI引导。')
st, d = api('POST', '/user/repos', {
    'name': REPO, 'description': DESC, 'private': False,
    'has_issues': True, 'has_wiki': False,
})
if st in (200, 201):
    print(f'✅ 仓库已创建: {d.get("html_url")}')
elif st == 422 and 'already exists' in str(d.get('message', '')):
    print(f'ℹ️ 仓库已存在，继续推送: {d.get("html_url")}')
else:
    print(f'❌ 建仓失败 [{st}]: {d.get("message")}'); sys.exit(1)

# ---------- 3. git push ----------
print('推送代码...')
r = subprocess.run(['git', 'push', '-u', 'origin', 'main', '--tags'],
                   capture_output=True, text=True)
out = (r.stdout + r.stderr).strip()
print(out[-600:] if out else f'(exit {r.returncode})')
if r.returncode != 0:
    print('❌ push 失败'); sys.exit(1)
print('✅ 代码 + v0.1 tag 已推送')

# ---------- 4. topics ----------
st, d = api('PUT', f'/repos/{USER}/{REPO}/topics', {
    'names': ['ocd', 'mental-health', 'pwa', 'cbt', 'erp',
              'self-help', 'obsessive-compulsive-disorder', 'offline-first']
})
print(f'{"✅" if st == 200 else "❌"} topics: {st} {d.get("names", d.get("message", ""))}')

# ---------- 5. Release v0.1 ----------
st, d = api('POST', f'/repos/{USER}/{REPO}/releases', {
    'tag_name': 'v0.1', 'name': 'v0.1', 'draft': False, 'prerelease': False,
    'body': ('**锚 MindAnchor v0.1** — 思维强迫应急引导 PWA\n\n'
             '- 紧急协议: 中断→呼吸→着陆→寄存(含冲动观察)\n'
             '- SUDS 0-100 量表 + 焦虑证据回访\n'
             '- 每日5分钟微训练 + 暴露阶梯\n'
             '- 7天趋势图 + AI对话引导(可选)\n'
             '- 全本地存储, 离线可用, PWA可安装'),
})
print(f'{"✅" if st in (200, 201) else "❌"} release: {d.get("html_url", d.get("message"))}')

# ---------- 6. 验证 ----------
st, d = api('GET', f'/repos/{USER}/{REPO}')
if st == 200:
    print(f'\n🎉 完成! 仓库地址: https://github.com/{USER}/{REPO}')
    print(f'   stars/forks: {d.get("stargazers_count")}/{d.get("forks_count")}')
    print(f'   默认分支: {d.get("default_branch")}')
else:
    print('⚠️ 验证失败:', d.get('message'))
