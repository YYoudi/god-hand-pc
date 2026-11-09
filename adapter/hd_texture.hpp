// SPDX-License-Identifier: GPL-3.0-only
// Original experimental RGBA upload contract; no game bytes/addresses.
#pragma once
#include <cstdint>
#include <cstring>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>
namespace godhand_hd {
struct Input {
    std::vector<uint32_t> words;
    explicit operator bool() const { return !words.empty(); }
};
// Caller must verify the complete file digest/profile before parsing/uploading.
// ReferenceRGBA is private game-derived data at runtime, never a public fixture.
inline Input parse(std::span<const uint8_t> bytes) {
    if(bytes.size()<32 || bytes.size()>64u*1024u*1024u || std::memcmp(bytes.data(),"GHHD001\0",8)!=0)
        throw std::invalid_argument("unsupported upload envelope");
    auto u32=[&](size_t at) {return uint32_t(bytes[at]) | (uint32_t(bytes[at+1])<<8u) |
        (uint32_t(bytes[at+2])<<16u) | (uint32_t(bytes[at+3])<<24u);};
    uint32_t h[6];for(size_t i=0;i<6;++i)h[i]=u32(8+4*i);
    const auto power=[](uint32_t x){return x && !(x&(x-1));};
    if(h[0]!=128 || h[1]!=128 || h[2]<=128 || h[3]<=128 || h[2]>2048 || h[3]>2048 ||
       !power(h[2]) || !power(h[3]) || h[4]!=16384 || h[5]!=h[2]*h[3] ||
       bytes.size()!=32ull+4ull*(h[4]+h[5]))
        throw std::invalid_argument("unsupported upload shape/length");
    Input out;out.words.reserve(4ull+h[4]+h[5]);
    for(size_t i=0;i<4;++i)out.words.push_back(h[i]);
    for(size_t at=32;at<bytes.size();at+=4)out.words.push_back(u32(at));
    return out;
}
inline void replace_once(std::string& text,const std::string& from,const std::string& to) {
    const auto at=text.find(from);
    if(at==std::string::npos || text.find(from,at+from.size())!=std::string::npos)
        throw std::invalid_argument("HD shader preimage differs");
    text.replace(at,from.size(),to);
}
inline const char* declarations=R"GLSL(
layout(std430,binding=13) readonly buffer HdInputBuffer { uint hdInput[]; };
)GLSL";
inline const char* sampler=R"GLSL(
layout(std430,binding=14) readonly buffer HdMatchBuffer { uint hdMatch[]; };
uint hdPoint(int x,int y) {
    uint w=hdInput[2],h=hdInput[3];
    uint u=uint(x)&(w-1u),v=uint(y)&(h-1u);
    return hdInput[4u+hdInput[0]*hdInput[1]+v*w+u];
}
uint hdSample(float u,float v,bool linear) {
    precise float x=u*float(hdInput[2])/float(hdInput[0]);
    precise float y=v*float(hdInput[3])/float(hdInput[1]);
    if(!linear) return hdPoint(int(x),int(y));
    x-=0.5;y-=0.5;
    int ix=int(floor(x)),iy=int(floor(y));
    precise float fx=x-float(ix),fy=y-float(iy);
    uint a=hdPoint(ix,iy),b=hdPoint(ix+1,iy),c=hdPoint(ix,iy+1),d=hdPoint(ix+1,iy+1);
    uint result=0u;
    for(uint shift=0u;shift<32u;shift+=8u)
        result|=lerpChannel((a>>shift)&255u,(b>>shift)&255u,(c>>shift)&255u,(d>>shift)&255u,fx,fy)<<shift;
    return result;
}
)GLSL";
inline const char* classifier=R"GLSL(
layout(std430,binding=14) buffer HdMatchBuffer { uint hdMatch[]; };
shared uint hdMismatch;
void main() {
    uint s=gl_WorkGroupID.x,lane=gl_LocalInvocationIndex;
    if(s>=uRaster.y) return;
    bool candidate=(st(s,S_FLAGS)&F_TME)!=0u && st(s,S_TEXSIZE)==(128u|(128u<<16u)) &&
        st(s,S_TPSM)==0x14u && ((st(s,S_TEXMODE)>>16u)&255u)==0u && (st(s,S_CLAMP_LO)&15u)==0u;
    if(!candidate) {if(lane==0u) hdMatch[s]=0u;return;}
    if(lane==0u) hdMismatch=0u;
    barrier();
    for(uint p=lane;p<16384u;p+=256u) {
        if(samplePoint(s,int(p%128u),int(p/128u))!=hdInput[4u+p]) {atomicOr(hdMismatch,1u);break;}
    }
    barrier();
    if(lane==0u) hdMatch[s]=hdMismatch==0u?1u:0u;
}
)GLSL";

inline std::string raster_source(std::string body) {
    replace_once(body,"float fabsQ(float q)",std::string(declarations)+sampler+"\nfloat fabsQ(float q)");
    replace_once(body,"#if HIRES\n    if ((flags & F_LINEAR) == 0u)",
        "    if (hdMatch[s]!=0u) return hdSample(texUf,texVf,(flags & F_LINEAR)!=0u);\n#if HIRES\n    if ((flags & F_LINEAR) == 0u)");
    return body;
}
inline std::string classifier_source(std::string body) {
    const std::string main="void main()";
    const auto at=body.find(main);
    if(at==std::string::npos || body.find(main,at+main.size())!=std::string::npos)
        throw std::invalid_argument("HD classifier preimage differs");
    body.resize(at);body+=declarations;body+=classifier;return body;
}
}
