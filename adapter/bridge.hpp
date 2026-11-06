// SPDX-License-Identifier: GPL-3.0-only
// Original host-read integration API. Never called on generated guest code.
#pragma once
#include <cstddef>
#include <cstdint>
namespace godhand_pc_packs {
void apply(uint64_t offset, void* destination, size_t size, uint64_t disc_size, const char* route) noexcept;
}
