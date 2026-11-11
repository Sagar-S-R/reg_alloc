"""Block liveness, single-range intervals, and spill costs."""
from dataclasses import dataclass
from .ir import Instr, defs, uses
from .cfg import CFG, build_cfg
@dataclass
class Interval:
    start:int; end:int
@dataclass
class Liveness:
    cfg:CFG; live_in:list[set[str]]; live_out:list[set[str]]; intervals:dict[str,Interval]; spill_cost:dict[str,int]; live_after:list[set[str]]
    program:list[Instr]
def analyze(program:list[Instr])->Liveness:
    cfg=build_cfg(program); n=len(cfg.blocks); use=[set() for _ in range(n)]; de=[set() for _ in range(n)]
    for b,blk in enumerate(cfg.blocks):
        for i in blk:
            use[b]|=set(uses(program[i]))-de[b]; de[b]|=set(defs(program[i]))
    li=[set() for _ in range(n)]; lo=[set() for _ in range(n)]; change=True
    while change:
        change=False
        for b in range(n-1,-1,-1):
            out=set().union(*(li[s] for s in cfg.succ[b])) if cfg.succ[b] else set(); inn=use[b]|(out-de[b])
            if out!=lo[b] or inn!=li[b]: lo[b]=out;li[b]=inn;change=True
    after=[set() for _ in program]; positions={}; costs={}
    for b,blk in enumerate(cfg.blocks):
        live=set(lo[b])
        for i in reversed(blk):
            after[i]=set(live)
            for v in uses(program[i])+defs(program[i]):
                pos=2*i+(1 if v in defs(program[i]) else 0); positions.setdefault(v,[]).append(pos); costs[v]=costs.get(v,0)+10**cfg.loop_depth[b]
            live=(live-set(defs(program[i])))|set(uses(program[i]))
    for b,blk in enumerate(cfg.blocks):
        for v in li[b]: positions.setdefault(v,[]).append(2*blk[0])
        for v in lo[b]: positions.setdefault(v,[]).append(2*blk[-1]+1)
    intervals={v:Interval(min(ps),max(ps)) for v,ps in positions.items()}
    return Liveness(cfg,li,lo,intervals,costs,after,program)
