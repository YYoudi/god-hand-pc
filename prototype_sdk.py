"""Original GPL-3.0-only, read-only cross-build SDK identity producer.

Reworks our private linear/CFG/direct-target selector algorithms into importable
code. Inputs are supplied by the caller; no game bytes, populated address maps,
upstream metadata, private scripts or generated functions are embedded/executed.
Exact normalized spans are static candidates, NOT independent SDK names, full
R5900 semantics, correct function boundaries, ABI/lifetime or runtime evidence.
In particular, context-only narrowing never enables an ambiguous HLE binding.
"""
from collections import deque
from dataclasses import dataclass
import copy
import hashlib
import math
import re
import struct

from prototype_call_graph import refine_domains

MAX_IMAGE = 24 * 1024 * 1024
MAX_SPAN = 8192
MAX_MATCHES = 65536
ADDRESS_OPS = frozenset((8,9,13,24,25,26,27,30,31,32,33,34,35,36,37,38,39,
                         40,41,42,43,44,45,46,47,49,53,55,57,61,63))
NO_RT_WRITE = frozenset((40,41,42,43,44,45,46,47,49,53,55,57,61,63))
# The historical linear look-ahead and CFG transfer policies differ for LD.
# CFG must invalidate the loaded GPR; sharing the look-ahead stop set would
# incorrectly preserve an address origin across a load into its own base.
CFG_NO_RT_WRITE = NO_RT_WRITE - {55}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def integer(value, low=0, high=0xffffffff):
    require(type(value) is int and low <= value <= high, 'Integer outside bounds')
    return value


