// SPDX-License-Identifier: GPL-3.0-only
// Original additive GPU-resident result path inside GSGpuBackend::Impl.
    bool hdInitialize(const std::string& prefix) {
        hdInput=godhand_hd::load();
        if(!hdInput) return false;
        int64_t bindings=0,computeBlocks=0;
        gl().GetInteger64v(0x90DDu,&bindings);
        gl().GetInteger64v(0x90DBu,&computeBlocks);
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
        std::fprintf(stderr,"[pc-hd-gpu] match results remain on GPU; batches reclassified; CPU match readback disabled\n");
        return true;
    }
    std::string hdRasterText() const {
        return hdInput ? godhand_hd::raster_source(GSGpuShaders::kRaster) : std::string(GSGpuShaders::kRaster);
    }
    void hdPrepare() {
        if(!hdInput) return;
        const Api& g=gl();
        // Reset every batch, including ineligible and reused state identities.
        std::vector<uint32_t> zeros(stateCount,0u);
        g.BindBuffer(kShaderStorageBuffer,hdMatchBuffer);
        g.BufferData(kShaderStorageBuffer,zeros.size()*4u,zeros.data(),kDynamicDraw);
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
        barrier(); // GPU writes must be visible to both raster consumer paths.
        ++hdChecks;
        if(hdChecks<=8u) std::fprintf(stderr,"[pc-hd-gpu] submitted classifier batch=%u states=%u; match_count=unread\n",hdChecks,stateCount);
    }
