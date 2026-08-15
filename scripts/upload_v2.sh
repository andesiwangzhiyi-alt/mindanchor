#!/usr/bin/env bash
# ============================================================
# 锚 MindAnchor — GitHub 上传 v2（curl + JSON 文件，解决中文编码与 TLS 指纹问题）
# 步骤: 提取token -> 建仓 -> git push -> topics -> release -> 验证
# ============================================================
set -uo pipefail
cd "$(dirname "$0")/.."

REMOTE=$(git remote get-url origin)
TOKEN=$(echo "$REMOTE" | sed -E 's|https://[^:]+:([^@]+)@.*|\1|')
GH_USER=$(echo "$REMOTE" | sed -E 's|https://([^:]+):.*|\1|')
REPO="mindanchor"
API="https://api.github.com"
AUTH="Authorization: token ${TOKEN}"
TMP="_api_req.json"

echo "账号: ${GH_USER}  仓库: ${REPO}"

# ---- 1. 创建公开仓库（JSON 写入文件，UTF-8 安全）----
python - <<'PYEOF'
import json
d = {
    "name": "mindanchor",
    "description": "锚 MindAnchor — 思维强迫(OCD)发作时的应急引导PWA: 打断回路/降焦虑/拉回现实。纯前端,本地存储,离线可用,含每日微训练/暴露阶梯/焦虑回访/AI引导。",
    "private": False, "has_issues": True, "has_wiki": False
}
open('_api_req.json', 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False))
PYEOF
RESP=$(curl -sS -X POST -H "$AUTH" -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json; charset=utf-8" --data @"${TMP}" "${API}/user/repos")
echo "$RESP" | python -c "import sys,json;d=json.load(sys.stdin);print('建仓:', d.get('html_url') or d.get('message'))" || { echo "建仓失败: $RESP"; exit 1; }

# ---- 2. git push ----
echo "推送代码..."
PUSH_OUT=$(git push -u origin main --tags 2>&1)
echo "$PUSH_OUT" | tail -4
echo "$PUSH_OUT" | grep -q "rejected\|error\|fatal" && { echo "❌ push 失败"; exit 1; }
echo "✅ 代码 + v0.1 tag 已推送"

# ---- 3. topics ----
python - <<'PYEOF'
import json
open('_api_req.json','w',encoding='utf-8').write(json.dumps({
    "names": ["ocd","mental-health","pwa","cbt","erp","self-help","obsessive-compulsive-disorder","offline-first"]
}))
PYEOF
curl -sS -X PUT -H "$AUTH" -H "Accept: application/vnd.github.mercy-preview+json" \
  -H "Content-Type: application/json; charset=utf-8" --data @"${TMP}" \
  "${API}/repos/${GH_USER}/${REPO}/topics" -o /dev/null -w "topics: HTTP %{http_code}\n"

# ---- 4. Release v0.1 ----
python - <<'PYEOF'
import json
body = ("**锚 MindAnchor v0.1** — 思维强迫应急引导 PWA\n\n"
        "- 紧急协议: 中断→呼吸→着陆→寄存(含冲动观察)\n"
        "- SUDS 0-100 量表 + 焦虑证据回访\n"
        "- 每日5分钟微训练 + 暴露阶梯\n"
        "- 7天趋势图 + AI对话引导(可选)\n"
        "- 全本地存储, 离线可用, PWA可安装")
open('_api_req.json','w',encoding='utf-8').write(json.dumps({
    "tag_name":"v0.1","name":"v0.1","draft":False,"prerelease":False,"body":body
}, ensure_ascii=False))
PYEOF
curl -sS -X POST -H "$AUTH" -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json; charset=utf-8" --data @"${TMP}" \
  "${API}/repos/${GH_USER}/${REPO}/releases" \
  | python -c "import sys,json;d=json.load(sys.stdin);print('release:', d.get('html_url') or d.get('message'))"

# ---- 5. 验证 ----
curl -sS -H "$AUTH" "${API}/repos/${GH_USER}/${REPO}" \
  | python -c "import sys,json;d=json.load(sys.stdin);print(f'✅ 仓库: https://github.com/{d[\"full_name\"]} | 分支: {d[\"default_branch\"]} | 可见性: {\"public\" if not d[\"private\"] else \"private\"}')"

rm -f "${TMP}"
echo "🎉 全部完成"