def words(blob, *, maximum=MAX_IMAGE):
    require(type(blob) is bytes and 0 < len(blob) <= maximum and len(blob)%4 == 0,
            'Bounded nonempty immutable word-aligned bytes required')
    return struct.unpack('<'+'I'*(len(blob)//4), blob)


def address_value(value):
    return 0x100000 <= value < 0x2000000 or 0x20000000 <= value < 0x22000000


@dataclass(frozen=True)
class TextImage:
    start: int
    text: bytes
    sha256: str
    text_offset: int = 0

    def __post_init__(self):
        integer(self.start); integer(self.text_offset, 0, MAX_IMAGE)
        require(self.start%4 == 0, 'Aligned text base required')
        words(self.text)
        require(self.start+len(self.text) <= 0x100000000, 'Text address overflow')
        require(type(self.sha256) is str and re.fullmatch('[0-9a-f]{64}', self.sha256),
                'Exact lowercase SHA-256 required')

    @property
    def end(self):
        return self.start+len(self.text)

    def span(self, start, size):
        integer(start); integer(size, 4, MAX_IMAGE)
        require(start%4 == size%4 == 0 and self.start <= start <= self.end-size,
                'Span outside aligned text')
        return self.text[start-self.start:start-self.start+size]

    def word(self, address):
        return struct.unpack('<I', self.span(address,4))[0]


def load_text_elf(blob, expected_sha256):
    """Validate a bounded ELF32LE/MIPS envelope and unique .text, read-only.

    Not an ELF loader, executable permission/relocation or full ELF validator.
    The caller must supply the independently qualified original input identity.
    """
    require(type(blob) is bytes and 52 <= len(blob) <= MAX_IMAGE, 'ELF size')
    require(type(expected_sha256) is str and
            re.fullmatch('[0-9a-f]{64}',expected_sha256), 'Expected SHA-256')
    require(hashlib.sha256(blob).hexdigest() == expected_sha256, 'ELF identity')
    h=struct.unpack_from('<16sHHIIIIIHHHHHH',blob)
    require(h[0][:7] == b'\x7fELF\x01\x01\x01' and h[2] == 8 and h[3] == 1 and
            h[8] == 52, 'ELF32LE/MIPS header required')
    require(h[11] == 40 and 0 < h[12] <= 4096 and h[13] < h[12] and
            h[6] >= 52 and h[6]+h[12]*40 <= len(blob), 'ELF section table')
    if h[10]:
        require(h[9] == 32 and h[5] >= 52 and h[5]+h[10]*32 <= len(blob),
                'ELF program table')
    sections=[struct.unpack_from('<10I',blob,h[6]+i*40) for i in range(h[12])]
    names=sections[h[13]]
    require(names[1] == 3 and names[4]+names[5] <= len(blob), 'ELF string table')
    strings=blob[names[4]:names[4]+names[5]]; selected=[]
    for section in sections:
        require(section[0] < len(strings), 'ELF section name index')
        end=strings.find(b'\0',section[0])
        require(end >= 0, 'ELF unterminated section name')
        if strings[section[0]:end] == b'.text':
            require(section[1] == 1 and section[4]+section[5] <= len(blob),
                    'ELF text bounds/type')
            selected.append(section)
    require(len(selected) == 1, 'Unique ELF text section required')
    section=selected[0]
    return TextImage(section[3],blob[section[4]:section[4]+section[5]],
                     expected_sha256,section[4])


def normalize_linear(blob):
    """Historical finite look-ahead address normalization, not a MIPS emulator."""
    original=words(blob); result=list(original); masks={}
    for i,w in enumerate(original):
        op=w>>26
        if op in (2,3):
            result[i]=w&0xfc000000; masks[i]='direct code target'
        if op != 15:
            continue
        reg=(w>>16)&31; hi=(w&0xffff)<<16
        for j in range(i+1,min(i+10,len(original))):
            a=original[j]; o=a>>26; rs=(a>>21)&31; rt=(a>>16)&31; lo=a&0xffff
            if o in (2,3,4,5,6,7,1):
                break
            if rs == reg and o in ADDRESS_OPS:
                address=(hi+(lo if o==13 or lo<0x8000 else lo-0x10000))&0xffffffff
                if o==13:
                    address=hi|lo
                if address_value(address):
                    result[i]&=0xffff0000; result[j]&=0xffff0000
                    masks[i]='absolute address high'; masks[j]='absolute address low'
            if rt==reg and o not in NO_RT_WRITE:
                break
    return struct.pack('<'+'I'*len(result),*result),masks


def normalize_cfg(blob, base):
    """Bounded reachable-flow address-origin model, preserving other immediates.

    Models the selected historical selector instruction families and delay-slot
    paths; unsupported writes become unknowns. This is NOT a complete ISA/CFG,
    semantic equivalence, SDK name, function-boundary or runtime certificate.
    """
    original=words(blob,maximum=MAX_SPAN); integer(base)
    require(base%4 == 0 and base+len(blob) <= 0x100000000, 'CFG base overflow')
    n=len(original); initial=tuple([(0,frozenset())]+[None]*31)
    states={0:initial}; queue=deque([0]); masks={}

    def transfer(i,state,record=False):
        s=list(state); w=original[i]; op=w>>26; rs=w>>21&31; rt=w>>16&31
        rd=w>>11&31; imm=w&65535; simm=imm if imm<32768 else imm-65536; v=s[rs]
        if record and v is not None and v[1] and op in ADDRESS_OPS:
            address=((v[0]|imm) if op==13 else (v[0]+simm))&0xffffffff
            if address_value(address):
                masks[i]='absolute address operand'
                for origin in v[1]:masks[origin]='address LUI origin'
        if op==15:s[rt]=(imm<<16,frozenset([i]))
        elif op in (8,9,24,25):s[rt]=None if v is None else ((v[0]+simm)&0xffffffff,v[1])
        elif op==13:s[rt]=None if v is None else (v[0]|imm,v[1])
        elif op==0:
            fn=w&63
            if fn in (0x21,0x2d,0x25) and (rs==0 or rt==0):s[rd]=s[rt] if rs==0 else s[rs]
            elif fn not in (8,9,12,13,15,17,19,24,25,26,27,48,49,50,51,52,54):s[rd]=None
        elif op in (2,3,4,5,6,7,20,21,22,23) or op in CFG_NO_RT_WRITE:pass
        elif op in (16,17,18):
            if rs in (0,2):s[rt]=None
        elif op==28:s[rd]=None
        else:s[rt]=None
        s[0]=(0,frozenset());return tuple(s)

    def edges(i,state,record=False):
        w=original[i]; op=w>>26; fn=w&63; rs=w>>21&31; rt=w>>16&31
        imm=w&65535; simm=imm if imm<32768 else imm-65536
        after=transfer(i,state,record)
        branch=(op in (1,2,3,4,5,6,7,20,21,22,23) or op==0 and fn in (8,9)
                or op in (17,18) and rs==8)
        if not branch:return [(i+1,after)] if i+1<n else []
        if i+1>=n:return []
        delay=transfer(i+1,after,record)
        if op==3 or op==0 and fn==9 or op==1 and rt in (16,17,18,19):
            s=list(delay)
            for reg in list(range(1,16))+[24,25,26,27,31]:s[reg]=None
            return [(i+2,tuple(s))] if i+2<n else []
        if op==0 and fn==8:return []
        if op==2:
            address=((base+i*4+4)&0xf0000000)|((w&0x03ffffff)<<2)
            return [((address-base)//4,delay)] if base<=address<base+n*4 and address%4==0 else []
        target=i+1+simm; out=[]
        if 0<=target<n:out.append((target,delay))
        if op in (5,21) and rs==rt:out=[]
        if i+2<n and not(op in (4,20) and rs==rt):
            likely=op in (20,21,22,23) or op==1 and rt in (2,3)
            out.append((i+2,after if likely else delay))
        return out

    def merge(old,new):
        if old is None:return new
        return tuple((a[0],a[1]|b[1]) if a is not None and b is not None and
                     a[0]==b[0] else None for a,b in zip(old,new))

    steps=0
    while queue:
        i=queue.popleft();steps+=1
        require(steps<200000,'CFG work budget exceeded')
        for j,new in edges(i,states[i]):
            merged=merge(states.get(j),new)
            if states.get(j)!=merged:states[j]=merged;queue.append(j)
    for i,state in states.items():edges(i,state,True)
    result=list(original)
    for i in masks:result[i]&=0xffff0000
    for i,w in enumerate(original):
        if w>>26 in (2,3):result[i]=w&0xfc000000
    return struct.pack('<'+'I'*n,*result),masks


def coarse(blob):
    result=[]
    for w in words(blob):
        op=w>>26
        if op in (2,3):w&=0xfc000000
        elif op in ADDRESS_OPS or op==15:w&=0xffff0000
        result.append(w)
    return struct.pack('<'+'I'*len(result),*result)


def aligned_matches(haystack, needle):
    """Do not skip a valid aligned occurrence after an unaligned byte match."""
    require(type(haystack) is bytes and type(needle) is bytes and
            0<len(needle)<=len(haystack)<=MAX_IMAGE, 'Search byte bounds')
    require(len(needle)%4==0, 'Word-sized signature required')
    at=-1; result=[]
    while True:
        at=haystack.find(needle,at+1)
        if at<0:return result
        if at%4==0:
            result.append(at)
            require(len(result)<=MAX_MATCHES,'Candidate match budget exceeded')


@dataclass(frozen=True)
class SdkSymbol:
    address: int
    name: str
    method: str
    score: float

    def __post_init__(self):
        integer(self.address)
        require(self.address%4==0,'SDK address alignment')
        require(type(self.name) is str and re.fullmatch('[A-Za-z_][A-Za-z0-9_]{0,127}',self.name),
                'SDK identifier required')
        require(type(self.method) is str and 0<len(self.method)<=200 and
                not any(ord(c)<32 for c in self.method),'Metadata method label')
        require(type(self.score) in (int,float) and math.isfinite(self.score) and
                0<=self.score<=1,'Finite metadata score required')


def initial_candidates(prototype,retail,function_ranges,symbols,registered):
    """Read exact selected retail spans; search independent prototype addresses.

    Caller supplies frozen, reviewed metadata and discovered-entry inputs. Name
    and score provenance is metadata, never new ABI/runtime/name verification.
    """
    require(isinstance(prototype,TextImage) and isinstance(retail,TextImage),'Text images required')
    function_ranges=tuple(function_ranges); symbols=tuple(symbols); registered=frozenset(registered)
    # Registration tables can comment every occupied word slot, rather than
    # only function entry points. Bound those comments by the actual text word
    # count, not a fabricated universal function-count ceiling.
    require(0<len(function_ranges)<=100000 and 0<len(symbols)<=4096 and
            len(registered)<=len(prototype.text)//4,'Metadata bounds')
    for start,end in function_ranges:
        integer(start);integer(end,1,0x100000000)
        require(start%4==end%4==0 and start<end,'Function interval required')
    require(all(isinstance(s,SdkSymbol) for s in symbols),'SDK records required')
    require(len({s.name for s in symbols})==len(symbols),'Duplicate SDK name')
    for address in registered:
        integer(address)
        require(address%4==0 and prototype.start<=address<prototype.end,
                'Registration comment outside aligned prototype text')
    pnorm,_=normalize_linear(prototype.text);rnorm,rmasks=normalize_linear(retail.text)
    result=[]
    for symbol in symbols:
        address=symbol.address
        if not retail.start<=address<retail.end:continue
        owners=[(a,b) for a,b in function_ranges if a<=address<b]
        require(len(owners)==1,'SDK span must have exactly one metadata owner')
        _,end=owners[0];end=min([end]+[s.address for s in symbols if address<s.address<end])
        size=end-address
        if size<16 or size>MAX_SPAN or size%4:continue
        retail.span(address,size)
        matches=[prototype.start+i for i in aligned_matches(pnorm,rnorm[address-retail.start:end-retail.start])]
        masks={str(i*4+retail.start-address):why for i,why in rmasks.items()
               if address<=i*4+retail.start<end}
        candidate=dict(name=symbol.name,retail_address=address,retail_name_method=symbol.method,
                       retail_name_score=symbol.score,bytes=size,normalization_masks=masks,
                       unique_exact_normalized_matches=matches,
                       prototype_registered=[a for a in matches if a in registered])
        if len(matches)==1:
            candidate.update(prototype_address=matches[0],
                prototype_sha256=hashlib.sha256(prototype.span(matches[0],size)).hexdigest(),
                retail_sha256=hashlib.sha256(retail.span(address,size)).hexdigest())
        result.append(candidate)
    return result


def cfg_candidates(prototype,retail,candidates,entries):
    candidates=tuple(candidates);entries=frozenset(entries)
    require(0<len(candidates)<=4096 and len(entries)<=100000,'CFG candidate/input bounds')
    for a in entries:integer(a);require(a%4==0,'Discovered entry alignment')
    pc=coarse(prototype.text);result=[]
    for c in candidates:
        address=c['retail_address'];size=integer(c['bytes'],16,MAX_SPAN)
        raw=retail.span(address,size);normalized,masks=normalize_cfg(raw,address)
        matches=[];considered=[]
        for offset in aligned_matches(pc,coarse(raw)):
            at=prototype.start+offset
            if at not in entries and at not in c['prototype_registered']:continue
            considered.append(at);body=prototype.span(at,size);norm,pm=normalize_cfg(body,at)
            if norm==normalized:matches.append(dict(address=at,bytes=size,
                sha256=hashlib.sha256(body).hexdigest(),mask_indices=sorted(pm)))
        result.append(dict(name=c['name'],retail_address=address,bytes=size,
            coarse_candidates=considered,full_cfg_matches=matches,retail_mask_indices=sorted(masks),
            retail_name_method=c['retail_name_method']))
    return result


def qualify_candidates(prototype,retail,candidates):
    """Finite-domain DIRECT-target consistency; no previous map as an input."""
    candidates=tuple(candidates);require(0<len(candidates)<=4096,'Qualification candidate bounds')
    domains={}
    for c in candidates:
        SdkSymbol(c['retail_address'],c['name'],c['retail_name_method'],0)
        size=integer(c['bytes'],16,MAX_SPAN);retail.span(c['retail_address'],size)
        expected_norm,_=normalize_cfg(retail.span(c['retail_address'],size),c['retail_address'])
        require(len(c['full_cfg_matches'])<=MAX_MATCHES,'Qualification match bounds')
        for m in c['full_cfg_matches']:
            body=prototype.span(m['address'],size)
            require(m['bytes']==size and m['sha256']==hashlib.sha256(body).hexdigest(),
                    'Candidate identity no longer matches text')
            require(normalize_cfg(body,m['address'])[0]==expected_norm,
                    'Candidate normalized body no longer matches retail')
        values={m['address'] for m in c['full_cfg_matches']}
        require(len(values)==len(c['full_cfg_matches']),'Duplicate CFG match')
        if values:
            if c['retail_address'] in domains:require(domains[c['retail_address']]==values,'Aliased domain mismatch')
            domains[c['retail_address']]=values

    def edges(c,m):
        a=c['retail_address'];b=m['address'];out=[]
        for offset in range(0,c['bytes'],4):
            rw=retail.word(a+offset);pw=prototype.word(b+offset)
            if rw>>26 not in (2,3):continue
            require(pw>>26==rw>>26,'Direct opcode mismatch')
            rt=((a+offset+4)&0xf0000000)|((rw&0x3ffffff)<<2)
            pt=((b+offset+4)&0xf0000000)|((pw&0x3ffffff)<<2)
            out.append((offset,rt,pt))
        return out

    calls={(c['retail_address'],m['address']):[(rt,pt) for _,rt,pt in edges(c,m) if rt in domains]
           for c in candidates for m in c['full_cfg_matches']}
    refined=refine_domains(domains,calls)
    anchors={node:next(iter(values)) for node,values in refined.items() if len(values)==1}
    selected=[];rejected=[];unresolved=[]
    for c in candidates:
        for m in c['full_cfg_matches']:
            checks=[];errors=[]
            for offset,rt,pt in edges(c,m):
                if rt in anchors:
                    good=anchors[rt]==pt
                    checks.append(dict(offset=offset,retail_target=rt,prototype_target=pt,valid=good))
                    if not good:errors.append(offset)
            if len(c['full_cfg_matches'])!=1 and not checks:
                unresolved.append(dict(name=c['name'],prototype_address=m['address'],
                    reason='No outgoing known-anchor evidence; context alone does not enable a binding'))
                continue
            if errors:
                rejected.append(dict(name=c['name'],prototype_address=m['address'],call_edge_errors=errors))
                continue
            require(m['address'] in refined[c['retail_address']], 'Selection outside consistent domain')
            row=copy.deepcopy(c);row.update(prototype_address=m['address'],prototype_sha256=m['sha256'],
                known_call_edges_checked=checks,call_edge_errors=errors);selected.append(row)
    require(len({x['name'] for x in selected})==len(selected),'Duplicate selected SDK name')
    return dict(selected=selected,rejected=rejected,unresolved=unresolved,
                domains_before={str(k):sorted(v) for k,v in domains.items()},
                domains_after={str(k):sorted(v) for k,v in refined.items()})


def binding_text(qualified, *, line_ending='lf'):
    """Private generated include text; callers must not publish its contents."""
    require(line_ending in ('lf','crlf'),'Explicit LF/CRLF policy required')
    rows=qualified['selected'];require(0<len(rows)<=4096,'Binding count bounds')
    seen=set();out=[]
    for row in rows:
        symbol=SdkSymbol(row['prototype_address'],row['name'],'qualified-private-input',0)
        require(symbol.name not in seen,'Duplicate binding name');seen.add(symbol.name)
        out.append('{0x%08xu,"%s"},\n'%(symbol.address,symbol.name))
    text=''.join(out)
    return text if line_ending=='lf' else text.replace('\n','\r\n')
