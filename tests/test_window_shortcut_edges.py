"""Invented host events only; no OS input, window, GPU or game."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WindowShortcutEdgeTests(unittest.TestCase):
    def test_short_held_repeat_focus_legacy_and_owner_order(self):
        compiler = next((shutil.which(x) for x in ("g++", "clang++", "c++") if shutil.which(x)), None)
        if not compiler:
            self.skipTest("C++17 compiler required for original host event model")
        source = r'''
#include "adapter/window_shortcut_edges.hpp"
#include <cassert>
using namespace godhand_pc::window_shortcuts;
int main() {
    PressEdges edges;
    for (auto key : {Key::Controls, Key::Developer, Key::Back}) {
        assert(!edges.take(key,true));
        edges.observe(key,Action::Press,true);
        edges.observe(key,Action::Release,true);
        assert(edges.take(key,true)); // final level is up, but the press survives
        assert(!edges.take(key,true));
        edges.observe(key,Action::Press,true);
        assert(edges.take(key,true,true)); // event + legacy edge is ONE action
        assert(!edges.take(key,true));
        for (unsigned i=0;i<100;++i) {
            edges.observe(key,Action::Repeat,true);
            assert(!edges.take(key,true));
        }
        edges.observe(key,Action::Release,true);
        assert(!edges.take(key,true));
        assert(edges.take(key,true,true)); // legacy polling path still works
        assert(!edges.take(key,true));
        edges.observe(key,Action::Press,true);
        edges.observe(key,Action::Press,true); // same-frame presses coalesce
        assert(edges.take(key,true));assert(!edges.take(key,true));
        edges.observe(key,Action::Press,true);
        assert(!edges.take(key,false,true)); // focus lost; discard even raw edge
        assert(!edges.take(key,true));
        edges.observe(key,Action::Press,false);
        assert(!edges.take(key,true));
    }
    // Closing an overlay must not leave an old Back to close a future overlay.
    edges.observe(Key::Back,Action::Press,true);
    (void)edges.take(Key::Back,true); // consumed by owner even when currently closed
    assert(!edges.take(Key::Back,true));
    edges.observe(Key::Controls,Action::Press,true);
    edges.observe(Key::Developer,Action::Press,true);
    assert(edges.take(Key::Controls,true)); // existing F1 owner runs first
    const bool controls_open = true;
    const bool developer_requested = edges.take(Key::Developer,true);
    assert(developer_requested && controls_open); // caller MUST refuse the request
    assert(!edges.take(Key::Developer,true)); // no deferred activation after close
    edges.observe(Key::Controls,Action::Press,true);
    edges.observe(Key::Developer,Action::Press,true);
    edges.observe(Key::Back,Action::Press,true);
    assert(!edges.take(Key::Controls,false)); // one lost-focus observation clears all
    assert(!edges.take(Key::Developer,true));assert(!edges.take(Key::Back,true));
    edges.observe(static_cast<Key>(99),Action::Press,true);
    assert(!edges.take(static_cast<Key>(99),true,true));
    edges.observe(Key::Developer,static_cast<Action>(99),true);
    assert(!edges.take(Key::Developer,true));
    edges.observe(Key::Developer,Action::Press,true);edges.clear();
    assert(!edges.take(Key::Developer,true));
}
'''
        # initializer_list is part of the synthetic harness, not the component.
        source = "#include <initializer_list>\n" + source
        with tempfile.TemporaryDirectory(prefix="gh-key-edges-") as directory:
            d = Path(directory)
            cpp, exe = d / "probe.cpp", d / ("probe.exe" if os.name == "nt" else "probe")
            cpp.write_text(source, encoding="utf-8")
            subprocess.run([compiler,"-std=c++17","-O2","-I",str(ROOT),str(cpp),"-o",str(exe)],
                           capture_output=True,check=True,timeout=90)
            subprocess.run([str(exe)],capture_output=True,check=True,timeout=20)


if __name__ == "__main__":
    unittest.main()
