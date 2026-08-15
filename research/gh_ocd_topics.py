"""抓取 GitHub topic:ocd 与 topic:ocd-mental-health 页面的仓库列表"""
from playwright.sync_api import sync_playwright
import json, re, time

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
TOPICS = ['ocd', 'ocd-mental-health', 'obsessive-compulsive-disorder', 'ocd-app']
out = {}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1280, 'height': 900})

    for t in TOPICS:
        try:
            page.goto(f'https://github.com/topics/{t}', timeout=30000)
            time.sleep(2.0)
            items = page.eval_on_selector_all(
                'article h3 a[href*="/"]',
                'els => els.map(e => e.getAttribute("href"))'
            )
            descs = page.eval_on_selector_all(
                'article p',
                'els => els.map(e => e.innerText.trim().slice(0,150))'
            )
            stars = page.eval_on_selector_all(
                'article a[href$="/stargazers"]',
                'els => els.map(e => e.innerText.trim())'
            )
            repos = []
            for i, h in enumerate(items):
                if h and h.count('/') == 1:
                    repos.append({
                        'name': h.strip('/'),
                        'desc': descs[i] if i < len(descs) else '',
                        'stars': stars[i] if i < len(stars) else ''
                    })
            out[t] = repos
            print(f'[{t}] {len(repos)} repos')
        except Exception as e:
            out[t] = []
            print(f'[{t}] ERR {str(e)[:120]}')
    browser.close()

with open('C:/Users/25671/ocd_topics.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('SAVED')
