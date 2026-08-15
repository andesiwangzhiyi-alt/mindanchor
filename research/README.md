# 调研材料（research/）

本目录是「锚」开发前的 OCD 数字干预调研过程产物，用于复现调研结果。

> ⚠️ 本机网络环境特殊（GitHub 直连被墙、curl TLS 被拦截），因此调研脚本使用
> **Playwright 驱动系统 Chrome** 访问 GitHub（走系统代理），这是本环境验证过的可靠方案。
> 在普通网络环境下，直接 curl/wget 即可，无需这些脚本。

## 脚本说明

| 文件 | 用途 |
|---|---|
| `gh_search_ocd.py` | （第一版尝试）httpx 走 Clash 代理搜 GitHub API——因代理 TLS 失败弃用 |
| `gh_ocd_playwright.py` | Playwright 驱动 Chrome 搜 GitHub API（9 组关键词）+ DuckDuckGo HTML 搜索 |
| `gh_ocd_topics.py` | 抓取 GitHub topic 页面（ocd / ocd-mental-health / obsessive-compulsive-disorder / ocd-app） |
| `gh_ocd_details.py` | 抓取重点仓库详情（stars/描述/语言/更新时间，API 逐仓库） |
| `dl_ocd_repos.py` | 第一版仓库下载（expect_download 方案，失败——codeload 下载事件不触发） |
| `dl_ocd_repos2.py` | 最终方案：Playwright `page.request`（Chromium 网络栈）直接取 zip 字节，成功 |

## 数据文件

| 文件 | 内容 |
|---|---|
| `ocd_search_out.json` | GitHub API 搜索 45 个仓库原始结果 |
| `ocd_topics.json` | GitHub topic 页面抓取结果 |
| `ocd_repo_details.json` | 重点仓库详情 |

## 复现步骤（普通网络）

```bash
# 1. GitHub API 搜索
curl -s "https://api.github.com/search/repositories?q=ocd+therapy&sort=stars" | jq '.items[] | {name, stars, description}'

# 2. 下载参考仓库
git clone https://github.com/bchwangk/krishna
git clone https://github.com/jsnicholas/OCDetour
git clone https://github.com/caldwellpatrickh/ocd-practice
git clone https://github.com/spaciouskarter78/ERPMate
```

调研结论与项目分析见 `docs/调研报告-OCD数字干预.md` 与 `docs/开源项目源码分析.md`。
