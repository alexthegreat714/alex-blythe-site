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

CAD, mesh, solve and results show their prerequisites. They do not inherit the
demo's recorded results, become green merely because a tab was visited, or launch
jobs. The private execution workspace remains separately authenticated.

Live model integration has been exercised locally through the new isolated
conversation gateway. Enabling public inference remains a separate access-policy
decision. See `services/conversation/README.md` for limits and proof details.

Existing unrelated demo CSS changes and local worker scripts are preserved.
