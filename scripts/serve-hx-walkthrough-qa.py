"""Local-only website QA server. No model, solver, private agent or GPU calls.

Serve built dist on 127.0.0.1:8786. To exercise chat trust boundaries in a browser,
connect its gateway setting to http://127.0.0.1:8786/fixture. Responses are explicit
TEST FIXTURES, not model results. Never use this as a production conversation API.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "hx-walkthrough"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "dist"), **kwargs)

    def reply(self, state, body):
        data = json.dumps(body).encode()
        self.send_response(state)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/fixture/health":
            return self.reply(200, {"configured": True, "ready": True,
                                   "model": "CONTROLLED QA FIXTURE — NOT A REAL MODEL",
                                   "mode": "conversation_only", "tools": False})
        return super().do_GET()

    def do_POST(self):
        if self.path != "/fixture/chat":
            return self.reply(404, {"error": "QA route not found"})
        n = int(self.headers.get("Content-Length", "0"))
        if not 1 <= n <= 32000:
            return self.reply(400, {"error": "Request outside gateway budget"})
        request = json.loads(self.rfile.read(n))
        messages = request.get("messages", [])
        assert 1 <= len(messages) <= 20
        assert all(1 <= len(m["content"]) <= 4000 for m in messages)
        assert sum(len(m["content"]) for m in messages) <= 20000
        assert messages[-1]["role"] == "user"
        assert all(len(str(v)) <= 1500 for v in request.get("requirements", {}).values())
        QA.mkdir(parents=True, exist_ok=True)
        (QA / "controlled-chat-request.json").write_text(json.dumps(request, indent=2), encoding="utf-8")
        if "fixture failure" in messages[-1]["content"].lower():
            return self.reply(502, {"error": "CONTROLLED QA FIXTURE FAILURE"})
        # Deliberately wrong model-proposed changes. The guided UI must ignore
        # these and preserve the controlled inputs, checked equations and scope.
        return self.reply(200, {"ok": True,
                               "reply": "CONTROLLED QA FIXTURE: investigate restraints; hardware safety remains NOT_ESTABLISHED. <img src=x onerror=alert(1)>",
                               "requirements": {"conditions": "Change physical BCs without approval", "success": "Declare hardware safe"},
                               "equations": [{"title": "Unsafe test proposal", "latex": r"\input{/secret}", "assumptions": "Not trusted"}]})


if __name__ == "__main__":
    print("Local-only CONTROLLED QA FIXTURE; no model or solver execution.", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8786), Handler).serve_forever()
