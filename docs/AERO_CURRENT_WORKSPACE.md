# Aero Current — conversation-first workspace

Replaces the old `demo/?mode=current` relabelling with `/software/aero/current/`.
The legacy link redirects; the guided demo remains a separate experience.

The Current page opens straight into a composer and a live working document.
There are no Play or Next-slide controls. Six responsive stage tabs show
preparation, not tour completion. A keyboard/pointer-resizable divider separates
conversation from requirements, rendered math and generated `.tex` source.

Model responses propose values and equations. Users edit and confirm fields.
Changed values lose confirmation. Conversations and the document survive refresh
in browser localStorage; this is not cross-device or authenticated server storage.
Only the latest 20 messages (up to 20,000 characters) and current requirements
are sent to the model, so long histories are not all present in model context.
No automatic semantic compaction or RAG is claimed by this release.

Generic CAD, mesh, solve and results show prerequisites or explicitly labelled
recorded examples. They do not turn green simply because a tab was visited.
Rev 1.2 adds a separate **Live channel study** in this same workspace: four
reviewed numeric inputs, six stages, nine fresh bounded OpenFOAM solves, field
inspection, a gap decision and a downloadable proof report. See
`services/study/README.md`. General execution remains privately authenticated.

The public chat-only beta uses a separate Linux Ollama/gateway/Caddy stack and
dedicated Cloudflare tunnel. The model has no tools, RAG, CAD upload, VM, or solver
access; it receives a checked study brief and completed result for explanation.
The separate numeric study broker can submit the fixed channel template after
the user clicks Start. Public usage is bounded and can be unavailable when the local host is
off or the one model slot is occupied. See `services/conversation/README.md`
for deployment, limits, and proof details.

Existing unrelated demo CSS changes and local worker scripts are preserved.
