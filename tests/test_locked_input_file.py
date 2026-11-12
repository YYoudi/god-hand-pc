"""Invented bytes only; real Windows sharing, not a native game/key test."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "nt", "Windows file-sharing semantics required")
class LockedInputFileTests(unittest.TestCase):
    def test_held_read_hash_refusals_moves_and_release(self):
        compiler = next((shutil.which(x) for x in ("g++", "clang++", "c++") if shutil.which(x)), None)
        if not compiler:
            self.skipTest("C++17 compiler required")
        # A deliberately noncryptographic hasher exercises original byte delivery
        # and refusal/lifetime policy. Real native integration must use SHA-256.
        data = bytes(((i * 7) ^ (i >> 4)) & 255 for i in range(131089))
        fnv = 14695981039346656037
        for value in data:
            fnv = ((fnv ^ value) * 1099511628211) & ((1 << 64) - 1)
        expected = "0" * 48 + f"{fnv:016x}"
        source = r'''
#include "adapter/locked_input_file.hpp"
#include <windows.h>
#include <cassert>
#include <cstdio>
#include <iostream>
#include <stdexcept>
using godhand_pc::inputs::LockedInputFile;
using godhand_pc::inputs::InputStatus;
struct Stats { uint64_t bytes=0; unsigned chunks=0; };
struct ToyHash {
    Stats* stats;
    uint64_t value=14695981039346656037ull;
    bool fail=false;
    void update(const void* p,size_t n) {
        ++stats->chunks; stats->bytes+=n;
        if(fail)throw std::runtime_error("invented hasher failure");
        const auto* b=static_cast<const unsigned char*>(p);
        for(size_t i=0;i<n;++i)value=(value^b[i])*1099511628211ull;
    }
    std::string finishHex() {
        char tail[17];std::snprintf(tail,sizeof(tail),"%016llx",static_cast<unsigned long long>(value));
        return std::string(48,'0')+tail;
    }
};
static HANDLE writer(const std::filesystem::path& p) {
    return CreateFileW(p.c_str(),GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,
        nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
}
static void writerDenied(const std::filesystem::path& p) {
    const auto h=writer(p);assert(h==INVALID_HANDLE_VALUE);assert(GetLastError()==ERROR_SHARING_VIOLATION);
}
static void writerAllowed(const std::filesystem::path& p) {
    const auto h=writer(p);assert(h!=INVALID_HANDLE_VALUE);CloseHandle(h); // no bytes written
}
static void moveThroughReferences(LockedInputFile& destination,LockedInputFile& source) {
    destination=std::move(source); // valid aliasing case without a deliberate self-move warning
}
int main(int argc,char** argv) {
    assert(argc==3);const std::filesystem::path path(argv[1]);const std::string expected(argv[2]);
    constexpr uint64_t size=131089;Stats stats;
    {
        auto input=LockedInputFile::verify(path,size,expected,ToyHash{&stats});
        assert(input.verified()&&input.status()==InputStatus::Verified&&input.digest()==expected);
        assert(stats.bytes==size&&stats.chunks==3);writerDenied(path);
        const auto read=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,
            nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
        assert(read!=INVALID_HANDLE_VALUE);CloseHandle(read);
        auto moved=std::move(input);assert(input.status()==InputStatus::Empty&&moved.verified());writerDenied(path);
        LockedInputFile assigned;assigned=std::move(moved);assert(assigned.verified()&&!moved.verified());writerDenied(path);
        moveThroughReferences(assigned,assigned);assert(assigned.verified());writerDenied(path);
    }
    writerAllowed(path);
    for(const auto& digest : {std::string(63,'0'),std::string(64,'G'),std::string(64,'A'),std::string(65,'0')}) {
        Stats s;auto bad=LockedInputFile::verify(path,size,digest,ToyHash{&s});
        assert(bad.status()==InputStatus::InvalidExpectation&&s.bytes==0);writerAllowed(path);
    }
    {
        Stats s;auto zero=LockedInputFile::verify(path,0,expected,ToyHash{&s});
        assert(zero.status()==InputStatus::InvalidExpectation&&s.bytes==0);
        auto wrong=LockedInputFile::verify(path,size+1,expected,ToyHash{&s});
        assert(wrong.status()==InputStatus::SizeMismatch&&s.bytes==0);writerAllowed(path);
        auto changed=LockedInputFile::verify(path,size,std::string(64,'0'),ToyHash{&s});
        assert(changed.status()==InputStatus::DigestMismatch&&changed.digest()==expected&&s.bytes==size);writerAllowed(path);
    }
    {
        Stats s;const auto heldWriter=writer(path);assert(heldWriter!=INVALID_HANDLE_VALUE);
        auto blocked=LockedInputFile::verify(path,size,expected,ToyHash{&s});
        assert(blocked.status()==InputStatus::OpenFailed&&blocked.osError()==ERROR_SHARING_VIOLATION&&s.bytes==0);
        CloseHandle(heldWriter);
        auto missing=LockedInputFile::verify(path.parent_path()/"does-not-exist",size,expected,ToyHash{&s});
        assert(missing.status()==InputStatus::OpenFailed&&s.bytes==0);
        auto directory=LockedInputFile::verify(path.parent_path(),size,expected,ToyHash{&s});
        assert(!directory.verified());
    }
    {
        Stats s;bool threw=false;
        try {(void)LockedInputFile::verify(path,size,expected,ToyHash{&s,14695981039346656037ull,true});}
        catch(const std::runtime_error&) {threw=true;}
        assert(threw);writerAllowed(path);
    }
    std::cout<<"original synthetic held-input checks passed\n";
}
'''
        with tempfile.TemporaryDirectory(prefix="gh-input-lock-") as directory:
            d = Path(directory).resolve()
            fixture = d / "invented-input.dat"
            fixture.write_bytes(data)
            cpp, exe = d / "probe.cpp", d / "probe.exe"
            cpp.write_text(source, encoding="utf-8")
            compiled = subprocess.run([compiler,"-std=c++17","-O2","-Wall","-Wextra","-Werror",
                                       "-DNOMINMAX","-I",str(ROOT),str(cpp),
                                       str(ROOT/"adapter/locked_input_file.cpp"),"-o",str(exe)],
                                      capture_output=True,timeout=90)
            self.assertEqual(compiled.returncode, 0,
                             (compiled.stdout + compiled.stderr).decode("utf-8", "replace"))
            result = subprocess.run([str(exe),str(fixture),expected],capture_output=True,check=True,timeout=20)
            self.assertEqual(result.stdout.strip(), b"original synthetic held-input checks passed")
            self.assertEqual(fixture.read_bytes(), data)
            self.assertFalse((d / "does-not-exist").exists())


if __name__ == "__main__":
    unittest.main()
