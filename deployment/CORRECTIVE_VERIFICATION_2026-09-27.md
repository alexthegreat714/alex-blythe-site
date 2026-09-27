# Focused corrective pass — 2026-09-27

## Corrected

- Homepage: three Selected Engineering Work cards immediately after the identity/current-role area, with the primary hero link pointing to them.
- Earlier CFD and launch-acoustics articles: unchanged original pages, now reached through `/writing/` instead of prominent individual homepage cards. Added the archive's canonical URL to the sitemap.
- Aero: two-part executive summary before the pipeline film, private-access link and Try Aero. Consolidated repeated authority/hash/LLM limitations into that summary; retained the later scope-specific limitations.
- Channel evidence: added only `#channel-study` to the existing evidence-hub article. No evidence/results/data were rewritten.
- ForgeClaw: `src/data/software.ts` now uses public `v0.1.0-alpha.5`, not the previously displayed alpha.6. The metadata feeds the software index/project page. No OCR97 changes.
- Redirects: prepared platform-native Cloudflare Single Redirect rules and `npm run audit:redirects`. **Not activated; live redirect requirement remains incomplete.**

## Version authority

Public repository `PrecisionArtsLab/ForgeClaw`: latest tag `v0.1.0-alpha.5` at `94471f2bf9a8e6aad078977c4be05427b818e92a`; `pyproject.toml` version `0.1.0a5`. The root README, packaged PUBLIC_README, release checklist and public-release audit agree. No GitHub Release is published. Website alpha.6 was unsupported by that public release state; repository material did not need changing. Historical alpha.3/alpha.4 tags are not conflicting current-version claims.

## Verification

- Production build: 53 pages, success. Same pre-existing Vite >500 kB chunk advisory as baseline; no new build warnings/errors.
- Automated rendered checks: homepage, Aero, ForgeClaw and writing at 390 px and 1440 px in light and dark themes; 16 page/viewport/theme checks passed, no JavaScript page errors or horizontal document overflow. Screenshots inspected.
- Selected section has exactly three cards; all three targets return 200; Channel fragment exists. Aero summary is visually above the pipeline film and demos.
- Static internal audit: 53 pages, eight artifact HTML documents, 324 unique internal targets, 27 PDF/ZIP downloads present. No new missing targets/anchors or other audit regressions.
- Protected homepage section, Bifrost PDF and Road to Type 2 archive compared against committed originals. Unchanged. Original articles and engineering evidence/status records unchanged; evidence-hub diff is the anchor alone.
- Revised-page canonicals point to their current routes. All 11 sitemap entries are canonical, with no retired URLs; no internal links to retired routes. Existing sitemap omissions and unrelated metadata issues were not expanded into this pass.

## Actual public redirect observation

HEAD requests on 2026-09-27, before account-required activation:

| Old URL | Status | Location | Final URL | Final status |
| --- | --- | --- | --- | --- |
| `/my-projects/` | 200 | absent | `/my-projects/` | 200 |
| `/resume/` | 200 | absent | `/resume/` | 200 |

Intended one-hop destinations are `/software/` and `/#experience`; both destination pages return 200. Non-slash old URLs currently 301 only to their obsolete slash forms, not to the intended destinations. No HTTP loop was observed, but the required canonical redirects are **not working**. The audit intentionally exits nonzero until fixed. See `LEGACY_REDIRECTS.md` for account activation and exact rules. GitHub Pages cannot apply these edge rules merely because their JSON is committed.

## Pre-existing audit findings retained outside this corrective scope

Seven distinct broken destinations (eight link occurrences):

- Three links on the heat-exchanger program page incorrectly nest `maturity-pass-20260916/` beneath `heat-exchanger-benchmark-program-v1/`: README, HX-02 visible packet and HX-03 README. Existing files are under `/demos/aero/heat-exchanger-maturity-pass-20260916/`.
- Three links on that page omit `diagnostics/` before LTOL-003 RESULTS.md, LTOL-003 RESULT.json and LTOL-002 RESULTS.md.
- Two report pages link to `two-fluid-cht-profile-2026-09-19/`; the existing destination is `two-fluid-cht-profile-freeze-2026-09-19/`.

The baseline also lacks 32 canonical pages in its sitemap and has pre-existing cooling/current metadata findings. Those are not introduced by this pass and are not represented as a clean whole-site audit.

## Account-required follow-up

Sign in to Cloudflare and activate the two redirects with website DNS proxying and verified origin TLS as documented, then rerun the real public header audit. Once redirects pass, optionally resubmit the sitemap and inspect the old URLs in Search Console. No webmaster-account changes were attempted.
