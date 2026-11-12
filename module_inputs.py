"""Original GPL-3.0-only read-only SNR2 input catalog, no game fixtures.

Reuses our existing ISO/FST/AFS readers instead of overriding a third-party Disc
class. This is bounded source-input metadata, NOT relocation, code discovery,
loading, ABI or runtime acceptance. Callers verify the exact disc/profile and
keep it open themselves. Window checks length, not adversarial same-size writes.
Raw module bytes, paths/offset maps and generated code must remain private.
"""
from dataclasses import dataclass
import hashlib
import struct
from resources import META_LIMIT, require, iso_root, fst_files, afs_entries


@dataclass(frozen=True)
class ModuleMetadata:
    bytes: int
    sha256: str
    symbol_records: int
    relocation_records: int
    export_records: int
    load_alignment: int


@dataclass(frozen=True)
class ModuleInput:
    path: str
    afs_ordinal: int
    offset: int
    metadata: ModuleMetadata


def inspect_module_bytes(raw):
    """Check an immutable, bounded SNR2 source envelope, never execute it.

    Only header/table extents and the declared load alignment are inspected.
    Symbol names/types/addresses, relocation operations, code/data bounds,
    constructors, compact streams and link/lifetime semantics are NOT verified.
    """
    require(isinstance(raw,bytes) and 60 <= len(raw) <= META_LIMIT,
            'Expected bounded immutable module bytes')
    require(raw[:4] == b'SNR2', 'Unsupported module signature/version')
    h=struct.unpack_from('<15I',raw)
    require(h[11] == len(raw), 'Module declared size differs from source extent')
    alignment=h[10]
    require(0 < alignment <= 4096 and alignment & (alignment-1) == 0,
            'Unsupported module load alignment')
    for offset,count,stride in ((h[1],h[2],12),(h[3],h[4],12),(h[8],h[9],4)):
        require(count <= 65536 and 0 <= offset <= len(raw) and
                count*stride <= len(raw)-offset and
                (count == 0 or offset >= 60 and offset % 4 == 0),
                'Module metadata table outside source/budget')
    return ModuleMetadata(len(raw),hashlib.sha256(raw).hexdigest(),h[4],h[2],h[9],alignment)


def module_inputs(disc):
    """Return local REL source descriptors; no extraction or output files.

    Require the supported bijective FST/AFS mapping. Only catalog metadata and
    REL extents are requested; physical payload aliases are not certified.
    Returned offsets describe the backing stream, not guest addresses.
    This format-level function does NOT select or certify a runtime profile.
    """
    root=iso_root(disc)
    require('GODHAND.FST' in root and '_DATA.AFS' in root,
            'Disc lacks the supported module catalogs')
    files=fst_files(root['GODHAND.FST']);archive=afs_entries(root['_DATA.AFS'])
    require(len(files)==len(archive) and sorted(files.values())==list(range(len(archive))),
            'Expected bijective FST/AFS source catalog')
    result=[]
    for name,index in sorted(files.items()):
        if not name.lower().endswith('.rel'):continue
        view=archive[index]
        metadata=inspect_module_bytes(view.read(0,view.size))
        result.append(ModuleInput(name,index,view.offset,metadata))
    return tuple(result)
