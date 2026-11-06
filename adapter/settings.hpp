// SPDX-License-Identifier: GPL-3.0-only
// Original data-only loader. Digest implementation is supplied by the host.
#pragma once
#include "overlay.hpp"
#include <charconv>
#include <filesystem>
#include <fstream>
#include <optional>
#include <string>
#include <string_view>

namespace godhand_pc_packs {
inline constexpr uint64_t retail_disc_size = 1567686656;
inline constexpr std::string_view retail_profile = "retail-us-slus-21503";

inline uint64_t decimal(std::string_view text) {
    uint64_t value = 0;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    if (text.empty() || parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size())
        throw std::runtime_error("pack parameter is not unsigned decimal");
    return value;
}

struct Settings {
    std::optional<Overlay> overlay;
    std::string error;
};

template<class Environment, class Digest>
Settings load(uint64_t disc_size, Environment environment, Digest digest) {
    try {
        const std::string_view keys[] = {"GODHAND_PC_TEXTURE_FILE", "GODHAND_PC_TEXTURE_OFFSET",
            "GODHAND_PC_TEXTURE_SIZE", "GODHAND_PC_TEXTURE_SHA256", "GODHAND_PC_TEXTURE_PROFILE"};
        std::string values[5];
        size_t present = 0;
        for (size_t i = 0; i < 5; ++i) {
            values[i] = environment(keys[i]);
            present += !values[i].empty();
        }
        if (present == 0) return {};
        if (present != 5) throw std::runtime_error("incomplete native pack protocol");
        if (disc_size != retail_disc_size || values[4] != retail_profile)
            throw std::runtime_error("unsupported pack disc/profile");
        const auto offset = decimal(values[1]);
        const auto size = decimal(values[2]);
        if (size == 0 || size > payload_budget || offset > disc_size || size > disc_size - offset)
            throw std::runtime_error("pack exceeds disc bounds or budget");
        if (values[3].size() != 64 || !std::all_of(values[3].begin(), values[3].end(), [](char c) {
                return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'); }))
            throw std::runtime_error("invalid expected payload digest");
        std::ifstream input(std::filesystem::path(values[0]), std::ios::binary);
        if (!input) throw std::runtime_error("cannot open pack payload");
        std::vector<uint8_t> bytes(static_cast<size_t>(size));
        input.read(reinterpret_cast<char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
        if (input.gcount() != static_cast<std::streamsize>(bytes.size()) ||
            input.peek() != std::char_traits<char>::eof())
            throw std::runtime_error("pack payload length mismatch");
        if (digest(std::span<const uint8_t>(bytes)) != values[3])
            throw std::runtime_error("pack payload digest mismatch");
        return {Overlay(offset, std::move(bytes), disc_size), {}};
    } catch (const std::exception& error) {
        return {std::nullopt, error.what()};
    }
}
}
