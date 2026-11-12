"""Original GPL-3.0-only VU-image metadata and host registration source.

No microcode, guest instruction decoder or game-derived source is included.
FNV identity follows the pinned GPL runtime/tool byte-hash contract; it is not
cryptographic provenance. A separate SHA-256 binds each exact private input.
"""
import hashlib
import re

IMAGE_SIZE = 16_384
_IDENTIFIER = re.compile(r'[0-9a-f]{16}\Z')
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def fnv1a64(data):
    if not isinstance(data, bytes):
        raise ValueError('FNV input must be bytes')
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f'{value:016x}'


def qualify_image(filename, data, expected_sha256):
    """Read-only exact 16-KiB image qualification, never code/ISA validation."""
    if not isinstance(filename, str) or not re.fullmatch(r'vu1_[0-9a-f]{16}\.bin', filename):
        raise ValueError('Expected a canonical VU image basename')
    if not isinstance(data, bytes) or len(data) != IMAGE_SIZE:
        raise ValueError('Expected exactly 16384 original image bytes')
    if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(expected_sha256):
        raise ValueError('Explicit lower-case SHA-256 required')
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256:
        raise ValueError('VU image SHA-256 mismatch')
    identity = fnv1a64(data)
    if filename != f'vu1_{identity}.bin':
        raise ValueError('VU image filename/FNV identity mismatch')
    return {'filename': filename, 'image_id': identity,
            'sha256': actual, 'bytes': IMAGE_SIZE}


def wrapper_source(image_ids, line_ending='lf'):
    """Reproduce the original counted host wrapper, not generated game code.

    Hashes are opaque qualified input data, never hard-coded prototype mappings.
    The finite profile limit is an emission guard, not all-game coverage.
    """
    if not isinstance(image_ids, (list, tuple)) or not 1 <= len(image_ids) <= 256:
        raise ValueError('Expected a finite nonempty image-ID profile')
    if any(not isinstance(x, str) or not _IDENTIFIER.fullmatch(x) for x in image_ids):
        raise ValueError('Expected canonical image IDs, not source fragments')
    if len(set(image_ids)) != len(image_ids):
        raise ValueError('Duplicate/colliding image IDs refused')
    if line_ending not in ('lf', 'crlf'):
        raise ValueError('Unsupported source line ending')
    ids = sorted(image_ids)
    text = '#include "ps2_vu1_impl.inl"\n#include <atomic>\n#include <cstdio>\n'
    for identity in ids:
        text += f'''template<> VU1InterpreterAccess::StepResult VU1InterpreterAccess::runImage<0x{identity}ull>(VU1Interpreter&,const Vu1RunArgs&);
static std::atomic<unsigned long long> calls_{identity}{{0}};
static VU1InterpreterAccess::StepResult invoke_{identity}(VU1Interpreter& vu,const Vu1RunArgs& args){{
 calls_{identity}.fetch_add(1,std::memory_order_relaxed);
 return VU1InterpreterAccess::runImage<0x{identity}ull>(vu,args);
}}
'''
    text += 'void registerPrototypeVu1Programs(){\n'
    text += ''.join(f' registerVu1CompiledProgram(0x{x}ull,&invoke_{x});\n' for x in ids)
    text += '}\nvoid reportPrototypeVu1Programs(){\n'
    text += ''.join(f' std::fprintf(stderr,"PROTOTYPE_VU1_AOT image={x} calls=%llu\\n",calls_{x}.load(std::memory_order_relaxed));\n' for x in ids)
    text += '}\n'
    if line_ending == 'crlf':
        text = text.replace('\n', '\r\n')
    return text.encode('utf-8')
