// Original GPL-3.0-only activity admission barrier; no game code or audio data.
#pragma once
#include <cstddef>
#include <mutex>
#include <utility>

namespace godhand_pc_pause {
// Admission and freeze acquisition share one tiny critical section. A freeze
// token is available only after all admitted consumers leave. It then rejects
// new consumers until released. No mutex is held for a token's whole lifetime.
// This is NOT a producer drain, audio device stop or machine-quiescence oracle.
class ActivityBarrier {
public:
    class Token {
    public:
        Token() = default;
        Token(const Token &) = delete;
        Token &operator=(const Token &) = delete;
        Token(Token &&other) noexcept
            : owner_(std::exchange(other.owner_, nullptr)), freeze_(other.freeze_) {}
        Token &operator=(Token &&other) noexcept {
            if (this != &other) {
                reset(); owner_ = std::exchange(other.owner_, nullptr); freeze_ = other.freeze_;
            }
            return *this;
        }
        ~Token() { reset(); }
        explicit operator bool() const noexcept { return owner_ != nullptr; }
        void reset() noexcept {
            if (auto *owner = std::exchange(owner_, nullptr)) owner->release(freeze_);
        }
    private:
        friend class ActivityBarrier;
        Token(ActivityBarrier *owner, bool freeze) : owner_(owner), freeze_(freeze) {}
        ActivityBarrier *owner_ = nullptr;
        bool freeze_ = false;
    };

    Token try_enter() {
        std::lock_guard lock(mutex_);
        if (frozen_) return {};
        ++active_;
        return Token(this, false);
    }
    Token try_freeze() {
        std::lock_guard lock(mutex_);
        if (frozen_ || active_ != 0) return {};
        frozen_ = true;
        return Token(this, true);
    }

private:
    void release(bool freeze) noexcept {
        std::lock_guard lock(mutex_);
        if (freeze) frozen_ = false;
        else --active_;
    }
    std::mutex mutex_;
    std::size_t active_ = 0;
    bool frozen_ = false;
};
inline ActivityBarrier &audio_activity() { static ActivityBarrier instance; return instance; }
} // namespace godhand_pc_pause
