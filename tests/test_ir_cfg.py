from regalloc.ir import parse_tac,render,defs,uses
from regalloc.cfg import build_cfg
def test_roundtrip():
 p=parse_tac('x = 2\ny = x + x\nprint y'); assert parse_tac(render(p))==p
 assert defs(p[1])==['y'] and uses(p[1])==['x','x']
def test_error():
 try: parse_tac('bad line')
 except ValueError as e: assert 'line 1' in str(e)
 else: assert False
def test_cfg_loop():
 p=parse_tac('i = 0\nL:\ni = i + 1\nc = i < 2\nif c goto L\nprint i');g=build_cfg(p)
 assert any(g.loop_depth) and len(g.blocks)>=3
