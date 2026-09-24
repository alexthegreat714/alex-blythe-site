"""Publish only explicitly allowed aggregate data; never copy a private tree."""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

CHARTS = (
    'task_wall_time.svg', 'ttft_vs_context.svg', 'prefill_vs_context.svg',
    'decode_tokens_per_second.svg', 'gpu_memory_vs_context.svg',
    'host_memory_vs_context.svg', 'gpu_energy_per_task.svg',
)
METRICS = (
    'wall_seconds', 'ttft_seconds', 'prefill_seconds', 'decode_seconds',
    'prefill_tokens_per_second', 'decode_tokens_per_second', 'prompt_tokens',
    'output_tokens', 'load_seconds',
)
ALLOWED = {'system_id', 'model', 'workload', 'context_setting', 'n',
           'gpu_energy_j_observed_median', 'peak_gpu_memory_used_mib_median',
           'peak_system_memory_used_bytes_median'} | {
    f'{metric}_{stat}' for metric in METRICS
    for stat in ('median', 'mean', 'min', 'max', 'stdev', 'p95')
}
PRIVATE = re.compile(r'(?i)(?:\b[a-z]:[\\/]|localhost|127\.0\.0\.1|192\.168\.|10\.0\.0\.|gx10-a448|DESKTOP-H4GCI7V|ssh://|api[_-]?key|access[_-]?token)')

def safe(text):
    if PRIVATE.search(text):
        raise ValueError('Private identifier found in selected public export')
    return text

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(safe(content), encoding='utf-8')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--site', type=Path, required=True)
    args = p.parse_args()
    dest = args.site / 'public/demos/aero/hardware-benchmark-2026-09-24'
    for run, label in [('20260924_cache_neutral', 'cache-neutral'),
                       ('20260923_full_v2', 'warm-cache')]:
        source = args.source / 'runs' / run / 'benchmark_results.json'
        rows = json.loads(source.read_text(encoding='utf-8-sig'))['rows']
        exported = []
        for row in rows:
            if row['system_id'] not in ('3090', 'spark'):
                raise ValueError('Unknown system identifier')
            item = {key: value for key, value in row.items() if key in ALLOWED}
            assert item['n'] >= 5
            exported.append(item)
        payload = {'schema': 'aero.public.inference_benchmark.v1',
                   'suite': label, 'publication_date': '2026-09-24',
                   'scope': 'Synthetic inference and mocked tools; not CFD/FEA',
                   'rows': exported}
        write(dest / f'{label}-results.json', json.dumps(payload, indent=2) + '\n')
        stream = io.StringIO(newline='')
        keys = sorted(set().union(*(r.keys() for r in exported)))
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(exported)
        write(dest / f'{label}-results.csv', stream.getvalue())
    from render_hardware_benchmark_charts import render
    render(dest)
    report = args.site / 'src/content/research/rtx-3090-vs-gb10-aero-inference-benchmark.md'
    write(dest / 'REPORT.md', report.read_text(encoding='utf-8'))
    write(dest / 'README.md', '''# Aero public local-inference benchmark — September 24, 2026

Public release 1.0. Measurements September 23–24, 2026.

This is a deliberately selected aggregate export, not the complete private archive.
No private toolkit, machine access details, raw filesystem paths or credentials are included.
System IDs 3090 and spark are generic retained labels. spark means the tested GX10/GB10 node.

Primary suite: cache-neutral (deterministic unique prompt prefixes; n=5 per completed group).
Historical suite: warm-cache (repeated identical prompts; cache reuse affects prefill).
Both preserve actual measured values. Missing values remain null/blank, not zero.
Same Gemma 3 12B Q4_K_M checkpoint in the primary suite; Ollama 0.32.5 versus 0.20.4.
Runtime differences prevent a silicon-only or memory-bandwidth causal interpretation.
One warm-up precedes measured repetitions; medians are the primary reported statistic.
Agent loops contain four sequential model calls and mocked deterministic tools.
No CFD/FEA execution or production end-to-end engineering decision was measured.

Charts are rendered from the public primary-suite aggregates. Device power is not whole-system wall power.
GPU-memory and host/unified-memory counters are not interchangeable or isolated model memory.
Model labels and selected statistical fields are preserved; all other source keys are excluded.
The export script is versioned with the public website source.
REPORT.md records methodology, incomplete capacity tests and limitations.
SHA256_MANIFEST.json hashes the public data/report/chart subset, excluding itself and verification.
VERIFICATION.json records a separate reopening and digest check; it is not self-hashed.
''')
    files = [x for x in sorted(dest.rglob('*')) if x.is_file()
             and x.name not in ('SHA256_MANIFEST.json', 'VERIFICATION.json')]
    manifest = {x.relative_to(dest).as_posix(): hashlib.sha256(x.read_bytes()).hexdigest()
                for x in files}
    write(dest / 'SHA256_MANIFEST.json', json.dumps({'algorithm': 'SHA-256', 'files': manifest}, indent=2)+'\n')
    missing, mismatch = [], []
    for name, digest in manifest.items():
        file = dest / name
        if not file.exists(): missing.append(name)
        elif hashlib.sha256(file.read_bytes()).hexdigest() != digest: mismatch.append(name)
    result = {'checked': len(manifest), 'missing': missing, 'mismatches': mismatch,
              'missing_count': len(missing), 'mismatch_count': len(mismatch)}
    write(dest / 'VERIFICATION.json', json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    if missing or mismatch: raise SystemExit(1)

if __name__ == '__main__':
    main()
