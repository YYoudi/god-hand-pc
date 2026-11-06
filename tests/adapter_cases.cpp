// SPDX-License-Identifier: GPL-3.0-only
// Invented byte/file fixtures only. The digest callback is deliberately a test
// double, not a SHA implementation. Actual host SHA integration is a runtime gate.
#include "settings.hpp"
#include <fstream>
#include <iostream>
#include <map>

using namespace godhand_pc_packs;
static void check(bool value) { if (!value) throw std::runtime_error("synthetic adapter check failed"); }
template<class F> static void refuses(F action) {
    bool rejected = false;
    try { action(); } catch (const std::exception&) { rejected = true; }
    check(rejected);
}
int main(int argc, char** argv) {
    check(argc == 2);
    size_t cases = 0;
    for (uint64_t at = 0; at < 24; ++at) for (size_t length = 1; length <= 12; ++length) {
        std::vector<uint8_t> payload(length);
        for (size_t i = 0; i < length; ++i) payload[i] = static_cast<uint8_t>(117 + i);
        Overlay overlay(at, payload, 64);
        for (uint64_t start = 0; start < 64; ++start) for (size_t size = 0; size <= 32; ++size) {
            std::vector<uint8_t> output(size + 16, 82), expected = output;
            size_t changed = 0;
            for (size_t i = 0; i < size; ++i) if (start + i >= at && start + i < at + length) {
                expected[8 + i] = payload[static_cast<size_t>(start + i - at)];
                ++changed;
            }
            check(overlay.apply(start, std::span(output).subspan(8, size)) == changed);
            check(output == expected); // includes both eight-byte canary borders
            ++cases;
        }
    }
    refuses([] { Overlay(0, {}, 64); });
    refuses([] { Overlay(65, {1}, 64); });
    refuses([] { Overlay(63, {1, 2}, 64); });
    refuses([] { Overlay(0, std::vector<uint8_t>(payload_budget + 1), payload_budget + 1); });
    std::vector<uint8_t> sentinel(4, 82);
    Overlay end(0, {7}, 64);
    refuses([&] { end.apply(UINT64_MAX - 1, sentinel); });
    check(sentinel == std::vector<uint8_t>(4, 82));
    check(decimal("18446744073709551615") == UINT64_MAX);
    for (auto value : {"", "-1", "+1", " 1", "1x", "18446744073709551616"})
        refuses([&] { decimal(value); });

    const auto file = std::filesystem::path(argv[1]);
    auto write = [&](std::string_view data) { std::ofstream out(file, std::ios::binary); out << data; };
    const std::string original(16, 'Q'); write(original);
    std::map<std::string, std::string> environment;
    int digest_calls = 0;
    auto get = [&](std::string_view name) { return environment[std::string(name)]; };
    auto digest = [&](std::span<const uint8_t> data) {
        ++digest_calls;
        const bool correct = data.size() == original.size() &&
            std::equal(data.begin(), data.end(), original.begin());
        return std::string(64, correct ? 'a' : 'b');
    };
    auto disabled = load(retail_disc_size, get, digest);
    check(!disabled.overlay && disabled.error.empty() && digest_calls == 0);
    environment = {{"GODHAND_PC_TEXTURE_FILE", file.string()}, {"GODHAND_PC_TEXTURE_OFFSET", "19"},
        {"GODHAND_PC_TEXTURE_SIZE", "16"}, {"GODHAND_PC_TEXTURE_SHA256", std::string(64, 'a')},
        {"GODHAND_PC_TEXTURE_PROFILE", std::string(retail_profile)}};
    const auto valid_environment = environment;
    auto valid = load(retail_disc_size, get, digest);
    check(valid.overlay.has_value() && valid.error.empty() && digest_calls == 1);
    check(valid.overlay->bytes == std::vector<uint8_t>(original.begin(), original.end()));
    size_t invalid_cases = 0;
    for (const auto& [key, value] : valid_environment) {
        environment = valid_environment; environment.erase(key);
        const auto result = load(retail_disc_size, get, digest);
        check(!result.overlay && !result.error.empty()); ++invalid_cases;
    }
    for (const auto& [key, value] : std::map<std::string, std::string>{
            {"GODHAND_PC_TEXTURE_PROFILE", "prototype"}, {"GODHAND_PC_TEXTURE_OFFSET", "-1"},
            {"GODHAND_PC_TEXTURE_SIZE", "0"}, {"GODHAND_PC_TEXTURE_SHA256", std::string(64, 'A')},
            {"GODHAND_PC_TEXTURE_FILE", (file.parent_path() / "absent.txt").string()}}) {
        environment = valid_environment; environment[key] = value;
        const auto result = load(retail_disc_size, get, digest);
        check(!result.overlay && !result.error.empty()); ++invalid_cases;
    }
    environment = valid_environment;
    check(!load(retail_disc_size - 1, get, digest).overlay); ++invalid_cases;
    for (auto data : {std::string(15, 'Q'), std::string(17, 'Q'), std::string(16, 'R')}) {
        write(data);
        const auto result = load(retail_disc_size, get, digest);
        check(!result.overlay && !result.error.empty()); ++invalid_cases;
    }
    write(original); environment["GODHAND_PC_TEXTURE_SHA256"] = std::string(64, 'b');
    check(!load(retail_disc_size, get, digest).overlay); ++invalid_cases;
    std::cout << "overlap_cases=" << cases << " invalid_settings=" << invalid_cases << '\n';
}
