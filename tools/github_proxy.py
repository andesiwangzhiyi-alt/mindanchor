#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""github_proxy.py — 本机 DNS 被劫持时，给 git/curl 用的最小解析型代理。

背景（本机实测 2026-11）：
  * 校园网 DNS 把 github.com / api.github.com 解析到 121.251.192.8（黑洞 IP）→ git 报
    "schannel: failed to receive handshake, SSL/TLS connection failed"
  * 但 GitHub 的**真实 IP 是通的**（20.205.243.166:443、140.82.112.6:443 TCP 可连）
  * 公网 UDP 53 也被劫持（nslookup github.com 8.8.8.8 无应答），但 **DoH 可用**：
    https://doh.pub/dns-query?name=github.com&type=A → 140.82.112.4

所以：跑一个只做「CONNECT 时用 DoH 解析、其余原样转发」的本地代理，让 git 自己
发 CONNECT github.com:443，DNS 由代理侧解决，git 不需要解析。

用法：
    python tools/github_proxy.py                # 默认 127.0.0.1:8899，前台运行
    python tools/github_proxy.py --port 8899 --daemon   # 后台线程，随进程退出

    # 另开一个终端（本机环境变量里不要有 HTTPS_PROXY 指向死掉的 Clash 节点）
    git -c http.proxy=http://127.0.0.1:8899 -c http.schannelCheckRevoke=false push origin main

注意：只代理 CONNECT，不做缓存/改写；用完关掉即可。
"""
import argparse
import json
import socket
import socketserver
import sys
import threading
import time
import urllib.request

DOH = "https://doh.pub/dns-query"

# DoH 有时只返回被墙的那几个 IP（GitHub 的 IP 池里只有部分段可达）。
# 这里补一份已知可用的兜底地址，DoH 结果全部连不上时逐个试。
EXTRA_IPS = {
    "github.com": ["140.82.112.3", "140.82.112.4", "140.82.113.3", "140.82.113.4",
                   "140.82.114.3", "140.82.114.4", "140.82.116.3", "140.82.116.4",
                   "140.82.121.3", "140.82.121.4", "20.205.243.166", "20.27.177.113",
                   "20.200.245.247", "20.233.83.145"],
    "api.github.com": ["140.82.112.6", "140.82.113.6", "140.82.114.6", "140.82.116.6",
                       "140.82.121.6", "20.205.243.168", "20.27.177.116", "20.200.245.245"],
    "codeload.github.com": ["140.82.112.9", "140.82.112.10", "140.82.113.9", "20.205.243.165"],
    "raw.githubusercontent.com": ["185.199.108.133", "185.199.109.133", "185.199.110.133", "185.199.111.133"],
    "objects.githubusercontent.com": ["185.199.108.133", "185.199.109.133", "185.199.110.133", "185.199.111.133"],
    "github.githubassets.com": ["185.199.108.154", "185.199.109.154", "185.199.110.154"],
}
_cache = {}
_good = {}
_lock = threading.Lock()
BUFSIZE = 65536


def resolve_all(host):
    """DoH 解析全部 A 记录，带 5 分钟缓存。host 已经是 IP 时直接返回。"""
    try:
        socket.inet_aton(host)
        return [host]
    except OSError:
        pass
    now = time.time()
    with _lock:
        hit = _cache.get(host)
        if hit and now - hit[1] < 300:
            return hit[0]
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    opener.addheaders = [("accept", "application/dns-json")]
    with opener.open(f"{DOH}?name={host}&type=A", timeout=10) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    ips = [a["data"] for a in data.get("Answer", []) if a.get("type") == 1]
    if not ips:
        raise OSError("no A record for " + host)
    # 上次连通的 IP 排到最前（GitHub 的 IP 池里有的段被墙、有的通）
    good = _good.get(host)
    if good and good in ips:
        ips = [good] + [i for i in ips if i != good]
    for ip in EXTRA_IPS.get(host, []):
        if ip not in ips:
            ips.append(ip)
    with _lock:
        _cache[host] = (ips, now)
    return ips


def connect_host(host, port, timeout=6):
    """按 DoH 给出的 IP 逐个尝试；连通后记住这个 IP 供下次优先使用。"""
    last = None
    for ip in resolve_all(host):
        try:
            s = socket.create_connection((ip, port), timeout=timeout)
            _good[host] = ip
            return s
        except OSError as e:  # noqa: PERF203
            last = e
    raise OSError(f"no reachable IP for {host}:{port} ({last})")


def pump(src, dst):
    try:
        while True:
            chunk = src.recv(BUFSIZE)
            if not chunk:
                break
            dst.sendall(chunk)
    except OSError:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(30)
        try:
            head = b""
            while b"\r\n\r\n" not in head and len(head) < 16384:
                chunk = self.request.recv(4096)
                if not chunk:
                    return
                head += chunk
        except OSError:
            return
        if not head:
            return
        first = head.split(b"\r\n", 1)[0].decode("latin-1")
        parts = first.split()
        if len(parts) < 2:
            return
        method, target = parts[0].upper(), parts[1]

        if method == "CONNECT":
            host, _, port = target.partition(":")
            port = int(port or 443)
            try:
                upstream = connect_host(host, port)
            except Exception as e:  # noqa: BLE001
                sys.stderr.write(f"[github_proxy] CONNECT {target} 失败: {e}\n")
                try:
                    self.request.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                except OSError:
                    pass
                return
            self.request.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            t = threading.Thread(target=pump, args=(self.request, upstream), daemon=True)
            t.start()
            pump(upstream, self.request)
            t.join(timeout=5)
            return

        # 普通 HTTP：绝对 URI 形式，直接转发
        try:
            from urllib.parse import urlsplit
            u = urlsplit(target if "://" in target else "http://" + target)
            upstream = connect_host(u.hostname, u.port or 80)
            path = u.path or "/"
            if u.query:
                path += "?" + u.query
            rest = head.split(b"\r\n", 1)[1]
            upstream.sendall(f"{method} {path} HTTP/1.1\r\n".encode() + rest)
            pump(upstream, self.request)
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[github_proxy] {method} {target} 失败: {e}\n")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--daemon", action="store_true", help="后台线程运行（不阻塞调用方）")
    a = ap.parse_args()
    srv = Server((a.host, a.port), Handler)
    print(f"github_proxy 监听 http://{a.host}:{a.port}  (DoH: {DOH})")
    if a.daemon:
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        return srv
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n退出")


if __name__ == "__main__":
    main()
