# Challenge 01: input freeze and isolated readiness review

## Completed

- NASA TM-4074 original PDF retained by the source custodian and hashed.
- Table XIII first subtable selected: M=0.15, Re=5.95e6, No. 180 grit at x/c=0.05.
- All 18 operating points retained; 36 measured coefficients transcribed, visually checked, then sealed with AES-256-GCM. No reference values or key are included in public plaintext.
- The source paper, plaintext extraction and key remain outside the website repository. The custody directory is restricted to the current local account and SYSTEM.
- A non-root OpenFOAM container passed an actual network/filesystem isolation probe. It started the solver help command, not a CFD case.
- A fresh Gemma 3 12B reviewer ran in a separate non-root, read-only, network-disabled container. Its sole read-only mount was the model-weight subdirectory; no repository, source PDF, reference, key or prior chat was mounted. Only the input-only prompt was sent through stdin. Runtime logs confirmed full layer offload to the desktop RTX 3090, not the GB10.
- 19 software tests pass (13 chronology/comparison tests plus six isolation-configuration checks).

## Review disposition: HOLD

The raw model output is retained, including terminal-control characters emitted by its CLI. It is a planning review, not a prediction. It identified geometry convention, dimensional properties, transition, tunnel correction and turbulence uncertainties.

Its recommendation that steady-state treatment should be sufficient across this series is NOT accepted as established. Its claim that actual measured coordinates are mandatory is also too absolute: a justified nominal geometry can be a declared approximation, not an exact as-built reconstruction. A transition-model suggestion is not evidence that the chosen solver implements the physical trip correctly. These points require input-only numerical design and testing before preregistration.

This is not a valid experimental result and not a numerical mesh proof. No mesh, force coefficient, production run or comparison is supplied. The original Preparation 0.1 PDF/source package remains a historical record; it is not silently rewritten.

## Reproduce the readiness tools

Run `python -m unittest discover -s tools -v` after extracting the checkpoint sources (Python, cryptography and matplotlib are required).

`isolation.py --input input/input.json --output FRESH_OUTPUT` probes the pinned OpenFOAM image without solving. `fresh_review.py` creates a disposable Ollama reviewer using the named local public-model cache and pinned image; its machine-specific cache/GPU choices are explicit, not a dependency imposed on Aero's portable application. Both scripts remove only their own captured container IDs. Neither can obtain the custody key or unseal a reference.

The public receipts include hashes of local raw logs. The complete inference stderr and server logs remain local; only the reviewed response, prompt and isolation metadata are in this public checkpoint. The checkpoint manifest lists exactly what the download contains.

## Next

Define the nominal geometry, dimensional realization, transition-trip equivalence, inlet-turbulence policy, all-angle time treatment, mesh levels and numerical/experimental acceptance bounds using only permitted inputs. Verify the execution driver, freeze and publish the full preregistration, then solve and freeze a complete prediction before reference reveal. Difficult operating points and failed runs must remain visible.
