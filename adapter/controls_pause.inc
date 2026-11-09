// Original GPL-3.0-only executor safe-point adapter. Included inside its loop.
// Caller readiness is deliberately conservative, not a full-machine proof.
// Gate callbacks run under its mutex: do not call gate.now/request from here.
if (godhand_pc_pause::enabled()) {
    const bool diagnostic = godhand_pc_probe::active();
    auto eeHash = [&]() noexcept {
        uint64_t hash = 14695981039346656037ull;
        for (size_t n = 0; n < PS2_RAM_SIZE; ++n) {
            hash ^= m_rdram[n]; hash *= 1099511628211ull;
        }
        return hash;
    };
    auto iopHash = [&]() noexcept {
        uint64_t hash = 14695981039346656037ull;
        if (!m_runtime.m_iopSubsystem) return uint64_t{0};
        uint8_t bytes[4096];
        for (uint32_t address = 0; address < 2u*1024u*1024u; address += sizeof(bytes)) {
            if (!m_runtime.m_iopSubsystem->readMemory(address, bytes, sizeof(bytes))) return uint64_t{0};
            for (auto v : bytes) { hash ^= v; hash *= 1099511628211ull; }
        }
        return hash;
    };
    uint64_t beforeEe = 0, beforeIop = 0;
    const bool held = godhand_pc_pause::gate().service([&]() {
        if (m_runtime.m_iopSubsystem) m_runtime.m_iopSubsystem->flushPendingWork();
        if (!m_pendingInvocations.empty()) return false;
        for (const auto &[id, thread] : m_threads)
            if (!thread.invocations.empty() || thread.resumeCompletion || thread.wait.completion) return false;
        if (m_runtime.m_iopSubsystem && m_runtime.m_iopSubsystem->hasPendingRpc()) return false;
        if (ps2xGsStallActive() || ps2xGsSignalQueuePending()) return false;
        if (ps2x::asyncvif::waitPipelineIdle(m_runtime.memory(), std::chrono::microseconds(2000))) return false;
        if (m_runtime.memory().m_gifArbiter && !m_runtime.memory().m_gifArbiter->empty()) return false;
        return true;
    }, [&]() { return m_stopRequested.load(std::memory_order_acquire); }, [&]() noexcept {
        if (diagnostic) { beforeEe = eeHash(); beforeIop = iopHash(); }
        std::fprintf(stderr, "[pc-pause] parked field=%llu cycle=%llu probe=%d ee=%016llx iop=%016llx\n",
            (unsigned long long)m_vsyncTick, (unsigned long long)m_eeCycle, diagnostic,
            (unsigned long long)beforeEe, (unsigned long long)beforeIop);
    }, [&](auto elapsed) noexcept {
        const bool eeEqual = diagnostic && beforeEe == eeHash();
        const bool iopEqual = diagnostic && beforeIop != 0 && beforeIop == iopHash();
        std::fprintf(stderr, "[pc-pause] resumed field=%llu cycle=%llu held_ms=%lld probe=%d ee_equal=%d iop_equal=%d\n",
            (unsigned long long)m_vsyncTick, (unsigned long long)m_eeCycle,
            (long long)std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count(),
            diagnostic, eeEqual, iopEqual);
        std::lock_guard lock(m_eventMutex);
        for (auto &deadline : m_deadlines) deadline.hostDeadline += elapsed;
        if (m_pacingRefTime != std::chrono::steady_clock::time_point{}) m_pacingRefTime += elapsed;
        if (g_deadlinesDeferredUntil != std::chrono::steady_clock::time_point{}) g_deadlinesDeferredUntil += elapsed;
        updateNextDeadline();
    });
    if (held) continue;
}
