#!/usr/bin/env bash
# ============================================================
# 锚 MindAnchor — 设备码授权 + 自动上传一体化
# 轮询设备码授权 -> 获取 token -> 自动建仓上传
# ============================================================
set -uo pipefail
cd "$(dirname "$0")/.."

DEVICE_CODE="436975bb5c4005291d3d0d2ac317dd39eb29a404"
INTERVAL=5
CLIENT_ID="178c6fc778ccc68e1d6a"
echo "[upload] 开始轮询设备码授权... (每 ${INTERVAL}s)"

for i in $(seq 1 170); do
  sleep "$INTERVAL"
  POLL=$(curl -sS -X POST -H "Accept: application/json" \
    -d "client_id=${CLIENT_ID}&device_code=${DEVICE_CODE}&grant_type=urn:ietf:params:oauth:grant-type:device_code" \
    https://github.com/login/oauth/access_token 2>/dev/null)
  case "$POLL" in
    *access_token*)
      TOKEN=$(echo "$POLL" | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
      [ -n "${TOKEN:-}" ] || { echo "[upload] token 解析失败: $POLL"; exit 1; }
      echo "[upload] ✅ 授权成功，token 已获取"
      break ;;
    *authorization_pending*) [ $((i % 6)) -eq 0 ] && echo "[upload] 等待授权中... (代码 3CA3-1A62)" ;;
    *slow_down*) INTERVAL=$((INTERVAL + 5)) ;;
    *expired_token*) echo "[upload] ❌ 代码已过期，需重新发起"; exit 1 ;;
    *access_denied*) echo "[upload] ❌ 用户拒绝了授权"; exit 1 ;;
    *) echo "[upload] 轮询响应异常: $POLL" ;;
  esac
  if [ $((i % 6)) -eq 0 ]; then
    echo "[upload] 还剩约 $(( (170 - i) * INTERVAL / 60 )) 分钟窗口"
  fi
done

[ -n "${TOKEN:-}" ] || { echo "[upload] ❌ 超时未授权"; exit 1; }

# 获取用户名
GH_USER=$(curl -sS -H "Authorization: token ${TOKEN}" https://api.github.com/user 2>/dev/null \
  | python -c "import sys,json;print(json.load(sys.stdin)['login'])" 2>/dev/null)
[ -n "${GH_USER:-}" ] || { echo "[upload] ❌ 获取用户名失败"; exit 1; }
echo "[upload] 账号: ${GH_USER}"

# 执行上传（token 通过环境变量传递，避免命令行暴露）
GH_TOKEN="${TOKEN}" bash scripts/upload_github.sh "${GH_USER}" "${TOKEN}"
