"""Deterministic bounded synthetic TAC generator."""
import random
def generate(n_instrs:int, seed:int)->str:
    rng=random.Random(seed); lines=[f"v{i} = {rng.randint(1,20)}" for i in range(8)]
    for i in range(max(0,n_instrs-8)):
        a,b=f"v{rng.randrange(8)}",f"v{rng.randrange(8)}"; d=f"v{8+i}"
        lines.append(f"{d} = {a} {rng.choice(['+','-','*'])} {b}")
    lines.append(f"print v{max(7,n_instrs-1)}")
    return "\n".join(lines)+"\n"
