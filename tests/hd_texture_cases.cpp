// SPDX-License-Identifier: GPL-3.0-only
// Invented in-memory data only, no game inputs, native dependencies or GPU.
#include "hd_texture.hpp"
#include <cassert>
#include <iostream>

static void word(std::vector<uint8_t>& data,size_t at,uint32_t value) {
    for(size_t i=0;i<4;++i)data[at+i]=static_cast<uint8_t>(value>>(i*8));
}
int main() {
    std::vector<uint8_t> bytes(32+4*(16384+512*512),0);
    std::memcpy(bytes.data(),"GHHD001\0",8);
    const uint32_t h[]={128,128,512,512,16384,512*512};
    for(size_t i=0;i<6;++i)word(bytes,8+4*i,h[i]);
    word(bytes,32,0x80030201u);word(bytes,bytes.size()-4,0xff112233u);
    const auto decoded=godhand_hd::parse(bytes);
    assert(decoded && decoded.words.size()==4+16384+512*512);
    assert(decoded.words[2]==512 && decoded.words[3]==512 && decoded.words[4]==0x80030201u);
    assert(decoded.words.back()==0xff112233u); // Preserve raw128 and255 alpha, no conversion.
    unsigned rejects=0;
    const auto refuses=[&](const auto& blob){try{godhand_hd::parse(blob);assert(false);}catch(const std::invalid_argument&){++rejects;}};
    for(size_t at:{0u,8u,12u,16u,20u,24u,28u}) {auto copy=bytes;copy[at]^=1u;refuses(copy);}
    auto shortData=bytes;shortData.pop_back();refuses(shortData);
    auto trailing=bytes;trailing.push_back(0);refuses(trailing);
    for(uint32_t size:{0u,128u,129u,4096u,0xffffffffu}) {auto copy=bytes;word(copy,16,size);refuses(copy);}
    refuses(std::span<const uint8_t>{});
    std::string invented="float fabsQ(float q) { return q; }\n#if HIRES\n    if ((flags & F_LINEAR) == 0u) {}\nvoid main() {}\n";
    const auto raster=godhand_hd::raster_source(invented);
    assert(raster.find("hdMatch[s]!=0u")!=std::string::npos);
    assert(raster.find("hdInput[4u+hdInput[0]*hdInput[1]+v*w+u]")!=std::string::npos);
    const auto classify=godhand_hd::classifier_source(invented);
    assert(classify.find("p<16384u")!=std::string::npos && classify.find("atomicOr(hdMismatch,1u)")!=std::string::npos);
    for(auto bad:{std::string{},invented+invented}) {
        try{godhand_hd::raster_source(bad);assert(false);}catch(const std::invalid_argument&){}
        try{godhand_hd::classifier_source(bad);assert(false);}catch(const std::invalid_argument&){}
    }
    assert(rejects==15);
    std::cout<<"invented envelope raw-alpha bounds preimages: PASS\n";
}
