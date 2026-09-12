"""External Aero chat health check; alert on sustained outage and recovery only."""
import json
import os
from pathlib import Path
import urllib.request

URL = os.getenv("AERO_PUBLIC_CHAT_URL", "https://aero-chat.alex-blythe.com/health")
STATE_PATH = Path(os.getenv("AERO_PUBLIC_MONITOR_STATE", str(Path.home() / ".aero-public-chat" / "monitor.json")))

def check():
    try:
        request = urllib.request.Request(URL, headers={"User-Agent": "Aero-public-health/1"})
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.load(response)
        return (response.status == 200 and payload.get("ready") is True
                and payload.get("mode") == "conversation_only" and payload.get("tools") is False)
    except (OSError, ValueError, TypeError):
        return False

def next_state(previous, healthy):
    failures = 0 if healthy else int(previous.get("failures", 0)) + 1
    old = previous.get("status", "unknown")
    status = "up" if healthy else "down" if failures >= 3 else old
    event = "recovered" if healthy and old == "down" else "down" if status == "down" and old != "down" else None
    return {"status": status, "failures": failures}, event

def ntfy_target():
    env = dict(os.environ)
    local_env = Path(__file__).resolve().parents[4] / "Sky" / ".env"
    env_file = os.getenv("AERO_PUBLIC_NTFY_ENV_FILE", str(local_env))
    if env_file and Path(env_file).is_file():
        for line in Path(env_file).read_text(encoding="utf-8-sig").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                if key in ("ARGUS_NTFY_URL", "ARGUS_NTFY_TOPIC"):
                    env.setdefault(key, value.strip().strip('"').strip("'"))
    base = env.get("ARGUS_NTFY_URL", "https://ntfy.sh").rstrip("/")
    topic = env.get("ARGUS_NTFY_TOPIC", "")
    if not base.startswith("https://") or not topic or "/" in topic:
        return None
    return f"{base}/{topic}"

def notify(event):
    target = ntfy_target()
    if not target:
        return False
    message = ("Aero public chat recovered; model readiness is healthy."
               if event == "recovered" else
               "Aero public chat has failed three consecutive external readiness checks.")
    request = urllib.request.Request(target, data=message.encode("utf-8"), method="POST",
                                     headers={"Title": "Aero public chat", "Priority": "high" if event == "down" else "default"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.status < 300
    except OSError:
        return False

def main():
    try:
        previous = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = {}
    current, event = next_state(previous, check())
    if event and not notify(event):
        # Retry a transition on the next check if the alert path was unavailable.
        current["status"] = previous.get("status", "unknown")
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(current), encoding="utf-8")
    temporary.replace(STATE_PATH)
    print(f"Aero public chat: {current['status']} ({current['failures']} consecutive failures)")

if __name__ == "__main__":
    main()
