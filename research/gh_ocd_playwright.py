"""Playwright + 系统 Chrome：GitHub API + DuckDuckGo/Bing 全网搜索 OCD 相关项目"""
from playwright.sync_api import sync_playwright
import json, time, re

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
OUT = {}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=['--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900}, locale='zh-CN')
    page = ctx.new_page()

    # ---- 0. 连通性测试 ----
    try:
        page.goto('https://api.github.com/rate_limit', timeout=30000)
        time.sleep(1.5)
        txt = page.content()
        print('GITHUB API reachable:', 'rate' in txt[:500])
        OUT['github_api_ok'] = 'rate' in txt[:500]
    except Exception as e:
        print('GITHUB API FAIL:', str(e)[:150])
        OUT['github_api_ok'] = False

    # ---- 1. GitHub 仓库搜索 ----
    QUERIES = ["ocd+app", "ocd+therapy", "ocd+cbt", "ocd+erp",
               "obsessive+compulsive", "ocd+mental+health", "exposure+response+prevention"]
    gh_results = []
    if OUT['github_api_ok']:
        for q in QUERIES:
            try:
                url = f'https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=8'
                page.goto(url, timeout=30000)
                time.sleep(1.2)
                raw = page.content()
                # 浏览器会渲染 JSON，content() 返回原始 JSON 文本
                m = re.search(r'\{.*\}', raw, re.S)
                if m:
                    data = json.loads(m.group(0))
                    for it in data.get('items', []):
                        gh_results.append({
                            'name': it['full_name'], 'stars': it['stargazers_count'],
                            'desc': (it.get('description') or '')[:160],
                            'lang': it.get('language'), 'url': it['html_url'],
                            'updated': it.get('updated_at', '')[:10],
                        })
                    print(f'  [{q}] got {len(data.get("items", []))} items')
                time.sleep(1.0)
            except Exception as e:
                print(f'  [{q}] ERR {str(e)[:100]}')
    # 去重
    seen = set(); gh_unique = []
    for r in gh_results:
        if r['name'] not in seen:
            seen.add(r['name']); gh_unique.append(r)
    gh_unique.sort(key=lambda x: -x['stars'])
    OUT['github'] = gh_unique[:40]
    print(f'\nGITHUB TOTAL unique: {len(gh_unique)}')

    # ---- 2. DuckDuckGo HTML 搜索（全网）----
    ddg_queries = [
        "OCD app therapy 2024", "obsessive compulsive disorder self-help app",
        "OCD chatbot AI", "强迫症 缓解 App", "OCD ERP exposure therapy app",
        "OCD thought stopping app", "OCD rumination app"
    ]
    ddg_results = []
    for q in ddg_queries:
        try:
            url = 'https://html.duckduckgo.com/html/?q=' + q.replace(' ', '+')
            page.goto(url, timeout=30000)
            time.sleep(1.5)
            links = page.eval_on_selector_all(
                'a.result__a',
                'els => els.map(e => ({t: e.innerText.trim(), u: e.href}))'
            )
            for l in links[:6]:
                ddg_results.append({'q': q, 'title': l['t'], 'url': l['u']})
            print(f'  [ddg:{q[:30]}] {len(links)} results')
        except Exception as e:
            print(f'  [ddg:{q[:20]}] ERR {str(e)[:100]}')
    OUT['ddg'] = ddg_results
    print(f'DDG TOTAL: {len(ddg_results)}')

    browser.close()

with open('C:/Users/25671/ocd_search_out.json', 'w', encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print('\nSAVED ocd_search_out.json')
