## Documentation / reproducibility request

I am reproducing the public NVIDIA DrivAerML **surface** Transolver checkpoint and would appreciate a checkpoint-specific training/inference recipe. This is not a claim that the checkpoint is faulty.

Checkpoint: [nvidia/transolver_drivaerml](https://huggingface.co/nvidia/transolver_drivaerml/tree/96477aeb86d24c26ccf0797bca1b3851268017d0), `transolver_drivaerml_surface_checkpoint/Transolver.0.501.mdlus`.

SHA-256: `eb98f399a050a8f8a24919335c61642e4a835bd4044f7e21abec231aa31fd82c`.

### Observations

- The saved arguments specify 20 layers, MLP ratio 2, 512 slices, `use_te:false`, and `plus:false`; the model card describes eight layers.
- Creator metadata reports PhysicsNeMo 1.3.0. The public [v1.3.0 constructor](https://github.com/NVIDIA/physicsnemo/blob/14e0874847ffb56b35abf7708a1665e71605999c/physicsnemo/models/transolver/transolver.py) lacks the `plus` argument, so I cannot identify the exact training code from that version string alone.
- The [legacy training preprocessing](https://github.com/NVIDIA/physicsnemo/blob/14e0874847ffb56b35abf7708a1665e71605999c/examples/cfd/external_aerodynamics/transolver/preprocess.py) uses area-weighted STL centering without the anisotropic coordinate scaling in the [modern example](https://github.com/NVIDIA/physicsnemo/blob/a078229716ce39d9d9273b23d54b073d3adb925e/examples/cfd/external_aerodynamics/transformer_models/src/conf/data/core.yaml). The modern datapipe computes an arithmetic STL-center mean.
- Strict state loading and a forward pass work in PhysicsNeMo 2.2.0, but that does not prove training/inference equivalence.

### Requested clarification

1. Exact training source commit, resolved model/data/training configuration, and supported inference runtime for these weights.
2. Confirmation of the saved 20-layer architecture versus the card's description.
3. Exact coordinate origin and scale used in training: STL arithmetic mean, area-weighted centroid, VTP centroid, and whether `[12,4.5,3.25]` scaling applies.
4. Native DrivAerML-to-training conversion for pressure and wall shear: dimensions, sign, pressure reference, density and velocity conventions. Does the velocity input use the native approximately 38.889 m/s condition, or another normalized/reference convention? Published inference wrappers default to 30 m/s; I am not assuming this is a training value.
5. Normalization-generation recipe for `global_stats.json`, ideally with a checksum-linked reference input and expected output.
6. Normal construction/orientation, training and inference point-context size, sampling/chunking, and precision settings.
7. Exact training/validation/test run IDs, especially whether native run 1 is held out.

I want to avoid choosing preprocessing by whichever produces the lowest reference error. A pinned recipe or pointer to an existing checkpoint-specific example would help distinguish a valid reproduction from a merely successful model execution. If this belongs in the PhysicsNeMo-CFD repository or model discussions instead, please point me to the preferred location. Thank you.
