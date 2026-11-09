// SPDX-License-Identifier: GPL-3.0-only
// Original private GPU extension methods inside GSGpuBackend::Impl.
    bool hdInitialize(const std::string& prefix) {
        hdInput=godhand_hd::load();
        if(!hdInput) return false;
        int64_t bindings=0,computeBlocks=0;
        gl().GetInteger64v(0x90DDu,&bindings); // MAX_SHADER_STORAGE_BUFFER_BINDINGS
        gl().GetInteger64v(0x90DBu,&computeBlocks); // MAX_COMPUTE_SHADER_STORAGE_BLOCKS
        if(bindings<15 || computeBlocks<(scale>1u?12:10)) {
            std::fprintf(stderr,"[pc-hd] disabled: insufficient SSBO capabilities\n");hdInput.words.clear();return false;
        }
        const std::string body=godhand_hd::classifier_source(GSGpuShaders::kRaster);
        if(!compile(hdClassifier,prefix,body.c_str(),{"uRaster"})) {
            std::fprintf(stderr,"[pc-hd] disabled: classifier compile failure\n");hdInput.words.clear();return false;
        }
        hdInputBuffer=makeBuffer(hdInput.words.size()*4u,hdInput.words.data(),13u);
        hdMatchBuffer=makeBuffer(4u,nullptr,14u);
        std::fprintf(stderr,"[pc-hd] uploaded %ux%u authored RGBA, %u bytes, scale=%u\n",hdInput.words[2],hdInput.words[3],hdInput.words[2]*hdInput.words[3]*4u,scale);
        return true;
    }
    std::string hdRasterText() const {
        return hdInput ? godhand_hd::raster_source(GSGpuShaders::kRaster) : std::string(GSGpuShaders::kRaster);
    }
    void hdPrepare() {
        if(!hdInput) return;
        const Api& g=gl();
        std::vector<uint32_t> matched(stateCount,0u);
        g.BindBuffer(kShaderStorageBuffer,hdMatchBuffer);
        g.BufferData(kShaderStorageBuffer,matched.size()*4u,matched.data(),kDynamicDraw);
        g.BindBufferBase(kShaderStorageBuffer,14u,hdMatchBuffer);
        g.BindBufferBase(kShaderStorageBuffer,13u,hdInputBuffer);
        bool candidate=false;
        for(uint32_t i=0;i<stateCount;++i) {
            const auto* s=states.data()+i*kStateWords;
            candidate|=(s[SFlags]&FTme) && s[STexSize]==(128u|(128u<<16u)) && s[STpsm]==0x14u &&
                ((s[STexMode]>>16u)&255u)==0u && (s[SClampLo]&15u)==0u;
        }
        if(!candidate) return;
        g.UseProgram(hdClassifier.id);
        g.Uniform4ui(hdClassifier.loc[0],epoch,stateCount,0u,0u);
        g.DispatchCompute(stateCount,1u,1u);
        barrier();
        g.BindBuffer(kShaderStorageBuffer,hdMatchBuffer);
        g.GetBufferSubData(kShaderStorageBuffer,0,matched.size()*4u,matched.data());
        ++hdChecks;
        for(uint32_t bit:matched) if(bit) {
            ++hdMatches;
            if(hdMatches<=8u) std::fprintf(stderr,"[pc-hd] exact full-source match %u (all16384 texels), replacement=%ux%u\n",hdMatches,hdInput.words[2],hdInput.words[3]);
        }
    }
