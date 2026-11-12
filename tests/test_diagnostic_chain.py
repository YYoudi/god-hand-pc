"""Invented opaque links only; no game allocator, pointers, bytes or runtime."""
from pathlib import Path
import os,shutil,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]


class DiagnosticChainTests(unittest.TestCase):
    def test_bounded_reader_refusals_without_mutation_or_false_ownership(self):
        compiler=next((shutil.which(x) for x in ('g++','clang++','c++') if shutil.which(x)),None)
        if not compiler:self.skipTest('C++17 compiler required')
        source=r'''
#include "adapter/diagnostic_chain.hpp"
#include <cassert>
#include <map>
using namespace godhand_pc::diagnostic_chain;
int main(){
 std::map<unsigned,unsigned> links{{1,2},{2,3},{3,0},{8,8},{10,11},{11,10}};
 const auto before=links;unsigned reads=0;
 auto reader=[&](unsigned id,unsigned& next){++reads;auto i=links.find(id);if(i==links.end())return false;next=i->second;return true;};
 auto r=walk(0,3,reader);assert(r.status==Status::Complete&&r.nodes.empty()&&reads==0);
 r=walk(1,3,reader);assert(r.status==Status::Complete&&r.nodes==std::vector<unsigned>({1,2,3})&&reads==3);
 reads=0;r=walk(1,2,reader);assert(r.status==Status::Limit&&r.nodes==std::vector<unsigned>({1,2})&&reads==2);
 reads=0;r=walk(8,5,reader);assert(r.status==Status::Cycle&&r.nodes==std::vector<unsigned>({8})&&reads==1);
 reads=0;r=walk(10,5,reader);assert(r.status==Status::Cycle&&r.nodes==std::vector<unsigned>({10,11})&&reads==2);
 reads=0;r=walk(99,5,reader);assert(r.status==Status::Unreadable&&r.nodes.empty()&&reads==1);
 reads=0;r=walk(1,0,reader);assert(r.status==Status::InvalidBudget&&reads==0);
 r=walk(0,4097,reader);assert(r.status==Status::InvalidBudget&&reads==0);
 assert(links==before);assert(std::string(name(Status::Complete))=="complete-links-only");
}
'''.replace('#include <map>','#include <map>\n#include <string>')
        with tempfile.TemporaryDirectory(prefix='gh-chain-') as directory:
            d=Path(directory);cpp=d/'probe.cpp';cpp.write_text(source,encoding='utf8');exe=d/('probe.exe' if os.name=='nt' else 'probe')
            b=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-O2','-I',str(ROOT),str(cpp),'-o',str(exe)],capture_output=True,text=True,timeout=90)
            self.assertEqual(b.returncode,0,b.stdout+b.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)


if __name__=='__main__':unittest.main()
