"""Conformal Canvas 本地代理:托管 Web 界面 + 转发 API 到 C++ 服务。

解决浏览器跨域(CORS)问题:
- 通过本代理访问 http://127.0.0.1:8000 时,页面与 API 同源,浏览器不会做跨域拦截
- 直接从 file:// 打开 index.html 时,请求本代理也会附加 CORS 响应头,同样可用

用法:
    python proxy.py                 # 默认 8000 端口,转发到 127.0.0.1:7854
    python proxy.py 8080            # 自定义端口
    PORT=9000 TARGET=http://192.168.1.5:7854 python proxy.py

先启动 conformal_canvas 服务,再运行本代理,浏览器打开 http://127.0.0.1:8000 即可。
"""

import http.server
import os
import socketserver
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else "8000"))
TARGET = os.environ.get("TARGET", "http://127.0.0.1:7854")

PROXY_PATHS = ("/handle_escher_image", "/handle_conformal_image")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self.path = "/index.html"
        super().do_GET()

    def _proxy(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        req = urllib.request.Request(
            TARGET + self.path,
            data=body,
            method="POST",
            headers={"Content-Type": self.headers.get("Content-Type", "application/octet-stream")},
        )
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/octet-stream"))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "text/plain"))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            sys.stderr.write("proxy error: %r\n" % e)
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            msg = ("无法连接到 C++ 服务 %s\n请先启动 conformal_canvas" % TARGET).encode("utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

    def do_POST(self):
        try:
            self._proxy()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            msg = ("代理内部错误: %r" % e).encode("utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))


if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
        print("Conformal Canvas Web UI: http://127.0.0.1:%d" % PORT)
        print("Forwarding API to: %s" % TARGET)
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
