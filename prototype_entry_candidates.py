"""Original GPL-3.0-only static entry-candidate model; no game data/decoder.

The caller supplies independently parsed export entries and resolved original
DIRECT import-call uses. This only proposes subdivisions of discovery ranges.
Neither these inputs nor agreement with an older map prove function boundaries,
ABI, execution, return behavior or overlay lifetime. Qualify spans separately.
"""
from bisect import bisect_right
from dataclasses import dataclass


@dataclass(frozen=True)
class DirectImportUse:
    module: str
    site: int
    entry: int


@dataclass(frozen=True)
class EntryCandidate:
    start: int
    end: int
    owner_start: int
    owner_end: int
    uses: tuple


def missing_import_entries(discovery_ranges, export_entries, uses, modules):
    """Select missing exported entry candidates used by explicit module scope.

    Ranges must be disjoint aligned half-open ELF32 spans. Uses must resolve to
    exactly registered export entries, not guessed offsets into one. An entry
    already at a discovery start is not missing. A proposed end is the next
    exported entry within the same owner, or that owner's end, NOT a certified
    function extent. All supplied exports are fences, even if not used in scope.
    Reject unknown selected modules, unmatched imports and unmapped exports;
    never silently fall back to a historical seed/address table. No I/O/writes.
    """
    def require(ok, message):
        if not ok:
            raise ValueError(message)

    def address(value, *, end=False):
        return type(value) is int and 0 <= value <= (0x100000000 if end else 0xfffffffc) and value % 4 == 0

    def module_key(value):
        return isinstance(value, str) and 0 < len(value) <= 128 and value.isascii() and all(32 < ord(c) < 127 for c in value)

    require(not isinstance(modules, (str, bytes)), 'Invalid explicit module scope')
    ranges = tuple(discovery_ranges)
    entries = tuple(export_entries)
    calls = tuple(uses)
    selected = tuple(modules)
    require(0 < len(ranges) <= 65536 and len(entries) <= 65536 and len(calls) <= 1000000,
            'Unsupported candidate input count')
    require(all(isinstance(r, (tuple, list)) and len(r) == 2 and
                address(r[0]) and address(r[1], end=True) and r[0] < r[1] for r in ranges),
            'Invalid discovery range')
    ranges = tuple(sorted(tuple(r) for r in ranges))
    require(all(a[1] <= b[0] for a,b in zip(ranges, ranges[1:])),
            'Overlapping discovery ranges')
    require(all(address(e) for e in entries) and len(entries) == len(set(entries)),
            'Invalid or duplicate export entries')
    require(selected and all(module_key(m) for m in selected) and len(selected) == len(set(selected)),
            'Invalid explicit module scope')
    starts = tuple(a for a,_ in ranges)
    def owner(entry):
        i = bisect_right(starts, entry)-1
        return ranges[i] if i >= 0 and entry < ranges[i][1] else None

    require(all(owner(e) is not None for e in entries), 'Export outside discovery ranges')
    exported = set(entries)
    require(all(isinstance(u, DirectImportUse) and module_key(u.module) and
                address(u.site) and address(u.entry) and u.entry in exported for u in calls),
            'Invalid direct import use or unregistered entry')
    supplied_modules = {u.module for u in calls}
    require(all(m in supplied_modules for m in selected), 'Unknown selected module')
    require(len({(u.module, u.site) for u in calls}) == len(calls), 'Duplicate direct import site')
    chosen = set(selected)
    start_set = set(starts)
    grouped = {}
    for use in calls:
        if use.module in chosen and use.entry not in start_set:
            grouped.setdefault(use.entry, []).append(use)
    ordered_exports = sorted(exported)
    result = []
    for entry in sorted(grouped):
        first,last = owner(entry)
        i = bisect_right(ordered_exports, entry)
        end = min(last, ordered_exports[i]) if i < len(ordered_exports) else last
        refs = tuple(sorted(grouped[entry], key=lambda u: (u.module, u.site)))
        result.append(EntryCandidate(entry, end, first, last, refs))
    return tuple(result)
