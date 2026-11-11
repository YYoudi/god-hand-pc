// SPDX-License-Identifier: GPL-3.0-only
// Original host-only event latch. No game data, key codes or windowing dependency.
#pragma once
#include <cstdint>

namespace godhand_pc::window_shortcuts {
enum class Key : unsigned { Controls, Developer, Back, Count };
enum class Action : unsigned { Press, Release, Repeat };

// One pending edge per owned shortcut, consumed on the window thread.
// In particular, release must not erase an unconsumed short press.
// Call take even when the legacy edge is true: otherwise the event would fire
// again on the next frame. Unowned keys and OS repeats are not our input.
class PressEdges {
public:
    void observe(Key key, Action action, bool focused) {
        if (!focused) { clear(); return; }
        if (valid(key) && action == Action::Press) pending_ |= mask(key);
    }
    [[nodiscard]] bool take(Key key, bool focused, bool legacy_edge = false) {
        if (!focused) { clear(); return false; }
        if (!valid(key)) return false;
        const auto bit = mask(key);
        const bool queued = (pending_ & bit) != 0;
        pending_ &= ~bit;
        return queued || legacy_edge;
    }
    void clear() { pending_ = 0; }
private:
    static bool valid(Key key) { return static_cast<unsigned>(key) < static_cast<unsigned>(Key::Count); }
    static uint32_t mask(Key key) { return 1u << static_cast<unsigned>(key); }
    uint32_t pending_ = 0;
};
} // namespace godhand_pc::window_shortcuts
