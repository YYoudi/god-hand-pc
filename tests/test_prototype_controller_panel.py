"""Original invented host/UI inputs; no OS events, graphics or game data."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrototypeControllerPanelTests(unittest.TestCase):
    def test_explicit_sticks_share_gates_and_v1_layout_is_unchanged(self):
        compiler=next((shutil.which(x) for x in ('g++','clang++','c++') if shutil.which(x)),None)
        if not compiler:self.skipTest('C++17 compiler required')
        source=r'''
#include "adapter/prototype_controller_panel.hpp"
#include <cassert>
using namespace godhand_pc::prototype_controller;
int main(){
 Context good{true,true,true,false,false};Panel v1;assert(v1.show(good));
 constexpr std::array<std::string_view,4> text={"lup:0.2\n","ldown:0.2\n","lleft:0.2\n","lright:0.2\n"};
 auto legacy=layout(640,480);assert(legacy.buttons.size()==9);
 for(size_t n=0;n<9;++n){auto b=legacy.buttons[n];assert(b.x==12+float(n%5)*124&&b.y==395+float(n/5)*25&&b.width==120&&b.height==22);}
 for(size_t n=0;n<stickActions.size();++n){
  const auto a=stickActions[n];assert(pulse(a)==text[n]);assert(!v1.request(a,1000,good));
  auto b=stickLayout(640,480).buttons[n];float x=b.x+b.width/2,y=b.y+b.height/2;
  assert(!legacy.at(x,y));assert(!hit(ControlSet::DigitalV1,640,480,x,y));
  assert(hit(ControlSet::LeftStickV2,640,480,x,y)==a);
  Click old;assert(old.observe(x,y,640,480,1000,true));assert(!old.take(640,480,1001,true));
  Click edge(ControlSet::LeftStickV2);assert(edge.observe(x,y,640,480,1000,true));assert(edge.take(640,480,1001,true)==a);
  Panel p(ControlSet::LeftStickV2);assert(p.show(good));int sent=0;
  assert(p.request(a,1000,good));assert(!p.request(Action::Down,1001,good));
  p.tick(1002,good,[&](Action got){assert(got==a);++sent;return Result::Submitted;});assert(sent==1);
  assert(!p.request(Action::Circle,1200,good));assert(!p.request(a,1200,good));
  assert(p.request(Action::Down,1302,good));assert(!p.request(a,1303,good));
  p.tick(1303,good,[&](Action got){assert(got==Action::Down);++sent;return Result::Submitted;});assert(sent==2);
  for(int gate=0;gate<5;++gate){auto c=good;if(gate==0)c.controlsOpen=true;if(gate==1)c.focused=false;if(gate==2)c.verifiedProfile=false;if(gate==3)c.keyboardOnly=false;if(gate==4)c.bridgeBusy=true;
   Panel q(ControlSet::LeftStickV2);assert(q.show(good));assert(q.request(a,2000,good));q.tick(2001,c,[&](Action){++sent;return Result::Submitted;});q.tick(3000,good,[&](Action){++sent;return Result::Submitted;});assert(sent==2);
  }
  Panel bad(ControlSet::LeftStickV2);assert(bad.show(good));assert(bad.request(a,1000,good));bad.tick(1000,good,[](Action){return Result::UnknownDelivery;});assert(bad.faulted());assert(!bad.request(Action::Down,2000,good));
 }
 Panel invalid(static_cast<ControlSet>(99));assert(!invalid.show(good));
 Click invalidClick(static_cast<ControlSet>(99));assert(!invalidClick.observe(30,30,640,480,1000,true));
 assert(!stickLayout(479,480).valid);assert(!stickLayout(640,299).valid);
}
'''
        with tempfile.TemporaryDirectory(prefix='gh-stick-') as directory:
            d=Path(directory);cpp=d/'probe.cpp';cpp.write_text(source,encoding='utf-8');exe=d/('probe.exe' if os.name=='nt' else 'probe')
            b=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-O2','-I',str(ROOT),str(cpp),'-o',str(exe)],capture_output=True,text=True,timeout=90)
            self.assertEqual(b.returncode,0,b.stdout+b.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_native_callback_chain_bindings_and_f1_owner_with_stubs(self):
        compiler=next((shutil.which(x) for x in ('g++','clang++','c++') if shutil.which(x)),None)
        if not compiler:self.skipTest('C++17 compiler required')
        raylib=r'''
#pragma once
struct Color{unsigned char r,g,b,a;};struct Rectangle{float x,y,width,height;};
constexpr int MOUSE_BUTTON_LEFT=0;
extern int width,height;extern bool focus;
inline int GetScreenWidth(){return width;}inline int GetScreenHeight(){return height;}
inline bool IsWindowFocused(){return focus;}
inline void DrawRectangleRec(Rectangle,Color){}inline void DrawRectangleLinesEx(Rectangle,float,Color){}
inline void DrawText(const char*,int,int,int,Color){}
'''
        inputs=r'''
#pragma once
#include <string>
#include <string_view>
#include <vector>
extern bool overlay;extern std::string binding;
namespace ps2_host_input {
inline bool overlayOpen(){return overlay;}
namespace controls {
enum class Kind{Keys,Controller,Other};
inline std::vector<std::string> bindings(unsigned,std::string_view){return {binding};}
inline Kind kindOf(std::string_view b){return b.find('&')==b.npos?Kind::Keys:Kind::Other;}
}}
'''
        source=r'''
#include "adapter/prototype_controller_native.hpp"
#include <cassert>
using namespace godhand_pc::prototype_controller;
int width=640,height=480;bool focus=true,overlay=false;std::string binding="Keyboard/K";
struct GLFWwindow{};GLFWwindow window;bool hasWindow=true;PrototypeMouseCallback installed=nullptr;
double mouseX=0,mouseY=0;int chained=0;
void oldMouse(GLFWwindow*,int,int,int){++chained;}
void foreignMouse(GLFWwindow*,int,int,int){}
extern "C" GLFWwindow* glfwGetCurrentContext(){return hasWindow?&window:nullptr;}
extern "C" PrototypeMouseCallback glfwSetMouseButtonCallback(GLFWwindow*,PrototypeMouseCallback cb){auto p=installed;installed=cb;return p;}
extern "C" void glfwGetCursorPos(GLFWwindow*,double* x,double* y){*x=mouseX;*y=mouseY;}
int main(){
 NativePanel p;assert(!p.initialize(false,true));assert(!p.initialize(true,false));
 hasWindow=false;assert(!p.initialize(true,true));hasWindow=true;installed=&oldMouse;
 assert(p.initialize(true,true));NativePanel other;assert(!other.initialize(true,true));
 assert(p.showFromF2());
 const auto b=layout(width,height).buttons[2];mouseX=b.x+5;mouseY=b.y+5;
 int sent=0;auto dispatch=[&](Action a){assert(a==Action::Down);++sent;return Result::Submitted;};
 installed(&window,0,1,0);installed(&window,0,0,0);assert(chained==2);
 p.tick(monotonicMs(),false,dispatch);assert(sent==1);
 p.tick(monotonicMs(),false,dispatch);assert(sent==1);
 p.shutdown();assert(installed==&oldMouse);
 // Fresh instance: F1 takes ownership after a mouse callback, before frame tick.
 NativePanel q;assert(q.initialize(true,true));assert(q.showFromF2());
 installed(&window,0,1,0);overlay=true;q.tick(monotonicMs(),false,dispatch);
 overlay=false;q.tick(monotonicMs()+1000,false,dispatch);assert(sent==1);
 installed(&window,0,1,0);q.tick(monotonicMs()+1001,false,dispatch);assert(sent==1); // closed
 assert(q.showFromF2());binding="Pointer-0/LeftButton";
 installed(&window,0,1,0);q.tick(monotonicMs(),false,dispatch);assert(sent==1&&!q.showFromF2());
 binding="Keyboard/K & Keyboard/L";assert(!q.showFromF2());
 binding="Keyboard/K";assert(q.showFromF2());
 installed(&window,0,1,0);++width;q.tick(monotonicMs(),false,dispatch);assert(sent==1);--width;
 installed(&window,0,1,0);focus=false;q.tick(monotonicMs(),false,dispatch);focus=true;
 q.tick(monotonicMs(),false,dispatch);assert(sent==1);
 q.writerFault();assert(!q.showFromF2());
 installed=&foreignMouse;q.shutdown();assert(installed==&foreignMouse); // no callback theft
 assert(!other.initialize(true,true,static_cast<ControlSet>(99)));
 assert(other.initialize(true,true));other.shutdown();
 NativePanel sticks;assert(sticks.initialize(true,true,ControlSet::LeftStickV2));assert(sticks.showFromF2());
 const auto s=stickLayout(width,height).buttons[3];mouseX=s.x+5;mouseY=s.y+5;
 installed(&window,0,1,0);installed(&window,0,0,0);
 sticks.tick(monotonicMs(),false,[&](Action a){assert(a==Action::StickRight);++sent;return Result::Submitted;});assert(sent==2);
 sticks.shutdown();
}
'''
        with tempfile.TemporaryDirectory(prefix='gh-panel-native-') as directory:
            d=Path(directory);(d/'raylib.h').write_text(raylib,encoding='utf-8');(d/'ps2_host_input.h').write_text(inputs,encoding='utf-8')
            cpp=d/'probe.cpp';cpp.write_text(source,encoding='utf-8');exe=d/('probe.exe' if os.name=='nt' else 'probe')
            b=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-O2','-I',str(d),'-I',str(ROOT),str(cpp),'-o',str(exe)],capture_output=True,text=True,timeout=90)
            self.assertEqual(b.returncode,0,b.stdout+b.stderr)
            r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_request_gates_edges_and_delivery_limits(self):
        compiler = next((shutil.which(x) for x in ('g++','clang++','c++') if shutil.which(x)),None)
        if not compiler:
            self.skipTest('C++17 compiler required')
        source = r'''
#include "adapter/prototype_controller_panel.hpp"
#include <cassert>
#include <limits>
using namespace godhand_pc::prototype_controller;
int main() {
 Context good{true,true,true,false,false};
 for(int n=0;n<5;++n) {
  Panel p;auto bad=good;
  if(n==0)bad.verifiedProfile=false;
  if(n==1)bad.keyboardOnly=false;
  if(n==2)bad.focused=false;
  if(n==3)bad.controlsOpen=true;
  if(n==4)bad.bridgeBusy=true;
  int sent=0;auto send=[&](Action){++sent;return Result::Submitted;};
  if(n<4)assert(!p.show(bad));
  assert(p.show(good));
  assert(p.request(Action::Down,1000,good));
  p.tick(1001,bad,send);assert(sent==0&&!p.pending());
  if(n==0||n==1||n==3)assert(!p.visible());
  // F1/focus transitions must never defer an action until the owner closes.
  p.tick(1002,good,send);assert(sent==0);
 }
 Panel p;assert(!p.visible());assert(p.show(good));
 assert(!p.request(static_cast<Action>(99),1000,good));
 int sent=0;auto send=[&](Action a){assert(a==Action::Down);++sent;return Result::Submitted;};
 assert(p.request(Action::Down,1000,good));
 assert(!p.request(Action::Up,1000,good));
 p.tick(1001,good,send);assert(sent==1&&p.status()==Status::Submitted&&p.lastAction()==Action::Down);
 p.tick(1002,good,send);assert(sent==1);
 assert(p.busy(1300));assert(!p.busy(1301));
 assert(!p.request(Action::Up,1300,good));
 assert(p.request(Action::Down,1301,good));p.tick(1302,good,send);assert(sent==2);
 assert(p.request(Action::Hide,1303,good));assert(!p.visible());
 assert(!p.request(Action::Down,2000,good));
 assert(p.show(good));assert(p.request(Action::Down,2000,good));
 p.tick(1999,good,send);assert(sent==2&&p.status()==Status::ReversedClock);
 assert(p.request(Action::Down,2000,good));p.tick(2501,good,send);
 assert(sent==2&&p.status()==Status::Expired);
 assert(p.request(Action::Down,3000,good));p.tick(3500,good,send);assert(sent==3);
 assert(p.request(Action::Down,4000,good));
 p.tick(4000,good,[](Action){return Result::Refused;});assert(p.status()==Status::BackendRefused&&!p.faulted());
 assert(p.request(Action::Down,4001,good));
 p.tick(4001,good,[](Action){return Result::UnknownDelivery;});
 assert(p.faulted()&&p.status()==Status::WriterFault);
 assert(!p.request(Action::Down,5000,good));assert(!p.show(good));
 p.hide();p.tick(5000,good,send);assert(sent==3&&p.status()==Status::WriterFault);
 Panel end;assert(end.show(good));assert(end.request(Action::Down,UINT64_MAX-1,good));
 end.tick(UINT64_MAX-1,good,[](Action){return Result::Submitted;});assert(end.busy(UINT64_MAX-1));
 for(auto a:actions) {
  auto s=pulse(a);
  if(a==Action::OpenMenu||a==Action::Hide)assert(s.empty());
  else {assert(s.size()<20);assert(s.substr(s.size()-5)==":0.2\n");}
 }
 for(auto dims:std::array<std::array<int,2>,4>{{{480,300},{640,480},{640,515},{1280,720}}}) {
  auto l=layout(dims[0],dims[1]);assert(l.valid);
  for(size_t n=0;n<actions.size();++n) {
   auto b=l.buttons[n];auto x=b.x+b.width/2,y=b.y+b.height/2;
   assert(l.at(x,y)==actions[n]);
   Click c;assert(c.observe(x,y,dims[0],dims[1],1000,true));
   assert(!c.observe(x,y,dims[0],dims[1],1000,true)); // no double queue
   assert(c.take(dims[0],dims[1],1500,true)==actions[n]);
   assert(!c.take(dims[0],dims[1],1500,true));
   assert(c.observe(x,y,dims[0],dims[1],1000,true));
   assert(!c.take(dims[0]+1,dims[1],1000,true)); // resize
   assert(!c.take(dims[0],dims[1],1001,true));
   assert(c.observe(x,y,dims[0],dims[1],1000,true));assert(!c.take(dims[0],dims[1],1501,true));
   assert(c.observe(x,y,dims[0],dims[1],1000,true));assert(!c.take(dims[0],dims[1],999,true));
   assert(c.observe(x,y,dims[0],dims[1],1000,true));assert(!c.take(dims[0],dims[1],1000,false));
   assert(c.observe(x,y,dims[0],dims[1],1000,true));c.clear();assert(!c.take(dims[0],dims[1],1000,true));
  }
  assert(!l.at(-1,0));assert(!l.at(float(dims[0]),float(dims[1])));
  assert(!l.at(std::numeric_limits<float>::quiet_NaN(),0));
 }
 assert(!layout(479,300).valid&&!layout(480,299).valid);
 Click c;assert(!c.observe(20,20,640,480,1000,false));
 assert(!c.observe(std::numeric_limits<float>::infinity(),20,640,480,1000,true));
}
'''
        with tempfile.TemporaryDirectory(prefix='gh-panel-') as directory:
            d=Path(directory);cpp=d/'probe.cpp';exe=d/('probe.exe' if os.name=='nt' else 'probe')
            cpp.write_text(source,encoding='utf-8')
            build=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-O2','-I',str(ROOT),str(cpp),'-o',str(exe)],capture_output=True,text=True,timeout=90)
            self.assertEqual(build.returncode,0,build.stdout+build.stderr)
            run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)


if __name__=='__main__':
    unittest.main()
