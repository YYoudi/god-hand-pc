// Original synthetic diagnostic, no game input or generated code.
// Link unchanged pinned GPL runtime; guarded allocations make freed-context
// reads reproducible instead of relying on CRT heap reuse. Not a runtime fix.
#include "runtime/ee_scheduler.h"
#include "ps2_runtime_macros.h"
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <new>
#include <vector>
namespace {
struct Guard { void *p; void *base; size_t bytes; };
Guard guards[4096]{}; size_t guardCount=0; bool guarded=false; bool nested=false; bool sequence=false; int depth=0;
int childId=0, calls=0, observed=0; bool deleting=true;
void *allocate(size_t n) {
    if (guarded && n>=1024) {
        const size_t size=(n+4095)&~size_t(4095);
        void *base=VirtualAlloc(nullptr,size,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
        if (!base || guardCount>=4096) throw std::bad_alloc{};
        void *p=static_cast<char*>(base)+size-((n+15)&~size_t(15));
        guards[guardCount++]={p,base,size}; return p;
    }
    if (void *p=std::malloc(n?n:1)) return p;
    throw std::bad_alloc{};
}
void release(void *p) noexcept {
    if (!p) return;
    for(size_t i=0;i<guardCount;++i) if(guards[i].p==p) {
        if(!VirtualFree(guards[i].base,guards[i].bytes,MEM_DECOMMIT)) std::abort();
        return; // Reservation retained so no new allocation reuses this address.
    }
    std::free(p);
}
void observer(uint8_t*,R5900Context *c,PS2Runtime *r) {
    const unsigned bits=static_cast<unsigned>(_mm_cvtsi128_si32(_mm_castps_si128(c->vu0_r)));
    observed=(_mm_movemask_epi8(_mm_cmpeq_epi32(_mm_castps_si128(c->vu0_r),_mm_set1_epi32(0x3f93579b)))==0xffff);
    std::fprintf(stderr,"SYNTHETIC observer shared_random=%08x ok=%d\n",bits,observed);
    c->vu0_r=_mm_castsi128_ps(_mm_set1_epi32(0x3f92468a));c->pc=0x100c;
    throw EeDispatcherTransfer{};
}
void finish(uint8_t*,R5900Context *c,PS2Runtime *r) {
    const bool ok=(_mm_movemask_epi8(_mm_cmpeq_epi32(_mm_castps_si128(c->vu0_r),_mm_set1_epi32(0x3f92468a)))==0xffff);
    observed=(observed==1 && ok)?2:0;
    std::fprintf(stderr,"SYNTHETIC ordinary-transfer-state ok=%d\n",ok);
    r->eeScheduler().requestStop();c->pc=0;
}
void child(uint8_t*,R5900Context *c,PS2Runtime *r) {
    ++calls; std::fprintf(stderr,"SYNTHETIC child calls=%d deleting=%d\n",calls,deleting);
    c->vu0_r=_mm_castsi128_ps(_mm_set1_epi32(0x3f93579b));
    r->eeScheduler().exitCurrent(deleting);
}
void nest(uint8_t*,R5900Context *c,PS2Runtime *r) {
    ++depth;c->vu0_r=_mm_castsi128_ps(_mm_set1_epi32(0x3f93579b));c->pc=0;
    std::fprintf(stderr,"SYNTHETIC nesting depth=%d\n",depth);
    if(depth<4){GuestInvocation i{};i.context.pc=0x1010;SET_GPR_U32(&i.context,29,0x20000);if(sequence){std::vector<GuestInvocation> v;v.push_back(std::move(i));r->eeScheduler().invokeCurrentSequence(std::move(v));}else r->eeScheduler().invokeCurrent(std::move(i));}
}
void mainGuest(uint8_t*,R5900Context *c,PS2Runtime *r) {
    if(nested){c->pc=0x1008;calls=1;GuestInvocation i{};i.context.pc=0x1010;SET_GPR_U32(&i.context,29,0x20000);if(sequence){std::vector<GuestInvocation> v;v.push_back(std::move(i));r->eeScheduler().invokeCurrentSequence(std::move(v));}else r->eeScheduler().invokeCurrent(std::move(i));}
    auto &s=r->eeScheduler(); EeThreadCreateParams p{};
    p.entry=0x1004;p.stack=0x10000;p.stackSize=0x1000;p.priority=1;
    childId=s.createThread(p);
    if(childId<2 || s.startThread(childId,0,*c,false)!=0) std::abort();
    std::fprintf(stderr,"SYNTHETIC created child=%d\n",childId);
    p.entry=0x1008;p.priority=2;
    const int observerId=s.createThread(p);
    if(observerId<2 || s.startThread(observerId,0,*c,false)!=0) std::abort();
    s.sleepCurrent();
}
LONG WINAPI crash(EXCEPTION_POINTERS *p) {
    std::fprintf(stderr,"SYNTHETIC FAULT code=%08lx operation=%llu address=%p calls=%d\n",
       p->ExceptionRecord->ExceptionCode,
       static_cast<unsigned long long>(p->ExceptionRecord->ExceptionInformation[0]),
       reinterpret_cast<void*>(p->ExceptionRecord->ExceptionInformation[1]),calls);
    return EXCEPTION_EXECUTE_HANDLER;
}
}
void *operator new(size_t n){return allocate(n);}
void *operator new[](size_t n){return allocate(n);}
void operator delete(void *p) noexcept{release(p);}
void operator delete[](void *p) noexcept{release(p);}
void operator delete(void *p,size_t) noexcept{release(p);}
void operator delete[](void *p,size_t) noexcept{release(p);}
const uint32_t g_ps2RecompiledFunctionTableBase=0x1000;
const uint32_t g_ps2RecompiledFunctionTableEnd=0x1014;
const uint32_t g_ps2RecompiledFunctionTableSlotCount=5;
PS2Runtime::RecompiledFunction g_ps2RecompiledFunctionTable[5]={mainGuest,child,observer,finish,nest};
int main(int argc,char **argv) {
    guarded=argc>1 && argv[1][0]=='g';deleting=argc<3 || argv[2][0]!='k';
    sequence=argc>3 && argv[3][0]=='s';nested=argc>3 && (argv[3][0]=='n'||sequence);
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    SetUnhandledExceptionFilter(crash);
    std::fprintf(stderr,"SYNTHETIC guarded=%d delete=%d GuestThreadBytes=%zu\n",guarded,deleting,sizeof(GuestThread));
    PS2Runtime r;
    std::vector<uint8_t> ram(32*1024*1024);
    R5900Context main{};main.pc=0x1000;
    if(!r.registerFunction(0x1000,mainGuest)||!r.registerFunction(0x1004,child))return 3;
    r.eeScheduler().reset(ram.data(),main);
    r.eeScheduler().run();
    const auto *t=r.eeScheduler().thread(childId);
    bool ok=calls==1 && observed==2 && (nested?depth==4:(deleting?t==nullptr:t!=nullptr));
    std::fprintf(stderr,"SYNTHETIC terminal ok=%d calls=%d child_present=%d\n",ok,calls,t!=nullptr);
    return ok?0:4;
}
