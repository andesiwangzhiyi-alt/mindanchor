"""抓取重点 OCD 仓库详情"""
from playwright.sync_api import sync_playwright
import json, re, time

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
REPOS = [
    "bchwangk/krishna", "jsnicholas/OCDetour", "pushpakcodes/MindEase_OCD_Tracker_and_AI_Companion",
    "EishaRathore/CureOCD", "spaciouskarter78/ERPMate", "Personalized-Neuromodulation/tDCS_ERP_OCD",
    "womenhackfornonprofits/ocdaction", "IT21219498/MindSculptor_Website", "nkranendonk/ocdtherapy",
    "wondernoodle09/ocdapp", "Hac254/cbt-therapy-ocd-tool", "caldwellpatrickh/ocd-practice",
    "xemura/ocd-simulator", "feline-felicity/ocd-helper", "BIDMCDigitalPsychiatry/LAMP-Mobile",
    "BIDMCDigitalPsychiatry/LAMP-platform", "ChildMindInstitute/MindLogger",
]
out = {}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    for repo in REPOS:
        try:
            page.goto(f'https://api.github.com/repos/{repo}', timeout=25000)
            time.sleep(0.8)
            raw = page.content()
            m = re.search(r'\{.*\}', raw, re.S)
            if not m:
                print(f'[skip] {repo}: no json')
                continue
            d = json.loads(m.group(0))
            out[repo] = {
                'stars': d.get('stargazers_count'),
                'desc': (d.get('description') or '')[:180],
                'lang': d.get('language'),
                'updated': d.get('updated_at', '')[:10],
                'created': d.get('created_at', '')[:10],
                'topics': (d.get('topics') or [])[:8],
            }
            print(f'★{out[repo]["stars"]:<5} {repo:<55} [{out[repo]["lang"]}] {out[repo]["updated"]}')
            print(f'        {out[repo]["desc"]}')
        except Exception as e:
            print(f'[ERR] {repo}: {str(e)[:80]}')
    browser.close()

with open('C:/Users/25671/ocd_repo_details.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('SAVED')
