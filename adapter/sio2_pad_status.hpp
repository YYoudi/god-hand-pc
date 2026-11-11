// SPDX-License-Identifier: GPL-3.0-only
// Original pad-batch status model. No game bytes, addresses or generated code.
// Protocol provenance and deliberately bounded acceptance: SIO2_PAD_STATUS.md.
#pragma once
#include <cstdint>
#include <optional>

namespace godhand_pc::sio2 {

// Only ordinary pad commands, at most one for each physical controller port.
// A mixed/card/multitap/duplicate batch must retain its existing device policy;
// refusing a model result is never equivalent to acknowledging a device.
class PadBatchStatus {
public:
    void observe(unsigned port, bool acknowledged) {
        if (port > 1 || (ports_ & (1u << port))) {
            supported_ = false;
            return;
        }
        ports_ |= 1u << port;
        if (!acknowledged) missing_ |= 1u << port;
    }
    void refuse() { supported_ = false; }
    [[nodiscard]] std::optional<uint32_t> result() const {
        if (!supported_ || !ports_) return std::nullopt;
        const uint32_t count = ports_ == 3 ? 2u : 1u;
        return 0x1000u | (count << 8u) |
               (missing_ ? (0xc000u | (missing_ << 16u)) : 0u);
    }
private:
    uint32_t ports_ = 0, missing_ = 0;
    bool supported_ = true;
};
} // namespace godhand_pc::sio2
