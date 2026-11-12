"""Original GPL-3.0-only static entry-input production, no embedded game data.

Reworks our private import/local-table selector source into parameterized code.
The caller supplies its independently qualified original ELF/discovery/modules
and a named registry resolver. Static candidates, terminal pairs and agreement
with earlier maps are NOT full CFG/ISA/ABI/index-domain/runtime/lifetime proofs.
No code executes on the guest, no guest/ready flags or opcodes are modified.
All returned raw maps/words/symbols and generated CSVs must remain PRIVATE.
"""
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
import csv
import hashlib
import io
import struct

from module_inputs import inspect_module_bytes
from prototype_entry_candidates import DirectImportUse,missing_import_entries
from prototype_table_candidates import missing_table_entries
from prototype_sdk import MAX_IMAGE,TextImage,integer,load_text_elf,require


@dataclass(frozen=True)
class Section:
    name: str
    kind: int
    flags: int
    address: int
    offset: int
    size: int


def elf_sections(blob,expected_sha256):
    """Qualified original text plus file-section metadata, not an ELF loader."""
    text=load_text_elf(blob,expected_sha256)
    h=struct.unpack_from('<16sHHIIIIIHHHHHH',blob)
    rows=[struct.unpack_from('<10I',blob,h[6]+i*40) for i in range(h[12])]
    names=rows[h[13]];pool=blob[names[4]:names[4]+names[5]];sections=[]
    for row in rows:
        end=pool.find(b'\0',row[0]);require(end>=row[0] and end-row[0]<=255,'ELF section name bounds')
        try:name=pool[row[0]:end].decode('ascii')
        except UnicodeDecodeError as error:raise ValueError('ASCII section names required') from error
        require(row[3]+row[5]<=0x100000000,'ELF section address overflow')
        if row[1]!=8:require(row[4]+row[5]<=len(blob),'File-backed ELF section bounds')
        sections.append(Section(name,row[1],row[2],row[3],row[4],row[5]))
    return text,tuple(sections)


def discovery_units(text,units):
    require(isinstance(text,TextImage),'Qualified text required')
    units=tuple(sorted(tuple(u) for u in units))
    require(0<len(units)<=65536,'Discovery count bounds')
    for a,b,name in units:
        integer(a);integer(b,1,0x100000000)
        require(a%4==b%4==0 and text.start<=a<b<=text.end,'Discovery text bounds/alignment')
        require(type(name) is str and 0<len(name)<=200 and name.isascii() and
                all(32<ord(c)<127 for c in name),'Discovery label bounds')
    require(all(a[1]<=b[0] for a,b in zip(units,units[1:])),'Overlapping discovery ranges')
    return units


def owner_lookup(units):
    ordered=tuple(x[0] for x in units)
    def owner(address):
        i=bisect_right(ordered,address)-1
        return units[i] if i>=0 and address<units[i][1] else None
    return owner


@dataclass(frozen=True)
class ModuleSource:
    name: str
    path: str
    afs_index: int
    data: bytes


@dataclass(frozen=True)
class ResolvedSymbol:
    name: str
    address: int
    symbol_type: int


