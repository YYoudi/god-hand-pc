"""Original GPL-3.0-only private observer-source assembly, not game translation.

Only original declarations/calls and hash/line metadata are public. Raw and
instrumented game bodies stay private. Exact text postimages/comment preservation
are NOT independent C++ read-only, CFG, ABI, lifetime or native-execution proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import sys

from prototype_sdk import require
from prototype_sdk_inputs import digest, identity, ordinary_bytes, qualified_bytes
from source_inserts import apply_inserts

ROOT=Path(__file__).resolve().parent
IDS={'damage','refill','warp_create','warp_destroy'}
PC_WORD=re.compile(rb'// 0x([0-9a-fA-F]{1,8}): 0x([0-9a-fA-F]{1,8})(?![0-9a-fA-F])')


def public_policy(root):
    blob=ordinary_bytes(Path(root)/'adapter/prototype_observer_inserts.json',64*1024)
    data=json.loads(blob)
    require(type(data) is dict and set(data)=={'schema','version','provenance','profiles'} and
            data['schema']==1 and data['version']=='prototype-observer-inserts-v1' and
            type(data['profiles']) is list and len(data['profiles'])==4 and
            {r['id'] for r in data['profiles']}==IDS, 'Unsupported original observer policy')
    for row in data['profiles']:
        require(type(row) is dict and set(row)=={'id','source_sha256','output_sha256','output','line_ending','insertions'} and
                row['output']=='prototype_observe_'+row['id']+'.cpp' and
                row['line_ending'] in ('lf','crlf'), 'Unreviewed observer output/policy fields')
        identity(row['source_sha256']);identity(row['output_sha256'])
    require(len({r['source_sha256'] for r in data['profiles']})==4,'Duplicate observer source identity')
    return data,digest(blob)


def source_catalog(folder,expected):
    """Hash immediate original generated units; parse/execute no function bodies."""
    root=Path(folder);info=root.lstat();identity(expected)
    require(stat.S_ISDIR(info.st_mode) and not root.is_symlink() and
            not getattr(info,'st_file_attributes',0)&1024,'Ordinary generated source directory required')
    files=sorted(root.glob('*.cpp'),key=lambda p:p.name)
    require(1<=len(files)<=20000,'Finite generated source catalog required')
    total=0;aggregate=hashlib.sha256();by_hash={}
    for file in files:
        require(re.fullmatch(r'[A-Za-z0-9_.-]{1,180}\.cpp',file.name),'Generated basename policy differs')
        blob=ordinary_bytes(file);total+=len(blob)
        require(total<=512*1024*1024,'Generated source catalog exceeds byte budget')
        h=digest(blob);aggregate.update((file.name+'\0'+h+'\n').encode('utf-8'))
        by_hash.setdefault(h,[]).append(file)
    require(aggregate.hexdigest()==expected,'Generated source catalog identity differs')
    return by_hash,dict(cpp_files=len(files),bytes=total,sha256=expected)


def produce_profiles(policy,index):
    """Plan every private output before any output directory exists."""
    outputs={};records=[]
    for row in policy['profiles']:
        matches=index.get(row['source_sha256'],[])
        require(len(matches)==1,'Missing/ambiguous exact observer input')
        raw=qualified_bytes(matches[0],row['source_sha256'])
        output=apply_inserts(raw,row['insertions'],source_sha256=row['source_sha256'],
                             output_sha256=row['output_sha256'],line_ending=row['line_ending'])
        before=PC_WORD.findall(raw);after=PC_WORD.findall(output)
        require(before and before==after,'Original PC/word comment sequence changed/missing')
        require(row['output'] not in outputs,'Duplicate observed output')
        outputs[row['output']]=output
        records.append(dict(id=row['id'],raw_basename=matches[0].name,raw_sha256=digest(raw),
            output=row['output'],output_sha256=digest(output),bytes=len(output),
            line_ending=row['line_ending'],insertions=len(row['insertions']),
            original_pc_word_comments=len(before),original_pc_word_sequence_unchanged=True))
    return outputs,records


def private_session(name):
    require(type(name) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',name),'Fresh private session name required')
    p=ROOT
    for part in ('.local','prototype-observers','sessions',name):
        p=p/part
        if p.exists() or p.is_symlink():
            info=p.lstat()
            require(stat.S_ISDIR(info.st_mode) and not p.is_symlink() and
                    not getattr(info,'st_file_attributes',0)&1024,'Aliased/non-directory output refused')
    require(not p.exists(),'Session exists; preserve it')
    require(subprocess.run(['git','check-ignore','--quiet','--',str(p)],cwd=ROOT,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE).returncode==0,'Output must already be Git-ignored')
    return p


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('generated','generated-sha256','session'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--check-only',action='store_true');args=parser.parse_args(argv)
    try:
        output=private_session(args.session)
        policy,policy_hash=public_policy(ROOT)
        index,catalog=source_catalog(args.generated,args.generated_sha256)
        planned,records=produce_profiles(policy,index)
        receipt=dict(schema=1,policy_sha256=policy_hash,catalog=catalog,profiles=records,
            limits='Private insertion-only text production, not new translation/ABI/read-only/native/fidelity proof.')
        if not args.check_only:
            output.mkdir(parents=True,exist_ok=False)
            for name,blob in planned.items():
                with (output/name).open('xb') as f:f.write(blob)
            with (output/'observers-private.json').open('x',encoding='utf-8',newline='\n') as f:
                json.dump(receipt,f,indent=2);f.write('\n')
        print(json.dumps(dict(check_only=args.check_only,profiles=len(records),
            preserved_pc_word_comments=sum(r['original_pc_word_comments'] for r in records),native_run=False)))
        return 0
    except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as error:
        print('Prototype observer inputs refused: '+str(error),file=sys.stderr);return 2


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
