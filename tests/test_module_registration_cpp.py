"""Compile original rendered host code against invented stubs, never game code."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from module_registration import parse_generated_table, render_registration
from test_module_registration import TABLE, NAMES


class RenderedRegistrationTests(unittest.TestCase):
    def test_actual_rendered_guards_sparse_calls_remove_and_partial_failure(self):
        compiler=next((shutil.which(x) for x in ('g++','clang++','c++') if shutil.which(x)),None)
        if not compiler:self.skipTest('C++17 compiler required')
        digest=hashlib.sha256(b'A'*16).hexdigest()
        runtime=r'''
#pragma once
#include <cstdint>
#include <vector>
struct R5900Context{};class PS2Runtime;
using Fn=void(*)(uint8_t*,R5900Context*,PS2Runtime*);
extern int runtimeCalls,moduleCalls,hashCalls,clearCalls,failAt;
extern bool hashOK;extern uint8_t* ramBase;
extern uint32_t clearedBegin,clearedEnd;
extern std::vector<uint32_t> installed;
inline bool add(int& count,uint32_t address,Fn fn){
 ++count;if(count==failAt)return false;
 if(!fn)return false;
 installed.push_back(address);return true;
}
class PS2Runtime{public:using RecompiledFunction=Fn;
 bool registerFunction(uint32_t a,Fn f){return add(runtimeCalls,a,f);}};
'''
        module=r'''
#pragma once
#include "ps2_runtime.h"
namespace ps2x{
inline bool setModuleFunction(uint32_t a,Fn f){return add(moduleCalls,a,f);}
inline void clearModuleFunctions(uint32_t a,uint32_t b){
 ++clearCalls;clearedBegin=a;clearedEnd=b;installed.clear();}
}
'''
        functions='''#pragma once
#include "ps2_runtime.h"
namespace invented{
void invented_first(uint8_t*,R5900Context*,PS2Runtime*);
void invented_second(uint8_t*,R5900Context*,PS2Runtime*);
}
'''
        sha=r'''
#pragma once
#include "ps2_runtime.h"
#include <cassert>
#include <string>
namespace godhand{struct Sha256{static std::string hex(const uint8_t* p,uint32_t n){
 ++hashCalls;assert(p==ramBase+0x1040&&n==16);
 return hashOK?"EXPECTED_HASH":"not the expected identity";}};}
'''.replace('EXPECTED_HASH',digest)
        main=r'''
#include "invented_pack.h"
#include "ps2_runtime.h"
#include <cassert>
int runtimeCalls=0,moduleCalls=0,hashCalls=0,clearCalls=0,failAt=0;
bool hashOK=true;uint8_t* ramBase=nullptr;uint32_t clearedBegin=0,clearedEnd=0;
std::vector<uint32_t> installed;
namespace invented{
void invented_first(uint8_t*,R5900Context*,PS2Runtime*){}
void invented_second(uint8_t*,R5900Context*,PS2Runtime*){}
}
void reset(){runtimeCalls=moduleCalls=hashCalls=clearCalls=failAt=0;
 hashOK=true;installed.clear();}
int main(){
 uint8_t ram[8192]{};ramBase=ram;PS2Runtime runtime;
 assert(!invented::install(&runtime,0x1004,ram,false));
 assert(hashCalls==0&&runtimeCalls==0&&moduleCalls==0);
 invented::remove(0x1000);assert(clearCalls==0);
 assert(!invented::install(&runtime,0x1000,ram,true));assert(hashCalls==1);
 assert(runtimeCalls==0&&moduleCalls==0);
 hashOK=false;assert(!invented::install(&runtime,0x1000,ram,false));
 assert(hashCalls==2&&installed.empty());
 reset();failAt=2;assert(!invented::install(&runtime,0x1000,ram,false));
 assert(installed.size()==1&&installed[0]==0x1040);
 invented::remove(0x1000);assert(clearCalls==0&&installed.size()==1);
 // Deliberately proves the preserved partial-failure limitation, NOT rollback.
 reset();assert(invented::install(&runtime,0x1000,ram,false));
 assert(installed==std::vector<uint32_t>({0x1040,0x104c}));
 assert(runtimeCalls==EXPECT_RUNTIME&&moduleCalls==EXPECT_MODULE);
 invented::remove(0x1004);assert(clearCalls==0&&installed.size()==2);
 invented::remove(0x1000);assert(clearCalls==1&&installed.empty());
 assert(clearedBegin==0x1000&&clearedEnd==0x1100);
 invented::remove(0x1000);assert(clearCalls==1);
 assert(invented::install(&runtime,0x1000,ram,false));
 invented::remove(0x1000);assert(clearCalls==2);
}
'''
        with tempfile.TemporaryDirectory(prefix='gh-reg-') as directory:
            d=Path(directory);(d/'godhand').mkdir()
            for name,text in (('ps2_runtime.h',runtime),('ps2_module_table.h',module),
                              ('godhand/sha256.h',sha),('invented_functions.h',functions)):
                (d/name).write_text(text,encoding='utf-8')
            for api in ('runtime','module'):
                with self.subTest(api=api):
                    for name,text in render_registration(parse_generated_table(TABLE,NAMES),b'A'*256,
                            0x1000,0x1040,0x1050,namespace='invented',log_name='Example',registration_api=api):
                        (d/name).write_text(text,encoding='utf-8')
                    (d/'main.cpp').write_text(main.replace('EXPECT_RUNTIME','2' if api=='runtime' else '0')
                                                  .replace('EXPECT_MODULE','2' if api=='module' else '0'),encoding='utf-8')
                    exe=d/('probe.exe' if os.name=='nt' else 'probe')
                    b=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-O1','-I',str(d),
                                      str(d/'invented_pack.cpp'),str(d/'main.cpp'),'-o',str(exe)],
                                     capture_output=True,text=True,timeout=90)
                    if b.stdout or b.stderr:print('Retained invented registration compiler diagnostics:\n'+b.stdout+b.stderr)
                    self.assertEqual(b.returncode,0,b.stdout+b.stderr)
                    r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
                    self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                    self.assertIn('PROTOTYPE_MODULE_INSTALLED Example entries=2',r.stderr)
                    self.assertIn('PROTOTYPE_MODULE_CLEARED Example',r.stderr)


if __name__=='__main__':unittest.main()
