"""Reference and allocated TAC interpreter."""
from dataclasses import dataclass
import re
from .ir import Instr

@dataclass
class RunResult:
    output:list[int]
    instrs_executed:int
    mem_loads:int=0
    mem_stores:int=0

def run(program:list[Instr], allocation=None, k:int|None=None, max_steps:int=10_000_000)->RunResult:
    labels={i.target:n for n,i in enumerate(program) if i.op=="label"}; vars={}; regs=[0]*(k or (allocation.k if allocation else 0)); mem={}; out=[]; pc=steps=loads=stores=0
    def read(x):
        nonlocal loads
        if re.fullmatch(r"-?\d+",x): return int(x)
        if allocation is None:
            if x not in vars: raise ValueError(f"undefined variable: {x}")
            return vars[x]
        loc=allocation.mapping[x]
        if loc.kind=="mem": loads+=1; return mem.get(loc.index,0)
        return regs[loc.index]
    def write(x,val):
        nonlocal stores
        if allocation is None: vars[x]=val; return
        loc=allocation.mapping[x]
        if loc.kind=="mem": stores+=1; mem[loc.index]=val
        else: regs[loc.index]=val
    while pc<len(program):
        if steps>=max_steps: raise RuntimeError("maximum instruction steps exceeded")
        i=program[pc]; steps+=1; nxt=pc+1
        if i.op=="label": pass
        elif i.op=="goto": nxt=labels[i.target]
        elif i.op=="if":
            if read(i.operands[0])!=0: nxt=labels[i.target]
        elif i.op=="print": out.append(read(i.operands[0]))
        elif i.op=="assign": write(i.dest,read(i.operands[0]))
        elif i.op=="bin":
            a,b=map(read,i.operands); op=i.target
            if op=="/" and b==0: raise ZeroDivisionError("division by zero")
            val={"+":lambda:a+b,"-":lambda:a-b,"*":lambda:a*b,"/":lambda:a//b,"%":lambda:a%b,"<":lambda:int(a<b),">":lambda:int(a>b),"<=":lambda:int(a<=b),">=":lambda:int(a>=b),"==":lambda:int(a==b),"!=":lambda:int(a!=b)}[op]()
            write(i.dest,val)
        pc=nxt
    return RunResult(out,steps,loads,stores)
