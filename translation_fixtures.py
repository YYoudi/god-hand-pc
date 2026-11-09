"""Original GPL-3.0-only, game-free ELF controls for translation diagnostics."""
from pathlib import Path
import argparse
import hashlib
import json
import struct

BASE = 0x00180000
FAULT = 0x00000005  # Deliberately unsupported at the evaluated translator pin.
JR_RA = 0x03E00008
NOP = 0
CASES = {
    'return-tail': ('InventedReturnTail', (0x24020025, JR_RA, NOP, FAULT, NOP),
                    12, ({'a0': 0, 'outcome': 'returns', 'v0': 37},)),
    'reachable-fault': ('InventedReachableFault', (FAULT, JR_RA, NOP),
                        0, ({'a0': 0, 'outcome': 'throws'},)),
    # bne a0,zero,+3 -> BASE+16, beyond an earlier return; two genuine paths.
    'branch-ingress': ('InventedBranchIngress', (0x14800003, NOP, JR_RA, NOP, FAULT, NOP),
                       16, ({'a0': 0, 'outcome': 'returns'}, {'a0': 1, 'outcome': 'throws'})),
}


def minimal_elf(words, base=BASE):
    if (type(base) is not int or base % 16 or not 0 < base < 0x02000000 or
            not words or len(words) > 1024 or base + len(words)*4 > 0x02000000 or
            any(type(w) is not int or not 0 <= w <= 0xffffffff for w in words)):
        raise ValueError('Invalid bounded invented instruction input')
    code = struct.pack('<'+'I'*len(words), *words)
    names = b'\0.text\0.shstrtab\0'
    text_offset = 0x1000
    names_offset = (text_offset + len(code) + 15) & ~15
    sections_offset = (names_offset + len(names) + 15) & ~15
    data = bytearray(sections_offset + 3*40)
    ident = b'\x7fELF\x01\x01\x01' + bytes(9)
    struct.pack_into('<16sHHIIIIIHHHHHH', data, 0, ident, 2, 8, 1, base,
                     52, sections_offset, 0, 52, 32, 1, 40, 3, 2)
    struct.pack_into('<8I', data, 52, 1, text_offset, base, base,
                     len(code), len(code), 5, 0x1000)
    data[text_offset:text_offset+len(code)] = code
    data[names_offset:names_offset+len(names)] = names
    struct.pack_into('<10I', data, sections_offset+40, 1, 1, 6, base,
                     text_offset, len(code), 0, 0, 16, 0)
    struct.pack_into('<10I', data, sections_offset+80, 7, 3, 0, 0,
                     names_offset, len(names), 0, 0, 1, 0)
    return bytes(data)


def private_output(path, root):
    root = Path(root).resolve()
    private = (root/'.local').resolve()
    target = Path(path).resolve()
    if (private == root or not private.is_relative_to(root) or
            target == private or not target.is_relative_to(private)):
        raise ValueError('Synthetic outputs must be a child of ignored .local')
    return target


def write_suite(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    result = {'schema': 1, 'origin': 'original invented input, no game material', 'cases': []}
    for key, (name, words, fault_offset, outcomes) in CASES.items():
        directory = destination/key
        directory.mkdir()
        binary = directory/'input.elf'
        raw = minimal_elf(words)
        binary.write_bytes(raw)
        table = directory/'functions.csv'
        table.write_text(f'Name,Start,End,Size\n{name},0x{BASE:08X},0x{BASE+4*len(words):08X},{4*len(words)}\n', encoding='utf-8')
        config = directory/'input.toml'
        config.write_text('[general]\n'+''.join(
            f'{k} = {json.dumps(v.as_posix())}\n'
            for k,v in [('input',binary),('output',directory/'generated'),('ghidra_output',table)])+
            'single_file_output = false\noutput_worker_threads = 1\nghidra_map_merge = true\n'
            'patch_syscalls = false\npatch_cop0 = false\npatch_cache = false\n'
            'auto_stub_by_name = false\ndirect_tail_calls = false\n', encoding='utf-8')
        case = {'name': key, 'function': name, 'entry': BASE, 'fault': BASE+fault_offset,
                'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                'input': str(binary), 'map': str(table), 'config': str(config),
                'expected': list(outcomes)}
        (directory/'expected.json').write_text(json.dumps(case,indent=2)+'\n',encoding='utf-8')
        result['cases'].append(case)
    (destination/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    target = private_output(args.output,Path(__file__).resolve().parent)
    print(json.dumps(write_suite(target),indent=2))


if __name__=='__main__':
    try: main()
    except (ValueError,OSError) as error: raise SystemExit(str(error))
