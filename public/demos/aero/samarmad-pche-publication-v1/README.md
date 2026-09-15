# Samarmad PCHE benchmark — pre-reveal record (v1)

This page records a prediction package for a printed-circuit heat-exchanger study before the publication's experimental measurement tables were opened for comparison. The numerical result at this stage is **FAIL**: the three-grid OpenFOAM study does not meet the preregistered residual and pressure-drop grid-sensitivity gates. Mass and energy balances pass; that does not rescue the failed solver/convergence disposition.

## Source

Samarmad and Jaffal, “Performance evaluation of a printed circuit heat exchanger with a novel two-way corrugated channel,” *Results in Engineering* 19, 101303 (2023), [DOI 10.1016/j.rineng.2023.101303](https://doi.org/10.1016/j.rineng.2023.101303). The author-uploaded full-text record reports CC BY-NC-ND 4.0. This page contains no article PDF, source text, figure, table, or digitized experimental data. Local use was documented as noncommercial with attribution; commercial reuse is not cleared. This is not legal advice.

## What was actually run

The geometry is an independently authored reconstruction of one periodic corrugated Model 6 cell, not author CAD. Its inlet/outlet conditions and properties were frozen in a separate local input packet. The cold inlet was set to 293 K based on the detailed BC table and test-loop description despite a conflicting 290 K overview statement. A 5 mm fabricated channel pitch was selected over a 4 mm simplified numerical-overview width; the stated amplitude was interpreted as 0.8 mm because the source omitted units. These choices and uncertainties are retained, not silently reconciled.

The first-principles baseline is a straight, fully developed semicircular-channel screen: Re 519.12, hydraulic diameter 1.5275 mm, straight-channel pressure drop 576.2 Pa, and heat duty 27.46–30.90 W per channel pair. It explicitly omits corrugation, entrance and manifold effects and is not claimed as a prediction of the corrugated exchanger.

OpenFOAM Foundation v10 ran coarse, medium and fine tetrahedral meshes of 494,670, 1,003,677 and 2,770,939 cells to the common 250 s output. All regions pass `checkMesh`; mass imbalance is at most 0.090% against 0.5%, and hot/cold energy imbalance at most 3.672% against 5%. However, the maximum final residuals are 2.14e-4, 5.77e-6 and 6.70e-6 against a frozen 1e-6 limit. Medium-to-fine pressure drop changes by 22.6% hot and 22.2% cold against a 5% limit. The frozen numerical disposition is therefore **FAIL**. Very high Courant and solid diffusion diagnostics are also preserved. Reaching end time is not treated as convergence.

The cited paper provides no structural material, supports, mechanical loads, or structural measurement. A separately planned three-grid CalculiX thermal-mapping exercise is exploratory only and failed its exact 100% transfer-coverage gate at 92.95%, 94.56%, and 99.9976%; no decks were generated for that plan. A distinct earlier single assumption-only CalculiX shakedown is not source validation.

## Freeze and reveal status

The prediction manifest contains 653 hashed entries. Its SHA-256 is `e09516c5946190b72e29009f0bc3f99ae3f7586c2c29e89e3f9dc02539e07cfb`; its inventory SHA-256 is `9f34e3f2615437fe15c61b60b36fcddb671ca09cdecd0739689201494437e92d`. An independent local verification checked all entries with zero mismatches. OpenTimestamps submissions have been made to four calendars, but blockchain confirmation is still pending. Consequently the publication's experimental tables have **not been opened or compared** in this revision.

The orchestration agent had prior exposure to an abstract-level summary and a Section 4.1 discrepancy, and the solver container was not hermetic. This is a reference-withheld solver run, not a fully blind benchmark. After external timestamp verification, a separate reveal report will compare only matching frozen test conditions and measurement definitions. If no exact match exists, the result will be marked **UNSCORED**; v1 will not be retuned. Any post-reveal tuning will be a separate calibration study.

## Files

- [`run_summary.json`](run_summary.json) — machine-readable pre-reveal status and numerical gates.
- [`pre_reveal_prediction_freeze.json`](pre_reveal_prediction_freeze.json) — hash inventory of the frozen prediction package.
- [`pre_reveal_prediction_freeze.json.ots`](pre_reveal_prediction_freeze.json.ots) — OpenTimestamps proof (calendar-submitted; confirmation pending).

This public summary reports Aero's independently generated run; it does not reproduce the source article or constitute design-release evidence.
