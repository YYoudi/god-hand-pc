// SPDX-License-Identifier: GPL-3.0-only
// Original host loader; game-derived reference/input files must stay private.
#pragma once
#include "hd_texture.hpp"
#include <cstdlib>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <string_view>

namespace godhand_hd {
// Implemented by our app bridge using the privately fetched generic SHA helper.
std::string digest(std::span<const uint8_t> bytes);

inline std::filesystem::path utf8_path(std::string_view value) {
    std::u8string encoded;
    encoded.reserve(value.size());
    for(unsigned char byte:value) encoded.push_back(static_cast<char8_t>(byte));
    return std::filesystem::path(encoded);
}

template<class Hash>
Input read_input(const std::filesystem::path& file, std::string_view profile,
                 std::string_view expected, Hash hash) {
    if(profile!="retail-us-slus-21503" || expected.size()!=64 ||
       expected.find_first_not_of("0123456789abcdef")!=std::string_view::npos)
        throw std::invalid_argument("incomplete HD identity protocol");
    std::ifstream input(file,std::ios::binary|std::ios::ate);
    if(!input) throw std::invalid_argument("cannot open HD input");
    const auto size=input.tellg();
    if(size<32 || size>64*1024*1024) throw std::invalid_argument("HD input budget");
    std::vector<uint8_t> bytes(static_cast<size_t>(size));input.seekg(0);
    if(!input.read(reinterpret_cast<char*>(bytes.data()),bytes.size()) ||
       input.peek()!=std::char_traits<char>::eof())
        throw std::invalid_argument("HD input length changed");
    if(hash(std::span<const uint8_t>(bytes))!=expected)
        throw std::invalid_argument("input hash mismatch");
    return parse(bytes);
}

inline Input load() noexcept {
    const char* file=std::getenv("GODHAND_PC_HD_FILE");
    if(!file || !*file) return {};
    try {
        const char* profile=std::getenv("GODHAND_PC_HD_PROFILE");
        const char* expected=std::getenv("GODHAND_PC_HD_SHA256");
        auto input=read_input(utf8_path(file),profile?profile:"",expected?expected:"",digest);
        const auto* h=input.words.data();
        std::fprintf(stderr,"[pc-hd] input verified source=%ux%u replacement=%ux%u replacement_bytes=%u\n",
                     h[0],h[1],h[2],h[3],h[2]*h[3]*4u);
        return input;
    } catch(const std::exception& error) {
        std::fprintf(stderr,"[pc-hd] disabled: %s\n",error.what());return {};
    }
}
}
