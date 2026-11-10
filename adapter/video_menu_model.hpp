// Original GPL-3.0-only menu state, not a native UI or pause/readiness oracle.
#pragma once
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

namespace godhand_pc_video {
using Scale = std::optional<uint32_t>; // null: upstream INI, not hardcoded1x/3x

inline bool validScale(Scale value) noexcept { return !value || (*value >= 1 && *value <= 8); }
inline bool validRevision(const std::string &value) noexcept {
    if (value.size() != 64) return false;
    for (char c : value)
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
    return true;
}

struct Snapshot { Scale scale; std::string revision; };
struct Request { uint32_t id; Scale scale; std::string expectedRevision; };
enum class Phase { Closed, AwaitHold, Editing, AwaitReply };
enum class Reply { Saved, Stale, Rejected, Unknown };
enum class Notice { None, SavedForRestart, ReloadRequired, NotSaved, OutcomeUnknown, LimitReached };

class Model {
public:
    static constexpr uint32_t MaxRequests = 64;
    Model(Scale runRequest, Snapshot saved) : runRequest_(runRequest), saved_(std::move(saved)), draft_(saved_.scale) {
        if (!validScale(runRequest_)) throw std::invalid_argument("Invalid run request");
        validate(saved_);
    }
    bool open(bool drawable, bool exclusiveOwnerAvailable) noexcept {
        if (open_ || !drawable || !exclusiveOwnerAvailable) return false;
        open_ = true; held_ = false;
        if (!pending_) draft_ = saved_.scale;
        return true;
    }
    void close() noexcept {
        open_ = false; held_ = false;
        if (!pending_) draft_ = saved_.scale; // unsent edits are discarded, never implicitly saved
    }
    void observeHold(bool acknowledged) noexcept { held_ = acknowledged; }
    Phase phase() const noexcept {
        if (!open_) return Phase::Closed;
        if (!held_) return Phase::AwaitHold;
        return pending_ ? Phase::AwaitReply : Phase::Editing;
    }
    bool edit(Scale scale) noexcept {
        if (phase() != Phase::Editing || !validScale(scale)) return false;
        draft_ = scale;
        return true;
    }
    std::optional<Request> save() {
        if (phase() != Phase::Editing || reloadRequired_ || draft_ == saved_.scale) return std::nullopt;
        if (sequence_ == MaxRequests) { notice_ = Notice::LimitReached; return std::nullopt; }
        pending_ = Request{++sequence_, draft_, saved_.revision};
        notice_ = Notice::None;
        return pending_;
    }
    bool reply(uint32_t id, Reply result, Snapshot committed = {std::nullopt, {}}) {
        if (!pending_ || pending_->id != id) return false; // duplicates/out-of-order replies do not mutate state
        if (result == Reply::Saved) {
            validate(committed);
            if (committed.revision == pending_->expectedRevision || committed.scale != pending_->scale)
                throw std::invalid_argument("Invalid committed revision");
            saved_ = std::move(committed);
            draft_ = saved_.scale;
            notice_ = Notice::SavedForRestart;
        } else if (result == Reply::Stale) {
            reloadRequired_ = true; notice_ = Notice::ReloadRequired;
        } else if (result == Reply::Rejected) {
            notice_ = Notice::NotSaved; // caller must KNOW no commit occurred
        } else if (result == Reply::Unknown) {
            reloadRequired_ = true; notice_ = Notice::OutcomeUnknown;
        } else {
            throw std::invalid_argument("Unknown reply kind");
        }
        pending_.reset();
        return true;
    }
    bool refresh(Snapshot current) {
        validate(current);
        if (pending_) return false; // do not lose an in-flight save/unknown acknowledgement
        saved_ = std::move(current); draft_ = saved_.scale;
        reloadRequired_ = false; notice_ = Notice::None;
        return true;
    }
    Scale runRequest() const noexcept { return runRequest_; } // immutable; NOT observed effective GL scale
    const Snapshot &saved() const noexcept { return saved_; }
    Scale draft() const noexcept { return draft_; }
    const std::optional<Request> &pending() const noexcept { return pending_; }
    Notice notice() const noexcept { return notice_; }
    bool reloadRequired() const noexcept { return reloadRequired_; }

private:
    static void validate(const Snapshot &value) {
        if (!validScale(value.scale) || !validRevision(value.revision))
            throw std::invalid_argument("Invalid saved video snapshot");
    }
    const Scale runRequest_;
    Snapshot saved_;
    Scale draft_;
    std::optional<Request> pending_;
    bool open_ = false, held_ = false, reloadRequired_ = false;
    uint32_t sequence_ = 0;
    Notice notice_ = Notice::None;
};
} // namespace godhand_pc_video
