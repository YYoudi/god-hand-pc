// SPDX-License-Identifier: GPL-3.0-only
// All values invented; no game or GPU input required.
#include "hd_timing.hpp"
#include <cassert>
#include <cstdio>
#include <limits>

using namespace godhand_hd;
template<class Error,class F> void refuses(F action) {
    bool threw=false;
    try { action(); } catch(const Error&) { threw=true; }
    assert(threw);
}
int main() {
    TimingTotals total;
    total.add({8,0,0,7,0,0,false});
    total.add({12,3,2,130,97,41,true});
    total.add({4,1,0,110,84,53,true});
    assert(total.batches==3 && total.states==24 && total.candidates==4 && total.matches==2);
    assert(total.gpuSamples==2 && total.prepareNs==247 && total.readbackNs==181 && total.gpuNs==94);
    assert(total.maxPrepareNs==130 && total.maxReadbackNs==97 && total.maxGpuNs==53);
    for(const auto bad: {TimingSample{1,2,0},TimingSample{3,1,2},TimingSample{2,1,0,7,8},
                        TimingSample{2,1,0,7,0,2,false},TimingSample{2,0,0,7,0,0,true}}) {
        refuses<std::invalid_argument>([&] { total.add(bad); });
        assert(total.batches==3 && total.prepareNs==247);
    }
    total.states=std::numeric_limits<uint64_t>::max();
    refuses<std::overflow_error>([&] { total.add({1,0,0,1,0,0,false}); });
    assert(total.batches==3 && total.prepareNs==247 && total.states==std::numeric_limits<uint64_t>::max());
    total={};assert(total.batches==0 && total.maxPrepareNs==0);
    // Timers are not subtracted from wall time or converted to fictitious FPS.
    total.add({1,1,1,10,7,33,true});
    assert(total.gpuNs==33 && total.prepareNs==10);
    std::puts("invented timing totals invariants atomic overflow reset: PASS");
}
