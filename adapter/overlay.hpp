// SPDX-License-Identifier: GPL-3.0-only
// Original continuation range helper. No game data or instruction addresses.
#pragma once
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <limits>
#include <span>
#include <stdexcept>
#include <utility>
#include <vector>

namespace godhand_pc_packs {
inline constexpr uint64_t payload_budget = 16u * 1024u * 1024u;

struct Overlay {
    uint64_t offset;
    std::vector<uint8_t> bytes;

    Overlay(uint64_t start, std::vector<uint8_t> data, uint64_t disc_size)
        : offset(start), bytes(std::move(data)) {
        if (bytes.empty() || bytes.size() > payload_budget || start > disc_size ||
            bytes.size() > disc_size - start)
            throw std::runtime_error("payload exceeds disc bounds or budget");
    }

    size_t apply(uint64_t read_start, std::span<uint8_t> destination) const {
        if (destination.size() > std::numeric_limits<uint64_t>::max() - read_start)
            throw std::runtime_error("read range overflow");
        const auto begin = std::max(read_start, offset);
        const auto end = std::min(read_start + destination.size(), offset + bytes.size());
        if (end <= begin) return 0;
        const auto count = static_cast<size_t>(end - begin);
        std::memcpy(destination.data() + (begin - read_start), bytes.data() + (begin - offset), count);
        return count;
    }
};
}
