// Original GPL-3.0-only invented concurrency tests, no runtime/game/audio input.
#include "audio_activity.hpp"
#include <atomic>
#include <cassert>
#include <iostream>
#include <latch>
#include <thread>
#include <vector>

using godhand_pc_pause::ActivityBarrier;

int main() {
    // Negative control: a naked atomic state check does not reserve activity.
    std::atomic<bool> parked{false};
    std::atomic<unsigned> consumed{0};
    std::latch checked(1), acknowledged(1), complete(1);
    std::thread oldCallback([&] {
        if (!parked.load()) {
            checked.count_down(); acknowledged.wait(); ++consumed;
        }
        complete.count_down();
    });
    checked.wait(); parked.store(true); const auto before = consumed.load();
    acknowledged.count_down(); complete.wait(); oldCallback.join();
    assert(parked.load() && before == 0 && consumed.load() == 1);

    ActivityBarrier gate;
    std::latch admitted(1), attempted(1), finished(1);
    std::thread callback([&] {
        auto lease = gate.try_enter(); assert(lease);
        admitted.count_down(); attempted.wait(); ++consumed;
        lease.reset(); finished.count_down();
    });
    admitted.wait();
    assert(!gate.try_freeze()); // Must not acknowledge across an admitted callback.
    attempted.count_down(); finished.wait(); callback.join();
    auto hold = gate.try_freeze(); assert(hold);
    const auto frozenCount = consumed.load();
    for (int n = 0; n < 100; ++n) assert(!gate.try_enter() && !gate.try_freeze());
    assert(consumed.load() == frozenCount);
    auto moved = std::move(hold); assert(!hold && moved);
    hold.reset(); assert(!gate.try_enter()); // Moved-from token must not unfreeze.
    moved.reset(); moved.reset();
    auto resume = gate.try_enter(); assert(resume);
    auto reassigned = std::move(resume); assert(!resume && reassigned);
    reassigned = {}; assert(gate.try_freeze()); // temporary freeze releases too.

    // Several independent consumers: releasing only one is insufficient.
    auto a = gate.try_enter(); auto b = gate.try_enter(); assert(a && b);
    a.reset(); assert(!gate.try_freeze()); b.reset(); assert(gate.try_freeze());

    // Concurrent admission/freeze stress; do not assume fairness or a deadline
    // for every attempt. Assert exclusion, then prove eventual idle acquisition.
    std::atomic<unsigned> inside{0}, freezes{0};
    std::vector<std::thread> readers;
    for (int n = 0; n < 4; ++n) readers.emplace_back([&] {
        for (int i = 0; i < 20000; ++i) {
            auto token = gate.try_enter();
            if (token) { ++inside; std::this_thread::yield(); --inside; }
        }
    });
    for (int i = 0; i < 20000; ++i) {
        auto freeze = gate.try_freeze();
        if (freeze) { ++freezes; assert(inside.load() == 0); }
    }
    for (auto &reader : readers) reader.join();
    auto final = gate.try_freeze(); assert(final && inside.load() == 0);
    (void)freezes;
    std::cout << "legacy-race admission drain exclusion move resume concurrent: PASS\n";
}
