@echo off
rem 锚 MindAnchor 一键启动：起本地服务器并打开浏览器
cd /d %~dp0
start "" /b python -m http.server 8123 --bind 127.0.0.1
timeout /t 1 /nobreak >nul
start "" http://127.0.0.1:8123/index.html
