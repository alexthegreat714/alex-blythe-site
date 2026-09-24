"""Readable charts from published aggregates only; never launches inference."""
import hashlib
import json
from pathlib import Path


def render(dest):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = json.loads((dest / 'cache-neutral-results.json').read_text())['rows']
    plt.rcParams.update({'font.family': 'Arial', 'font.size': 12,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'aero-hardware-20260924',
                         'axes.spines.top': False, 'axes.spines.right': False})
    systems = [('3090', 'RTX 3090', '#177E89'), ('spark', 'GB10 (Spark label)', '#c45932')]
    tasks = [('interactive', 'Interactive response'), ('agent_loop', 'Mocked agent loop'),
             ('engineering_validity', 'Validity response'), ('large_context', '32k-input task'),
             ('overnight', 'Campaign text task')]
    charts = dest / 'charts'
    charts.mkdir(exist_ok=True)

    def finish(fig, ax, name, title, subtitle, footer, left=.13):
        ax.set_axisbelow(True)
        ax.grid(axis='y', alpha=.2)
        fig.suptitle(title, x=.13, ha='left', fontsize=19, weight='bold')
        fig.text(.13, .90, subtitle, fontsize=11)
        fig.text(.13, .025, footer, fontsize=10)
        fig.subplots_adjust(left=left, right=.95, top=.78, bottom=.17)
        ax.legend(loc='lower left', bbox_to_anchor=(0,1.015), ncol=2, frameon=False, fontsize=11)
        target = charts / name
        fig.savefig(target, metadata={'Date': None})
        plt.close(fig)
        target.write_text('\n'.join(line.rstrip() for line in target.read_text(encoding='utf-8').splitlines())+'\n',
                          encoding='utf-8', newline='\n')

    for name, metric, title, unit, footer in [
        ('task_wall_time.svg','wall_seconds_median','Model response and mocked-loop time','Seconds; lower is faster','Inference only; no solver or real tool execution. Different Ollama versions.'),
        ('decode_tokens_per_second.svg','decode_tokens_per_second_median','Decode throughput by task','Output tokens / second','Server-reported decode timing; not total engineering workflow speed.'),
        ('gpu_energy_per_task.svg','gpu_energy_j_observed_median','Observed device energy by task','Joules','GPU / SoC domains differ; sampled telemetry, not whole-system wall energy.'),
    ]:
        fig, ax = plt.subplots(figsize=(10,6.6))
        for i,(system,label,color) in enumerate(systems):
            values=[next(r[metric] for r in rows if r['system_id']==system and r['workload']==task) for task,_ in tasks]
            bars=ax.barh([k+(i-.5)*.34 for k in range(len(tasks))],values,height=.3,color=color,label=label)
            ax.bar_label(bars,labels=[f'{v:,.3f}' if metric=='wall_seconds_median' else f'{v:,.1f}' for v in values],padding=4,fontsize=11)
        ax.set_yticks(range(len(tasks)),[label for _,label in tasks])
        ax.invert_yaxis()
        ax.set_xlim(0,ax.get_xlim()[1]*1.16)
        ax.set_xlabel(unit)
        finish(fig,ax,name,title,'Gemma 3 12B Q4_K_M · unique-prefix suite · median of 5 repeats',footer,left=.28)

    for name,metric,title,unit,scale,footer in [
        ('ttft_vs_context.svg','ttft_seconds_median','Time to first token vs context','Seconds',1,'Five repeats per point; no measured 3090 points at 64k or 128k.'),
        ('prefill_vs_context.svg','prefill_tokens_per_second_median','Fresh-prompt prefill vs context','Prompt tokens / second',1,'Different Ollama versions; not a silicon-only bandwidth measurement.'),
        ('gpu_memory_vs_context.svg','peak_gpu_memory_used_mib_median','Dedicated GPU memory vs context','MiB used',1,'3090 device-wide framebuffer counter. GB10 equivalent counter unavailable.'),
        ('host_memory_vs_context.svg','peak_system_memory_used_bytes_median','Host / unified memory vs context','GiB used',2**30,'System-wide counters include other allocations; not isolated model memory.'),
    ]:
        fig,ax=plt.subplots(figsize=(10,6.2))
        for system,label,color in systems:
            selected=sorted([r for r in rows if r['system_id']==system and r['workload']=='context_scaling' and r.get(metric) is not None],key=lambda r:r['context_setting'])
            if selected:
                ax.plot([r['context_setting']/1024 for r in selected],[r[metric]/scale for r in selected],marker='o',linewidth=2.5,color=color,label=label)
        ax.set_xscale('log',base=2)
        ax.set_xticks([4,8,16,32,64,128],['4k','8k','16k','32k','64k','128k'])
        ax.set_xlim(3.6,142)
        ax.set_ylim(bottom=0)
        ax.set_xlabel('Configured context window (tokens; k = 1,024)')
        ax.set_ylabel(unit)
        finish(fig,ax,name,title,'Gemma 3 12B Q4_K_M · unique-prefix suite · median of 5 repeats',footer)


if __name__=='__main__':
    site=Path(__file__).resolve().parents[1]
    dest=site/'public/demos/aero/hardware-benchmark-2026-09-24'
    render(dest)
    report=site/'src/content/research/rtx-3090-vs-gb10-aero-inference-benchmark.md'
    (dest/'REPORT.md').write_bytes(report.read_bytes())
    files={f.relative_to(dest).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()
           for f in sorted(dest.rglob('*')) if f.is_file() and f.name not in ('SHA256_MANIFEST.json','VERIFICATION.json')}
    (dest/'SHA256_MANIFEST.json').write_text(json.dumps({'algorithm':'SHA-256','files':files},indent=2)+'\n',encoding='utf-8',newline='\n')
    assert all(hashlib.sha256((dest/name).read_bytes()).hexdigest()==digest for name,digest in files.items())
    print(f'{len(files)} public artifact hashes verified; aggregate data unchanged.')
