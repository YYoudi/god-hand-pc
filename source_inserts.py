"""Original GPL-3.0-only, hash-qualified insertion-only source transformation.

No game code/addresses/hooks are embedded. An operator-supplied private profile
must qualify the base and complete expected output. This checks text production,
not C++ semantics, read-only behavior, ABI, execution or copyright provenance.
"""
import hashlib
import re

LIMIT = 16 * 1024 * 1024
_DIGEST = re.compile(r'[0-9a-f]{64}\Z')


def apply_inserts(source, insertions, *, source_sha256, output_sha256, line_ending):
    if not isinstance(source, bytes) or not 0 < len(source) <= LIMIT:
        raise ValueError('Bounded immutable source bytes required')
    for value in (source_sha256, output_sha256):
        if not isinstance(value, str) or not _DIGEST.fullmatch(value):
            raise ValueError('Explicit lower-case source/output SHA-256 required')
    if hashlib.sha256(source).hexdigest() != source_sha256:
        raise ValueError('Source identity mismatch')
    if line_ending not in ('lf', 'crlf'):
        raise ValueError('Explicit LF/CRLF output required')
    if not isinstance(insertions, (tuple, list)) or not 1 <= len(insertions) <= 32:
        raise ValueError('Finite nonempty insertion profile required')
    try:
        text = source.decode('utf-8')
    except UnicodeDecodeError as error:
        raise ValueError('UTF-8 source required') from error
    text = text.replace('\r\n', '\n')
    if '\r' in text or '\0' in text:
        raise ValueError('Unsupported source control bytes')
    # Split only on LF, not Unicode separators accepted by str.splitlines().
    parts = text.split('\n')
    lines = [part + '\n' for part in parts[:-1]]
    if parts[-1]:
        lines.append(parts[-1])
    plan = {}
    for row in insertions:
        if not isinstance(row, dict) or set(row) != {'before_line', 'text'}:
            raise ValueError('Only insertion position and text are supported')
        index, payload = row['before_line'], row['text']
        if type(index) is not int or not 0 <= index <= len(lines) or index in plan:
            raise ValueError('Invalid or duplicate insertion boundary')
        if (not isinstance(payload, str) or not payload or not payload.endswith('\n')
                or '\r' in payload or '\0' in payload):
            raise ValueError('Nonempty canonical LF insertion text required')
        if len(payload.encode('utf-8')) > 64 * 1024:
            raise ValueError('Insertion exceeds budget')
        plan[index] = payload
    output = ''.join(plan.get(i, '') + line for i, line in enumerate(lines))
    output += plan.get(len(lines), '')
    if line_ending == 'crlf':
        output = output.replace('\n', '\r\n')
    blob = output.encode('utf-8')
    if len(blob) > LIMIT or hashlib.sha256(blob).hexdigest() != output_sha256:
        raise ValueError('Expected complete output identity mismatch')
    return blob
