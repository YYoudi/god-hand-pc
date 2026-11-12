"""Original GPL-3.0-only finite pointer-set span model; no game data/decoder.

Callers must provide independently code-backed pointer sets. A pointer-looking
data run is not enough. Unioning overlapping sets prevents one subarray from
silently swallowing entry fences supplied by another. Results remain candidate
spans, not function/CFG/ABI, valid-index-domain, runtime or ownership proofs.
"""
from bisect import bisect_right
from dataclasses import dataclass


@dataclass(frozen=True)
class TableEntryCandidate:
    start: int
    end: int
    owner_start: int
    owner_end: int
    sets: tuple


def missing_table_entries(discovery_ranges, pointer_sets):
    """Return missing entry spans fenced by ALL supplied code-backed sets.

    Identical entries/aliases within or across sets are valid; duplicate or
    overlapping discovery owners are not. Refuse unmapped/unaligned pointers
    instead of assigning a guessed body. Input objects are never changed.
    """
    def require(ok, message):
        if not ok:raise ValueError(message)
    def aligned(v, end=False):
        return type(v) is int and 0 <= v <= (0x100000000 if end else 0xfffffffc) and v % 4 == 0
    ranges=tuple(discovery_ranges);groups=tuple(tuple(g) for g in pointer_sets)
    require(0 < len(ranges) <= 65536 and 0 < len(groups) <= 4096 and
            all(0 < len(g) <= 4096 for g in groups), 'Unsupported table-candidate shape')
    require(all(isinstance(r,(tuple,list)) and len(r)==2 and aligned(r[0]) and
                aligned(r[1],True) and r[0]<r[1] for r in ranges), 'Invalid discovery range')
    ranges=tuple(sorted(tuple(r) for r in ranges))
    require(all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:])), 'Overlapping discovery ranges')
    require(all(aligned(v) for g in groups for v in g), 'Invalid table entry')
    starts=tuple(a for a,_ in ranges);start_set=set(starts)
    def owner(a):
        i=bisect_right(starts,a)-1
        return ranges[i] if i>=0 and a<ranges[i][1] else None
    membership={}
    for i,group in enumerate(groups):
        for a in set(group):membership.setdefault(a,[]).append(i)
    require(all(owner(a) is not None for a in membership), 'Table entry outside discovery ranges')
    fences=sorted(membership);result=[]
    for i,a in enumerate(fences):
        if a in start_set:continue
        first,last=owner(a)
        end=min(last,fences[i+1]) if i+1<len(fences) else last
        result.append(TableEntryCandidate(a,end,first,last,tuple(membership[a])))
    return tuple(result)
