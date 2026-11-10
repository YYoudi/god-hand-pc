// Original GPL-3.0-only diagnostic of the real view; ordinary launches set it off.
#pragma once
#include "video_menu_host.hpp"
#include "video_menu_io.hpp"
#include "rlgl.h"
#include <chrono>
#include <cstdio>
#include <filesystem>
#include <string_view>

namespace godhand_pc_video {
class Probe {
public:
    Probe(bool scratch, std::filesystem::path directory) : directory_(std::move(directory)) {
        const char *value = std::getenv("GODHAND_PC_VIDEO_MENU_SELFTEST");
        if (!value || std::string_view(value) == "0") return;
        mode_ = value;
        if (!scratch || (mode_ != "scale2" && mode_ != "stale" && mode_ != "stop-open"))
            throw std::invalid_argument("Native menu diagnostic requires scratch preferences and a known script");
        const char *field = std::getenv("GODHAND_PC_VIDEO_MENU_SELFTEST_FIELD");
        if (field && *field) {
            const std::string_view text(field);
            uint32_t number = 0;
            if (text.size() > 5) throw std::invalid_argument("Invalid menu diagnostic field");
            for (char c : text) {
                if (c < '0' || c > '9') throw std::invalid_argument("Invalid menu diagnostic field");
                number = number * 10 + static_cast<uint32_t>(c - '0');
            }
            if (number < 1 || number > 42000) throw std::invalid_argument("Invalid menu diagnostic field");
            target_ = number;
        }
    }
    void tick(Host &host, bool drawable, uint64_t field) noexcept {
        if (mode_.empty() || done_) return;
        if (failed_) { host.command(Command::Close, drawable); return; }
        try {
            const auto now = Clock::now();
            if (step_ > 0 && now > deadline_) throw std::runtime_error("Native menu diagnostic deadline expired");
            if (step_ == 0) {
                if (field < target_) return;
                if (!drawable) throw std::runtime_error("Native menu not drawable at target");
                host.command(Command::Toggle, drawable);
                if (!host.view().isOpen()) throw std::runtime_error("Native menu did not acquire ownership");
                ++step_; deadline_ = now + std::chrono::seconds(20);
            } else if (step_ == 1 && host.view().model().phase() == Phase::Editing) {
                field_ = field; capture_ = "held-before"; heldAt_ = now; ++step_;
                std::fprintf(stderr, "[pc-video-test] held field=%llu\n", (unsigned long long)field);
            } else if (step_ == 2 && now - heldAt_ >= std::chrono::milliseconds(1500)) {
                if (field != field_) throw std::runtime_error("Guest field advanced during acknowledged hold");
                capture_ = "held-again"; ++step_;
            } else if (step_ == 3 && capture_.empty()) {
                if (mode_ == "stop-open") { done_ = true; log("stop-open-ready"); return; }
                selectTwo(host, drawable); ++step_;
            } else if (step_ == 4) {
                const auto notice = host.view().model().notice();
                if (mode_ == "stale") {
                    if (notice != Notice::ReloadRequired) {
                        if (notice == Notice::SavedForRestart || notice == Notice::OutcomeUnknown)
                            throw std::runtime_error("Stale control did not receive the expected refusal");
                        return;
                    }
                    capture_ = "stale-refused"; ++step_;
                } else if (notice == Notice::SavedForRestart) saved(host, field);
                else if (notice == Notice::OutcomeUnknown || notice == Notice::NotSaved)
                    throw std::runtime_error("Menu save not acknowledged");
            } else if (step_ == 5 && capture_.empty()) {
                host.command(Command::Down, drawable); // save -> reload
                host.command(Command::Accept, drawable); ++step_;
            } else if (step_ == 6 && !host.view().model().reloadRequired() &&
                       host.view().model().saved().scale == Scale{7u}) {
                host.command(Command::Down, drawable); host.command(Command::Down, drawable); // reload -> close -> scale
                selectTwo(host, drawable); ++step_;
            } else if (step_ == 7 && host.view().model().notice() == Notice::SavedForRestart) saved(host, field);
            else if (step_ == 8 && capture_.empty()) {
                host.command(Command::Close, drawable); done_ = true; log("PASS save-ack-close");
            }
            if (!done_ && now > deadline_) throw std::runtime_error("Native menu diagnostic deadline expired");
        } catch (const std::exception &error) {
            failed_ = true; std::fprintf(stderr, "[pc-video-test] FAIL %s\n", error.what());
            host.command(Command::Close, drawable);
        }
    }
    // Called after the actual native frame + menu draw, before EndDrawing.
    void capture() noexcept {
        if (capture_.empty() || failed_) return;
        try {
            auto destination = directory_ / (capture_ + ".png");
            if (std::filesystem::exists(destination)) throw std::runtime_error("Capture already exists; preserve it");
            rlDrawRenderBatchActive();
            Image image = LoadImageFromScreen();
            const bool ok = ExportImage(image, destination.string().c_str());
            UnloadImage(image);
            if (!ok) throw std::runtime_error("Native framebuffer export failed");
            std::fprintf(stderr, "[pc-video-test] captured %s\n", capture_.c_str());
            capture_.clear();
        } catch (const std::exception &error) {
            failed_ = true; std::fprintf(stderr, "[pc-video-test] FAIL capture %s\n", error.what());
        }
    }
    void shutdown() const noexcept {
        if (!mode_.empty()) std::fprintf(stderr, "[pc-video-test] shutdown done=%d failed=%d\n", done_, failed_);
    }
private:
    using Clock = std::chrono::steady_clock;
    std::filesystem::path directory_;
    std::string mode_, capture_;
    uint64_t target_ = 4800, field_ = 0;
    int step_ = 0;
    bool failed_ = false, done_ = false;
    Clock::time_point heldAt_{}, deadline_{};
    static void log(const char *message) { std::fprintf(stderr, "[pc-video-test] %s\n", message); }
    void saved(Host &host, uint64_t field) {
        if (host.view().model().saved().scale != Scale{2u} || field != field_)
            throw std::runtime_error("Save selection/held field differs");
        capture_ = "saved-for-restart"; step_ = 8; log("verified saved-next=2 (current unchanged)");
    }
    static void selectTwo(Host &host, bool drawable) {
        host.command(Command::UseIni, drawable);
        host.command(Command::Right, drawable); host.command(Command::Right, drawable);
        host.command(Command::Down, drawable); host.command(Command::Accept, drawable);
    }
};
} // namespace godhand_pc_video
