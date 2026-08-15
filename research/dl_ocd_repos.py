"""用 Playwright 驱动 Chrome 下载 GitHub 仓库 zip 包（绕过直连封锁）"""
from playwright.sync_api import sync_playwright
import os, time

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
REPOS = {
    'krishna':      'https://github.com/bchwangk/krishna/archive/refs/heads/main.zip',
    'ocdetour':     'https://github.com/jsnicholas/OCDetour/archive/refs/heads/main.zip',
    'ocd-practice': 'https://github.com/caldwellpatrickh/ocd-practice/archive/refs/heads/main.zip',
    'erpmate':      'https://github.com/spaciouskarter78/ERPMate/archive/refs/heads/main.zip',
}
OUTDIR = 'C:/Users/25671/ocd_repos'
os.makedirs(OUTDIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=['--no-sandbox'])
    ctx = browser.new_context(accept_downloads=True)
    page = ctx.new_page()
    for name, url in REPOS.items():
        try:
            with page.expect_download(timeout=60000) as dl_info:
                try:
                    page.goto(url, timeout=30000)
                except Exception:
                    pass  # 导航到 zip 会抛 "Download is starting"，下载事件仍会触发
            dl = dl_info.value
            dest = os.path.join(OUTDIR, f'{name}.zip')
            dl.save_as(dest)
            print(f'OK {name}: {os.path.getsize(dest)} bytes')
        except Exception as e:
            print(f'FAIL {name}: {str(e)[:120]}')
        time.sleep(0.8)
    browser.close()
print('DONE')
