"""Invented command/response outcomes only; no disc, firmware, device or game."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Sio2PadStatusTests(unittest.TestCase):
    def test_missing_ports_order_and_refusals(self):
        compiler = next((shutil.which(n) for n in ("g++", "clang++", "c++") if shutil.which(n)), None)
        if not compiler:
            self.skipTest("A C++17 compiler is required for the original status model")
        source = r'''
#include "adapter/sio2_pad_status.hpp"
#include <cassert>
#include <cstdint>
using godhand_pc::sio2::PadBatchStatus;
int main() {
    PadBatchStatus empty; assert(!empty.result());
    // Explicit independent expected register words, not a second copy of the model.
    const uint32_t singleMissing[2] = {0x1d100, 0x2d100};
    const uint32_t bothByPresence[4] = {0x3d200, 0x2d200, 0x1d200, 0x1200};
    for (unsigned port=0; port<2; ++port) {
        PadBatchStatus present; present.observe(port,true);
        assert(present.result() && *present.result()==0x1100);
        PadBatchStatus absent; absent.observe(port,false);
        assert(absent.result() && *absent.result()==singleMissing[port]);
    }
    for (unsigned order=0; order<2; ++order) {
        for (unsigned present=0; present<4; ++present) {
            PadBatchStatus status;
            status.observe(order,(present & (1u<<order))!=0);
            status.observe(1-order,(present & (1u<<(1-order)))!=0);
            assert(status.result() && *status.result()==bothByPresence[present]);
            for (unsigned port=0;port<2;++port)
                assert(((*status.result() & (0x10000u<<port))==0)==bool(present&(1u<<port)));
        }
    }
    // Retained faulty-global policy blames port0 for a missing port1.
    assert((0x1d100u & 0x10000u)!=0);
    PadBatchStatus correct; correct.observe(0,true);correct.observe(1,false);
    assert((*correct.result() & 0x10000u)==0 && (*correct.result() & 0x20000u)!=0);
    for (unsigned duplicate=0;duplicate<2;++duplicate) {
        PadBatchStatus status;status.observe(duplicate,true);status.observe(duplicate,false);
        assert(!status.result());
    }
    PadBatchStatus unsupported;unsupported.observe(2,true);assert(!unsupported.result());
    unsupported.observe(0,true);assert(!unsupported.result());
    PadBatchStatus mixed;mixed.observe(0,true);mixed.refuse();assert(!mixed.result());
    PadBatchStatus invalid;invalid.observe(99,false);assert(!invalid.result());
}
'''
        with tempfile.TemporaryDirectory(prefix="gh-sio2-status-") as directory:
            folder = Path(directory)
            cpp, exe = folder / "test.cpp", folder / ("test.exe" if os.name == "nt" else "test")
            cpp.write_text(source, encoding="utf-8")
            subprocess.run([compiler, "-std=c++17", "-O2", "-I", str(ROOT), str(cpp), "-o", str(exe)],
                           check=True, capture_output=True, timeout=90)
            subprocess.run([str(exe)], check=True, capture_output=True, timeout=20)


if __name__ == "__main__":
    unittest.main()
