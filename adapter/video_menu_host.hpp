// Original GPL-3.0-only binding to pinned host controls and our checked pause Gate.
// Source preparation only: no factory/launcher/IPC/installer enables this yet.
#pragma once
#include "video_menu_view.hpp"
#include "runtime/ps2_controls_screen.h"
#include "godhand_pc_controls/host_pause.hpp"

namespace godhand_pc_video {
class Host {
public:
    Host(Scale runRequest, Snapshot saved, Hooks hooks)
        : view_(runRequest, std::move(saved), std::move(hooks)) {}

    // Replaces the existing controls tick + pause request at the same pre-sample
    // point. Do NOT retain another F1-only gate.request afterward: it would
    // silently release a hold still needed by this view.
    void tick(bool nativeDrawable) {
        const bool enabled = godhand_pc_pause::enabled();
        view_.pollToggle(nativeDrawable && enabled, ps2x::controls::isOpen());
        // Tick even when unavailable for opening. Skipping F1 here would leave
        // its raw Back+Start/focus history stale across a video-menu hold.
        ps2x::controls::hostTick(nativeDrawable && !view_.isOpen());
        requestHold();
        view_.poll(enabled && godhand_pc_pause::gate().requested() && godhand_pc_pause::gate().parked());
        requestHold(); // Escape may have closed the last owner in poll()
    }
    bool overlaysOpen() const noexcept { return ps2x::controls::isOpen() || view_.isOpen(); }
    const View &view() const noexcept { return view_; }
    void command(Command command, bool nativeDrawable) {
        view_.command(command, nativeDrawable && godhand_pc_pause::enabled(), ps2x::controls::isOpen());
        requestHold();
    }
    void draw() const {
        ps2x::controls::draw();
        view_.draw(); // original source placement must be before native screen export
    }
    void shutdown() {
        ps2x::controls::shutdown();
        view_.shutdown();
        requestHold(); // release both owners before the existing stop/join path
    }

private:
    View view_;
    void requestHold() const {
        if (godhand_pc_pause::enabled()) godhand_pc_pause::gate().request(overlaysOpen());
    }
};
} // namespace godhand_pc_video
