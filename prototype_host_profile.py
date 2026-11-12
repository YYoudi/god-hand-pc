"""Original GPL-3.0-only host-value derivation, no game words/address table.

The reviewed policy stores hash-only windows/field kinds for PREVIOUSLY qualified
prototype roles. This is not semantic discovery, a disassembler, CFG/entry/ABI
proof, or observation of a new native run. Populated results remain private.
"""
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import struct

from prototype_sdk import integer, require
from prototype_sdk_inputs import digest, identity
from prototype_host_sources import parameter

# Original host policy and invented module-API test values, NOT game parameters.
HOST_CONSTANTS = dict(ram_bytes=32*1024*1024, guest_mask=(1 << 28)-1,
    max_module_bytes=16*1024*1024, minimum_pointer=1024*1024,
    invented_return_pc=0x12340, invented_result=0x12345678,
    invented_test_slot=28*1024*1024, diagnostic_pad_bytes=512,
    warp_guard_bytes=48, player_guard_bytes=1536,
    snr_magic24=int.from_bytes(b'SNR', 'little'), mask24=(1 << 24)-1)


@dataclass(frozen=True)
class View:
    base: int
    blob: bytes

    def __post_init__(self):
        integer(self.base)
        require(self.base % 4 == 0 and type(self.blob) is bytes and
                32 <= len(self.blob) <= 24*1024*1024 and
                self.base+len(self.blob) <= 1 << 32, 'Bounded aligned immutable view required')


def fingerprint_windows(views, anchors):
    """One bounded aligned scan per view/size, returning only requested hashes.

    No literal game needle is embedded, old address map used, or unaligned match
    silently skipped. Missing and multiple matches both refuse. The window is
    NOT a complete function body or a proof of a genuine entry point.
    """
    wanted = defaultdict(set)
    for row in anchors:
        require(type(row) is dict and set(row) == {'view', 'window_bytes', 'sha256'} and
                row['view'] in views and type(row['window_bytes']) is int and
                row['window_bytes'] in (32, 64, 128), 'Unsupported fingerprint window')
        identity(row['sha256'])
        wanted[(row['view'], row['window_bytes'])].add(row['sha256'])
    require(0 < len(anchors) <= 256 and len(views) <= 8, 'Finite fingerprint/view scope required')
    found = {}
    for (name, size), hashes in wanted.items():
        blob = views[name].blob
        hits = {h: [] for h in hashes}
        for offset in range(0, len(blob)-size+1, 4):
            h = digest(blob[offset:offset+size])
            if h in hits:
                hits[h].append(offset)
                require(len(hits[h]) <= 1, 'Ambiguous aligned fingerprint')
        for h, positions in hits.items():
            require(len(positions) == 1, 'Missing aligned fingerprint')
            found[(name, size, h)] = positions[0]
    return found


def signed16(word):
    value = word & 65535
    return value-65536 if value & 32768 else value


def preserves_register(word, reg):
    """Small closed no-write check ONLY between the chosen LUI and operand.

    JR is a non-writer to this register; allowing its encoded delay-slot operand
    is not CFG/return-path or executed-delay-slot proof. Unknowns refuse.
    """
    op, rs, rt, rd, fn = word >> 26, word >> 21 & 31, word >> 16 & 31, word >> 11 & 31, word & 63
    if op in (8, 9, 13, 15, 24, 25, 32, 33, 35, 36, 37, 55):
        return rt != reg
    if op == 0 and fn == 8:
        return True
    if op == 0 and fn in (0, 2, 3, 0x21, 0x25, 0x2d):
        return rd != reg
    return False


def extract_operand(view, offset, row):
    blob = view.blob
    word = struct.unpack_from('<I', blob, offset)[0]
    op, rs, rt = word >> 26, word >> 21 & 31, word >> 16 & 31
    kind = row['kind']
    if kind in ('simm16', 'uimm16'):
        require((op, rs, rt) == (row['opcode'], row['rs'], row['rt']) and
                op in (9, 15, 25, 35, 43, 49, 55, 57), 'Qualified operand shape differs')
        require(type(row['shift']) is int and row['shift'] in (0, 16) and
                type(row['negate']) is bool, 'Unsupported operand transformation')
        require((kind == 'uimm16' and op == 15 and rs == 0 and row['shift'] == 16 and not row['negate']) or
                (kind == 'simm16' and op != 15 and row['shift'] == 0), 'Wrong immediate semantics')
        value = signed16(word) if kind == 'simm16' else word & 65535
        value <<= row['shift']
        return -value if row['negate'] else value
    require(kind == 'lui-address' and op == 15 and rs == 0 and 0 < rt == row['high_register'] < 32,
            'Qualified LUI shape differs')
    distance = row['low_word']
    require(type(distance) is int and 1 <= distance <= 3 and offset+(distance+1)*4 <= len(blob),
            'Bounded LUI operand distance required')
    for i in range(1, distance):
        require(preserves_register(struct.unpack_from('<I', blob, offset+i*4)[0], rt),
                'Unknown/clobber between qualified LUI and operand')
    low = struct.unpack_from('<I', blob, offset+distance*4)[0]
    require(low >> 21 & 31 == rt and low >> 26 == row['low_opcode'] and
            low >> 16 & 31 == row['low_target'] and row['low_opcode'] in (9, 25, 35, 43, 55),
            'Qualified low operand shape differs')
    return (((word & 65535) << 16)+signed16(low)) & 0xffffffff


