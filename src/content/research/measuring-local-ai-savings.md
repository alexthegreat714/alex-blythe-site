---
title: Measuring Local AI Savings Without Lying to Yourself
summary: A draft measurement template for comparing local execution, cloud planning, latency, energy, and failure costs without cherry-picking.
date: 2026-07-18
author: Alex Blythe
tags: [Local AI, Measurement, Cost]
readingTime: 5 min
draft: true
relatedSoftware: [OCR97, ForgeClaw]
type: Technical note
---

> Draft measurement template. No savings figures are published in this version.

“Runs locally” is not the same as “costs less,” and a lower cloud-token count does not prove a better system. Honest comparisons need to include setup time, failed attempts, verification work, hardware use, latency, and the value of keeping sensitive material off external services.

## Define the workload first

Measure a repeatable task with fixed inputs, acceptance criteria, and a declared quality threshold. Record which steps ran locally, which used a remote service, and which required human review.

## Count failure cost

A cheap run that silently produces the wrong result is not cheap. Rework, retries, and review belong in the measurement alongside compute and API spend.

## Publish the limits

Future versions of this note will include a reusable worksheet and dated test cases. Until then, it is a template for measurement rather than a savings claim.

