"""Original GPL-3.0-only PRIVATE-output SDK producer CLI, no game distribution.

Reads explicitly hash-qualified personal ELF/metadata/discovery inputs. Outputs
contain private addresses and must stay in this repository's ignored .local.
This command does not extract a disc, generate/compile/launch a game, qualify
new SDK names/ABI/lifetime or implement a retail debug backend.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import subprocess
import sys

from prototype_sdk import (MAX_IMAGE, SdkSymbol, binding_text, cfg_candidates,
                           initial_candidates, load_text_elf, qualify_candidates,
                           require)

ROOT=Path(__file__).resolve().parent


def digest(blob):return hashlib.sha256(blob).hexdigest()


def identity(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}',value),
            'Independently qualified lowercase SHA-256 required')
    return value


def ordinary_bytes(path, maximum=MAX_IMAGE):
    p=Path(path);info=p.lstat()
    require(stat.S_ISREG(info.st_mode) and not p.is_symlink() and
            not getattr(info,'st_file_attributes',0)&1024,'Ordinary input file required')
    require(0<info.st_size<=maximum,'Input file size budget exceeded')
    # Keep the one-byte growth sentinel without reserving the whole 24MiB
    # ceiling for every tiny discovery source file. Shrink/growth still refuse.
    with p.open('rb') as f:blob=f.read(info.st_size+1)
    require(len(blob)==info.st_size and len(blob)<=maximum,'Input changed/oversized while reading')
    return blob


def qualified_bytes(path, expected):
    blob=ordinary_bytes(path)
    require(digest(blob)==identity(expected),'Input file identity mismatch')
    return blob


def discovery_inputs(folder, expected):
    """Hash every immediate .cpp; parse headers/comments, never execute source.

    Identity digest is SHA256 of sorted UTF-8 `basename\0fileSHA256\n` records.
    A registration-slot comment is NOT proof of an existing runtime function.
    """
    identity(expected);root=Path(folder);info=root.lstat()
    require(stat.S_ISDIR(info.st_mode) and not root.is_symlink() and
            not getattr(info,'st_file_attributes',0)&1024,'Ordinary discovery directory required')
    files=sorted(root.glob('*.cpp'),key=lambda p:p.name)
    require(2<=len(files)<=20000,'Discovery source count bounds')
    aggregate=hashlib.sha256();total=0;entries=set();registered=None
    for file in files:
        require(re.fullmatch('[A-Za-z0-9_.-]{1,180}\.cpp',file.name),'Discovery basename policy')
        blob=ordinary_bytes(file);total+=len(blob)
        require(total<=512*1024*1024,'Discovery total byte budget exceeded')
        aggregate.update((file.name+'\0'+digest(blob)+'\n').encode('utf-8'))
        if file.name=='register_functions.cpp':
            registered={int(a,16) for a in re.findall(rb'// (0x[0-9a-f]+)',blob)}
        else:
            match=re.search(rb'// Address: (0x[0-9a-fA-F]+) - (0x[0-9a-fA-F]+)',blob[:700])
            require(match is not None,'Missing discovered function header')
            start,end=(int(a,16) for a in match.groups())
            require(start%4==end%4==0 and start<end<=0x100000000,'Invalid discovered interval')
            require(start not in entries,'Duplicate discovered function entry')
            entries.add(start)
    require(registered is not None and aggregate.hexdigest()==expected,
            'Discovery source identity/registry mismatch')
    return entries,registered,dict(cpp_files=len(files),bytes=total,
                                 discovered_entries=len(entries),
                                 registration_comment_slots=len(registered),sha256=expected)


def metadata_inputs(functions,symbols):
    try:
        table=functions.decode('utf-8-sig');metadata=symbols.decode('utf-8-sig')
    except UnicodeDecodeError as error:raise ValueError('UTF-8 metadata required') from error
    reader=csv.DictReader(io.StringIO(table))
    require(reader.fieldnames is not None and {'Start','End'}<=set(reader.fieldnames),
            'Function CSV Start/End columns required')
    ranges=[]
    for row in reader:
        require(len(ranges)<100000,'Function metadata count budget')
        try:ranges.append((int(row['Start'],16),int(row['End'],16)))
        except (TypeError,ValueError) as error:raise ValueError('Invalid function CSV address') from error
    pattern=r'X\(0x([0-9A-Fa-f]+)u,\s*(\w+),\s*"([^"\r\n]+)",\s*([0-9.]+)f\)'
    records=[SdkSymbol(int(a,16),name,method,float(score))
             for a,name,method,score in re.findall(pattern,metadata)]
    require(0<len(records)<=4096 and len(records)==len(re.findall(r'^\s*X\(',metadata,re.M)),
            'Unsupported/missing SDK metadata row')
    return ranges,records


def private_session(name):
    require(type(name) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',name),
            'Fresh session uses 1..64 lowercase letters/digits/hyphens')
    p=ROOT
    for part in ('.local','prototype-sdk','sessions',name):
        p=p/part
        if p.exists() or p.is_symlink():
            info=p.lstat()
            require(stat.S_ISDIR(info.st_mode) and not p.is_symlink() and
                    not getattr(info,'st_file_attributes',0)&1024,'Aliased/non-directory output refused')
    require(not p.exists(),'Session already exists; choose a fresh name')
    result=subprocess.run(['git','check-ignore','--quiet','--',str(p)],cwd=ROOT,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    require(result.returncode==0,'Private output must be Git-ignored before production')
    return p


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('prototype-elf','retail-elf','functions','sdk-metadata'):
        parser.add_argument('--'+name,required=True)
        parser.add_argument('--'+name+'-sha256',required=True)
    parser.add_argument('--discovery',required=True)
    parser.add_argument('--discovery-sha256',required=True)
    parser.add_argument('--session',required=True)
    parser.add_argument('--binding-line-ending',choices=('lf','crlf'),default='lf')
    parser.add_argument('--check-only',action='store_true',help='Validate/read/produce in memory, no output writes')
    args=parser.parse_args(argv)
    try:
        output=private_session(args.session)
        prototype=load_text_elf(qualified_bytes(args.prototype_elf,args.prototype_elf_sha256),args.prototype_elf_sha256)
        retail=load_text_elf(qualified_bytes(args.retail_elf,args.retail_elf_sha256),args.retail_elf_sha256)
        ranges,symbols=metadata_inputs(qualified_bytes(args.functions,args.functions_sha256),
                                       qualified_bytes(args.sdk_metadata,args.sdk_metadata_sha256))
        entries,registered,discovery=discovery_inputs(args.discovery,args.discovery_sha256)
        initial=initial_candidates(prototype,retail,ranges,symbols,registered)
        cfg=cfg_candidates(prototype,retail,initial,entries)
        qualified=qualify_candidates(prototype,retail,cfg)
        bindings=binding_text(qualified,line_ending=args.binding_line_ending).encode('utf-8')
        summary=dict(scope='PRIVATE static identity candidates, not ABI/lifetime/runtime/name proof or a public game build',
            prototype_sha256=prototype.sha256,retail_sha256=retail.sha256,
            function_metadata_sha256=args.functions_sha256,sdk_metadata_sha256=args.sdk_metadata_sha256,
            discovery=discovery,initial_candidates=len(initial),cfg_candidates=len(cfg),
            selected=len(qualified['selected']),domains=len(qualified['domains_after']),
            known_direct_checks=sum(len(x['known_call_edges_checked']) for x in qualified['selected']),
            rejected=len(qualified['rejected']),unresolved=len(qualified['unresolved']),
            binding_line_ending=args.binding_line_ending,binding_sha256=digest(bindings),
            no_disc_extraction_translation_build_or_native_launch=True)
        if not args.check_only:
            output.mkdir(parents=True,exist_ok=False)
            payloads={'initial-private.json':dict(candidates=initial),
                      'cfg-private.json':dict(candidates=cfg),'qualified-private.json':qualified,
                      'summary-private.json':summary}
            for name,value in payloads.items():
                with (output/name).open('x',encoding='utf-8',newline='\n') as stream:
                    stream.write(json.dumps(value,indent=2)+'\n')
            with (output/'bindings-private.inc').open('xb') as stream:stream.write(bindings)
        print(json.dumps(dict(selected=summary['selected'],known_direct_checks=summary['known_direct_checks'],
                              rejected=summary['rejected'],unresolved=summary['unresolved'],
                              check_only=args.check_only,private_output_created=not args.check_only)))
        return 0
    except (OSError,ValueError) as error:
        print(str(error),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
