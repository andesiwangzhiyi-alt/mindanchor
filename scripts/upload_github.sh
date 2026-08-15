#!/usr/bin/env bash
# ============================================================
# 锚 MindAnchor — GitHub 一键上传脚本
# 用法: bash scripts/upload_github.sh <用户名> <token>
# 功能: 创建公开仓库 -> 推送代码+tag -> 设置topics -> 创建v0.1 Release
# ============================================================
set -euo pipefail

GH_USER="$1"
GH_TOKEN="$2"
REPO_NAME="mindanchor"
REPO_DESC="锚 MindAnchor — 思维强迫(OCD)发作时的应急引导PWA: 打断回路/降焦虑/拉回现实。纯前端,本地存储,离线可用,含每日微训练/暴露阶梯/焦虑回访/AI引导。"

AUTH="Authorization: token ${GH_TOKEN}"

echo "==> 1/5 创建公开仓库 ${GH_USER}/${REPO_NAME}"
curl -sS -X POST -H "$AUTH" -H "Accept: application/vnd.github+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"${REPO_NAME}\",\"description\":\"${REPO_DESC}\",\"private\":false,\"has_issues\":true,\"has_wiki\":false}" \
  | python -c "import sys,json;d=json.load(sys.stdin);print('   created:',d.get('html_url') or d.get('message'))"

echo "==> 2/5 设置 git remote"
git remote remove origin 2>/dev/null || true
git remote add origin "https://${GH_USER}:${GH_TOKEN}@github.com/${GH_USER}/${REPO_NAME}.git"
git fetch origin 2>/dev/null || true

echo "==> 3/5 推送 main 分支 + v0.1 tag"
git push -u origin main --tags 2>&1 | tail -3

echo "==> 4/5 设置 topics"
curl -sS -X PUT -H "$AUTH" -H "Accept: application/vnd.github.mercy-preview+json" \
  https://api.github.com/repos/${GH_USER}/${REPO_NAME}/topics \
  -d '{"names":["ocd","mental-health","pwa","cbt","erp","self-help","obsessive-compulsive-disorder","offline-first"]}' \
  -o /dev/null -w "   topics: %{http_code}\n"

echo "==> 5/5 创建 v0.1 Release"
curl -sS -X POST -H "$AUTH" -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/${GH_USER}/${REPO_NAME}/releases \
  -d '{"tag_name":"v0.1","name":"v0.1","body":"**锚 MindAnchor v0.1** — 思维强迫应急引导 PWA\n\n- 紧急协议: 中断→呼吸→着陆→寄存(含冲动观察)\n- SUDS 0-100 量表 + 焦虑证据回访\n- 每日5分钟微训练 + 暴露阶梯\n- 7天趋势图 + AI对话引导(可选)\n- 全本地存储, 离线可用, PWA可安装","draft":false,"prerelease":false}' \
  | python -c "import sys,json;d=json.load(sys.stdin);print('   release:',d.get('html_url') or d.get('message'))"

echo "==> 完成! 仓库地址: https://github.com/${GH_USER}/${REPO_NAME}"
