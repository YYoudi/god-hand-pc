"""Original GPL-3.0-only finite-domain consistency model, no game data/decoder.

Callers supply full-span candidates and already decoded DIRECT-target
constraints. A consistent domain is not a proven SDK name, ABI, body boundary,
lifetime or runtime effect. Unknown targets must remain explicitly unverified.
"""


def refine_domains(domains, calls):
    """Return reduced immutable candidate domains without selecting arbitrarily.

    calls[(caller, candidate)] holds (known_callee, required_candidate) pairs.
    A singleton caller constrains a callee. Ambiguous callers are pruned only
    if a known target cannot satisfy their direct-target requirements. Multiple
    surviving candidates remain ambiguous. Contradictions raise, never fall
    back to an invented/old map. No input object is modified.
    """
    reduced = {node: set(values) for node, values in domains.items()}
    if not reduced or any(not values for values in reduced.values()):
        raise ValueError('Nonempty candidate domains required')
    constraints = {}
    for (caller, candidate), edges in calls.items():
        if caller not in reduced or candidate not in reduced[caller]:
            raise ValueError('Call constraint outside caller candidate domain')
        constraints[caller, candidate] = tuple(edges)
        if any(callee not in reduced for callee,_ in constraints[caller,candidate]):
            raise ValueError('Unknown callee is not a consistency constraint')
    changed = True
    while changed:
        changed = False
        for caller, values in reduced.items():
            surviving = {candidate for candidate in values if all(
                required in reduced[callee]
                for callee,required in constraints.get((caller,candidate), ()))}
            if not surviving:
                raise ValueError('Contradictory known direct-target constraints')
            if surviving != values:
                reduced[caller] = surviving; changed = True
        for caller, values in reduced.items():
            if len(values) != 1:
                continue
            for callee,required in constraints.get((caller,next(iter(values))), ()):
                if required not in reduced[callee]:
                    raise ValueError('Contradictory singleton target')
                if reduced[callee] != {required}:
                    reduced[callee] = {required}; changed = True
    return {node: frozenset(values) for node, values in reduced.items()}
