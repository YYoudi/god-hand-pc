"""Original GPL-3.0-only experimental generic-runtime patch, NOT game adoption.

Only the pinned upstream EeScheduler.cpp is accepted. Generated game source is
not an input. The candidate is written to a NEW ignored .local file; neither
the supplied source nor existing builds/libraries/profiles are changed.
"""
from pathlib import Path
import argparse
import hashlib

ROOT = Path(__file__).resolve().parent
SOURCE_SHA256 = '80297ca782b38abfefc3a1e53059dab8b6e05dcf3b2d136266f13cf65b88da4f'
CANDIDATE_SHA256 = 'eef04f79134fc139de2876274b028dbaee88e25496bb6707ff22eb7329b197a7'
UPSTREAM_REVISION = '1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a'

# Context is GPL upstream runtime, not game-derived source or an address map.
# Save the shared state while its owner still exists; skip only that retired
# dispatch's later catch read. Ordinary live transfers keep the original save.
EDITS = (
    ('thread_local bool t_onEeThread = false;',
     'thread_local bool t_onEeThread = false;\n'
     '    // Context may be retired by ExitThread/ExitDeleteThread before transfer unwind.\n'
     '    thread_local bool t_dispatchContextRetired = false;'),
    ('            loadSharedVu0Random(context);\n            function(',
     '            t_dispatchContextRetired = false;\n'
     '            loadSharedVu0Random(context);\n            function('),
    ('            ++g_loopStats.transfers;\n            saveSharedVu0Random(context);',
     '            ++g_loopStats.transfers;\n'
     '            if (!t_dispatchContextRetired)\n'
     '                saveSharedVu0Random(context);'),
    ('    const uint32_t ownedStack = deleteThreadRecord && exiting->ownsStack ? exiting->stack : 0u;\n'
     '    makeDormant(*exiting);',
     '    const uint32_t ownedStack = deleteThreadRecord && exiting->ownsStack ? exiting->stack : 0u;\n'
     '    // Preserve shared VU0 state before makeDormant clears invocations or erase frees context.\n'
     '    saveSharedVu0Random(exiting->activeContext());\n'
     '    t_dispatchContextRetired = true;\n'
     '    makeDormant(*exiting);'),
    ('    invocation.sequence = ++m_invocationSequence;\n'
     '    owner->invocations.push_back(std::move(invocation));',
     '    invocation.sequence = ++m_invocationSequence;\n'
     '    // push_back can move the currently executing invocation context.\n'
     '    saveSharedVu0Random(owner->activeContext());\n'
     '    t_dispatchContextRetired = true;\n'
     '    owner->invocations.push_back(std::move(invocation));'),
    ('    assert(!invocations.empty());\n    for (auto it = invocations.rbegin();',
     '    assert(!invocations.empty());\n'
     '    // Preserve state before any growth invalidates the dispatched context.\n'
     '    saveSharedVu0Random(owner->activeContext());\n'
     '    t_dispatchContextRetired = true;\n'
     '    for (auto it = invocations.rbegin();'),
)


def apply_unique_edits(text, edits):
    """All changes are computed before any file is opened for writing."""
    for before, after in edits:
        if not before or before == after or text.count(before) != 1:
            raise ValueError('Patch context is missing, ambiguous or unchanged')
        text = text.replace(before, after)
    return text


def render_candidate(source):
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unrecognized generic runtime revision; source left unchanged')
    text = source.decode('utf-8').replace('\r\n', '\n')
    # Explicit byte policy of the actually compiled Windows candidate. Do not
    # let the host platform silently choose LF/CRLF or bypass a failed hash.
    result = apply_unique_edits(text, EDITS).replace('\n', '\r\n').encode('utf-8')
    if hashlib.sha256(result).hexdigest() != CANDIDATE_SHA256:
        raise ValueError('Candidate fingerprint mismatch; no output written')
    return result


def write_new_candidate(destination, data, root=ROOT):
    private = (Path(root) / '.local').resolve()
    target = Path(destination).resolve()
    if not target.is_relative_to(private) or target == private:
        raise ValueError('Candidate must stay inside this checkout\'s ignored .local directory')
    if target.suffix != '.cpp':
        raise ValueError('Expected a new private .cpp output')
    if not target.parent.is_dir():
        raise ValueError('Create the private output directory explicitly first')
    with target.open('xb') as stream:
        stream.write(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True,
                        help='Pinned upstream generic EeScheduler.cpp, never game code')
    parser.add_argument('--output', type=Path, required=True,
                        help='NEW .cpp path within this checkout\'s ignored .local directory')
    args = parser.parse_args(argv)
    try:
        original = args.source.read_bytes()
        candidate = render_candidate(original)
        if args.source.resolve() == args.output.resolve():
            raise ValueError('Never overwrite the supplied source')
        write_new_candidate(args.output, candidate)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, str(error) + '\n')
    print('Experimental scheduler candidate written; no game/build/profile was modified.')
    print('Candidate SHA-256: ' + CANDIDATE_SHA256)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
