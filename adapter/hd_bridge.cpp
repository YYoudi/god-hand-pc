// SPDX-License-Identifier: GPL-3.0-only
// Original app bridge. Upstream's generic SHA implementation is not vendored.
#include "godhand_pc_hd/runtime.hpp"
#include "godhand/sha256.h"

namespace godhand_hd {
std::string digest(std::span<const uint8_t> bytes) {
    return godhand::Sha256::hex(bytes.data(),bytes.size());
}
}
