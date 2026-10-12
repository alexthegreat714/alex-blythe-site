# alex-blythe.com

Static Astro source for Alex Blythe's aerospace engineering and research website.

## Local development

```powershell
.\site.cmd install
.\site.cmd dev
```

## Production build

```powershell
.\site.cmd build
.\site.cmd preview
```

Pushes to `main` deploy through GitHub Actions. The `CNAME` file publishes the site for `alex-blythe.com` once the domain's DNS records point to GitHub Pages.

## Guided first-principles workspace

Open `/software/aero/current/?walkthrough=hx` for the six-step synthetic
heat-exchanger tube notebook. Existing saved cases remain in the browser;
`New case` restores the ordinary engineering intake. Controlled inputs update
analytical predictions, checked-source LaTeX, and downloadable evidence JSON.
The chat model may explain the evidence but cannot rewrite these inputs or
promote equation checks into hardware qualification.

The FE comparison reuses the separately assembled NumPy verification at
`public/demos/aero/first-principles-hx-v1/`. It is applicable only when all
reference inputs match. Edited inputs withhold that comparison rather than
reusing an old PASS. No new conventional solver, public GPU endpoint, live PDF
compiler, or private runtime change is introduced by this feature.

Regression checks (existing dependencies; no model calls):

```powershell
node scripts/test-hx-walkthrough.mjs
python -B -m unittest discover -s public/demos/aero/first-principles-hx-v1 -p verify.py -v
.\site.cmd build
node scripts/test-hx-proof.mjs
```

For explicit local browser trust-boundary QA, run
`python -B scripts/serve-hx-walkthrough-qa.py` after building and open
`http://127.0.0.1:8786/software/aero/current/?walkthrough=hx`. Connect the
conversation setting to `http://127.0.0.1:8786/fixture` only for this test.
It is prominently marked **CONTROLLED QA FIXTURE — NOT A REAL MODEL**.
It tests incorrect proposed changes, unsafe HTML/TeX, and the `fixture failure`
request without inference or private-service access. Do not deploy this fixture
as a conversation gateway. Refresh restores the normal configured endpoint.
