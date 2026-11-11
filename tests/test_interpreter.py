from regalloc.ir import parse_tac
from regalloc.interpreter import run
def test_reference():
 r=run(parse_tac('a = 7\nb = a * 2\nprint b')); assert r.output==[14] and r.mem_loads==0
def test_allocated_memory_counts():
 from regalloc.allocators import Allocation,Location
 p=parse_tac('x = 3\ny = x + x\nprint y')
 a=Allocation({'x':Location('mem',0),'y':Location('mem',1)},1)
 r=run(p,a,1); assert r.output==[6] and r.mem_loads==3 and r.mem_stores==2
