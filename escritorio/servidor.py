#!/usr/bin/env python3
"""Servidor do painel ao vivo.  python3 escritorio/servidor.py [porta]  →  http://localhost:8787"""
import json, os, sys, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

DIR = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(DIR, "estado.json")
PAINEL = os.path.join(DIR, "painel.html")


def ler():
    try:
        with open(ESTADO, "rb") as f:
            return f.read()
    except OSError:
        return b'{"versao":0,"agentes":{},"tarefas":[],"eventos":[],"tokens":{"economizados":0}}'


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _envia(self, corpo, tipo):
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"):
            with open(PAINEL, "rb") as f:
                return self._envia(f.read(), "text/html; charset=utf-8")
        if p == "/estado":
            return self._envia(ler(), "application/json")
        if p == "/eventos":  # Server-Sent Events: empurra o estado a cada mudança
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            ult, beat = None, time.time()
            try:
                while True:
                    try:
                        m = os.path.getmtime(ESTADO)
                    except OSError:
                        m = 0
                    if m != ult:
                        ult = m
                        self.wfile.write(b"data: " + ler().replace(b"\n", b"") + b"\n\n")
                        self.wfile.flush()
                    elif time.time() - beat > 15:
                        beat = time.time()
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
                    time.sleep(0.25)
            except (BrokenPipeError, ConnectionResetError):
                return
        self.send_error(404)


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    print(f"Escritório ao vivo em http://localhost:{porta}  (Ctrl+C para sair)")
    ThreadingHTTPServer(("127.0.0.1", porta), H).serve_forever()
