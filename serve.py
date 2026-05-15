"""SPA static file server with fallback to index.html"""
import http.server
import socketserver
import os
import sys

DIST_DIR = "/root/projects/art-design-pro/dist"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3006

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def do_GET(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) and '.' not in os.path.basename(self.path):
            self.path = '/index.html'
        return super().do_GET()

    def log_message(self, format, *args):
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

with ReusableTCPServer(("0.0.0.0", PORT), SPAHandler) as httpd:
    print(f"Serving {DIST_DIR} on port {PORT}", flush=True)
    httpd.serve_forever()
