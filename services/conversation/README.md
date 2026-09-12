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
  is excluded from generated TeX. The public gateway now substitutes only six
  reviewed first-principles formula forms and drops other model-generated LaTeX;
  the model can still discuss a broader relation in prose. No TeX engine or shell
  runs in this service.
- Scientific correctness is not guaranteed by valid JSON, valid LaTeX or a
  successful model call. An initial live test produced an incorrect differential
  continuity expression; this is recorded as a quality failure, not hidden by
  passing UI tests. Reference guidance was added and the mass-flow expression
  was checked in the subsequent focused retest. This is not a general eval.

## Public chat-only beta

Rev 1.2 adds a **separate** bounded numerical study service; the conversation
model remains tool-free. It can read a validated study brief and a completed
result through fixed internal routes, explain them and propose document changes.
It cannot submit a job. See `../study/README.md` for public solver scope, limits
and the combined Compose command. Use both Compose files when starting the
current deployment; the chat-only command below describes the original chat
deployment without the optional study worker.

The public website uses anonymous, rate-limited **conversation only**. It does
not inherit the private Aero/Aegis/VM login or grant execution access. The Linux
deployment in `compose.aero-public-chat.yaml` runs a dedicated Ollama model,
gateway and Caddy edge; only `127.0.0.1:5322` is published on the host. A
separate Cloudflare tunnel sends `aero-chat.alex-blythe.com` to that loopback
edge. No Ollama or gateway port is public. `PUBLIC_AERO_CHAT_URL` is baked into
the static website at build time and is not a credential.

The edge caps request bodies at 32 KB and replaces `X-Aero-Client-IP` with
Cloudflare's `CF-Connecting-IP`. The gateway rejects missing/malformed client
identities, enforces 6 requests per IP and 60 globally per ten minutes, and
admits one inference at a time. This is a small beta capacity, not a general
unlimited public model API. The origin header check is additional browser
friction, not authentication. Do not bypass the Cloudflare tunnel, expose the
loopback Caddy port on a public interface, or route the personal `/chat` here.

`/health` checks Ollama reachability and that the exact configured model is
installed. It cannot prove a future inference will succeed; deployment and
external browser smoke tests cover that. The model's equations and requirement
values remain reviewable proposals, not validated engineering results.

Host setup and verification:

```powershell
docker compose -f compose.aero-public-chat.yaml up -d --build
docker compose -f compose.aero-public-chat.yaml exec -T ollama ollama pull gemma3:12b
Invoke-RestMethod http://127.0.0.1:5322/health
python services/conversation/monitor_public.py
```

The dedicated Cloudflare tunnel config is
`%USERPROFILE%\.cloudflared\config-aero-public-chat.yml`; its credentials are
outside Git. The current host's startup task runs `start_public_tunnel.ps1` on
login. A second task runs `monitor_public.py` every five minutes and sends one
ntfy alert after three failed external health checks, then one on recovery.
The monitor checks only readiness metadata and never reads conversations.
Docker's `restart: unless-stopped` policy keeps the Linux containers running
while Docker Desktop is available. A powered-off host means public chat is
unavailable; the static case library remains usable.

Do not route this to the existing personal `/chat`, embed admin credentials, or
remove Caddy authentication from any private route. The browser deliberately
uses `credentials: 'omit'`; login-gating chat would require a separate reviewed
authentication design, not a Caddy Basic Auth toggle.

## Tests

```text
python -m unittest discover -s services/conversation -p test_server.py -v
PLAYWRIGHT_MODULE=<path> AERO_LIVE_TEST=1 node scripts/test-aero-current.mjs
```

Browser test fixtures for failure/XSS checks are explicitly labelled and run
after the real-model two-turn integration test. They are not used by the app.
