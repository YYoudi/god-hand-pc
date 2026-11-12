"""Invented bytes and original C++ stubs only; no game/real-runtime fixtures."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import prototype_vu1 as v


class VuMetadataTests(unittest.TestCase):
    def test_standard_fnv_byte_vectors(self):
        self.assertEqual(v.fnv1a64(b''), 'cbf29ce484222325')
        self.assertEqual(v.fnv1a64(b'a'), 'af63dc4c8601ec8c')
        self.assertEqual(v.fnv1a64(b'hello'), 'a430d84680aabd0b')

    def test_exact_invented_image_identity_without_mutation(self):
        image = bytes(range(256)) * 64
        digest = hashlib.sha256(image).hexdigest()
        identity = v.fnv1a64(image)
        result = v.qualify_image(f'vu1_{identity}.bin', image, digest)
        self.assertEqual(result, {'filename': f'vu1_{identity}.bin',
            'image_id': identity, 'sha256': digest, 'bytes': 16384})
        self.assertEqual(image, bytes(range(256)) * 64)

    def test_image_shape_and_basename_guards(self):
        image = b'\0' * 16384
        digest = hashlib.sha256(image).hexdigest()
        name = f'vu1_{v.fnv1a64(image)}.bin'
        for bad in [image[:-1], image+b'\0', bytearray(image), 'not bytes', None]:
            with self.assertRaises(ValueError):v.qualify_image(name,bad,digest)
        for bad in ['../'+name, 'folder/'+name, name.upper(), 'vu1_unknown.bin', None]:
            with self.assertRaises(ValueError):v.qualify_image(bad,image,digest)
        with self.assertRaises(ValueError):v.fnv1a64(bytearray(image))

    def test_independent_sha_and_fnv_name_mismatches_refused(self):
        image = b'\0' * 16384
        name = f'vu1_{v.fnv1a64(image)}.bin'
        for bad in ['0'*64, 'not a hash', None, 'A'*64]:
            with self.assertRaises(ValueError):v.qualify_image(name,image,bad)
        with self.assertRaises(ValueError):
            v.qualify_image('vu1_0000000000000000.bin',image,hashlib.sha256(image).hexdigest())

    def test_wrapper_is_canonical_and_keeps_counters_and_callbacks(self):
        ids = ['0000000000000002','0000000000000001']
        data = v.wrapper_source(ids)
        self.assertEqual(data,v.wrapper_source(tuple(reversed(ids))))
        self.assertLess(data.index(b'calls_0000000000000001'),
                        data.index(b'calls_0000000000000002'))
        self.assertIn(b'fetch_add(1,std::memory_order_relaxed)',data)
        self.assertIn(b'return VU1InterpreterAccess::runImage<0x0000000000000001ull>(vu,args);',data)
        self.assertIn(b'registerVu1CompiledProgram(0x0000000000000002ull,&invoke_0000000000000002);',data)

    def test_wrapper_rejects_duplicate_unbounded_and_source_fragment_inputs(self):
        for bad in [[], '0000000000000001', None, ['1'], [1],
                    ['0000000000000001']*2, ['0'*16]*257,
                    ['000000000000000A'], ['0'*16+'; injected()']]:
            with self.assertRaises(ValueError):v.wrapper_source(bad)

    def test_explicit_source_line_endings(self):
        ids=['0123456789abcdef']
        lf=v.wrapper_source(ids)
        crlf=v.wrapper_source(ids,'crlf')
        self.assertNotIn(b'\r',lf)
        self.assertEqual(crlf,lf.replace(b'\n',b'\r\n'))
        self.assertNotIn(b'\r\r\n',crlf)
        with self.assertRaises(ValueError):v.wrapper_source(ids,'guessed')

    def test_compiled_invented_dispatch_counter_and_hash_oracle(self):
        compiler=next((shutil.which(x) for x in ('g++','clang++','c++') if shutil.which(x)),None)
        if not compiler:self.skipTest('C++17 compiler required')
        header=r'''
#pragma once
#include <cstdint>
struct VU1Interpreter{int first=0,second=0;};struct Vu1RunArgs{int value=0;};
struct VU1InterpreterAccess{
 enum class StepResult{First,Second};
 template<uint64_t> static StepResult runImage(VU1Interpreter&,const Vu1RunArgs&);
};
using Fn=VU1InterpreterAccess::StepResult(*)(VU1Interpreter&,const Vu1RunArgs&);
void registerVu1CompiledProgram(uint64_t,Fn);
'''
        main=r'''
#include "ps2_vu1_impl.inl"
#include <array>
#include <cassert>
#include <cstdio>
#include <vector>
std::vector<uint64_t> ids;std::vector<Fn> callbacks;
void registerVu1CompiledProgram(uint64_t id,Fn fn){ids.push_back(id);callbacks.push_back(fn);}
template<> VU1InterpreterAccess::StepResult VU1InterpreterAccess::runImage<1>(VU1Interpreter& v,const Vu1RunArgs& a){v.first+=a.value;return StepResult::First;}
template<> VU1InterpreterAccess::StepResult VU1InterpreterAccess::runImage<2>(VU1Interpreter& v,const Vu1RunArgs& a){v.second+=a.value;return StepResult::Second;}
void registerPrototypeVu1Programs();void reportPrototypeVu1Programs();
int main(){
 registerPrototypeVu1Programs();assert(ids==std::vector<uint64_t>({1,2}));
 VU1Interpreter v;Vu1RunArgs a{3};
 assert(callbacks[0](v,a)==VU1InterpreterAccess::StepResult::First);
 callbacks[0](v,a);assert(callbacks[1](v,a)==VU1InterpreterAccess::StepResult::Second);
 assert(v.first==6&&v.second==3);reportPrototypeVu1Programs();
 // Original standalone integer oracle, no actual image/program/runtime inputs.
 std::array<unsigned char,16384> invented{};uint64_t hash=0xcbf29ce484222325ULL;
 for(auto byte:invented){hash^=byte;hash*=0x100000001b3ULL;}
 std::printf("%016llx\n",static_cast<unsigned long long>(hash));
}
'''
        with tempfile.TemporaryDirectory(prefix='gh-vu-') as directory:
            d=Path(directory)
            (d/'ps2_vu1_impl.inl').write_text(header,encoding='utf-8')
            (d/'wrapper.cpp').write_bytes(v.wrapper_source(['0000000000000002','0000000000000001']))
            (d/'main.cpp').write_text(main,encoding='utf-8')
            exe=d/('probe.exe' if os.name=='nt' else 'probe')
            b=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-O1','-I',str(d),
                str(d/'wrapper.cpp'),str(d/'main.cpp'),'-o',str(exe)],capture_output=True,text=True,timeout=90)
            if b.stdout or b.stderr:print('Invented VU wrapper compiler diagnostics:\n'+b.stdout+b.stderr)
            self.assertEqual(b.returncode,0,b.stdout+b.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual(r.stdout.strip(),v.fnv1a64(b'\0'*16384))
            self.assertIn('image=0000000000000001 calls=2',r.stderr)
            self.assertIn('image=0000000000000002 calls=1',r.stderr)


if __name__=='__main__':unittest.main()
