"""Invented launch strings only; no window, runtime, ISO or game data."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class PrototypeExecutionPolicyTests(unittest.TestCase):
    def test_explicit_visible_unbounded_selection_and_environment_allowlist(self):
        compiler=next((shutil.which(x) for x in ('g++','clang++','c++') if shutil.which(x)),None)
        if not compiler:self.skipTest('C++17 compiler required')
        source=r'''
#include "adapter/prototype_execution_policy.hpp"
#include <array>
#include <cassert>
using namespace godhand_pc::prototype_execution;
int main(){
 Inputs good{"interactive-v1","1","0","invented-data",true};
 auto p=select(good);assert(p.valid()&&p.kind==Kind::Interactive);
 good.seconds="";assert(select(good).valid());good.seconds="0";
 for(auto v:{"90","900","00","+0","-0"," 0","0 ","nan","0.0"}){auto i=good;i.seconds=v;assert(select(i).error==Error::InteractiveDeadline);}
 for(auto v:{"","0","true"," 1"}){auto i=good;i.visible=v;assert(select(i).error==Error::HiddenInteractive);}
 auto i=good;i.userData="";assert(select(i).error==Error::MissingUserData);
 i=good;i.sdk=false;assert(select(i).error==Error::UnqualifiedSdk);
 i=good;i.profile="interactive-v2";assert(select(i).error==Error::UnknownProfile);
 for(auto v:{"","diagnostic-v1"}){i=good;i.profile=v;i.visible="0";i.seconds="bad-old-input";i.sdk=false;i.userData="";assert(select(i).valid()&&select(i).kind==Kind::LegacyDiagnostic);}
 for(auto pair:std::array<std::array<const char*,2>,11>{{
  {"PROTOTYPE_EXECUTION_PROFILE","interactive-v1"},{"prototype_probe_visible","1"},
  {"PROTOTYPE_USERDATA_ROOT","invented path"},{"PROTOTYPE_DEV_PANEL","controller-v2"},
  {"PROTOTYPE_PROBE_SECONDS","0"},{"PROTOTYPE_MODULE_CONTROL","enabled"},
  {"PS2X_PAD2","0"},{"ps2x_pad8","0"},{"PS2X_FAKE_PADS","0"},
  {"PS2X_AUDIO_MUTE","1"},{"PATH","unrelated ordinary setting"}}})
  assert(allowedInteractiveVariable(pair[0],pair[1]));
 for(auto key:{"PS2X_PAD_SCRIPT","ps2x_pad_script","PS2X_PAD_FIFO","PS2X_PAD1","PS2X_PAD1_CROSS", "PS2X_SCREENSHOT_DIR","PS2X_STATE_LOAD","PROTOTYPE_DEVELOPER_PROBE_FIELD","PROTOTYPE_KEY_TRACE","GODHAND_TIME_LIMIT_SECONDS","GODHAND_FUTURE_DIAGNOSTIC","PROTOTYPE_UNKNOWN"})
  for(auto value:{"","0","1","invented"})assert(!allowedInteractiveVariable(key,value));
 assert(!allowedInteractiveVariable("PS2X_PAD2","1"));
 assert(!allowedInteractiveVariable("PROTOTYPE_MODULE_CONTROL","negative"));
 assert(!allowedInteractiveVariable("PROTOTYPE_PROBE_VISIBLE","0"));
 assert(!allowedInteractiveVariable("PROTOTYPE_PROBE_SECONDS","90"));
 assert(!allowedInteractiveVariable("PROTOTYPE_USERDATA_ROOT","invented\npath"));
}
'''
        with tempfile.TemporaryDirectory(prefix='gh-exec-') as directory:
            d=Path(directory);cpp=d/'probe.cpp';cpp.write_text(source,encoding='utf-8');exe=d/('probe.exe' if os.name=='nt' else 'probe')
            b=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-O2','-I',str(ROOT),str(cpp),'-o',str(exe)],capture_output=True,text=True,timeout=90)
            self.assertEqual(b.returncode,0,b.stdout+b.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)


if __name__=='__main__':unittest.main()
