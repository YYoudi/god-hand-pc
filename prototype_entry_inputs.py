"""Original GPL-3.0-only private-output prototype entry-input CLI.

Uses our source models plus the named pinned GPL upstream registry model (itself
reverse-engineered, NOT a new independent engine). No upstream/game code is
copied here. The prototype's own section address is ALWAYS passed explicitly.
Static input production only: no relocation execution, game generation/build,
native launch, guest flags/status writes or runtime/ABI/lifetime certificate.
"""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import stat
import subprocess
import sys
import types

from resources import Window,iso_root,afs_entries
from module_inputs import module_inputs
from prototype_entries import (ModuleSource,ResolvedSymbol,derive_entries,
    discovery_units,elf_sections,relocation_text,scan_direct_imports,scan_indirect_uses)
from prototype_sdk import require
from prototype_sdk_inputs import digest,identity,ordinary_bytes,qualified_bytes

ROOT=Path(__file__).resolve().parent
REGISTRY_REVISION='193076584e277c95644dcbbb4a6922c3a59ca2b8'


def dependency_checkout(checkout,git_blob):
    """Only exact Git bytes or its explicit LF->CRLF checkout postimage.

    Do not strip arbitrary CR bytes, ignore differences or accept another code
    revision. This is a source-postimage guard, not adversarial FS isolation.
    """
    require(type(checkout) is bytes and type(git_blob) is bytes,'Dependency source bytes required')
    if checkout==git_blob:return 'exact-git-blob'
    require(b'\r' not in git_blob and checkout==git_blob.replace(b'\n',b'\r\n'),
            'Registry source differs from pinned Git/explicit CRLF postimage')
    return 'git-lf-to-checkout-crlf'


def pinned_registry(source,elf,sndata_address):
    """Import only the reviewed pinned GPL metadata dependency, not game code."""
    root=Path(source)
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    require(actual==REGISTRY_REVISION,'Unsupported registry source revision')
    sources={};qualified={}
    for name in ('snr2fmt','snr2link'):
        relative='tools/snr2/'+name+'.py';blob=ordinary_bytes(root/relative)
        expected=subprocess.check_output(['git','show',REGISTRY_REVISION+':'+relative],cwd=root)
        policy=dependency_checkout(blob,expected)
        sources[relative]=dict(checkout_sha256=digest(blob),git_blob_sha256=digest(expected),
                               checkout_policy=policy)
        qualified[name]=blob
    require('snr2fmt' not in sys.modules,'Preloaded registry dependency refused')
    old_bytecode=sys.dont_write_bytecode;sys.dont_write_bytecode=True
    try:
        for name in ('snr2fmt','snr2link'):
            key='snr2fmt' if name=='snr2fmt' else '_godhand_pc_pinned_snr2link'
            # Execute ONLY the just-verified pinned dependency bytes, not an
            # unchecked existing .pyc or any private/generated game source.
            filename=str(root/'tools/snr2'/(name+'.py'))
            module=types.ModuleType(key);module.__file__=filename;sys.modules[key]=module
            exec(compile(qualified[name],filename,'exec'),module.__dict__)
        # Deliberately no retail/default VA: original prototype ELF section only.
        registry=module.Registry.from_boot_elf(elf,sndata_va=sndata_address)
    finally:sys.dont_write_bytecode=old_bytecode
    return registry,dict(revision=actual,source_files=sources,
        provenance='Pinned GPL upstream reverse-engineered BOOT registry metadata model; explicit own .sndata address, not retail-address/ABI/runtime proof')


def qualified_discovery(folder,expected,text):
    identity(expected);root=Path(folder);info=root.lstat()
    require(stat.S_ISDIR(info.st_mode) and not root.is_symlink() and
            not getattr(info,'st_file_attributes',0)&1024,'Ordinary discovery directory required')
    files=sorted(root.glob('*.cpp'),key=lambda p:p.name)
    require(2<=len(files)<=20000,'Discovery source count bounds')
    aggregate=hashlib.sha256();total=0;units=[];registry=False
    for file in files:
        require(re.fullmatch('[A-Za-z0-9_.-]{1,180}\.cpp',file.name),'Discovery basename policy')
        blob=ordinary_bytes(file);total+=len(blob)
        require(total<=512*1024*1024,'Discovery total byte budget')
        aggregate.update((file.name+'\0'+digest(blob)+'\n').encode('utf-8'))
        if file.name=='register_functions.cpp':
            require(b'struct GeneratedFunctionTableInitializer' in blob and
                    b'g_ps2RecompiledFunctionTableSlotCount' in blob and
                    b'// Address:' not in blob,'Discovery registration shape')
            registry=True;continue
        match=re.search(rb'// Address: (0x[0-9a-fA-F]+) - (0x[0-9a-fA-F]+)',blob[:700])
        require(match is not None,'Discovered function header required')
        units.append((int(match[1],16),int(match[2],16),file.name))
    require(registry and aggregate.hexdigest()==expected,'Discovery registry/identity mismatch')
    units=discovery_units(text,units)
    return units,dict(cpp_files=len(files),bytes=total,discovered_ranges=len(units),sha256=expected)


