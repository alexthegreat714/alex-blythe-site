# Aero conversation-only gateway

This service is separate from the personal agent stack. It speaks to a configured
Ollama model and returns a bounded JSON document proposal. It cannot call agents,
search local files, run a shell, load CAD, execute a solver or change the VM.

## Local proof configuration

```powershell
$env:AERO_CHAT_MODEL = 'gemma3:12b'
$env:AERO_CHAT_OLLAMA = 'http://127.0.0.1:11434'
$env:AERO_CHAT_ORIGINS = 'http://127.0.0.1:4322'
python services/conversation/server.py
```

The defaults bind only `127.0.0.1:5320`. The endpoint is configurable; there is
no GB10 assumption. This local test used the native desktop's already-loaded
12B model. No model is downloaded by the gateway.

Open `/software/aero/current/` through the loopback Astro preview on port 4322.
The UI automatically checks that gateway for local previews. Public builds have
no default model endpoint unless `PUBLIC_AERO_CHAT_URL` is set during the build.
A visitor can explicitly connect an HTTPS conversation-only gateway; the UI
explains that messages and the requirement record will be sent there.

## Data and execution boundaries

- `/health` discloses configuration, not proven upstream model availability.
- `/chat` accepts at most 20 recent messages / 20,000 characters, with a 32 KB
  request cap. Browser history persists locally; this server stores no chat.
- 15 requests/client/10 minutes, 60 total/10 minutes, one inference at a time.
  The server deliberately ignores client-supplied forwarded IP headers. Behind
  a proxy, clients share its budget unless the proxy independently enforces a
  reviewed per-client limit. CORS is not authentication or bot protection.
- Replies cannot mark a field confirmed. User edits and confirmations during an
  in-flight model request are preserved; stale document proposals are not applied.
- Equations are model proposals, not scientifically verified. The prompt supplies
  reference continuity, ideal-gas, area and sensible-heat formulas. Browser math
  uses KaTeX with trust disabled and bounded expansion. Unsupported/unsafe math
  is excluded from generated TeX. No TeX engine or shell runs in this service.
- Scientific correctness is not guaranteed by valid JSON, valid LaTeX or a
  successful model call. An initial live test produced an incorrect differential
  continuity expression; this is recorded as a quality failure, not hidden by
  passing UI tests. Reference guidance was added and the mass-flow expression
  was checked in the subsequent focused retest. This is not a general eval.

## Before public exposure

User choice is pending: public rate-limited inference or authenticated access.
Do not route this to the existing personal `/chat`, embed admin credentials, or
remove Caddy authentication from any private route. Public exposure additionally
requires a managed process/container, TLS proxy with body/connection limits,
abuse protection, inference capacity/budget and operational health monitoring.
This development HTTP server is not by itself a production Internet listener.

## Tests

```text
python -m unittest discover -s services/conversation -p test_server.py -v
PLAYWRIGHT_MODULE=<path> AERO_LIVE_TEST=1 node scripts/test-aero-current.mjs
```

Browser test fixtures for failure/XSS checks are explicitly labelled and run
after the real-model two-turn integration test. They are not used by the app.