def scan_direct_imports(text,units,modules,lookup):
    """Original J26 import relocations with JAL words and BOOT resolver only.

    Caller provenance for lookup remains explicit. Unresolved imports are not
    guessed/stubbed. Other original module contexts can override resolution.
    """
    units=discovery_units(text,units);modules=tuple(modules)
    require(0<len(modules)<=4096 and callable(lookup),'Module/resolver bounds')
    require(all(isinstance(m,ModuleSource) for m in modules),'Module source records required')
    require(len({m.name for m in modules})==len(modules),'Duplicate module name')
    starts={u[0] for u in units};owner=owner_lookup(units)
    reports=[];missing={};unresolved=0;jal_uses=0;rejections=[];total_bytes=0
    for module in modules:
        name,path,index,raw=module.name,module.path,module.afs_index,module.data
        require(type(name) is str and 0<len(name)<=128 and name.isascii() and
                all(32<ord(c)<127 for c in name),'Module name bounds')
        require(type(path) is str and 0<len(path)<=1024,'Module path bounds');integer(index,0,1000000)
        inspect_module_bytes(raw);total_bytes+=len(raw)
        require(total_bytes<=256*1024*1024,'Module source byte budget')
        h=struct.unpack_from('<15I',raw);reloc_off,reloc_count,syms_off,syms_count=h[1:5]
        symbols=[];source_hash=hashlib.sha256(raw).hexdigest()
        for k in range(syms_count):
            no,address,hash16,typ,flag=struct.unpack_from('<IIHBB',raw,syms_off+12*k)
            require(no<len(raw),'Symbol name range');z=raw.find(b'\0',no,min(len(raw),no+4097))
            require(z>=no,'Symbol name bounds/termination')
            symbols.append((raw[no:z].decode('latin-1'),address,hash16,typ,flag))
        module_uses=0
        for k in range(reloc_count):
            off,info,addend=struct.unpack_from('<IIi',raw,reloc_off+12*k)
            typ,si=info&255,info>>8
            require(si<syms_count and off<=len(raw)-4,'Relocation symbol/word range')
            if typ!=4 or symbols[si][3]!=1:continue
            w=struct.unpack_from('<I',raw,off)[0]
            if w>>26!=3:
                rejections.append(dict(module=name,relocation=k,offset=off,
                    reason='import J26 relocation is not an original JAL',word=w));continue
            require(off%4==0,'Import JAL alignment');jal_uses+=1;module_uses+=1
            symbol=symbols[si];hit=lookup(symbol[0],symbol[2])
            if hit is None:unresolved+=1;continue
            require(isinstance(hit,ResolvedSymbol),'Typed resolved symbol required')
            integer(hit.address);integer(hit.symbol_type,0,255)
            require(type(hit.name) is str and len(hit.name)<=4096 and hit.name==symbol[0],
                    'Resolved symbol name differs from original import')
            target=(hit.address+addend)&0xffffffff
            if not text.start<=target<text.end or target%4 or target in starts:continue
            owned=owner(target)
            if owned is None:
                rejections.append(dict(module=name,relocation=k,target=target,
                    reason='no containing fresh discovery range'));continue
            item=missing.setdefault(target,dict(target=target,name=hit.name,
                registry_type=hit.symbol_type,owner=owned,uses=[]))
            item['uses'].append(dict(module=name,afs_index=index,module_sha256=source_hash,
                relocation=k,offset=off,word=w,import_symbol=si,addend=addend))
        reports.append(dict(name=name,path=path,afs_index=index,bytes=len(raw),sha256=source_hash,
            symbols=syms_count,relocations=reloc_count,original_import_jal_uses=module_uses))
    return dict(modules=reports,total_original_import_jal_uses=jal_uses,
                unresolved_import_jal_uses=unresolved,
                candidates=[missing[k] for k in sorted(missing)],rejected=rejections)


