# Aero public chat beta — acceptance record

Date: 2026-09-12. Scope: the public browser requirements conversation only.
This is **not** public CFD execution or an engineering design-validation release.

## Live route and deployment

- Browser: `https://alex-blythe.com/software/aero/current/`
- Conversation API: `https://aero-chat.alex-blythe.com`
- Site deployment: commit `aa2b160`, GitHub Actions run `34708430603` completed successfully.
- Separate Cloudflare tunnel terminates at the loopback-only Caddy edge
  `127.0.0.1:5322`. The private Aegis tunnel and its Caddy login were unchanged.
- Linux containers own the dedicated Ollama `gemma3:12b` model, the constrained
  conversation gateway, and Caddy. The model ran 100% on the local RTX 3090.
  Ollama cloud features are disabled. Neither Ollama nor the gateway publishes
  a host port.

## Gates exercised

| Gate | Observed result |
| --- | --- |
| Gateway unit and monitor tests | 14 passed |
| Site build and UI test | Passed |
| Public HTTPS synthetic nozzle, cooling and adversarial cases | 3 passed |
| Public-browser two-turn conversation and LaTeX rendering | Passed |
| Requirements and chat after refresh | Passed |
| Modified field loses confirmation | Passed |
| Browser cannot start a solver | Passed |
| Client IP missing / wrong browser origin | 403 / 403 |
| Per-client quota after six invalid requests | Seventh returned 429 |
| Public `/api/tags` | 404, not proxied to Ollama |
| Private Aegis root | 401 Basic Auth, unchanged |
| Scheduled tunnel and external health checks | Both ran with result 0; health state `up` |

The local and live browser tests also checked mobile/tablet layout, HTML and
unsafe-TeX handling, and failed-send draft preservation. The empty conversation
screen now begins at the title; the decorative `A` and extra top spacing are gone.
The conversation header now includes an accessible availability indicator: amber
while the gateway is being checked, green when the conversation-only model is
ready, and red when it is unavailable. It checks on load, after a manual
connection, and periodically while the page is open. This indicator describes
the public conversation service only; VM and solver state remain behind the
authenticated private Aegis workspace.

## Failures found during acceptance and repairs

The first longer Gemma request hit the 1,800-token output cap and the gateway
returned 502; the raw response was not retained. A JSON schema, shorter
response budget, and stricter validation fixed that test. A later
response tried to put broken LaTeX in chat; the public gateway now accepts
only standard equation identifiers and maps them to four reviewed formulas.
An adversarial prompt made the raw model falsely claim an OpenFOAM run; a
server-side execution-claim gate now replaces such responses with an explicit
no-execution statement. The first-turn numeric-preservation check prevents
silent loss of user-stated engineering quantities.

These are bounded mitigations, not proof that every model-generated engineering
statement is correct. Requirement values and formulas remain proposals for user
review. The model has no RAG, CAD upload, file, agent, VM or solver tool.

## Capacity and operational limit

This is an anonymous, small-capacity beta: six requests per client and sixty
globally per ten minutes, one inference at a time, 32 KB body cap, and at most
eight upstream Caddy connections. A busy model can return 429. The static site
and saved browser cases remain available if the model is offline. Because the
Linux containers run on the local desktop host, public chat is unavailable
when that host or Docker is off. A move to always-on Linux hardware would be
the next availability upgrade, without changing the browser or trust boundary.

The external monitor checks readiness every five minutes. It alerts after
three consecutive failures and again on recovery; it does not read chat text.
The notification transition logic passed unit tests and a one-time healthy
ntfy delivery test returned success. No artificial outage was induced on the
live public service for this acceptance.
