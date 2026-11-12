"""Original GPL-3.0-only sparse-registration metadata and private source renderer.

Consumes a qualified generated format, NOT general C++ or a game disassembler.
Populated output includes game-derived aliases/addresses and must stay private.
No ABI, coverage, registration atomicity or module-lifetime certificate.
"""
from dataclasses import dataclass
import hashlib
import re
from resources import require, META_LIMIT


IDENTIFIER = r'[A-Za-z_][A-Za-z0-9_]*'


@dataclass(frozen=True)
class RegistrationTable:
    begin: int
    end: int
    slots: int
    entries: tuple


def parse_generated_table(text, declared_names):
    """Check the pinned producer's sparse assignments without filling holes.

    declared_names are caller-qualified forward-declaration identifiers, not ABI
    evidence. Every explicit assignment must be recognized; zero/unassigned slots
    are NOT invented aliases. This is not a parser for arbitrary C++ expressions.
    """
    require(isinstance(text, str) and len(text) <= META_LIMIT and '\0' not in text,
            'Expected bounded generated table text')
    require(not isinstance(declared_names, (str, bytes)), 'Expected a collection of declarations')
    names = frozenset(declared_names)
    require(names and all(isinstance(n, str) and re.fullmatch(IDENTIFIER, n) for n in names),
            'Expected qualified declaration identifiers')
    values = []
    for field, number in (('Base', r'0x[0-9a-f]+'), ('End', r'0x[0-9a-f]+'),
                          ('SlotCount', r'[0-9]+')):
        matches = re.findall(r'^extern const uint32_t g_ps2RecompiledFunctionTable'+field+
                             r' = ('+number+r')u;$', text, re.M)
        require(len(matches) == 1, 'Missing/ambiguous table extent metadata')
        values.append(int(matches[0], 0))
    begin, end, slots = values
    require(0 <= begin < end <= 32*1024*1024 and begin % 4 == end % 4 == 0
            and 0 < slots <= 8*1024*1024 and end-begin == slots*4,
            'Invalid generated table range/slot count')
    array_pattern = r'PS2Runtime::RecompiledFunction g_ps2RecompiledFunctionTable\[([0-9]+)u\] = \{\};'
    arrays = re.findall('^'+array_pattern+'$', text, re.M)
    require(arrays == [str(slots)], 'Unsupported/ambiguous table array declaration')
    pattern = re.compile(r'\s*g_ps2RecompiledFunctionTable\[([0-9]+)\] = ('+IDENTIFIER+
                         r'); // (0x[0-9a-f]+)')
    entries, seen = [], set()
    for line in text.splitlines():
        if not re.search(r'\bg_ps2RecompiledFunctionTable\b', line):
            continue
        if re.fullmatch(array_pattern, line):
            continue
        match = pattern.fullmatch(line)
        require(match is not None, 'Unsupported generated assignment; not silently skipped')
        index, name, address = int(match[1]), match[2], int(match[3], 16)
        require(0 <= index < slots and index not in seen and address == begin+index*4
                and name in names, 'Invalid, duplicate or undeclared generated alias')
        seen.add(index)
        entries.append((address, name))
    require(entries, 'Empty generated registration table')
    return RegistrationTable(begin, end, slots, tuple(entries))


def render_registration(table, linked, base, code_begin, code_end, *,
                        namespace, log_name, registration_api):
    """Render original host source, preserving the qualified legacy semantics.

    Caller selects runtime or module API explicitly. Partial registration failure
    returns false without rollback; active becomes true only after the full loop.
    Removal clears the qualified half-open module extent only if active/base
    match. Those preserved policies are NOT safety/atomicity/ownership proofs.
    The caller is still responsible for a valid runtime/RAM pointer and profile.
    Returned strings use LF; a caller chooses an explicit output-file convention.
    """
    require(isinstance(table, RegistrationTable) and isinstance(linked, bytes)
            and 60 <= len(linked) <= META_LIMIT, 'Expected qualified table/image')
    require(all(type(x) is int for x in (base, code_begin, code_end,
                                       table.begin, table.end, table.slots)) and
            0 <= base < base+len(linked) <= 32*1024*1024 and
            base <= code_begin < code_end <= base+len(linked) and
            base % 4 == code_begin % 4 == code_end % 4 == 0 and
            table.begin == code_begin and table.end <= code_end,
            'Invalid qualified module/code/table extent')
    require(isinstance(namespace, str) and len(namespace) <= 64 and
            re.fullmatch(IDENTIFIER, namespace) and isinstance(log_name, str) and
            re.fullmatch(r'[A-Za-z0-9_]{1,64}', log_name) and
            registration_api in ('runtime', 'module'), 'Unsupported host registration profile')
    # Revalidate a directly constructed table; the parser is not a trust token.
    require(table.end-table.begin == table.slots*4 and table.slots > 0 and
            table.end % 4 == 0 and isinstance(table.entries, tuple) and table.entries,
            'Invalid registration table metadata')
    seen = set()
    for address, name in table.entries:
        require(type(address) is int and table.begin <= address < table.end and
                address % 4 == 0 and address not in seen and isinstance(name, str)
                and re.fullmatch(IDENTIFIER, name), 'Invalid registration table entry')
        seen.add(address)
    digest = hashlib.sha256(linked[code_begin-base:code_end-base]).hexdigest()
    call = ('runtime->registerFunction(e.address,e.fn)' if registration_api == 'runtime'
            else 'ps2x::setModuleFunction(e.address,e.fn)')
    header = ('#pragma once\n#include <cstdint>\nclass PS2Runtime;\nnamespace '+namespace+
              ' { bool install(PS2Runtime*,uint32_t,const uint8_t*,bool); void remove(uint32_t); }\n')
    source = '\n'.join(['#include "'+namespace+'_pack.h"',
        '#include "'+namespace+'_functions.h"', '#include "ps2_runtime.h"',
        '#include "ps2_module_table.h"', '#include "godhand/sha256.h"',
        '#include <iostream>', '#include <cstring>', 'namespace '+namespace+' {',
        'struct Entry { uint32_t address; PS2Runtime::RecompiledFunction fn; };',
        'static const Entry entries[]={'])+'\n'
    source += ''.join(f'{{0x{address:x}u,&{name}}},\n' for address, name in table.entries)
    source += ('};\nstatic bool active=false;\n'
        'bool install(PS2Runtime* runtime,uint32_t base,const uint8_t* ram,bool negative) {\n'
        f' if(base!=0x{base:x}u)return false;\n'
        f' const auto hash=godhand::Sha256::hex(ram+0x{code_begin:x}u,0x{code_end-code_begin:x}u);\n'
        ' if(negative||hash!="'+digest+'"){std::cerr<<"PROTOTYPE_MODULE_REFUSED code hash\\n";return false;}\n'
        ' for(const auto& e:entries)if(!'+call+')return false;\n'
        ' active=true;std::cerr<<"PROTOTYPE_MODULE_INSTALLED '+log_name+' entries="<<std::size(entries)<<"\\n";return true;\n'
        '}\n'
        f'void remove(uint32_t base){{if(active&&base==0x{base:x}u){{ps2x::clearModuleFunctions(0x{base:x}u,0x{base+len(linked):x}u);active=false;std::cerr<<"PROTOTYPE_MODULE_CLEARED '+log_name+'\\n";}}\n'
        '}\n')
    return ((namespace+'_pack.h', header), (namespace+'_pack.cpp', source))
