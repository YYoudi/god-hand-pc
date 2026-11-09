// SPDX-License-Identifier: GPL-3.0-only
// Original measurement arithmetic only. Not wired into installed HD variants.
#pragma once
#include <algorithm>
#include <cstdint>
#include <limits>
#include <stdexcept>

namespace godhand_hd {
struct TimingSample {
    uint64_t states=0, candidates=0, matches=0;
    uint64_t prepareNs=0, readbackNs=0, gpuNs=0;
    bool gpuMeasured=false;
};

struct TimingTotals {
    uint64_t batches=0, states=0, candidates=0, matches=0, gpuSamples=0;
    uint64_t prepareNs=0, readbackNs=0, gpuNs=0;
    uint64_t maxPrepareNs=0, maxReadbackNs=0, maxGpuNs=0;

    void add(const TimingSample& sample) {
        if(sample.matches>sample.candidates || sample.candidates>sample.states ||
           sample.readbackNs>sample.prepareNs ||
           (!sample.gpuMeasured && sample.gpuNs!=0) ||
           (sample.gpuMeasured && sample.candidates==0))
            throw std::invalid_argument("inconsistent HD timing sample");
        auto sum=[](uint64_t a,uint64_t b) {
            if(b>std::numeric_limits<uint64_t>::max()-a)
                throw std::overflow_error("HD timing total overflow");
            return a+b;
        };
        // Validate the complete update first; refusal never leaves partial totals.
        TimingTotals next=*this;
        next.batches=sum(batches,1);
        next.states=sum(states,sample.states);
        next.candidates=sum(candidates,sample.candidates);
        next.matches=sum(matches,sample.matches);
        next.gpuSamples=sum(gpuSamples,sample.gpuMeasured?1:0);
        next.prepareNs=sum(prepareNs,sample.prepareNs);
        next.readbackNs=sum(readbackNs,sample.readbackNs);
        next.gpuNs=sum(gpuNs,sample.gpuNs);
        next.maxPrepareNs=std::max(maxPrepareNs,sample.prepareNs);
        next.maxReadbackNs=std::max(maxReadbackNs,sample.readbackNs);
        next.maxGpuNs=std::max(maxGpuNs,sample.gpuNs);
        *this=next;
    }
};
} // namespace godhand_hd