def scan_indirect_uses(blob,sections,text,units):
    """Conservative local GP metadata flow; unknown/control/join/delay barriers.

    Pointer prefixes are not complete arrays or valid runtime index domains.
    Stored-pointer uses are not a proved later callback load, alias or lifetime.
    """
    require(type(blob) is bytes and 52<=len(blob)<=MAX_IMAGE,'ELF byte budget')
    units=discovery_units(text,units);sections=tuple(sections)
    require(0<len(sections)<=4096 and all(isinstance(s,Section) for s in sections),'Section metadata required')
    for s in sections:
        integer(s.address);integer(s.size,0,MAX_IMAGE);integer(s.offset,0,MAX_IMAGE)
        require(s.address+s.size<=0x100000000 and
                (s.kind==8 or s.offset+s.size<=len(blob)),'Section input bounds')
    own_text=[s for s in sections if s.name=='.text']
    require(len(own_text)==1 and own_text[0].kind==1 and
            own_text[0].address==text.start and own_text[0].size==len(text.text) and
            blob[own_text[0].offset:own_text[0].offset+own_text[0].size]==text.text and
            hashlib.sha256(blob).hexdigest()==text.sha256,
            'Text/ELF/section identities differ')
    low,high=text.start,text.end;ws=struct.unpack('<'+'I'*(len(text.text)//4),text.text)
    starts={u[0] for u in units};owner=owner_lookup(units)
    def sx16(v):return v if v<32768 else v-65536
    def prefix(base,mask,stride):
        matches=[s for s in sections if s.name!='.text' and s.kind!=8 and s.flags&2 and
                 s.address<=base<=s.address+s.size-4]
        if len(matches)!=1 or base%4 or (stride%4 and (mask is None or mask%4)):return None
        section=matches[0];remaining=(section.address+section.size-base)//4
        limit=min(remaining,256,mask//4+1 if mask is not None else 256)
        values=[];stop=None
        for i in range(limit):
            v=struct.unpack_from('<I',blob,section.offset+base-section.address+4*i)[0]
            if not(low<=v<high and v%4==0):stop=dict(index=i,value=v);break
            values.append(v)
        if len(values)<3:return None
        return dict(base=base,section=section.name,mask=mask,stride=stride,values=values,
                    stop=stop,prefix_limit=limit,full_mask_domain_verified=False)
    def transfer(w):
        op=w>>26;rs=(w>>21)&31
        return op in (1,2,3,4,5,6,7,20,21,22,23) or op==0 and w&63 in (8,9,12,13) or op in (16,17,18) and rs==8
    joins=set()
    for j,w in enumerate(ws):
        op=w>>26;pc=low+4*j
        if op in (4,5,6,7,20,21,22,23) or op==1 or op in (16,17,18) and (w>>21)&31==8:
            joins.add((pc+4+4*sx16(w&65535))&0xffffffff)
        elif op in (2,3):joins.add(((pc+4)&0xf0000000)|((w&0x3ffffff)<<2))
    regs=[None]*32;regs[0]=('c',0);skip=set();uses=[];loads=[];unknown=Counter();tables={}
    def reset():regs[:]=[None]*32;regs[0]=('c',0)
    def plus(a,b):
        if a and b and a[0]==b[0]=='c':return ('c',(a[1]+b[1])&0xffffffff)
        if a and a[0]=='c' and a[1]==0:return b
        if b and b[0]=='c' and b[1]==0:return a
        if a and b and a[0]=='i' and b[0]=='c':a,b=b,a
        if a and b and a[0]=='c' and b[0]=='i':return ('a',a[1],b[1],b[2])
        if a and b and a[0]=='a' and b[0]=='c':return ('a',(a[1]+b[1])&0xffffffff,a[2],a[3])
        return None
    def store_reg(r,value):
        if r:regs[r]=value
    for j,w in enumerate(ws):
        pc=low+4*j;op=w>>26;rs=(w>>21)&31;rt=(w>>16)&31;rd=(w>>11)&31;sa=(w>>6)&31;fun=w&63;imm=w&65535
        if pc in joins or pc in starts:reset()
        if pc in skip:reset();continue
        if transfer(w):
            if op==0 and fun==9 and regs[rs] and regs[rs][0]=='l':
                v=regs[rs];uses.append(dict(kind='local-jalr',pc=pc,load_pc=v[4],
                    table=v[1],stride=v[2],mask=v[3],register=rs))
            reset();skip.add(pc+4);continue
        if op==15 and rs==0:store_reg(rt,('c',imm<<16));continue
        if op in (9,25):store_reg(rt,plus(regs[rs],('c',sx16(imm)&0xffffffff)));continue
        if op==13:
            a=regs[rs];store_reg(rt,('c',a[1]|imm) if a and a[0]=='c' else None);continue
        if op==12:
            a=regs[rs];store_reg(rt,('c',a[1]&imm) if a and a[0]=='c' else ('i',1,imm));continue
        if op==0:
            if w==0:continue
            if fun==0:
                a=regs[rt]
                v=('c',(a[1]<<sa)&0xffffffff) if a and a[0]=='c' else ('i',1<<sa,(a[2]<<sa)&0xffffffff if a and a[0]=='i' and a[2] is not None else None)
                store_reg(rd,v);continue
            if fun in (33,45):store_reg(rd,plus(regs[rs],regs[rt]));continue
            if fun==37:
                a,b=regs[rs],regs[rt]
                v=b if a==('c',0) else a if b==('c',0) else ('c',a[1]|b[1]) if a and b and a[0]==b[0]=='c' else None
                store_reg(rd,v);continue
            # R5900 MULT/U can write Rd. A MIPS-only no-destination assumption
            # here would keep a stale pointer origin across an EE GPR write.
            if fun in (2,3,4,6,7,16,18,20,22,23,24,25,32,34,35,36,38,39,40,42,43,44,46,47,56,58,59,60,62,63):store_reg(rd,None);continue
            if fun in (15,17,19,26,27,41):continue
            unknown[(op,fun)]+=1;reset();continue
        if op==35:
            address=plus(regs[rs],('c',sx16(imm)&0xffffffff));value=None
            if address and address[0]=='a':
                t=prefix(address[1],address[3],address[2])
                if t:
                    tables[(t['base'],t['stride'],t['mask'])]=t
                    value=('l',t['base'],t['stride'],t['mask'],pc)
                    loads.append(dict(pc=pc,table=t['base'],stride=t['stride'],mask=t['mask'],register=rt))
            store_reg(rt,value);continue
        if op in (30,32,33,34,36,37,38,39,55,26,27):store_reg(rt,None);continue
        if op in (31,40,41,42,43,44,45,46,63,49,54,57,62):
            if op==43 and regs[rt] and regs[rt][0]=='l':
                v=regs[rt];uses.append(dict(kind='local-stored-pointer',pc=pc,load_pc=v[4],
                    table=v[1],stride=v[2],mask=v[3],store_offset=sx16(imm),base_register=rs))
            continue
        if op==17 and rs==16 and fun in range(8):continue
        if op in (8,10,11,14,24):store_reg(rt,None);continue
        unknown[(op,fun)]+=1;reset()
    bybase={}
    for use in uses:bybase.setdefault(use['table'],[]).append(use)
    qualified=[]
    for base,refs in sorted(bybase.items()):
        ts=[t for t in tables.values() if t['base']==base];roots=[]
        for a in sorted({v for t in ts for v in t['values']}-starts):
            owned=owner(a)
            if owned:
                following=sorted({v for t in ts for v in t['values'] if a<v<owned[1]})
                roots.append(dict(start=a,proposed_end=following[0] if following else owned[1],owner=owned))
        qualified.append(dict(base=base,tables=ts,uses=refs,missing_entry_candidates=roots))
    return dict(instructions=len(ws),known_direct_branch_targets=len(joins),
        unknown_barrier_instructions=sum(unknown.values()),
        unknown_encodings=[dict(opcode=k[0],function=k[1],count=v) for k,v in sorted(unknown.items())],
        candidate_tables=qualified,indexed_pointer_loads=len(loads),qualified_local_uses=len(uses))


def terminal_pair(body):
    require(type(body) is bytes and 8<=len(body)<=MAX_IMAGE and len(body)%4==0,'Candidate body bounds')
    words=struct.unpack('<'+'I'*(len(body)//4),body)
    return words[-2]==0x03e00008 or len(words)>=3 and words[-3]==0x03e00008 and words[-1]==0


def known_noncall_exits(text,start,end):
    raw=text.span(start,end-start);result=[]
    for i,w in enumerate(struct.unpack('<'+'I'*(len(raw)//4),raw)):
        pc=start+4*i;op=w>>26;target=None
        if op in (4,5,6,7,20,21,22,23) or op==1 or op in (16,17,18) and (w>>21)&31==8:
            low=w&65535;target=(pc+4+4*(low if low<32768 else low-65536))&0xffffffff
        elif op==2:target=((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)
        if target is not None and not start<=target<end:result.append(dict(pc=pc,target=target))
    return result


def derive_entries(text,units,direct,indirect,modules):
    units=discovery_units(text,units);owners=[(a,b) for a,b,_ in units]
    require(not isinstance(modules,(str,bytes)),'Explicit module scope list required')
    modules=tuple(modules);known={m['name'] for m in direct['modules']}
    require(modules and len(set(modules))==len(modules) and
            all(m in known for m in modules),'Unknown/duplicate selected module')
    source=direct['candidates'];uses=[DirectImportUse(u['module'],u['offset'],c['target'])
                                    for c in source for u in c['uses'] if u['addend']==0]
    require(sum(len(c['uses']) for c in source)==len(uses),'Nonzero missing-import addend needs separate qualification')
    # A known selected module can have no missing direct import. Validate scope
    # against the ORIGINAL catalog first, then pass only contributing modules
    # to the use-specific model. Never substitute another module/old map.
    contributing=tuple(m for m in modules if m in {u.module for u in uses})
    candidates=missing_import_entries(owners,[c['target'] for c in source],uses,contributing) if contributing else ()
    exports=[]
    for c in candidates:
        body=text.span(c.start,c.end-c.start);require(terminal_pair(body),'Direct candidate lacks terminal return pair')
        exports.append(dict(Name='PrototypeExportEntry_%08x'%c.start,Start='0x%x'%c.start,
                            End='0x%x'%c.end,Size=str(c.end-c.start)))
    groups=[];provenance=[]
    for table in indirect['candidate_tables']:
        require(table['uses'],'Code-backed table uses required')
        for prefix in table['tables']:
            groups.append(prefix['values']);provenance.append(dict(base=table['base'],uses=table['uses'],
                mask=prefix['mask'],stride=prefix['stride']))
    selected=[]
    for c in missing_table_entries(owners,groups):
        body=text.span(c.start,c.end-c.start);external=known_noncall_exits(text,c.start,c.end)
        require(terminal_pair(body) and not external,'Indirect candidate fails terminal/known-outgoing checks')
        refs=[u for i in c.sets for u in provenance[i]['uses']]
        prefix='PrototypeDispatchEntry' if any(u['kind']=='local-jalr' for u in refs) else 'PrototypeMpegTableEntry'
        selected.append(dict(Name=prefix+('_%08x' if prefix=='PrototypeDispatchEntry' else '_%08X')%c.start,
            Start='0x%x'%c.start,End='0x%x'%c.end,Size=str(c.end-c.start),sets=list(c.sets),uses=refs,
            terminal_return_pair=True,known_noncall_transfers_outside_span=[],body_sha256=hashlib.sha256(body).hexdigest()))
    require(len({r['Start'] for r in selected+exports})==len(selected)+len(exports),'Duplicate derived entry start')
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=('Name','Start','End','Size'),extrasaction='ignore',lineterminator='\n')
    writer.writeheader();writer.writerows(selected+exports)
    return dict(groups=provenance,indirect=selected,direct=exports),stream.getvalue()


def relocation_text(records):
    """Own BOOT SNR2 relocation records in ORIGINAL table order, no sorting."""
    records=tuple(records);require(len(records)<=65536,'BOOT relocation budget')
    kinds={4:'j26',5:'hi16',6:'lo16'};out=['Address,kind\n']
    for address,info,addend in records:
        integer(address);integer(info);integer(addend,-0x80000000,0x7fffffff)
        if info&255 in kinds:
            require(address%4==0,'BOOT instruction relocation alignment')
            out.append('0x%x,%s\n'%(address,kinds[info&255]))
    return ''.join(out)