def literal(value, style):
    integer(value)
    require(type(style) is dict and set(style) == {'width', 'suffix'} and
            type(style['width']) is int and 0 <= style['width'] <= 8 and
            style['suffix'] in ('', 'u', 'U'), 'Explicit numeric spelling required')
    return parameter('0x'+format(value, '0'+str(style['width'])+'x')+style['suffix'], 'u32')


def derive_parameters(selectors, views, modules, roots):
    require(type(selectors) is dict and 0 < len(selectors) <= 256 and
            all(re.fullmatch('[A-Z][A-Z0-9_]{0,63}', k) for k in selectors), 'Finite named selectors required')
    anchors = [r['anchor'] for r in selectors.values() if 'anchor' in r]
    found = fingerprint_windows(views, anchors)
    results, evidence, active = {}, {}, set()

    def resolve(key):
        require(key in selectors and key not in active, 'Unknown/cyclic parameter alias')
        if key in results:
            return results[key]
        active.add(key)
        row = selectors[key]
        require(type(row) is dict, 'Selector record required')
        kind = row['kind']
        if kind == 'include':
            path = PurePosixPath(row['path'])
            require(set(row) == {'kind', 'root', 'path'} and row['root'] in roots and
                    not path.is_absolute() and '..' not in path.parts and '\\' not in row['path'],
                    'Invalid original include selector')
            result = parameter((Path(roots[row['root']])/Path(path)).as_posix(), 'include')
            evidence[key] = dict(kind=kind, root=row['root'], relative_path=row['path'])
        else:
            value = None
            if kind == 'host':
                require(set(row) == {'kind', 'name', 'format'} and row['name'] in HOST_CONSTANTS,
                        'Unknown original host constant')
                value = HOST_CONSTANTS[row['name']]
            elif kind in ('module-base', 'module-end'):
                require(set(row) == {'kind', 'module', 'format'} and row['module'] in modules,
                        'Unqualified module selector')
                base, size = modules[row['module']]
                integer(base); integer(size, 60, 16*1024*1024)
                require(base % 4 == 0 and base+size <= 32*1024*1024, 'Observed module extent outside selected RAM')
                value = base+(size if kind == 'module-end' else 0)
            elif kind == 'alias':
                require(set(row) == {'kind', 'parameter', 'add', 'format'} and
                        type(row['add']) is int and row['add'] in (0, 4, 8), 'Unsupported scalar alias')
                previous = resolve(row['parameter'])
                parameter(previous, 'u32')
                value = int(previous.rstrip('uU'), 16)+row['add']
            elif kind in ('vaddr', 'simm16', 'uimm16', 'lui-address'):
                fields = {'kind', 'anchor', 'format'}
                if kind in ('simm16', 'uimm16'):
                    fields |= {'opcode', 'rs', 'rt', 'shift', 'negate'}
                if kind == 'lui-address':
                    fields |= {'low_word', 'high_register', 'low_opcode', 'low_target'}
                require(set(row) == fields, 'Unexpected fingerprint selector fields')
                a = row['anchor']; offset = found[(a['view'], a['window_bytes'], a['sha256'])]
                view = views[a['view']]
                value = view.base+offset if kind == 'vaddr' else extract_operand(view, offset, row)
                evidence[key] = dict(kind=kind, view=a['view'], window_offset=offset,
                                     window_sha256=a['sha256'])
            else:
                raise ValueError('Unknown profile selector kind')
            result = literal(value, row['format'])
            evidence.setdefault(key, dict(kind=kind))
        results[key] = result
        active.remove(key)
        return result

    for key in selectors:
        resolve(key)
    return results, evidence
