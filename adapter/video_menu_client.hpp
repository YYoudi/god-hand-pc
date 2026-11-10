// Original GPL-3.0-only concrete local transport; no Raylib or guest dependency.
#pragma once
#include "video_menu_protocol.hpp"
#include "video_menu_io.hpp"
#include <chrono>

namespace godhand_pc_video {
class Client {
public:
    using Clock = std::chrono::steady_clock;
    explicit Client(std::filesystem::path directory, std::chrono::milliseconds timeout = std::chrono::seconds(5))
        : directory_(std::move(directory)), timeout_(timeout) {
        if (directory_.filename() != "video-menu" || !wire::nonce(directory_.parent_path().filename().string()) ||
            timeout_.count() < 1 || timeout_ > std::chrono::minutes(1))
            throw std::invalid_argument("Invalid menu client directory/timeout");
        const auto raw = message_io::readReady(directory_, "config");
        if (!raw) throw std::runtime_error("Menu config is not ready");
        config_ = wire::config(*raw);
        message_io::publish(directory_, "client", config_.session + "\n"); // exclusive: no channel reattachment
    }
    const wire::Config &config() const noexcept { return config_; }
    Submission submit(const Request &request) {
        if (fatal_ || blockedWrites_) return Submission::Unknown;
        if (pending_) return Submission::Rejected;
        if (request.id <= lastSetId_) { blockedWrites_ = true; return Submission::Unknown; }
        try { wire::requestFields(config_, {next_, false, request}); }
        catch (...) { return Submission::Rejected; }
        lastSetId_ = request.id;
        return begin(false, request);
    }
    Submission refresh() {
        if (fatal_) return Submission::Unknown;
        if (pending_) return Submission::Rejected;
        return begin(true, Request{0, std::nullopt, {}});
    }
    std::optional<Response> receive(uint32_t id) {
        if (!pending_ || pending_->operation.read || pending_->operation.request.id != id) return {};
        const auto done = take(false);
        if (!done) return {};
        const auto &status = done->status;
        return Response{id, status == "ok" ? Reply::Saved : status == "stale" ? Reply::Stale :
                            status == "rejected" ? Reply::Rejected : Reply::Unknown, done->snapshot};
    }
    std::optional<ReadResponse> receiveRefresh() {
        const auto done = take(true);
        if (!done) return {};
        return ReadResponse{done->status == "ok" ? ReadStatus::Ready :
                            done->status == "rejected" ? ReadStatus::Unavailable : ReadStatus::Unknown, done->snapshot};
    }

private:
    struct Pending { wire::Operation operation; Clock::time_point sent; };
    std::filesystem::path directory_;
    wire::Config config_;
    std::chrono::milliseconds timeout_;
    std::optional<Pending> pending_;
    uint32_t next_ = 1, lastSetId_ = 0;
    bool blockedWrites_ = false, fatal_ = false;

    Submission begin(bool read, Request request) {
        if (next_ > wire::MaxSequence) return Submission::Rejected;
        const wire::Operation operation{next_++, read, std::move(request)};
        try {
            const auto raw = wire::join(wire::requestFields(config_, operation));
            message_io::publish(directory_, "request-" + std::to_string(operation.sequence), raw);
            pending_ = Pending{operation, Clock::now()};
            return Submission::Queued;
        } catch (...) {
            fatal_ = true; blockedWrites_ = true; // publication may have crossed its ready point
            return Submission::Unknown;
        }
    }
    std::optional<wire::Decoded> take(bool read) {
        if (!pending_ || pending_->operation.read != read) return {};
        try {
            const auto raw = message_io::readReady(directory_, "reply-" + std::to_string(pending_->operation.sequence));
            if (raw) {
                auto value = wire::reply(config_, pending_->operation, *raw);
                pending_.reset();
                if (value.status == "ok") {
                    config_.saved = value.snapshot;
                    if (read) blockedWrites_ = false;
                } else if (value.status != "rejected") blockedWrites_ = true;
                return value;
            }
        } catch (...) {
            fatal_ = true; blockedWrites_ = true;
            pending_.reset();
            return wire::Decoded{"unknown", {std::nullopt, {}}};
        }
        if (Clock::now() - pending_->sent < timeout_) return {};
        pending_.reset(); blockedWrites_ = true;
        // Late reply is never reused as the next operation. A new read has a
        // distinct sequence, ordered behind this request by the broker.
        return wire::Decoded{"unknown", {std::nullopt, {}}};
    }
};
} // namespace godhand_pc_video
