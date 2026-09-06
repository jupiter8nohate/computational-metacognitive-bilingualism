"""Zero-dependency HTTP reference server for CMB-ADP-1."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .service import agent_card, citation_for, knowledge_graph, recommend, registry, summary_for


class _Handler(BaseHTTPRequestHandler):
    server_version = "CMB-ADP/0.1"

    def _json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store" if status >= 400 else "public, max-age=60")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/v1/agent-card":
                self._json(agent_card()); return
            if parsed.path == "/v1/health":
                self._json({"ok":True,"protocol":"CMB-ADP-1"}); return
            if parsed.path == "/v1/registry":
                self._json(registry()); return
            if parsed.path == "/v1/graph":
                self._json(knowledge_graph()); return
            if parsed.path == "/v1/recommend":
                phrase = query.get("q", [""])[0]
                limit = int(query.get("limit", ["3"])[0])
                self._json({"query":phrase,"results":recommend(phrase, limit=limit)}); return
            if parsed.path == "/v1/citation":
                self._json(citation_for(query.get("id", [""])[0])); return
            if parsed.path == "/v1/summary":
                principle_id = query.get("id", [""])[0]
                level = int(query.get("level", ["0"])[0])
                self._json({"id":principle_id,"level":level,"summary":summary_for(principle_id, level)}); return
            self._json({"error":"not_found"}, status=404)
        except (KeyError, TypeError, ValueError) as exc:
            self._json({"error":str(exc)}, status=400)

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    if not 0 <= port <= 65535:
        raise ValueError("port must be between 0 and 65535")
    server = ThreadingHTTPServer((host, port), _Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
