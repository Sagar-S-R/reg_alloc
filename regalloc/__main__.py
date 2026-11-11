"""Command-line inspection of TAC allocation."""
import argparse
from pathlib import Path
from .ir import parse_tac,render
from .liveness import analyze
from .interpreter import run
from .allocators import ALLOCATORS
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True); s=sub.add_parser("show")
    s.add_argument("file"); s.add_argument("--k",type=int,default=3); s.add_argument("--alloc",choices=ALLOCATORS,default="paper"); a=p.parse_args()
    program=parse_tac(Path(a.file).read_text(encoding='utf-8')); live=analyze(program); alloc=ALLOCATORS[a.alloc](live,a.k)
    print("INSTRUCTIONS\n"+render(program)); print("\nINTERVALS\nvar start end spill_cost")
    for v in sorted(live.intervals):
        q=live.intervals[v]; print(v,q.start,q.end,live.spill_cost.get(v,0))
    print("\nALLOCATION")
    for v in sorted(alloc.mapping):
        loc=alloc.mapping[v]; print(f"{v} -> {'R' if loc.kind=='reg' else 'M'}{loc.index}")
    print("\nREWRITTEN TAC\n"+render(program,alloc))
    ref=run(program); got=run(program,alloc,a.k)
    print(f"\nreference output: {ref.output}\nallocated output: {got.output}\noutput matches: {'yes' if ref.output==got.output else 'no'}")
    print(f"instructions: {got.instrs_executed}; loads: {got.mem_loads}; stores: {got.mem_stores}")
if __name__=="__main__": main()
