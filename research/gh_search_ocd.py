"""GitHub API 搜索 OCD 相关项目（走 Clash 代理，httpx）"""
import httpx, json, time

PROXY = "http://127.0.0.1:7897"
QUERIES = [
    "ocd app", "ocd therapy", "obsessive compulsive disorder",
    "ocd cbt", "ocd erp", "exposure response prevention",
    "ocd chatbot", "mental health ocd", "强迫症",
]

def search(q):
    try:
        r = httpx.get(
            "https://api.github.com/search/repositories",
            params={"q": q, "sort": "stars", "order": "desc", "per_page": 8},
            headers={"Accept": "application/vnd.github+json", "User-Agent": "research-script"},
            proxy=PROXY, timeout=25,
        )
        if r.status_code != 200:
            return f"[{r.status_code}] {r.text[:120]}"
        items = r.json().get("items", [])
        out = []
        for it in items:
            out.append({
                "name": it["full_name"],
                "stars": it["stargazers_count"],
                "desc": (it.get("description") or "")[:140],
                "lang": it.get("language"),
                "url": it["html_url"],
                "updated": it.get("updated_at", "")[:10],
            })
        return out
    except Exception as e:
        return f"[ERR] {e}"

for q in QUERIES:
    print(f"\n===== QUERY: {q} =====")
    res = search(q)
    if isinstance(res, str):
        print(res)
    else:
        for it in res:
            print(f"★{it['stars']:>5} {it['name']:<45} [{it['lang']}] {it['updated']}")
            print(f"        {it['desc']}")
    time.sleep(1.5)
