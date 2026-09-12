"""Public numeric study broker. No Docker access, model access, or private services."""
import ipaddress
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from core import BOUNDS, DEFAULTS, REVISION, atomic_json, brief, digest, validate

DATA = Path(os.getenv("AERO_STUDY_DATA", "/data"))
ORIGINS = set(os.getenv("AERO_STUDY_ORIGINS", "https://alex-blythe.com,https://www.alex-blythe.com").split(","))
LOCK = threading.Lock()


def worker_ready():
    try:
        data = json.loads((DATA / "worker.json").read_text())
        return data.get("ready") is True and time.time() - data["time"] < 15
    except (OSError, ValueError, KeyError):
        return False


def enqueue(ip, key, inputs):
    if not isinstance(key, str) or not re.fullmatch(r"[a-f0-9-]{36}", key):
        raise ValueError("A request UUID is required")
    values = validate(inputs)
    with LOCK, closing(sqlite3.connect(DATA / "quota.sqlite")) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, ip TEXT, request_key TEXT, created REAL, inputs TEXT)")
        canonical = json.dumps(values, sort_keys=True)
        previous = db.execute("SELECT id,inputs FROM runs WHERE ip=? AND request_key=?", (ip, key)).fetchone()
        if previous:
            if previous[1] != canonical:
                raise ValueError("This request UUID was already used with different inputs")
            return previous[0]
        now = time.time()
        db.execute("DELETE FROM runs WHERE created < ?", (now - 48 * 3600,))
        ip_count = db.execute("SELECT COUNT(*) FROM runs WHERE ip=? AND created>?", (ip, now-3600)).fetchone()[0]
        global_count = db.execute("SELECT COUNT(*) FROM runs WHERE created>?", (now-3600,)).fetchone()[0]
        if ip_count >= 2 or global_count >= 6:
            raise OverflowError("Study budget reached. Two studies per visitor and six total per hour; retry later.")
        active = 0
        retained = 0
        for folder in DATA.iterdir():
            if folder.is_dir() and (folder / "status.json").exists():
                retained += 1
                state = json.loads((folder / "status.json").read_text())
                active += state["state"] in ("queued", "running")
        if active >= 3 or retained >= 24:
            raise OverflowError("The study queue or retained evidence store is full. Try again later.")
        if not worker_ready():
            raise ConnectionError("The solver worker is offline; your study brief remains available.")
        job_id = secrets.token_hex(24)
        folder = DATA / job_id
        folder.mkdir()
        atomic_json(folder / "input.json", values)
        db.execute("INSERT INTO runs VALUES (?,?,?,?,?)", (job_id, ip, key, now, canonical))
        atomic_json(folder / "status.json", {"id": job_id, "state": "queued", "message": "Queued for the next available solver slot",
                    "completed": 0, "total": 9, "progress": 0, "updated_at": now})
        return job_id


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def setup(self):
        super().setup()
        self.connection.settimeout(12)

    def headers_for(self, code, kind, size):
        self.send_response(code)
        origin = self.headers.get("Origin")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(size))
        if code == 429:
            self.send_header("Retry-After", "300")

    def send(self, code, data):
        body = json.dumps(data, allow_nan=False).encode()
        self.headers_for(code, "application/json", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if self.headers.get("Origin") not in ORIGINS:
            return self.send(403, {"error": "Origin not allowed"})
        self.headers_for(204, "application/json", 0)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/study/health":
            return self.send(200, {"ready": worker_ready(), "revision": REVISION, "defaults": DEFAULTS, "bounds": BOUNDS,
                                   "retention_hours": 48, "max_seconds": 390, "report_max_seconds":90, "solves_per_study": 9})
        match = re.fullmatch(r"/study/runs/([a-f0-9]{48})(?:/(result|evidence|failure|report|paper))?", path)
        if not match:
            return self.send(404, {"error": "Not found"})
        folder = DATA / match[1]
        try:
            status = json.loads((folder / "status.json").read_text())
        except (OSError, ValueError):
            return self.send(404, {"error": "Run not found or evidence expired after 48 hours"})
        artifact = match[2]
        if artifact=='paper' and status['state']=='complete':
            file=folder/'paper.pdf'
            if not file.exists():return self.send(404,{'error':'This older run predates automatic PDF papers; start a fresh study.'})
            if digest(file)!=status.get('paper_sha256'):return self.send(409,{'error':'PDF integrity check failed'})
            body=file.read_bytes();self.headers_for(200,'application/pdf',len(body))
            self.send_header('Content-Disposition','inline; filename="aero-channel-study.pdf"');self.end_headers();self.wfile.write(body);return
        if not artifact:
            if status["state"] in ("queued", "running") and not worker_ready():
                status = {**status, "message": "Worker unavailable; progress has paused", "worker_offline": True}
            elif status['state']=='running' and time.time()-status['updated_at']>90:
                status = {**status, 'message':'No progress for more than 90 seconds. The run needs operator review; it is not being called complete.', 'stalled':True}
            return self.send(200, status)
        if artifact == "result" and status["state"] == "complete":
            if not (folder / "result.json").exists() or digest(folder / "result.json") != status["result_sha256"]:
                return self.send(409, {"error": "Result integrity check failed"})
            return self.send(200, json.loads((folder / "result.json").read_text()))
        if artifact == "report" and status["state"] == "complete":
            file = folder / "report.html"
            if not file.exists() or digest(file) != status.get("report_sha256"):
                return self.send(409, {"error": "Report integrity check failed"})
            body = file.read_bytes()
            self.headers_for(200, "text/html; charset=utf-8", len(body))
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; sandbox allow-popups")
            self.end_headers()
            self.wfile.write(body)
            return
        if artifact in ("evidence", "failure") and status["state"] == ("complete" if artifact == "evidence" else "failed"):
            file = folder / (artifact + ".zip")
            if not file.exists():
                return self.send(404, {"error": "No diagnostic bundle was retained for this interruption"})
            if artifact == "evidence" and digest(file) != status["evidence_sha256"]:
                return self.send(409, {"error": "Evidence integrity check failed"})
            self.headers_for(200, "application/zip", file.stat().st_size)
            self.send_header("Content-Disposition", 'attachment; filename="aero-channel-' + artifact + '.zip"')
            self.end_headers()
            with file.open("rb") as source:
                while chunk := source.read(65536):
                    self.wfile.write(chunk)
            return
        return self.send(409, {"error": "That artifact is not available for this run state"})

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/study/brief", "/study/runs"):
            return self.send(404, {"error": "Not found"})
        if self.headers.get("Origin") not in ORIGINS:
            return self.send(403, {"error": "Origin not allowed"})
        try:
            ip = str(ipaddress.ip_address(self.headers.get("X-Aero-Client-IP", "")))
        except ValueError:
            return self.send(403, {"error": "Untrusted edge request"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 2048 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("Expected a JSON request under 2 KB")
            data = json.loads(self.rfile.read(size))
            if path == "/study/brief":
                return self.send(200, brief(data))
            if not isinstance(data, dict) or set(data) != {"request_id", "inputs"}:
                raise ValueError("Expected request_id and inputs")
            job_id = enqueue(ip, data["request_id"], data["inputs"])
            return self.send(202, {"id": job_id})
        except (ValueError, TypeError, TimeoutError):
            return self.send(400, {"error": "Check the supported input ranges. Commands, files and additional fields are not accepted."})
        except OverflowError as exc:
            return self.send(429, {"error": str(exc)})
        except ConnectionError as exc:
            return self.send(503, {"error": str(exc)})


if __name__ == "__main__":
    DATA.mkdir(parents=True, exist_ok=True)
    ThreadingHTTPServer(("0.0.0.0", 5323), Handler).serve_forever()
