// SPDX-License-Identifier: GPL-3.0-only
// Original invented file bytes and hash callback, not the native SHA implementation.
#include "hd_runtime.hpp"
#include <cassert>
#include <iostream>

int main(int argc,char** argv) {
    assert(argc==2);
    const std::filesystem::path file=argv[1];
    std::vector<uint8_t> bytes(32+4*(16384+512*512),0);
    std::memcpy(bytes.data(),"GHHD001\0",8);
    const uint32_t h[]={128,128,512,512,16384,512*512};
    for(size_t n=0;n<6;++n)for(size_t b=0;b<4;++b)bytes[8+4*n+b]=static_cast<uint8_t>(h[n]>>(8*b));
    auto write=[&] {std::ofstream f(file,std::ios::binary|std::ios::trunc);f.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());};
    write();const std::string expected(64,'a');unsigned calls=0;
    // Compare explicitly: span equality is not part of C++20.
    auto checkedHash=[&](std::span<const uint8_t> input) {
        assert(input.size()==bytes.size() && std::memcmp(input.data(),bytes.data(),bytes.size())==0);++calls;return expected;
    };
    const auto good=godhand_hd::read_input(file,"retail-us-slus-21503",expected,checkedHash);
    assert(good && good.words[2]==512 && calls==1);
    unsigned rejected=0;
    for(auto profile:{"", "prototype"}) {
        try{godhand_hd::read_input(file,profile,expected,checkedHash);assert(false);}catch(const std::invalid_argument&){++rejected;}
    }
    for(auto digest:{std::string{},std::string(64,'A'),std::string(64,'b')}) {
        try{godhand_hd::read_input(file,"retail-us-slus-21503",digest,checkedHash);assert(false);}catch(const std::invalid_argument&){++rejected;}
    }
    bytes[16]=129;write();
    try{godhand_hd::read_input(file,"retail-us-slus-21503",expected,checkedHash);assert(false);}catch(const std::invalid_argument&){++rejected;}
    assert(rejected==6);
    std::cout<<"invented file identity digest shape refusal: PASS\n";
}
