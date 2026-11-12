"""Original GPL-3.0-only ELF metadata policy for PRIVATE discovery inputs.

No game bytes, addresses, names or instruction decoder. This is not a runnable
ELF repair, SDK/ABI qualification or a promise of complete recompiler discovery.
"""
from dataclasses import dataclass
import struct

LIMIT = 32 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class DiscoveryInput:
    data: bytes
    changes: tuple
    load_segments: int


def text_discovery_copy(source):
    """Clear non-.text section EXECINSTR flags in a NEW immutable byte string.

    All PT_LOAD file bytes, file length and every other byte must remain equal.
    Reject metadata edits inside a load segment, rather than silently weakening
    that invariant. This policy narrows discovery only; it never edits opcodes.
    The original is not opened/written here. Callers keep the result private.
    """
    require(isinstance(source, bytes) and 52 <= len(source) <= LIMIT,
            'Expected bounded immutable ELF bytes')
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', source)
    ident, _, machine, version, _, phoff, shoff, _, ehsize, phsize, phcount, shsize, shcount, names_index = h
    require(ident[:7] == b'\x7fELF\x01\x01\x01' and machine == 8 and version == 1,
            'Expected little-endian ELF32 MIPS version 1')
    require(ehsize == 52 and phsize == 32 and shsize == 40 and
            0 < phcount <= 64 and 0 < shcount <= 256 and 0 < names_index < shcount,
            'Unsupported ELF table shape')

    def span(offset, size):
        require(0 <= offset <= len(source) and 0 <= size <= len(source)-offset,
                'ELF range outside file')
        return source[offset:offset+size]

    span(phoff, phsize*phcount); span(shoff, shsize*shcount)
    require(phoff >= ehsize and shoff >= ehsize and
            (phoff+phsize*phcount <= shoff or shoff+shsize*shcount <= phoff),
            'Overlapping ELF header tables')
    programs = [struct.unpack_from('<8I', source, phoff+i*phsize) for i in range(phcount)]
    loads = []
    for p in programs:
        if p[0] != 1:
            continue
        require(p[4] <= p[5], 'ELF load file size exceeds memory size')
        require(p[2]+p[5] <= 0x100000000, 'ELF load virtual range wraps ELF32 space')
        span(p[1], p[4]); loads.append((p[1], p[4]))
    require(loads, 'No ELF load segments')
    sections = [struct.unpack_from('<10I', source, shoff+i*shsize) for i in range(shcount)]
    names = sections[names_index]
    require(names[1] == 3, 'ELF section-name table must be STRTAB')
    pool = span(names[4], names[5])
    require(pool and len(pool) <= 1024*1024 and pool[0] == 0, 'Invalid ELF section names')

    def name(section):
        start = section[0]
        require(start < len(pool), 'Section-name offset outside table')
        end = pool.find(b'\0', start)
        require(end >= start and end-start <= 255, 'Unterminated/oversized section name')
        try:
            return pool[start:end].decode('ascii')
        except UnicodeDecodeError as error:
            raise ValueError('Non-ASCII section name') from error

    labels = [name(s) for s in sections]
    text = [s for s,n in zip(sections,labels) if n == '.text']
    require(len(text) == 1 and text[0][1] == 1 and text[0][2] & 6 == 6 and
            text[0][5] > 0, 'Expected one nonempty allocated executable .text section')
    span(text[0][4], text[0][5])
    t = text[0]
    require(any(p[0] == 1 and p[1] <= t[4] and t[4]+t[5] <= p[1]+p[4]
                and p[2]+t[4]-p[1] == t[3] for p in programs),
            '.text is not coherently mapped by PT_LOAD file bytes')
    result = bytearray(source); changes = []
    for i,(s,label) in enumerate(zip(sections,labels)):
        if label == '.text' or not s[2] & 4:
            continue
        offset = shoff+i*shsize+8
        require(all(offset+4 <= start or start+size <= offset for start,size in loads),
                'Discovery metadata edit overlaps PT_LOAD bytes')
        struct.pack_into('<I', result, offset, s[2] & ~4)
        changes.append((i, offset, s[2], s[2] & ~4))
    data = bytes(result)
    require(all(data[start:start+size] == source[start:start+size] for start,size in loads),
            'Discovery policy changed PT_LOAD bytes')
    return DiscoveryInput(data, tuple(changes), len(loads))
