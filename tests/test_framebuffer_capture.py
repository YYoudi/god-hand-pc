"""Invented dimensions and read-call doubles, not a GL/window or game test."""
from pathlib import Path
import shutil,subprocess,tempfile,unittest
import pc

class CaptureTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('g++') or shutil.which('clang++'),'C++20 needed')
    def test_exact_helper_uses_render_extent_and_bounds_before_allocating(self):
        with tempfile.TemporaryDirectory(prefix='godhand-capture-invented-') as name:
            root=Path(name).resolve()
            (root/'raylib.h').write_text('''#pragma once
struct Image { void *data; int width,height,mipmaps,format; };
enum { PIXELFORMAT_UNCOMPRESSED_R8G8B8A8=7 };
inline int w=640,h=480;
inline int GetRenderWidth(){return w;} inline int GetRenderHeight(){return h;}
''')
            (root/'rlgl.h').write_text('''#pragma once
inline int flush=0,reads=0,rw=0,rh=0; inline bool fail=false;
inline void rlDrawRenderBatchActive(){++flush;}
inline unsigned char *rlReadScreenPixels(int x,int y){++reads;rw=x;rh=y;static unsigned char token;return fail?nullptr:&token;}
''')
            cpp=root/'case.cpp';cpp.write_text('''#include "framebuffer_capture.hpp"
#include <cassert>
int main(){using namespace godhand_pc_capture;
for(auto extent:{0,-1,16385,2147483647}){w=extent;h=480;assert(!readWindow().data);}
assert(reads==0 && flush==0);w=16384;h=16384;assert(!readWindow().data && reads==0);
w=640;h=480;auto a=readWindow();assert(a.data && a.width==640 && a.height==480 && rw==640 && rh==480 && reads==1 && flush==1);
w=800;h=600;auto b=readWindow();assert(b.data && b.width==800 && b.height==600 && b.mipmaps==1 && b.format==7);
fail=true;assert(!readWindow().data && reads==3);}
'''.replace('#include <cassert>','#include <cassert>\n#include <initializer_list>'))
            exe=root/'invented-capture.exe'
            subprocess.run([shutil.which('g++') or shutil.which('clang++'),'-std=c++20','-Wall','-Wextra','-Werror',
                '-I',str(root),'-I',str(pc.ROOT/'adapter'),str(cpp),'-o',str(exe)],check=True,capture_output=True,timeout=60)
            subprocess.run([str(exe)],check=True,capture_output=True,timeout=15)
