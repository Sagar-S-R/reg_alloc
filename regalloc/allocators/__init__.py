"""Register allocation types and registry."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Location:
    kind:str
    index:int
@dataclass
class Allocation:
    mapping:dict[str,Location]
    k:int
    @property
    def spilled(self)->set[str]: return {v for v,l in self.mapping.items() if l.kind=="mem"}
from .linear_scan import allocate_paper,allocate_cost,allocate_cost_len
from .graph_coloring import allocate_coloring
ALLOCATORS={"paper":allocate_paper,"cost":allocate_cost,"cost_len":allocate_cost_len,"coloring":allocate_coloring}
