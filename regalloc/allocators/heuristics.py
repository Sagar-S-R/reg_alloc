"""Pure linear-scan victim selection policies."""
def choose_victim(candidates, intervals, costs, strategy):
    key={"paper":lambda v:(-intervals[v].end,v),"cost":lambda v:(costs.get(v,0),v),"cost_len":lambda v:(costs.get(v,0)/max(1,intervals[v].end-intervals[v].start+1),v)}[strategy]
    return min(candidates,key=key)
