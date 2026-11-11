"""Simplified Chaitin-Briggs graph coloring allocator."""
from . import Allocation,Location
from regalloc.ir import defs
import heapq
def allocate_coloring(liveness,k):
    graph={v:set() for v in liveness.intervals}
    for i,live in enumerate(liveness.live_after):
        for d in defs(liveness.program[i]):
            for v in live:
                if v!=d: graph[d].add(v);graph[v].add(d)
    degree={v:len(ns) for v,ns in graph.items()}; remaining=set(graph); stack=[]
    easy=[v for v in remaining if degree[v]<k]; heapq.heapify(easy)
    risky=[(liveness.spill_cost.get(v,0)/max(1,degree[v]),v) for v in remaining]; heapq.heapify(risky)
    while remaining:
        while easy and easy[0] not in remaining: heapq.heappop(easy)
        if easy:
            v=heapq.heappop(easy); potential=False
        else:
            while risky and risky[0][1] not in remaining: heapq.heappop(risky)
            _,v=heapq.heappop(risky); potential=True
        stack.append((v,potential)); remaining.remove(v)
        for neighbor in graph[v] & remaining:
            degree[neighbor]-=1
            heapq.heappush(risky,(liveness.spill_cost.get(neighbor,0)/max(1,degree[neighbor]),neighbor))
            if degree[neighbor]<k: heapq.heappush(easy,neighbor)
    mapping={}; slots=0
    while stack:
        v,_=stack.pop(); used={mapping[n].index for n in graph[v] if n in mapping and mapping[n].kind=="reg"}; avail=next((r for r in range(k) if r not in used),None)
        if avail is None: mapping[v]=Location("mem",slots);slots+=1
        else: mapping[v]=Location("reg",avail)
    return Allocation(mapping,k)
