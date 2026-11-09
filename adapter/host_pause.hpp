// Original GPL-3.0-only host coordination primitive. No guest addresses or code.
#pragma once

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdlib>
#include <mutex>
#include <type_traits>

namespace godhand_pc_pause {
class Gate {
public:
    using Clock = std::chrono::steady_clock;
    using Duration = Clock::duration;

    void request(bool value) {
        {
            std::lock_guard lock(mutex_);
            wanted_.store(value, std::memory_order_release);
        }
        changed_.notify_all();
    }
    bool requested() const noexcept { return wanted_.load(std::memory_order_acquire); }
    bool parked() const noexcept { return parked_.load(std::memory_order_acquire); }

    // Executor only, outside guest execution. A blocked readiness check does not
    // acknowledge a pause. Only the integration can establish machine quiescence.
    // Neither this primitive nor its portable tests prove any runtime is safe.
    template<class Ready, class Stop, class Enter, class Rebase>
    bool service(Ready ready, Stop stop, Enter enter, Rebase rebase) {
        static_assert(std::is_nothrow_invocable_v<Enter>);
        static_assert(std::is_nothrow_invocable_v<Rebase, Duration>);
        if (!requested() || stop() || !ready()) return false;
        std::unique_lock lock(mutex_);
        if (!requested() || stop()) return false;
        started_ = Clock::now();
        parked_.store(true, std::memory_order_release);
        enter();
        while (requested() && !stop())
            changed_.wait_for(lock, std::chrono::milliseconds(5));
        const auto elapsed = Clock::now() - started_;
        // Rebase before releasing the executor or reporting resumed. Keep guest
        // cycle deadlines unchanged; only host-time anchors move in the adapter.
        rebase(elapsed);
        omitted_ += elapsed;
        parked_.store(false, std::memory_order_release);
        return true;
    }

    // Host telemetry/audio production-rate clock, not a replacement guest clock.
    // It freezes while parked and remains continuous across any number of holds.
    Clock::time_point now() {
        std::lock_guard lock(mutex_);
        return (parked() ? started_ : Clock::now()) - omitted_;
    }

private:
    std::atomic<bool> wanted_{false};
    std::atomic<bool> parked_{false};
    std::mutex mutex_;
    std::condition_variable changed_;
    Clock::time_point started_{};
    Duration omitted_{};
};

inline Gate &gate() { static Gate instance; return instance; }
inline bool enabled() {
    static const bool on = [] {
        const char *v = std::getenv("GODHAND_PC_CONTROLS_PAUSE");
        return v && v[0] == '1' && v[1] == '\0';
    }();
    return on;
}
inline Gate::Clock::time_point now() {
    return enabled() ? gate().now() : Gate::Clock::now();
}
} // namespace godhand_pc_pause
