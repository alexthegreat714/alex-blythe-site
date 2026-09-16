# HX-B01-SC-ANALYTICAL-01 — Seo straight-channel friction benchmark

**Run ID:** `HX-B01-SC-ANALYTICAL-01`  
**Created:** 2026-09-16 UTC  
**Class:** source-grounded, scoped analytical benchmark; non-blind at the
implementing-agent level; no CFD/FEA execution authorized.

## Question

Can Aero reproduce a defensible first-principles channel-friction estimate for
one matched-Reynolds water condition from Seo et al. (2015), then compare that
estimate to the publication's reported friction-factor correlation only after
the estimate is frozen?

## Source and information boundary

The source is the open-access article by Seo, Kim, Kim, Choi, and Lee,
*Entropy* 17(5), 3438–3457, DOI `10.3390/e17053438`.
The visible packet contains only the pre-analysis geometry, fluid, operating
condition, and output definition. The publication's fitted friction
correlation, experimental values, agreement/error statement, and conclusions
are withheld from the prediction record until after the blind-freeze hash.

The implementing agent has access to the public article while preparing the
custodian reveal; therefore this is not a claim of human-custodian or
pretraining isolation. The analytical prediction itself is generated from the
visible packet and the declared laminar relation without using the withheld
correlation.

## Visible inputs

- Configuration A: 3 hot plates, 4 cold plates, 22 channels per plate.
- Half-moon channel envelope: width 0.8 mm, height 0.6 mm; straight flow
  length 137 mm; SUS304L plates.
- Source-defined channel area: hot side `A_c = 31.7 mm²`; cold side
  `A_c = 42.2 mm²`; source-defined `D_h = 0.6685 mm`.
- Matched condition: `Re_h = Re_c = 300`; hot inlet 40 °C; cold inlet 20 °C.
- Constant water properties for the first-principles screen, evaluated at a
  declared 30 °C reference state: `rho = 995.65 kg/m³`,
  `mu = 0.00079722 Pa·s`.
- Target quantity: Fanning friction factor `f` and straight-channel friction
  pressure drop, not the article's total port-plus-channel pressure drop.

## Method

1. Reconcile the source hydraulic diameter from `4 A_c L_f / A_s`; retain the
   source value if the reconstruction agrees within rounding.
2. Use `V = Re mu / (rho D_h)` and `G = rho V`.
3. Use the fully developed laminar circular-duct Fanning screen `f = 16/Re`.
   This is explicitly a screening approximation, not a claim that the etched
   half-moon channel has circular-duct behavior.
4. Compute the channel-only friction drop with the article's pressure-loss
   structure, `DeltaP = 4 f L G² / (2 D_h rho)`.
5. Freeze all values, assumptions, definitions, and limitations before opening
   the withheld source reveal.

## Stop and interpretation rules

- If the source-area reconstruction does not reproduce `D_h = 0.6685 mm`,
  stop and report a geometry-definition mismatch.
- Do not compare channel-only `DeltaP` to the publication's combined
  channel-plus-port pressure drop.
- Do not call the post-reveal comparison experimental validation: the fitted
  correlation is derived from the experiment, and no raw pointwise data or
  port decomposition is available here.
- This run intentionally does not execute CFD, FEA, or a whole-core model.
  Such work remains unauthorized until profile coordinates, port/tap planes,
  and a matched pointwise target are custodian-verified.
