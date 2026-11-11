"""Basic-block control-flow graph construction."""
from dataclasses import dataclass
from .ir import Instr

@dataclass
class CFG:
    blocks: list[list[int]]
    succ: list[set[int]]
    pred: list[set[int]]
    loop_depth: list[int]
    instr_block: dict[int,int]

def build_cfg(program: list[Instr]) -> CFG:
    if not program: return CFG([],[],[],[],{})
    labels={i.target:n for n,i in enumerate(program) if i.op=="label"}
    leaders={0}
    for n,i in enumerate(program):
        if i.op=="label": leaders.add(n)
        if i.op in {"goto","if"}:
            leaders.add(labels[i.target])
            if n+1<len(program): leaders.add(n+1)
    starts=sorted(leaders); blocks=[list(range(s, starts[j+1] if j+1<len(starts) else len(program))) for j,s in enumerate(starts)]
    ib={i:b for b,blk in enumerate(blocks) for i in blk}; succ=[set() for _ in blocks]; pred=[set() for _ in blocks]
    for b,blk in enumerate(blocks):
        last=program[blk[-1]]
        if last.op in {"goto","if"}: succ[b].add(ib[labels[last.target]])
        if last.op!="goto" and b+1<len(blocks): succ[b].add(b+1)
    for b,ss in enumerate(succ):
        for x in ss: pred[x].add(b)
    depth=[0]*len(blocks); stack=[]
    def dfs(u):
        stack.append(u)
        for v in sorted(succ[u]):
            if v in stack:
                loop={v,u}; work=[u]
                while work:
                    x=work.pop()
                    for p in pred[x]:
                        if p not in loop: loop.add(p); work.append(p)
                for x in loop: depth[x]+=1
            elif not visited[v]: visited[v]=True; dfs(v)
        stack.pop()
    visited=[False]*len(blocks); visited[0]=True; dfs(0)
    return CFG(blocks,succ,pred,depth,ib)
