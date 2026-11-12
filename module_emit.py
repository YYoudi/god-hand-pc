"""Original GPL-3.0-only adapter for privately fetched LasVola SNR2 tools.

The parser/linker/ELF writer are dependencies, not vendored implementations.
Their identity and the caller's prototype profile must be qualified separately.
Consumes original disc bytes and explicit qualified base metadata, not a RAM dump
or previously generated game C++. All returned files contain private game data.
No runtime registration, ABI/lifetime qualification or complete setup claim.
"""
from dataclasses import dataclass
import csv
import hashlib
import io
import json
import re
import struct
from module_inputs import inspect_module_bytes
from resources import require, META_LIMIT


def backward_tail_end(raw, start, bound, starts, branch_target):
    """Narrow fallback for unlinked module-relative J words, NOT a CFG oracle.

    Only a transfer to an already known earlier start can terminate a range,
    past observed forward branches, with a delay slot and a bounded successor.
    Indirect transfers, reachability, branch-in-delay-slot and alias safety are
    not established. A caller must first prefer the pinned backend's own extent.
    """
    require(isinstance(raw, bytes) and type(start) is int and type(bound) is int
            and 0 <= start < bound <= len(raw) and start % 4 == bound % 4 == 0,
            'Invalid bounded module word range')
    word = lambda pc: struct.unpack_from('<I', raw, pc)[0]
    furthest = start
    for pc in range(start, bound - 7, 4):
        w = word(pc)
        target = branch_target(w, pc)
        if target is not None and target < bound:
            furthest = max(furthest, target)
        if w >> 26 == 2:
            target = (w & 0x03ffffff) << 2
            end = pc + 8
            if (target < start and target in starts and pc >= furthest and
                    (end == bound or word(end) == 0 or end in starts)):
                return end
    return None


@dataclass(frozen=True)
class ModuleEmission:
    files: tuple
    functions: int
    runtime_relocations: int
    linked_sha256: str


def _csv_bytes(header, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def emit_translation_inputs(raw, boot, base, *, basename,
                            expected_module_sha256, expected_boot_sha256, backend):
    """Return private ELF/maps using the caller's pinned GPL tool namespace.

    backend exposes snr2, snr2fmt, snr2link and snr2elf modules from the qualified
    checkout. We do not fetch/import arbitrary paths or choose a runtime base.
    Checks are finite profile/envelope/analysis guards, not an adversarial parser
    sandbox or proof that inferred routines/relocations execute correctly.
    """
    metadata = inspect_module_bytes(raw)
    require(isinstance(basename, str) and
            re.fullmatch(r'[a-z][a-z0-9_]{0,63}', basename) is not None,
            'Expected one original output identifier')
    require(isinstance(boot, bytes) and 52 <= len(boot) <= META_LIMIT,
            'Expected bounded immutable boot ELF bytes')
    for data, expected in ((raw, expected_module_sha256), (boot, expected_boot_sha256)):
        require(isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected)
                and hashlib.sha256(data).hexdigest() == expected,
                'Source bytes differ from explicitly qualified identity')
    require(type(base) is int and 0 <= base <= 0xffffffff and
            base % metadata.load_alignment == 0 and len(raw) <= 0x100000000-base,
            'Invalid qualified module base/alignment/extent')
    sections = backend.snr2elf.read_elf(boot)['sections']
    headers = [s for s in sections if s['name'] == '.sndata']
    require(len(headers) == 1, 'Expected one boot-owned module registry section')
    registry = backend.snr2link.Registry.from_boot_elf(boot, headers[0]['addr'])

    class TailModule(backend.snr2fmt.Module):
        def _extent(self, start, bound, starts):
            result = super()._extent(start, bound, starts)
            if result is not None:
                return result
            return backward_tail_end(self.raw, start, bound, starts,
                                     backend.snr2fmt.branch_target)

    module = TailModule(raw, basename + '.rel')
    analysis = backend.snr2.Analysis(module, base, registry)
    require(analysis.checks.get('ok') is True, 'Pinned module analysis refused input')
    linked = bytes(analysis.L.img)
    cs, ce, strings = analysis.cs, analysis.ce, module.strings_start()
    require(len(linked) == len(raw) and 60 <= cs < ce <= strings <= len(linked),
            'Unsupported linked module/code/data envelope')
    layout = [('.snr2.header', 0, cs, 'A'), ('.text', cs, ce, 'AX'),
              ('.data', ce, strings, 'WA'), ('.snr2.meta', strings, len(linked), 'A')]
    elf = backend.snr2elf.build_exec_elf(linked, base, base+module.h['ctor_off'], layout)
    require(backend.snr2elf.self_check(elf, linked, base, layout) is True,
            'Pinned emitted ELF self-check failed')
    relocations = [s for s in analysis.sites if s['in_code'] and s['dynamic']
                   and s['kind'] in ('j26', 'hi16', 'lo16')]
    info = dict(base=base, text_begin=base+cs, text_end=base+ce,
                masked_text_sha256=hashlib.sha256(linked[cs:ce]).hexdigest(),
                runtime_relocation_sites=[s['address'] for s in relocations],
                functions=len(analysis.functions))
    files = ((basename+'.elf', elf),
             (basename+'_functions.csv', _csv_bytes(['Name', 'Start', 'End', 'Size'],
              ((f['name'], hex(f['start']), hex(f['end']), f['size'])
               for f in analysis.functions))),
             (basename+'_runtime_relocations.csv', _csv_bytes(['Address', 'kind'],
              ((hex(s['address']), s['kind']) for s in relocations))),
             ('linked.bin', linked),
             ('link-private.json', (json.dumps(info, indent=2)+'\n').encode('utf-8')))
    return ModuleEmission(files, len(analysis.functions), len(relocations),
                          hashlib.sha256(linked).hexdigest())
