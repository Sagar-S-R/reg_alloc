from pathlib import Path
from regalloc.ir import parse_tac
from regalloc.liveness import analyze
from regalloc.interpreter import run
from regalloc.allocators import ALLOCATORS
def test_benchmarks():
 for f in Path('benchmarks').glob('*.tac'):
  p=parse_tac(f.read_text(encoding='utf-8')); l=analyze(p); ref=run(p,max_steps=100000)
  for k in [1,2,3,4,8]:
   for name,fn in ALLOCATORS.items():
    a=fn(l,k); assert run(p,a,k,max_steps=100000).output==ref.output
def test_hot_cold_cost():
 p=parse_tac(Path('benchmarks/hot_cold.tac').read_text(encoding='utf-8'));l=analyze(p)
 paper=ALLOCATORS['paper'](l,2);cost=ALLOCATORS['cost'](l,2)
 rp=run(p,paper,2);rc=run(p,cost,2)
 assert 'y' in cost.spilled and 'x' not in cost.spilled
 assert rc.mem_loads+rc.mem_stores < rp.mem_loads+rp.mem_stores
