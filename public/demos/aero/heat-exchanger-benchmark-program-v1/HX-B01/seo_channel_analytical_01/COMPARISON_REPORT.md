# HX-B01-SC-ANALYTICAL-01 — post-reveal comparison

**Disposition:** scoped analytical comparison completed; correlation comparison
FAIL; pointwise experimental validation NOT ESTABLISHED.  
**Run class:** source-grounded and result-withheld until freeze, but not a
human-custodian blind experiment because the implementing agent had access to
the public article while preparing the reveal.

## Freeze and reveal

The visible packet, pre-run plan, and first-principles prediction were frozen
before adding the publication-derived friction correlation. Their hashes and
the frozen values are recorded in [`BLIND_FREEZE.json`](BLIND_FREEZE.json).
The source correlation was added only in [`SOURCE_REVEAL.json`](SOURCE_REVEAL.json)
after that freeze. No model, geometry, property, or acceptance criterion was
changed after reveal.

## Frozen prediction versus revealed source correlation

| Quantity at matched `Re = 300` | Frozen analytical screen | Revealed source-derived value | Comparison |
|---|---:|---:|---:|
| Fanning friction factor | 0.0533333 | 0.0771347 | **FAIL**, −30.857% |
| Channel pressure drop | 2,810.20 Pa | 4,064.32 Pa (recomputed from revealed `f_N`) | **FAIL**, −30.857% |

The source reports its fitted correlation and experimental points within an
approximately ±8% envelope over `Re = 100–850`. Aero's frozen laminar
circular-duct screen lies outside that envelope at `Re = 300`; this is a
quantitative disagreement with the source correlation, not a claim that the
source's plotted experimental point was reproduced exactly. No numeric raw
point table or port/tap decomposition was available for a pointwise
experiment comparison.

## What the result means

The first-principles screen gets the qualitative pressure-drop direction right:
at fixed properties, both the screen and the revealed source relation predict
increasing pressure drop with Reynolds number. It misses the magnitude because
the circular-duct `16/Re` Fanning relation does not represent the etched
half-moon passage and the source's fitted factor includes the source's
configuration and measurement definition. The result is useful evidence that
the pipeline preserves a predeclared approximation and exposes its error; it is
not evidence that the approximation is suitable for design.

The geometry reconciliation also passed: `4 A_c L_f/A_s` gives
`0.667189 mm`, within 0.196% of the source-defined `0.6685 mm`. That checks
the source hydraulic-diameter convention, not the missing profile coordinates.

## Deliberate scope boundary

This run was intentionally analytical only. It did not run OpenFOAM, build a
whole-core/header model, infer port losses, or run CalculiX. The visible packet
does not define exact half-moon profile coordinates, pressure-tap planes, or a
numeric raw experimental table. Therefore the program records:

- analytical method and freeze discipline: **ESTABLISHED**;
- source-correlation comparison: **FAIL** (underpredicts by 30.857%);
- pointwise experimental validation: **NOT ESTABLISHED**;
- port-to-port pressure-drop validation: **NOT ESTABLISHED**;
- CFD/FEA execution for this B01 slice: **NOT RUN by predeclared scope**;
- design readiness: **NOT ESTABLISHED**.

The earlier HX-B01 Luna feasibility STOPs remain untouched. This scoped run
does not silently convert them into a full publication benchmark and does not
replace the HX-S01 synthetic CHT study. A future full B01 run requires
custodian-verified profile geometry, measurement planes, a matched point, and
an uncertainty-aware digitization/data package.

## References

Seo, J.-W., Kim, Y.-H., Kim, D., Choi, Y.-D., and Lee, K.-J. (2015), “Heat
Transfer and Pressure Drop Characteristics in Straight Microchannel of Printed
Circuit Heat Exchangers,” *Entropy* 17(5), 3438–3457,
[DOI 10.3390/e17053438](https://doi.org/10.3390/e17053438). The article is
open access under CC BY 4.0. The fitted correlation and its reported ±8%
agreement statement are source results revealed after the freeze; no article
PDF or figure is redistributed in this report.