def private_session(name):
    require(type(name) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',name),
            'Fresh private session uses lowercase letters/digits/hyphens')
    p=ROOT
    for part in ('.local','prototype-entries','sessions',name):
        p=p/part
        if p.exists() or p.is_symlink():
            info=p.lstat()
            require(stat.S_ISDIR(info.st_mode) and not p.is_symlink() and
                    not getattr(info,'st_file_attributes',0)&1024,'Aliased/non-directory output refused')
    require(not p.exists(),'Session already exists; choose a fresh name')
    check=subprocess.run(['git','check-ignore','--quiet','--',str(p)],cwd=ROOT,
                         stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    require(check.returncode==0,'Output must be Git-ignored before production')
    return p


def produce(elf,disc,boot_name,units,sections,text,source,modules):
    """Read-only original disc, explicit own BOOT section and module scope."""
    sndata=[s for s in sections if s.name=='.sndata' and s.kind!=8 and s.flags&2]
    require(len(sndata)==1,'One own allocated file-backed .sndata section required')
    registry,backend=pinned_registry(source,elf,sndata[0].address)
    root=iso_root(disc);require(boot_name in root,'Original disc BOOT file missing')
    require(root[boot_name].read(0,root[boot_name].size)==elf,'Disc/ELF bytes differ')
    archive=afs_entries(root['_DATA.AFS']);inputs=module_inputs(disc);sources=[]
    for item in inputs:
        view=archive[item.afs_ordinal];raw=view.read(0,view.size)
        require(digest(raw)==item.metadata.sha256,'Module input changed between catalog/read')
        sources.append(ModuleSource(PurePosixPath(item.path).name,item.path,item.afs_ordinal,raw))
    def lookup(name,hsh):
        hit=registry.lookup(name,hsh)
        return None if hit is None else ResolvedSymbol(hit.name,hit.addr,hit.type)
    direct=scan_direct_imports(text,units,sources,lookup)
    indirect=scan_indirect_uses(elf,sections,text,units)
    derived,table=derive_entries(text,units,direct,indirect,modules)
    relocations=relocation_text(registry.boot_relocs)
    return direct,indirect,derived,table,relocations,backend


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('disc','elf'):
        parser.add_argument('--'+name,required=True)
        parser.add_argument('--'+name+'-sha256',required=True)
    parser.add_argument('--boot-name',required=True)
    parser.add_argument('--discovery',required=True)
    parser.add_argument('--discovery-sha256',required=True)
    parser.add_argument('--registry-source',required=True)
    parser.add_argument('--module',action='append',required=True)
    parser.add_argument('--session',required=True)
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args(argv)
    try:
        output=private_session(args.session)
        require(re.fullmatch('[A-Z0-9_.-]{1,64}',args.boot_name),'Explicit BOOT root filename required')
        elf=qualified_bytes(args.elf,args.elf_sha256);text,sections=elf_sections(elf,args.elf_sha256)
        units,discovery=qualified_discovery(args.discovery,args.discovery_sha256,text)
        disc=Path(args.disc);info=disc.lstat();identity(args.disc_sha256)
        require(stat.S_ISREG(info.st_mode) and not disc.is_symlink() and
                not getattr(info,'st_file_attributes',0)&1024 and
                2048<=info.st_size<=8*1024**3,'Ordinary bounded disc input required')
        with disc.open('rb') as stream:
            require(hashlib.file_digest(stream,'sha256').hexdigest()==args.disc_sha256,'Disc identity mismatch')
            direct,indirect,derived,table,relocations,backend=produce(
                elf,Window(stream),args.boot_name,units,sections,text,args.registry_source,args.module)
            stream.seek(0)
            require(hashlib.file_digest(stream,'sha256').hexdigest()==args.disc_sha256,'Disc changed during production')
        summary=dict(scope='Private static entry inputs, not function/ABI/CFG/ISA/index/lifetime/runtime proof',
            disc_sha256=args.disc_sha256,elf_sha256=args.elf_sha256,discovery=discovery,
            registry=backend,selected_module_names=args.module,modules=len(direct['modules']),
            original_import_jal_uses=direct['total_original_import_jal_uses'],
            unresolved_import_jal_uses=direct['unresolved_import_jal_uses'],
            direct_candidates=len(direct['candidates']),direct_rejections=len(direct['rejected']),
            indirect_instructions=indirect['instructions'],local_uses=indirect['qualified_local_uses'],
            code_backed_tables=len(indirect['candidate_tables']),
            selected_direct=len(derived['direct']),selected_indirect=len(derived['indirect']),
            entry_csv_bytes=len(table.encode('utf-8')),entry_csv_sha256=digest(table.encode('utf-8')),
            runtime_relocations=len(relocations.splitlines())-1,
            relocation_csv_sha256=digest(relocations.encode('utf-8')),
            new_native_build_or_launch=False)
        if not args.check_only:
            output.mkdir(parents=True,exist_ok=False)
            for name,value in [('imports-private.json',direct),('indirect-private.json',indirect),
                               ('entries-private.json',derived),('summary-private.json',summary)]:
                with (output/name).open('x',encoding='utf-8',newline='\n') as f:
                    f.write(json.dumps(value,indent=2)+'\n')
            for name,value in [('functions-private.csv',table),('runtime-relocations-private.csv',relocations)]:
                with (output/name).open('xb') as f:f.write(value.encode('utf-8'))
        print(json.dumps(dict(selected_direct=summary['selected_direct'],selected_indirect=summary['selected_indirect'],
            runtime_relocations=summary['runtime_relocations'],check_only=args.check_only,
            private_output_created=not args.check_only)))
        return 0
    except (OSError,ValueError,subprocess.SubprocessError) as error:
        print(str(error),file=sys.stderr);return 2


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
