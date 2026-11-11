"""Three-address-code parser and renderer."""
from dataclasses import dataclass
import re

@dataclass
class Instr:
    op: str
    dest: str | None = None
    operands: list[str] | None = None
    target: str | None = None

def defs(instr: Instr) -> list[str]:
    return [instr.dest] if instr.dest is not None else []

def uses(instr: Instr) -> list[str]:
    if instr.op in {"assign", "print", "if"}:
        vals = instr.operands or []
        return [x for x in vals if not re.fullmatch(r"-?\d+", x)]
    if instr.op == "bin":
        return [x for x in instr.operands or [] if not re.fullmatch(r"-?\d+", x)]
    return []

def parse_tac(text: str) -> list[Instr]:
    out=[]
    for n, raw in enumerate(text.splitlines(),1):
        s=raw.split('#',1)[0].strip()
        if not s: continue
        m=re.fullmatch(r"([A-Za-z_]\w*):",s)
        if m: out.append(Instr("label",target=m[1])); continue
        m=re.fullmatch(r"goto\s+(\w+)",s)
        if m: out.append(Instr("goto",target=m[1])); continue
        m=re.fullmatch(r"if\s+(\w+)\s+goto\s+(\w+)",s)
        if m: out.append(Instr("if",operands=[m[1]],target=m[2])); continue
        if s.startswith("print "):
            x=s[6:].strip()
            if re.fullmatch(r"\w+|-?\d+",x): out.append(Instr("print",operands=[x])); continue
        m=re.fullmatch(r"(\w+)\s*=\s*(\w+|-?\d+)(?:\s*([+*/%<>!-]=?|==)\s*(\w+|-?\d+))?",s)
        if m:
            d,a,op,b=m.groups()
            if op:
                if op not in {"+","-","*","/","%","<",">","<=",">=","==","!="}: raise ValueError(f"line {n}: invalid operator")
                out.append(Instr("bin",d,[a,b],op))
            else: out.append(Instr("assign",d,[a]))
            continue
        raise ValueError(f"line {n}: invalid TAC: {s}")
    labels={i.target for i in out if i.op=="label"}
    for n,i in enumerate(out,1):
        if i.op in {"goto","if"} and i.target not in labels: raise ValueError(f"line {n}: unknown label {i.target}")
    return out

def render(program: list[Instr], allocation=None) -> str:
    def v(x):
        if allocation is None or x not in allocation.mapping: return x
        loc=allocation.mapping[x]; return ("R" if loc.kind=="reg" else "M")+str(loc.index)
    lines=[]
    for i in program:
        if i.op=="label": lines.append(f"{i.target}:")
        elif i.op=="goto": lines.append(f"goto {i.target}")
        elif i.op=="if": lines.append(f"if {v(i.operands[0])} goto {i.target}")
        elif i.op=="print": lines.append("print "+v(i.operands[0]))
        elif i.op=="assign": lines.append(f"{v(i.dest)} = {v(i.operands[0])}")
        else: lines.append(f"{v(i.dest)} = {v(i.operands[0])} {i.target} {v(i.operands[1])}")
    return "\n".join(lines)
