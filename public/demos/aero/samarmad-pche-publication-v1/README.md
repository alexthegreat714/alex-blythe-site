# Samarmad PCHE publication-targeted run — v1

**Final disposition: INCOMPLETE.** OpenFOAM numerical disposition is **FAIL**; publication comparison is **UNSCORED**; source-supported structural validation is **NOT SUPPORTED**. The pre-reveal prediction package remains frozen and unmodified.

## Source

Samarmad and Jaffal, “Performance evaluation of a printed circuit heat exchanger with a novel two-way corrugated channel,” *Results in Engineering* 19, 101303 (2023), [DOI 10.1016/j.rineng.2023.101303](https://doi.org/10.1016/j.rineng.2023.101303). The author-uploaded full-text record reports CC BY-NC-ND 4.0. This page contains no article PDF, source text, figure, table, or digitized experimental data. Local use was documented as noncommercial with attribution; commercial reuse is not cleared. This is not legal advice.

## What was actually run

The geometry is an independently authored reconstruction of one periodic corrugated Model 6 cell, not author CAD. Its inlet/outlet conditions and properties were frozen in a separate local input packet. The cold inlet was set to 293 K based on the detailed BC table and test-loop description despite a conflicting 290 K overview statement. A 5 mm fabricated channel pitch was selected over a 4 mm simplified numerical-overview width; the stated amplitude was interpreted as 0.8 mm because the source omitted units. These choices and uncertainties are retained, not silently reconciled.

The first-principles baseline is a straight, fully developed semicircular-channel screen: Re 519.12, hydraulic diameter 1.5275 mm, straight-channel pressure drop 576.2 Pa, and heat duty 27.46–30.90 W per channel pair. It explicitly omits corrugation, entrance and manifold effects and is not claimed as a prediction of the corrugated exchanger.

OpenFOAM Foundation v10 ran coarse, medium and fine tetrahedral meshes of 494,670, 1,003,677 and 2,770,939 cells to the common 250 s output. All regions pass `checkMesh`; mass imbalance is at most 0.090% against 0.5%, and hot/cold energy imbalance at most 3.672% against 5%. However, the maximum final residuals are 2.14e-4, 5.77e-6 and 6.70e-6 against a frozen 1e-6 limit. Medium-to-fine pressure drop changes by 22.6% hot and 22.2% cold against a 5% limit. The frozen numerical disposition is therefore **FAIL**. Very high Courant and solid diffusion diagnostics are also preserved. Reaching end time is not treated as convergence.

The cited paper provides no structural material, supports, mechanical loads, or structural measurement. A separately planned three-grid CalculiX thermal-mapping exercise is exploratory only and failed its exact 100% transfer-coverage gate at 92.95%, 94.56%, and 99.9976%; no decks were generated for that plan. A distinct earlier single assumption-only CalculiX shakedown is not source validation.

## Freeze and post-reveal comparison

The frozen manifest contains 653 entries. Its SHA-256 is `e09516c5946190b72e29009f0bc3f99ae3f7586c2c29e89e3f9dc02539e07cfb`; inventory SHA-256 is `9f34e3f2615437fe15c61b60b36fcddb671ca09cdecd0739689201494437e92d`. An independent verifier checked every entry with zero mismatches.

The publication result section has since been reviewed, but the frozen experimental point could not be matched to an exact source measurement from the accessible article data. The source reports a Reynolds-number sweep and plotted comparisons; this review did not identify pointwise raw data at Aero's frozen 0.246 m/s condition (solver Reynolds number ≈519.105 using declared properties). The frozen criteria require matching conditions and definitions; no error percentage is fabricated from a different point. Therefore the experimental comparison is **UNSCORED**. The article's own reported 11.6% Nusselt and 11.5% friction-factor deviations describe its Model 6 numerical results versus its experiments, not Aero's error.

The OpenTimestamps proof was submitted to four calendars, but Bitcoin confirmation remains pending. Publication results were reviewed after the inventory was re-hashed and after submission, but before confirmation; that procedural limitation is explicitly recorded. The proof is submitted/pending, not externally confirmed. The orchestrator had prior exposure to the article's abstract and Section 4.1 summary, and the solver was not isolated in a hermetic, network-disabled environment. This is not a fully blind benchmark.

## Files

- [`run_summary.json`](run_summary.json) — machine-readable pre-reveal status and numerical gates.
- [`pre_reveal_prediction_freeze.json`](pre_reveal_prediction_freeze.json) — hash inventory of the frozen prediction package.
- [`pre_reveal_prediction_freeze.json.ots`](pre_reveal_prediction_freeze.json.ots) — OpenTimestamps proof (calendar-submitted; confirmation pending).
- [`post_reveal_comparison_v1.json`](post_reveal_comparison_v1.json) — separate post-reveal disposition and explanation for the unscored comparison.

This public summary reports Aero's independently generated run; it does not reproduce the source article or constitute design-release evidence. V1 was not tuned after reveal; any later calibration must be a separately identified study.
