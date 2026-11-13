"""Invented append-log bytes only; no game, runtime or image fixtures."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class CommandLineReaderTests(unittest.TestCase):
    def test_partial_append_eof_exactly_once_and_bounded_faults(self):
        compiler=next((shutil.which(x) for x in ('g++','clang++','c++') if shutil.which(x)),None)
        if not compiler:self.skipTest('C++17 compiler required')
        source=r'''
#include "adapter/command_line_reader.hpp"
#include <cassert>
#include <sstream>
using namespace godhand_pc::command_lines;
Result read(Reader& r,const std::string& s,std::string& out){std::istringstream f(s);return r.poll(f,out);}
int main(){
 Reader r;std::string out="stale";
 assert(read(r,"",out)==Result::Pending&&out.empty());
 for(int i=0;i<1000;++i)assert(read(r,"invented",out)==Result::Pending&&r.offset()==0&&out.empty());
 assert(read(r,"invented\n",out)==Result::Line&&out=="invented"&&r.offset()==9);
 assert(read(r,"invented\n",out)==Result::Pending&&out.empty());
 assert(read(r,"invented\npart",out)==Result::Pending&&r.offset()==9);
 assert(read(r,"invented\npartial\r\n",out)==Result::Line&&out=="partial");
 assert(read(r,"invented\npartial\r\n\nlast\n",out)==Result::Line&&out.empty());
 assert(read(r,"invented\npartial\r\n\nlast\n",out)==Result::Line&&out=="last");
 assert(read(r,"short",out)==Result::Fault&&out.empty());
 assert(read(r,std::string(100,'x')+"\n",out)==Result::Fault);
 for(auto text:{std::string("bad\tline\n"),std::string("bad\rline\n"),std::string("a\0b\n",4),std::string(258,'x'),std::string(257,'x')+"\n"}){
  Reader bad;assert(read(bad,text,out)==Result::Fault&&out.empty()&&bad.offset()==0);
 }
 for(auto ending:{"\n","\r\n"}){
  Reader boundary;assert(read(boundary,std::string(256,'x')+ending,out)==Result::Line&&out.size()==256);
 }
 Reader split;assert(read(split,"hello\r",out)==Result::Pending);
 assert(read(split,"hello\r\n",out)==Result::Line&&out=="hello");
 Reader failed;std::istream invalid(nullptr);
 assert(failed.poll(invalid,out)==Result::Fault&&out.empty());
}
'''
        with tempfile.TemporaryDirectory(prefix='gh-lines-') as directory:
            d=Path(directory);cpp=d/'probe.cpp';cpp.write_text(source,encoding='utf-8');exe=d/('probe.exe' if os.name=='nt' else 'probe')
            b=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-O2','-I',str(ROOT),str(cpp),'-o',str(exe)],capture_output=True,text=True,timeout=90)
            self.assertEqual(b.returncode,0,b.stdout+b.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
