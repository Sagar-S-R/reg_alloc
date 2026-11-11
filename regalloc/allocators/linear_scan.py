"""Single-range linear-scan register allocation."""
from . import Allocation,Location
from .heuristics import choose_victim
def _allocate(liveness,k,strategy):
    intervals=liveness.intervals; mapping={}; active=[]; free=list(range(k))
    for v in sorted(intervals,key=lambda x:(intervals[x].start,x)):
        iv=intervals[v]; kept=[]
        for a in active:
            if intervals[a].end<iv.start: free.append(mapping[a].index)
            else: kept.append(a)
        active=kept; free.sort()
        if free: mapping[v]=Location("reg",free.pop(0)); active.append(v)
        else:
            victim=choose_victim(active+[v],intervals,liveness.spill_cost,strategy)
            if victim==v: mapping[v]=Location("mem",sum(x.kind=="mem" for x in mapping.values()))
            else:
                reg=mapping[victim].index; mapping[v]=Location("reg",reg); mapping[victim]=Location("mem",sum(x.kind=="mem" for x in mapping.values())); active.remove(victim); active.append(v)
        active.sort(key=lambda x:(intervals[x].end,x))
    return Allocation(mapping,k)
def allocate_paper(liveness,k): return _allocate(liveness,k,"paper")
def allocate_cost(liveness,k): return _allocate(liveness,k,"cost")
def allocate_cost_len(liveness,k): return _allocate(liveness,k,"cost_len")
