from regalloc.ir import parse_tac
from regalloc.liveness import analyze
def test_interval_and_cost():
 l=analyze(parse_tac('a = 1\nb = a + 2\nprint b'))
 assert l.intervals['a'].start==1 and l.intervals['b'].end==4
 assert l.spill_cost['a']==2 and l.spill_cost['b']==2
