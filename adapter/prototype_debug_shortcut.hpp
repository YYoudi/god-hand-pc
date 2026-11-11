// Original GPL-3.0-only host input sequencing. No game code, addresses or assets.
#pragma once
#include <cstdint>

namespace godhand_pc::prototype {
enum class Pulse { HoldL2, PressR3 };
enum class Phase { Idle, Pending, Holding, ChordSent, Finished, Refused };
enum class Refusal { None, ControlsOpen, Busy, WriterFailed, MissedTiming, ClockReversed };

// Requests the prototype's existing controller chord, NOT a guest function call
// or an acknowledgement that its debug menu opened. A backend must expire L2
// after 800 ms and R3 after 150 ms. No persistent held input is requested.
class DebugShortcut {
public:
    bool request(bool controlsOpen) {
        if (active()) { refusal_ = Refusal::Busy; return false; }
        refusal_ = Refusal::None;
        if (controlsOpen) { refuse(Refusal::ControlsOpen); return false; }
        phase_ = Phase::Pending;
        return true;
    }
    template<class Emit> void tick(uint64_t nowMs, bool controlsOpen, Emit emit) {
        if (!active()) return;
        if (controlsOpen) { refuse(Refusal::ControlsOpen); return; }
        if (phase_ == Phase::Pending) {
            if (!emit(Pulse::HoldL2)) { refuse(Refusal::WriterFailed); return; }
            start_ = last_ = nowMs;
            phase_ = Phase::Holding;
            return;
        }
        if (nowMs < last_) { refuse(Refusal::ClockReversed); return; }
        last_ = nowMs;
        const auto elapsed = nowMs - start_;
        if (phase_ == Phase::Holding) {
            // Never deliver R3 alone after the earlier L2 pulse expired.
            if (elapsed > 600) { refuse(Refusal::MissedTiming); return; }
            if (elapsed >= 150) {
                if (!emit(Pulse::PressR3)) { refuse(Refusal::WriterFailed); return; }
                phase_ = Phase::ChordSent;
            }
        }
        if (phase_ == Phase::ChordSent && elapsed >= 800) phase_ = Phase::Finished;
    }
    [[nodiscard]] bool active() const {
        return phase_ == Phase::Pending || phase_ == Phase::Holding || phase_ == Phase::ChordSent;
    }
    [[nodiscard]] Phase phase() const { return phase_; }
    [[nodiscard]] Refusal refusal() const { return refusal_; }
private:
    void refuse(Refusal reason) { phase_ = Phase::Refused; refusal_ = reason; }
    Phase phase_ = Phase::Idle;
    Refusal refusal_ = Refusal::None;
    uint64_t start_ = 0, last_ = 0;
};
} // namespace godhand_pc::prototype
