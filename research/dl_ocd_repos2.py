"""用 Playwright page.request（Chromium 网络栈）下载 GitHub zip"""
from playwright.sync_api import sync_playwright
import os, time

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
REPOS = {
    'krishna':      'https://codeload.github.com/bchwangk/krishna/zip/refs/heads/main',
    'ocdetour':     'https://codeload.github.com/jsnicholas/OCDetour/zip/refs/heads/main',
    'ocd-practice': 'https://codeload.github.com/caldwellpatrickh/ocd-practice/zip/refs/heads/main',
    'erpmate':      'https://codeload.github.com/spaciouskarter78/ERPMate/zip/refs/heads/main',
}
OUTDIR = 'C:/Users/25671/ocd_repos'
os.makedirs(OUTDIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    # 先探测默认分支
    for name, url in REPOS.items():
        try:
            r = page.request.get(url, timeout=60000)
            print(f'{name}: status={r.status}, len={len(r.body()) if r.ok else 0}')
            if r.ok:
                dest = os.path.join(OUTDIR, f'{name}.zip')
                with open(dest, 'wb') as f:
                    f.write(r.body())
                print(f'  -> saved {os.path.getsize(dest)} bytes')
        except Exception as e:
            print(f'FAIL {name}: {str(e)[:150]}')
        time.sleep(0.8)
    browser.close()
print('DONE')
