// SPDX-License-Identifier: GPL-3.0-only
// Original continuation bridge. Uses separately fetched generic host SHA-256.
#include "godhand_pc_packs/bridge.hpp"
#include "godhand_pc_packs/settings.hpp"
#include "godhand/sha256.h"
#include <atomic>
#include <cstdlib>
#include <iostream>

namespace godhand_pc_packs {
void apply(uint64_t offset, void* destination, size_t size, uint64_t disc_size, const char* route) noexcept {
    if (size == 0 || destination == nullptr || disc_size != retail_disc_size) return;
    try {
        static const Settings settings = [] {
            auto result = load(retail_disc_size, [](std::string_view name) {
                const auto* value = std::getenv(name.data());
                return value ? std::string(value) : std::string();
            }, [](std::span<const uint8_t> data) {
                return godhand::Sha256::hex(data.data(), data.size());
            });
            if (!result.error.empty())
                std::cerr << "[god-hand-pc-pack] disabled: " << result.error << '\n';
            else if (result.overlay)
                std::cerr << "[god-hand-pc-pack] configured " << result.overlay->bytes.size() << " bytes\n";
            return result;
        }();
        if (!settings.overlay) return;
        const auto count = settings.overlay->apply(offset, std::span(static_cast<uint8_t*>(destination), size));
        static std::atomic<unsigned> reports{0};
        if (count && reports.fetch_add(1) < 8)
            std::cerr << "[god-hand-pc-pack] applied " << count << " bytes (" << route << ")\n";
    } catch (const std::exception& error) {
        // The reader already obtained original bytes. Do not turn a pack error
        // into a failed game read or change bytes when validation failed.
        std::cerr << "[god-hand-pc-pack] read left original: " << error.what() << '\n';
    }
}
}
