"""Package an allowlisted public experiment, never a workspace-wide export."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile


def main(report, destination):
    destination.mkdir(parents=True, exist_ok=True)
    assets = ['comparison.json', 'pointwise_deltas.csv', 'mesh_summary.csv',
              'residual_history.csv', 'fine_convergence.csv', 'arithmetic_audit.json',
              'wall_comparison.png', 'velocity_comparison.png', 'reattachment.png',
              'fine_convergence.png']
    for name in assets:
        shutil.copy2(report / name, destination / name)
    shutil.copy2(report / 'diagnostics/cf_bias_followup.json', destination / 'cf-bias-followup.json')
    attribution = {
        'title': 'Aero vs Driver–Seegmiller experimental backward-facing step',
        'executed_date': '2026-11-22', 'published_date': '2026-11-23',
        'ai_workflow_model': 'OpenAI 6.1 High',
        'model_attribution_basis': 'Model label supplied by project owner Alex Blythe; not independently captured in the retained runtime metadata',
        'ai_role': 'Case preparation, Aero workflow orchestration, postprocessing, diagnosis and documentation',
        'numerical_solver': 'OpenFOAM Foundation 10, build 10-c4cf895ad8fa; simpleFoam; kOmegaSST; CPU',
        'model_is_not_the_numerical_solver': True,
        'paper_doi': '10.2514/3.8890',
        'disposition': 'Comparison completed; strict residual target not met on refined meshes; mesh independence and design validation not established',
        'public_scope': 'Public NASA experiment only. No private Aero toolkit, credentials, employer data or live-service configuration included.'
    }
    (destination / 'benchmark-metadata.json').write_text(json.dumps(attribution, indent=2), encoding='utf-8')
    source_records = json.loads((report / 'sources/downloads.json').read_text())
    wanted_sources = ['cp.expnew.dat', 'cf.exp.dat', 'profiles.exp.dat', 'backstep_bcs.jpg']
    source_records = [r for r in source_records if r['name'] in wanted_sources]
    for r in source_records:
        assert hashlib.sha256((report / 'sources' / r['name']).read_bytes()).hexdigest() == r['sha256']
    forbidden = re.compile(rb'(?i)(?:gh[pousr]_[a-z0-9]{20,}|sk-[a-z0-9]{30,}|Bearer\s+[a-z0-9._-]{25,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)')
    original_hashes = {}
    archive = destination / 'reproducibility.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=7) as bundle:
        def add(source, target):
            raw = source.read_bytes()
            if source.suffix in ('.json', '.py', '.txt', '.log', '.csv', '.dat'):
                assert not forbidden.search(raw), f'Credential-pattern rejection: {target}'
            bundle.writestr(target, raw)
            original_hashes[target] = hashlib.sha256(raw).hexdigest()
        for name in assets + ['cf-bias-followup.json', 'benchmark-metadata.json']:
            add(destination / name, name)
        for record in source_records:
            add(report / 'sources' / record['name'], 'sources/' + record['name'])
        bundle.writestr('sources/downloads.json', json.dumps(source_records, indent=2))
        add(report / 'diagnostics/backstep_cfl3d_cf_sst.dat', 'diagnostics/backstep_cfl3d_cf_sst.dat')
        for name in ['driver_seegmiller_validation.py', 'compare_driver_seegmiller.py', 'audit_driver_seegmiller.py']:
            add(report / 'reproduction' / name, 'reproduction/' + name)
        for label in ['coarse', 'medium', 'fine_initial', 'fine']:
            source = report / 'evidence' / label
            state_raw = (source / 'state.json').read_bytes()
            state = json.loads(state_raw)
            public_state = {k: state[k] for k in ('run_id', 'status', 'metrics')}
            public_state['original_state_sha256'] = hashlib.sha256(state_raw).hexdigest()
            public_state['publication_note'] = 'Public metadata projection; local runtime/control-plane fields omitted.'
            bundle.writestr(f'evidence/{label}/state.json', json.dumps(public_state, indent=2))
            add(source / 'solver.log', f'evidence/{label}/solver.log')
            for tree in ['case_input', 'case_result']:
                for path in sorted((source / tree).rglob('*')):
                    if not path.is_file():
                        continue
                    rel = path.relative_to(source / tree)
                    # Mesh/system/starting fields already exist in case_input.
                    # Keep solved volume times and samples without duplicate decks.
                    if tree == 'case_result' and rel.parts[0] in ('0', 'constant', 'system'):
                        continue
                    if rel.parts[0] not in ('0', 'constant', 'system', 'postProcessing', '1500', '1800', '2000') and rel.name not in ('input_contract.json', 'initialization.json', 'mapFields.log'):
                        continue
                    add(path, f'evidence/{label}/{tree}/{rel.as_posix()}')
        bundle.writestr('source-original-hashes.json', json.dumps(original_hashes, indent=2))
        bundle.writestr('README.txt', '''Aero experimental CFD comparison — public reproducibility bundle

Reference: Driver & Seegmiller, AIAA Journal 23(2), 163–171 (1985), doi:10.2514/3.8890.
NASA experimental data: https://tmbwg.github.io/turbmodels/backstep_val.html
The journal paper is peer-reviewed; this Aero execution report is not.

AI workflow attribution: OpenAI 6.1 High (model label supplied by Alex Blythe).
The AI assisted setup, orchestration, diagnostics and reporting. OpenFOAM, not
the language model, produced the numerical CFD predictions.

Executed with Aero's imported-case OpenFOAM pipeline, OpenFOAM Foundation 10,
build 10-c4cf895ad8fa, simpleFoam, kOmegaSST, serial CPU.
Three nested orthogonal meshes: 6,800 / 27,200 / 108,800 cells.
Fine includes an initial 2,000 iterations plus a 1,500-iteration continuation.
The exact continuation checkpoint is already mapped into fine/case_input/0.
Numerical settings and inputs are retained; no fitting of downstream data.

To replay the numerical solves, copy each evidence/NAME/case_input to a writable
working directory, source OpenFOAM 10, then run checkMesh and simpleFoam there.
Preserve constant/polyMesh. Do not replace it with blockMesh. Replay fine from
its retained initial fields; 1,500 replay iterations correspond to 3,500 total
on that grid. The recorded result of the initial fine run is also included.
The medium final sampled U/p/Cp/Cf data are retained; its latest volume directory
contains diagnostics only. This limitation is disclosed in the report.
For volume-field viewing, copy a retained solved time from case_result into a
writable copy of case_input; the bundle deduplicates mesh/system/initial files.

To recalculate the comparison from retained evidence:
  python reproduction/compare_driver_seegmiller.py .
  python reproduction/audit_driver_seegmiller.py .
Requires Python with numpy, scipy and matplotlib. The generator script is an
archive copy from Aero/tools; use the retained decks for exact replay.

NASA CFL3D SSTm data in diagnostics are another CFD reference, not experiment.
SSTm/CFL3D differs from our OpenFOAM wall treatment and steady incompressible
implementation; the 7/20 follow-up is supporting evidence, not a controlled
model-isolation experiment. Listed experimental error confidence is unspecified.

Public release excludes private toolkit modules, service configuration and
credentials. state.json files are explicit public projections of run metadata.
Hashes identify artifacts; they do not establish scientific correctness.
''')
    assert archive.stat().st_size < 95_000_000, 'Archive exceeds repository release limit'
    manifest = {'files': [{'path': p.name, 'bytes': p.stat().st_size,
                           'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in sorted(destination.iterdir()) if p.is_file() and p.name != 'manifest.json']}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps({'archive_bytes': archive.stat().st_size, 'assets': len(manifest['files'])}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('report_root', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    main(args.report_root, args.destination)
