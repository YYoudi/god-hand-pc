// SPDX-License-Identifier: GPL-3.0-only
// Invented typed host API/kernel model. NOT a GPU shader/driver/fidelity test.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <initializer_list>
#include <string>
#include <vector>

namespace godhand_hd {
struct Input { std::vector<uint32_t> words; explicit operator bool() const { return !words.empty(); } };
inline Input load() { return {{128,128,512,512}}; }
inline std::string classifier_source(const char*) { return "invented classifier stub"; }
inline std::string raster_source(const char*) { return "invented replacement stub"; }
}
namespace GSGpuShaders { constexpr const char* kRaster="invented original stub"; }
constexpr uint32_t kShaderStorageBuffer=21, kDynamicDraw=22;
constexpr uint32_t SFlags=0, STexSize=1, STpsm=2, STexMode=3, SClampLo=4;
constexpr uint32_t FTme=1, kStateWords=5;
struct Program { uint32_t id=41; std::array<int,1> loc={7}; };

struct Api {
    int64_t bindings=15, computeBlocks=12;
    mutable std::vector<std::string> calls;
    mutable std::vector<uint32_t> flags, pending;
    std::vector<uint32_t> predicted; // Invented kernel outcomes, not texture pixels.
    mutable uint32_t count=0;
    mutable bool visible=true;
    void GetInteger64v(uint32_t key,int64_t* out) const { *out=key==0x90DDu?bindings:computeBlocks; }
    void BindBuffer(uint32_t target,uint32_t buffer) const {
        assert(target==kShaderStorageBuffer && buffer==14); calls.push_back("bind-match");
    }
    void BufferData(uint32_t target,size_t bytes,const void* data,uint32_t usage) const {
        assert(target==kShaderStorageBuffer && usage==kDynamicDraw && bytes%4==0);
        const auto* words=static_cast<const uint32_t*>(data);
        if(bytes) flags.assign(words,words+bytes/4); else flags.clear();
        assert(std::all_of(flags.begin(),flags.end(),[](auto n){return n==0;}));
        pending.clear();visible=true;calls.push_back("reset");
    }
    void BindBufferBase(uint32_t target,uint32_t binding,uint32_t buffer) const {
        assert(target==kShaderStorageBuffer && binding==buffer && (binding==13 || binding==14));
        calls.push_back("binding"+std::to_string(binding));
    }
    void UseProgram(uint32_t id) const { assert(id==41);calls.push_back("program"); }
    void Uniform4ui(int location,uint32_t,uint32_t n,uint32_t z,uint32_t w) const {
        assert(location==7 && z==0 && w==0);count=n;calls.push_back("uniform");
    }
    void DispatchCompute(uint32_t x,uint32_t y,uint32_t z) const {
        assert(x==count && x==flags.size() && y==1 && z==1 && predicted.size()==x);
        pending=predicted;visible=false;calls.push_back("dispatch");
    }
    // Deliberately NO GetBufferSubData, query result or other CPU readback API.
};
struct Impl {
    Api api;
    godhand_hd::Input hdInput;
    Program hdClassifier;
    uint32_t hdInputBuffer=13,hdMatchBuffer=14,hdChecks=0;
    uint32_t stateCount=0,epoch=0,scale=3;
    bool compileOk=true;
    std::vector<uint32_t> states;
    Api& gl() { return api; }
    bool compile(Program&,const std::string&,const char*,std::initializer_list<const char*>) { return compileOk; }
    uint32_t makeBuffer(size_t,const void*,uint32_t binding) { return binding; }
    void barrier() { api.flags=api.pending;api.pending.clear();api.visible=true;api.calls.push_back("barrier"); }
    std::vector<uint32_t> consume() const { assert(api.visible);return api.flags; }
    void batch(size_t count,bool eligible=true) {
        stateCount=static_cast<uint32_t>(count);states.assign(count*kStateWords,0);
        for(size_t i=0;i<count;++i) {
            states[i*kStateWords+SFlags]=eligible?FTme:0;
            states[i*kStateWords+STexSize]=128u|(128u<<16u);
            states[i*kStateWords+STpsm]=0x14;
        }
        api.calls.clear();
    }
#include "hd_runtime_gpu.inc"
};

int main() {
    Impl empty;empty.hdPrepare();assert(empty.api.calls.empty());
    Impl badCaps;badCaps.api.bindings=14;assert(!badCaps.hdInitialize("invented"));
    assert(!badCaps.hdInput && badCaps.hdRasterText()==GSGpuShaders::kRaster);
    Impl badCompile;badCompile.compileOk=false;assert(!badCompile.hdInitialize("invented"));
    assert(!badCompile.hdInput);
    Impl good;assert(good.hdInitialize("invented"));
    const std::vector<std::string> submitted={"bind-match","reset","binding14","binding13","program","uniform","dispatch","barrier"};
    good.batch(2);good.api.predicted={1,0};good.hdPrepare();
    assert(good.api.calls==submitted && good.consume()==std::vector<uint32_t>({1,0}) && good.hdChecks==1);
    // Same state words/epoch, changed invented source outcome: reclassify, never reuse old true.
    good.batch(2);good.api.predicted={0,0};good.hdPrepare();
    assert(good.api.calls==submitted && good.consume()==std::vector<uint32_t>({0,0}) && good.hdChecks==2);
    good.batch(1,false);good.hdPrepare();
    assert(good.consume()==std::vector<uint32_t>({0}) && good.hdChecks==2 && good.api.calls.size()==4);
    good.batch(5);good.api.predicted={0,1,0,0,1};good.hdPrepare();
    assert(good.consume()==good.api.predicted && good.api.calls==submitted && good.hdChecks==3);
    good.batch(0);good.hdPrepare();assert(good.consume().empty() && good.api.calls.size()==4);
    // Every admission condition matters; each refused state clears the previous result.
    for(auto slot: {SFlags,STexSize,STpsm,STexMode,SClampLo}) {
        good.batch(1);good.states[slot]=(slot==STexMode)?0x10000u:(slot==SClampLo?1u:0u);
        good.hdPrepare();assert(good.consume()==std::vector<uint32_t>({0}) && good.hdChecks==3);
    }
    std::puts("invented GPU-result reset fresh batches barrier no CPU readback: PASS");
}
