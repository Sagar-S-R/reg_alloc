"""Run allocation quality and timing experiments."""
import csv
from pathlib import Path
import time
import math
from statistics import median
from regalloc.ir import parse_tac
from regalloc.liveness import analyze
from regalloc.interpreter import run
from regalloc.allocators import ALLOCATORS
from regalloc.bench_gen import generate

ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'results'; out.mkdir(exist_ok=True); rows=[]
    for path in sorted((ROOT/'benchmarks').glob('*.tac')):
        p=parse_tac(path.read_text(encoding='utf-8')); live=analyze(p); ref=run(p)
        for k in [2,3,4,6,8,16]:
            for name,fn in ALLOCATORS.items():
                a=fn(live,k); result=run(p,a,k); match=result.output==ref.output
                assert match,(path.name,k,name,result.output,ref.output)
                rows.append(dict(benchmark=path.name,k=k,allocator=name,spilled_vars=len(a.spilled),mem_loads=result.mem_loads,mem_stores=result.mem_stores,mem_ops=result.mem_loads+result.mem_stores,instrs_executed=result.instrs_executed,output_matches=match))
    with (out/'quality.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    timing=[]
    for n in [100,250,500,1000,2000,4000,8000]:
        p=parse_tac(generate(n,17)); live=analyze(p)
        for name in ['paper','coloring']:
            samples=[]
            for _ in range(5):
                t=time.perf_counter();ALLOCATORS[name](live,8);samples.append(time.perf_counter()-t)
            timing.append(dict(n_instrs=n,allocator=name,seconds=median(samples)))
    with (out/'timing.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=timing[0]);w.writeheader();w.writerows(timing)
    names=list(ALLOCATORS); lines=['# Experiment summary','','## Mem operations by benchmark and k','','| Benchmark | k | '+ ' | '.join(names)+' |','|---|---:|'+'---:|'*len(names)]
    for bench in sorted({r['benchmark'] for r in rows}):
        for k in [2,3,4,6,8,16]:
            vals=[next(r['mem_ops'] for r in rows if r['benchmark']==bench and r['k']==k and r['allocator']==name) for name in names]
            lines.append(f"| {bench} | {k} | "+' | '.join(map(str,vals))+' |')
    lines += ['', '## Cost spill heuristic reduction versus paper', '', '| Benchmark | k | Reduction (%) |','|---|---:|---:|']
    for bench in sorted({r['benchmark'] for r in rows}):
        for k in [2,3,4,6,8,16]:
            paper=next(r['mem_ops'] for r in rows if r['benchmark']==bench and r['k']==k and r['allocator']=='paper'); cost=next(r['mem_ops'] for r in rows if r['benchmark']==bench and r['k']==k and r['allocator']=='cost')
            pct=100*(paper-cost)/paper if paper else 0
            lines.append(f'| {bench} | {k} | {pct:.1f} |')
    lines += ['', '## Allocation timing', '', '| Instructions | Linear scan | Coloring |','|---:|---:|---:|']
    for n in [100,250,500,1000,2000,4000,8000]:
        vals=[next(r['seconds'] for r in timing if r['n_instrs']==n and r['allocator']==name) for name in ['paper','coloring']]
        lines.append(f'| {n} | {vals[0]:.6g} | {vals[1]:.6g} |')
    (out/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    try:
        import matplotlib.pyplot as plt
        figdir=out/'figures';figdir.mkdir(exist_ok=True)
        benches=sorted({r['benchmark'] for r in rows}); fig,axes=plt.subplots(math.ceil(len(benches)/3),3,figsize=(14,3*math.ceil(len(benches)/3))); axes=list(axes.flat)
        for ax,bench in zip(axes,benches):
            for name in names: ax.plot([2,3,4,6,8,16],[next(r['mem_ops'] for r in rows if r['benchmark']==bench and r['k']==k and r['allocator']==name) for k in [2,3,4,6,8,16]],marker='o',label=name)
            ax.set_title(bench);ax.set_xlabel('Registers (k)');ax.set_ylabel('Memory operations');ax.legend(fontsize=7)
        for ax in axes[len(benches):]: ax.remove()
        fig.tight_layout();fig.savefig(figdir/'fig1_mem_ops.png');plt.close(fig)
        fig,ax=plt.subplots()
        for name in ['paper','coloring']: ax.loglog([n for n in [100,250,500,1000,2000,4000,8000]],[next(r['seconds'] for r in timing if r['n_instrs']==n and r['allocator']==name) for n in [100,250,500,1000,2000,4000,8000]],marker='o',label=name)
        ax.set_xlabel('Instructions');ax.set_ylabel('Allocation time (s)');ax.legend();fig.tight_layout();fig.savefig(out/'figures'/'fig2_timing.png');plt.close(fig)
        fig,ax=plt.subplots(); benches=sorted({r['benchmark'] for r in rows}); width=.25
        for j,name in enumerate(['paper','cost','cost_len']): ax.bar([i+(j-1)*width for i in range(len(benches))],[next(r['mem_ops'] for r in rows if r['benchmark']==b and r['k']==4 and r['allocator']==name) for b in benches],width,label=name)
        ax.set_xticks(range(len(benches)),benches,rotation=35,ha='right');ax.set_ylabel('Memory operations (k=4)');ax.legend();fig.tight_layout();fig.savefig(out/'figures'/'fig3_k4.png');plt.close(fig)
    except ImportError: print('matplotlib unavailable; CSV and Markdown reports generated')
    print(f"Wrote {len(rows)} quality rows and {len(timing)} timing rows to {out}")
if __name__=='__main__':main()
