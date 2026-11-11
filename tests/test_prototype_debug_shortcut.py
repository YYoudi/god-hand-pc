"""Original invented input timing only. No disc, game code, GPU or input device."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DebugShortcutTests(unittest.TestCase):
    def test_native_sequence_and_refusals(self):
        compiler = next((shutil.which(n) for n in ("g++", "clang++", "c++") if shutil.which(n)), None)
        if not compiler:
            self.skipTest("A C++17 compiler is required for the original host timing test")
        source = r'''
#include "adapter/prototype_debug_shortcut.hpp"
#include <cassert>
#include <vector>
using namespace godhand_pc::prototype;
int main() {
    std::vector<Pulse> sent;
    auto send = [&](Pulse p) { sent.push_back(p); return true; };
    DebugShortcut s;
    assert(!s.request(true) && s.refusal()==Refusal::ControlsOpen);
    assert(s.request(false));
    s.tick(1000,false,send); assert(sent.size()==1 && sent[0]==Pulse::HoldL2);
    assert(!s.request(false));
    s.tick(1149,false,send); assert(sent.size()==1);
    s.tick(1150,false,send); assert(sent.size()==2 && sent[1]==Pulse::PressR3);
    s.tick(1799,false,send); assert(s.active());
    s.tick(1800,false,send); assert(!s.active() && s.phase()==Phase::Finished);
    s.tick(5000,false,send); assert(sent.size()==2);
    assert(s.request(false)); s.tick(6000,false,send);
    s.tick(6601,false,send); assert(s.refusal()==Refusal::MissedTiming && sent.size()==3);
    assert(s.request(false)); s.tick(7000,false,send);
    s.tick(7050,true,send); assert(s.refusal()==Refusal::ControlsOpen && sent.size()==4);
    assert(s.request(false)); s.tick(8000,false,send);
    s.tick(7999,false,send); assert(s.refusal()==Refusal::ClockReversed && sent.size()==5);
    assert(s.request(false)); s.tick(9000,false,[](Pulse){return false;});
    assert(s.refusal()==Refusal::WriterFailed);
    assert(s.request(false)); s.tick(10000,false,send);
    s.tick(10150,false,[](Pulse){return false;}); assert(s.refusal()==Refusal::WriterFailed);
    // A delayed first tick starts a new hold then; it never sends both at once.
    assert(s.request(false)); auto before=sent.size();s.tick(999999,false,send);
    assert(sent.size()==before+1 && sent.back()==Pulse::HoldL2);
    s.tick(1000149,false,send); assert(sent.size()==before+2);
}
'''
        with tempfile.TemporaryDirectory(prefix="gh-debug-shortcut-") as directory:
            folder = Path(directory)
            cpp, executable = folder / "test.cpp", folder / ("test.exe" if os.name == "nt" else "test")
            cpp.write_text(source, encoding="utf-8")
            subprocess.run([compiler, "-std=c++17", "-O2", "-I", str(ROOT), str(cpp), "-o", str(executable)],
                           check=True, capture_output=True, timeout=90)
            subprocess.run([str(executable)], check=True, capture_output=True, timeout=20)


if __name__ == "__main__":
    unittest.main()
