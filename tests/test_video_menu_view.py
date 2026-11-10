"""Original controller/draw-call doubles, not a real window, game or rendering proof."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import pc


BACKEND = r'''#pragma once
#include <set>
#include <string>
#include <vector>
struct Color { unsigned char r,g,b,a; };
enum { KEY_F2=1, KEY_ESCAPE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_R, KEY_ENTER, KEY_KP_ENTER };
namespace invented_host {
inline int width=640, height=480, releases=0;
inline bool overlay=false, focused=true;
inline std::set<int> keys;
inline std::vector<std::string> texts;
inline bool has(const std::string &text) { for (const auto &s:texts) if(s==text) return true; return false; }
}
inline bool IsWindowFocused(){return invented_host::focused;}
inline bool IsKeyPressed(int key){return invented_host::keys.count(key)!=0;}
inline int GetScreenWidth(){return invented_host::width;}
inline int GetScreenHeight(){return invented_host::height;}
inline int MeasureText(const char *text,int size){return static_cast<int>(std::string(text).size())*size/2;}
inline void DrawRectangle(int,int,int,int,Color){}
inline void DrawRectangleLines(int,int,int,int,Color){}
inline void DrawText(const char *text,int,int,int,Color){invented_host::texts.emplace_back(text);}
'''
INPUT = r'''#pragma once
#include "ps2_host_backend.h"
namespace ps2_host_input { inline void setOverlayOpen(bool open) {
invented_host::overlay=open; if(!open) ++invented_host::releases;
} }
'''
CONTROLS = r'''#pragma once
#include "ps2_host_input.h"
namespace ps2x::controls {
inline bool open=false,lastDrawable=false;
inline int ticks=0,shutdowns=0;
inline bool isOpen(){return open;}
inline void hostTick(bool drawable){lastDrawable=drawable;++ticks;}
inline void draw(){}
inline void shutdown(){++shutdowns;open=false;ps2_host_input::setOverlayOpen(false);}
}
'''
PAUSE = r'''#pragma once
namespace godhand_pc_pause {
inline bool on=true;
inline bool enabled(){return on;}
struct Gate { bool wanted=false,held=false;
void request(bool value){wanted=value;} bool requested()const{return wanted;} bool parked()const{return held;} };
inline Gate& gate(){static Gate value;return value;}
}
'''


class VideoMenuViewTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("g++") or shutil.which("clang++"), "C++20 needed")
    def test_exact_public_view_with_invented_host_events(self):
        self.compile_and_run("video_menu_view_cases.cpp", "view exclusivity hold ack close reload size unknown: PASS")

    @unittest.skipUnless(shutil.which("g++") or shutil.which("clang++"), "C++20 needed")
    def test_exact_public_host_binding_with_invented_controls_and_gate(self):
        self.compile_and_run("video_menu_host_cases.cpp", "host F1 tick exclusivity requested-vs-held close shutdown: PASS")

    def compile_and_run(self, fixture, expected):
        with tempfile.TemporaryDirectory(prefix="godhand-view-double-") as name:
            root = Path(name).resolve()
            assert root.is_relative_to(Path(tempfile.gettempdir()).resolve())
            (root / "ps2_host_backend.h").write_text(BACKEND)
            (root / "ps2_host_input.h").write_text(INPUT)
            (root / "runtime").mkdir()
            (root / "runtime/ps2_controls_screen.h").write_text(CONTROLS)
            (root / "godhand_pc_controls").mkdir()
            (root / "godhand_pc_controls/host_pause.hpp").write_text(PAUSE)
            executable = root / "invented-view.exe"
            subprocess.run([shutil.which("g++") or shutil.which("clang++"), "-std=c++20", "-O2",
                            "-Wall", "-Wextra", "-Werror", "-I", str(root), "-I", str(pc.ROOT / "adapter"),
                            str(pc.ROOT / "tests" / fixture), "-o", str(executable)],
                           check=True, capture_output=True, timeout=90)
            result = subprocess.check_output([str(executable)], text=True, timeout=15)
            self.assertEqual(result.strip(), expected)
