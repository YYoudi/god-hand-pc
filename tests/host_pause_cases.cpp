// Original invented executor/clock scenarios; no runtime, disc or game inputs.
#include "host_pause.hpp"
#include <cstdlib>
#include <iostream>
#include <thread>

using namespace std::chrono_literals;
using godhand_pc_pause::Gate;
void require(bool value) { if (!value) std::abort(); }
template<class Predicate> void until(Predicate predicate) {
    const auto deadline = Gate::Clock::now() + 3s;
    while (!predicate()) {
        require(Gate::Clock::now() < deadline);
        std::this_thread::sleep_for(1ms);
    }
}
int main() {
    Gate gate;
    std::atomic<bool> stopped{false}, ready{false};
    std::atomic<unsigned> ticks{0}, entries{0}, rebases{0};
    std::atomic<long long> omitted{0};
    const auto origin = gate.now();
    std::thread executor([&] {
        while (!stopped.load()) {
            gate.service([&]{return ready.load();}, [&]{return stopped.load();},
                         [&]() noexcept { ++entries; },
                         [&](auto delta) noexcept {
                             omitted += std::chrono::duration_cast<std::chrono::nanoseconds>(delta).count();
                             ++rebases;
                         });
            ++ticks;
            std::this_thread::sleep_for(100us);
        }
    });
    until([&]{return ticks.load() > 5;});
    gate.request(true);
    const auto before = ticks.load();
    until([&]{return ticks.load() > before + 5;});
    require(!gate.parked() && entries == 0); // blocker must not claim paused
    gate.request(false);
    ready = true;
    const auto cancelled = ticks.load();
    until([&]{return ticks.load() > cancelled + 5;});
    require(entries == 0); // cancellation before readiness, no later surprise hold
    for (unsigned i = 0; i < 3; ++i) {
        gate.request(true);
        until([&]{return gate.parked();});
        const auto frozen = gate.now();
        const auto count = ticks.load();
        std::this_thread::sleep_for(30ms);
        require(gate.now() == frozen && ticks.load() == count);
        gate.request(false);
        until([&]{return !gate.parked() && rebases.load() == i + 1;});
        require(gate.now() >= frozen);
        until([&]{return ticks.load() > count + 3;});
    }
    gate.request(true);
    until([&]{return gate.parked();});
    stopped = true; // stop must escape even without a host close/request(false)
    executor.join();
    require(!gate.parked() && entries == 4 && rebases == 4 && omitted > 0);
    require(gate.now() >= origin);
    std::cout << "blocker cancellation frozen-clock frozen-executor reentry stop: PASS\n";
}
