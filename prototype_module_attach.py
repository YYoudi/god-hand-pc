"""Original GPL-3.0-only checked attachment to our frozen private host harness.

No game addresses or generated functions are stored here. Populated output is
PRIVATE qualified host/profile source, not a public game-derived source file.
This is one exact harness layout, not a C++ parser, ABI or lifetime certificate.
"""
import hashlib
import re
from resources import require


def attach_qualified_module(source, *, expected_sha256, namespace, begin, size):
    """Add one qualified namespace to existing register/unregister/overlap hooks.

    Verify parent bytes before editing; preserve every other byte and existing
    call order. The caller qualifies base/extent/code and compiles/tests output.
    Existing ignored-return/partial-install policies are NOT repaired here.
    No game instruction, heap free, loader flag, readiness or guest PC is edited.
    """
    require(isinstance(source, bytes) and len(source) <= 1024*1024 and
            isinstance(expected_sha256, str) and re.fullmatch('[0-9a-f]{64}',expected_sha256)
            and hashlib.sha256(source).hexdigest()==expected_sha256,
            'Private parent harness differs from qualified identity')
    require(isinstance(namespace,str) and re.fullmatch('[A-Za-z_][A-Za-z0-9_]{0,63}',namespace)
            and type(begin) is int and type(size) is int and begin >= 0 and begin%4==0
            and 64 <= size <= 16*1024*1024 and begin+size <= 32*1024*1024,
            'Invalid qualified module namespace/extent')
    text=source.decode('utf-8')
    require(namespace+'::' not in text and namespace+'_pack.h' not in text,
            'Module namespace already attached')
    eol='\r\n' if b'\r\n' in source else '\n'
    anchors=('#include "runtime/ps2_cd_image.h"',
             'originalUnregister(ram,ctx,rt);',
             'const char* control=std::getenv("PROTOTYPE_MODULE_CONTROL");',
             '(void)prototype_event::install(rt,base,ram,std::strcmp(control,"negative")==0);')
    require(all(text.count(a)==1 for a in anchors), 'Unsupported private harness hook layout')
    changes=((anchors[0],'#include "'+namespace+'_pack.h"'+eol+anchors[0]),
             (anchors[1],namespace+'::remove(GPR_U32(ctx,4)&0x0fffffff);'+anchors[1]),
             (anchors[2],f'if(base<0x{begin+size:x}u && 0x{begin:x}u<base+h[11])'+namespace+
              f'::remove(0x{begin:x}u);'+eol+'   '+anchors[2]),
             (anchors[3],anchors[3]+' (void)'+namespace+
              '::install(rt,base,ram,std::strcmp(control,"negative")==0);'))
    for before,after in changes:text=text.replace(before,after,1)
    result=text.encode('utf-8')
    # Demonstrate exact reversal, not an inferred equivalence of unrelated text.
    reversed_text=text
    for before,after in reversed(changes):
        require(reversed_text.count(after)==1,'Ambiguous generated host attachment')
        reversed_text=reversed_text.replace(after,before,1)
    require(reversed_text.encode('utf-8')==source,'Host attachment altered unrelated bytes')
    return result
