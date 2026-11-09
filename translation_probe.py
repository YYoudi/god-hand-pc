"""Original GPL-3.0-only native probe of invented translation controls, not a game."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import uuid

import pc
import runtime_packs
import setup_pc as build
import translation_fixtures as fixtures

ROOT = Path(__file__).resolve().parent


def merge_native_environment(base, output):
    def allowed(key):
        return key.upper() not in ('CL','_CL_') and not key.upper().startswith(('GODHAND_','PS2X_'))
    env = {k:v for k,v in base.items() if allowed(k)}
    for line in output.splitlines():
        if '=' in line and not line.startswith('='):
            key,value = line.split('=',1)
            if allowed(key):
                env[key] = value
    return env


def environment_batch(vsroot):
    path = str(Path(vsroot).resolve())
    if any(c in path for c in '\r\n\0"%!?^&|<>'):
        raise ValueError('Toolchain path contains unsupported command characters')
    batch = Path(path)/'VC/Auxiliary/Build/vcvars64.bat'
    if not batch.is_file():
        raise ValueError('Existing MSVC vcvars64.bat required')
    return '@echo off\ncall "'+str(batch)+'" >nul\nif errorlevel 1 exit /b %errorlevel%\nset\n'


def native_environment(vsroot, directory):
    script = directory/'compiler-environment.cmd'
    script.write_text(environment_batch(vsroot),encoding='utf-8')
    if any(c in str(script) for c in '\r\n\0"%!?^&|<>'):
        raise ValueError('Private output path contains unsupported command characters')
    # Raw trusted command line avoids list2cmdline escaping nested cmd quotes.
    result = subprocess.check_output('cmd.exe /d /s /c ""'+str(script)+'""',
                                     text=True,errors='replace',timeout=30,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
    return merge_native_environment(os.environ,result)


def compiler_from_environment(env, vsroot):
    # where.exe uses the loaded VS environment, not a guessed installed version.
    result = subprocess.check_output(['where.exe','cl.exe'],env=env,text=True)
    compiler = Path(result.splitlines()[0]).resolve(strict=True)
    if compiler.name.lower() != 'cl.exe' or not compiler.is_relative_to(Path(vsroot).resolve()):
        raise ValueError('Compiler must belong to the explicitly selected toolchain')
    return compiler


def native_harness(cases, symbols):
    declarations = []
    rows = []
    for case in cases:
        name = symbols[case['name']]
        if not re.fullmatch(r'[A-Za-z_]\w*',name):
            raise ValueError('Unexpected synthetic function symbol')
        declarations.append('void '+name+'(uint8_t*,R5900Context*,PS2Runtime*);')
        for test in case['expected']:
            rows.append('{"'+case['name']+'",'+name+','+str(test['a0'])+','+
                        ('true' if test['outcome']=='throws' else 'false')+','+
                        str(case['entry'])+','+str(case['fault'])+','+str(test.get('v0',-1))+'}')
    return '''#include <cstdio>
#include <memory>
#include <stdexcept>
#include "ps2_runtime_macros.h"
#include "ps2_runtime.h"
'''+ '\n'.join(declarations)+'''
struct Probe { const char* name; void(*call)(uint8_t*,R5900Context*,PS2Runtime*); unsigned a0;
  bool expected_throw; unsigned entry; unsigned fault; int expected_v0; };
int main() {
  Probe cases[] = {'''+','.join(rows)+'''};
  for (const auto& probe: cases) {
    auto context = std::make_unique<R5900Context>();
    unsigned char scratch[64] = {};
    context->pc = probe.entry;
    SET_GPR_U64(context.get(),4,probe.a0);
    SET_GPR_U64(context.get(),31,0x00008000u);
    bool threw = false;
    try { probe.call(scratch,context.get(),nullptr); }
    catch (const std::runtime_error&) { threw=true; if(context->pc!=probe.fault) return 2; }
    if(threw!=probe.expected_throw) return 3;
    if(!threw && context->pc!=0x00008000u) return 4;
    if(!threw && probe.expected_v0>=0 && GPR_U32(context.get(),2)!=static_cast<unsigned>(probe.expected_v0)) return 5;
    std::printf("PASS %s a0=%u %s\\n",probe.name,probe.a0,threw?"throws":"returns");
  }
  return 0;
}
'''


def compile_plan(compiler, directory, includes, units, executable):
    directory = Path(directory)
    commands = []
    objects = []
    for index,unit in enumerate(units):
        obj = directory/(str(index)+'.obj')
        commands.append(('compile-'+str(index),[compiler,'/nologo','/c','/EHsc','/std:c++20',
            '/MD','/O2','/Z7','/DNDEBUG','/DPS2X_STRICT_RETURN_DIAGNOSTICS=0',
            *['/I'+str(p) for p in includes],'/Fo'+str(obj),unit],600))
        objects.append(obj)
    commands.append(('link',[compiler,'/nologo','/Fe'+str(executable),*objects],120))
    return commands


def probe(root, workspace_name, vsroot):
    if os.name != 'nt':
        raise ValueError('Native integration currently requires Windows/MSVC; fixture tests are portable')
    root = Path(root).resolve()
    workspace = runtime_packs.workspace_path(root,workspace_name)
    source = build.contained(workspace,workspace/'upstream')
    revision = pc.git('rev-parse','HEAD',cwd=source)
    checkout = pc.inspect_checkout(source,pc.load_pin(root)['revision'],revision)
    tool = build.contained(source,source/'build/port/runtime/ps2xRecomp/ps2_recomp.exe')
    if not tool.is_file():
        raise ValueError('Build the pinned recompiler in the private workspace first')
    directory = build.contained(pc.private_dir(root),pc.private_dir(root)/'translation-probes'/uuid.uuid4().hex)
    suite = fixtures.write_suite(directory)
    record = {'started_at':build.now(),'source':checkout,'tooling_revision':pc.git('rev-parse','HEAD',cwd=root),
              'tooling_dirty':bool(pc.git('status','--porcelain','--untracked-files=all',cwd=root)),
              'tooling_source_sha256':{name:build.digest(root/name) for name in
                                       ('translation_probe.py','translation_fixtures.py')},
              'recompiler_sha256':build.digest(tool),
              'scope':'Invented direct-call translation controls; no ISO or game execution. Not dispatcher, hardware or game-fidelity coverage.',
              'steps':[]}
    receipt = directory/'receipt.json'
    def save():
        receipt.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    def step(name,command,cwd,seconds):
        item = {'name':name,'command':list(map(str,command)),'started_at':build.now()}
        record['steps'].append(item)
        log = directory/(name+'.log')
        with log.open('xb') as output:
            child = subprocess.Popen(item['command'],cwd=cwd,env=env,stdout=output,stderr=output,
                                     creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            item['pid'] = child.pid
            save()
            print('Synthetic translation step',name,'PID',child.pid,flush=True)
            try: item['exit'] = child.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                child.kill();item['exit'] = child.wait();item['forced_owned_process'] = True
        item.update(ended_at=build.now(),log=str(log),log_sha256=build.digest(log))
        save()
        print('Synthetic translation terminal',name,item['exit'],flush=True)
        if item['exit'] != 0 or item.get('forced_owned_process'):
            raise ValueError(name+' failed; retained '+str(log))
        return log.read_text(errors='replace')
    try:
        save()
        env = native_environment(vsroot,directory)
        compiler = compiler_from_environment(env,vsroot)
        record.update(compiler=str(compiler),compiler_sha256=build.digest(compiler))
        sources = []
        symbols = {}
        for case in suite['cases']:
            text = step('generate-'+case['name'],[tool,case['config']],directory,90)
            case['diagnostic_counts'] = re.findall(r'Warnings:\s*(\d+),\s*errors:\s*(\d+)',text)
            if case['diagnostic_counts'] != [('0','1')]:
                raise ValueError('Pinned synthetic diagnostic expectation changed; retain and inspect')
            generated = Path(case['config']).parent/'generated'
            functions = [p for p in generated.glob('*.cpp') if p.name!='register_functions.cpp']
            if len(functions)!=1:
                raise ValueError('Unexpected invented function count')
            names = re.findall(r'void\s+(\w+)\s*\(uint8_t\*',functions[0].read_text())
            if len(names)!=1:
                raise ValueError('Unexpected invented function signature')
            symbols[case['name']] = names[0]
            sources.append(functions[0])
        driver = directory/'invented-driver.cpp'
        driver.write_text(native_harness(suite['cases'],symbols),encoding='utf-8')
        executable = directory/'invented-controls.exe'
        includes = [source/'runtime/ps2xRuntime/include',source/'runtime/ps2xRuntime/src/lib/Kernel',
                    source/'runtime/ps2xIOP/include',*[p.parent for p in sources]]
        # Separate units bound peak compiler work and preserve each terminal
        # result; a prior combined invocation timed out during code generation.
        for name,command,seconds in compile_plan(compiler,directory,includes,[driver,*sources],executable):
            step(name,command,directory,seconds)
        output = step('execute',[executable],directory,20)
        expected = sum(len(c['expected']) for c in suite['cases'])
        if len([line for line in output.splitlines() if line.startswith('PASS ')])!=expected:
            raise ValueError('Native control checks incomplete')
        record.update(status='passed',native_checks=output.splitlines(),cases=suite['cases'],
                      synthetic_executable_sha256=build.digest(executable))
    except BaseException as error:
        record.update(status='failed-or-interrupted',error=str(error))
        raise
    finally:
        record['ended_at'] = build.now()
        save()
    return {'receipt':str(receipt),'status':record['status'],'native_checks':record['native_checks']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace-name',default='retail-setup-v2')
    parser.add_argument('--vsroot',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(probe(ROOT,args.workspace_name,args.vsroot),indent=2))


if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.SubprocessError) as error: raise SystemExit(str(error))
