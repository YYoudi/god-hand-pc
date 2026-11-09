// Original GPL-3.0-only bounded diagnostic routing; no guest addresses or data.
#pragma once
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <string_view>

namespace godhand_pc_probe {
inline std::atomic<uint64_t> observed_field{0};
inline bool active() {
    static const bool on = [] {
        const char *flag = std::getenv("GODHAND_PC_CONTROLS_PROBE");
        const char *script = std::getenv("GODHAND_CONTROLS_SELFTEST");
        return flag && std::string_view(flag) == "1" && script && *script &&
               std::string_view(script) != "0";
    }();
    return on;
}
inline bool ready() {
    static const uint64_t target = []() -> uint64_t {
        if (!active()) return 0;
        const char *value = std::getenv("GODHAND_PC_CONTROLS_PROBE_FIELD");
        if (!value || *value < '0' || *value > '9') return 0;
        char *end = nullptr;
        errno = 0;
        const auto number = std::strtoull(value, &end, 10);
        return errno || !end || *end ? 0 : number;
    }();
    return !target || observed_field.load(std::memory_order_relaxed) >= target;
}
} // namespace godhand_pc_probe
