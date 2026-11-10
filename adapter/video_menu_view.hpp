// Original GPL-3.0-only native host view. Not installed/linked by including the model.
#pragma once
#include "video_menu_protocol.hpp"
#include "ps2_host_backend.h"
#include "ps2_host_input.h"
#include <algorithm>

namespace godhand_pc_video {
enum class Command { Toggle, Close, Up, Down, Left, Right, UseIni, Accept };
class View {
public:
    View(Scale runRequest, Snapshot saved, Hooks hooks)
        : model_(runRequest, std::move(saved)), hooks_(std::move(hooks)) {}
    bool isOpen() const noexcept { return model_.phase() != Phase::Closed; }
    const Model &model() const noexcept { return model_; }

    // Before F1's hostTick. The caller must still tick F1 with drawable=false
    // while this view owns input, so its raw chord/focus edges stay current.
    // Both screens share one overlay boolean, not independent input owners.
    void pollToggle(bool drawable, bool controlsOpen) {
        if (!IsWindowFocused() || !IsKeyPressed(KEY_F2)) return;
        command(Command::Toggle, drawable, controlsOpen);
    }
    // Shared actions for real keys and the explicitly guarded native diagnostic.
    // This does not synthesize hardware input or bypass the hold/edit state.
    void command(Command value, bool drawable = false, bool controlsOpen = true) {
        if (value == Command::Close) { close(); return; }
        if (value != Command::Toggle) {
            if (!sizeFits() || refreshPending_ || model_.phase() != Phase::Editing) return;
            switch (value) {
            case Command::Up: row_ = (row_ + Rows - 1) % Rows; break;
            case Command::Down: row_ = (row_ + 1) % Rows; break;
            case Command::Left: if (row_ == 0) step(-1); break;
            case Command::Right: if (row_ == 0) step(1); break;
            case Command::UseIni: model_.edit(std::nullopt); break;
            case Command::Accept:
                if (row_ == 0) step(1);
                else if (row_ == 1) save();
                else if (row_ == 2) refresh();
                else close();
                break;
            default: break;
            }
            return;
        }
        if (isOpen()) { close(); return; }
        if (!hooks_.submit || !hooks_.receive || !hooks_.refresh || !hooks_.receiveRefresh) return;
        if (!sizeFits()) return; // no input block behind an unreadable/invisible screen
        if (model_.open(drawable, !controlsOpen)) {
            ps2_host_input::setOverlayOpen(true);
            row_ = 0;
            status_.clear();
        }
    }

    // Caller must FIRST request(F1_open || isOpen()) on the checked audio-v2
    // Gate, THEN sample parked() && requested(). A visible screen/request alone
    // is not acknowledgement. Recompute the union after Escape/F2 closes it.
    void poll(bool acknowledgedHold) {
        model_.observeHold(isOpen() && acknowledgedHold);
        receive(); // an already-confirmed save may finish while the view is closed
        receiveRefresh();
        if (!isOpen()) return;
        if (!IsWindowFocused()) return; // no synthetic focus claim or background key capture
        if (IsKeyPressed(KEY_ESCAPE)) { command(Command::Close); return; }
        if (!sizeFits()) return;
        if (refreshPending_) return; // don't edit a draft that an in-flight read will replace
        if (model_.phase() != Phase::Editing) return;
        if (IsKeyPressed(KEY_UP)) command(Command::Up);
        if (IsKeyPressed(KEY_DOWN)) command(Command::Down);
        if (IsKeyPressed(KEY_LEFT)) command(Command::Left);
        if (IsKeyPressed(KEY_RIGHT)) command(Command::Right);
        if (IsKeyPressed(KEY_R)) command(Command::UseIni);
        if (IsKeyPressed(KEY_ENTER) || IsKeyPressed(KEY_KP_ENTER)) command(Command::Accept);
    }

    void close() {
        if (!isOpen()) return; // never release another screen's input owner
        model_.close();
        ps2_host_input::setOverlayOpen(false); // retains upstream per-player release quarantine
    }
    void shutdown() { close(); } // do not pretend an in-flight save was cancelled

    // Inside host BeginDrawing AFTER game/F1 and BEFORE the renderer export.
    // Draws only original text/primitives, no game textures/fonts or simulated scene.
    void draw() const {
        if (!isOpen()) return;
        const int width = GetScreenWidth(), height = GetScreenHeight();
        if (!sizeFits()) {
            DrawRectangle(0, 0, width, height, Color{22, 25, 31, 245});
            DrawText("PC settings: window too small", 8, 8, 12, Color{235, 237, 240, 255});
            DrawText("Resize, or F2/Esc to close", 8, 28, 12, Color{235, 237, 240, 255});
            return;
        }
        const int x = 16, y = 16, panelWidth = width - 32, panelHeight = height - 32;
        const int font = std::clamp(height / 30, 12, 20);
        const int line = font + 8;
        const Color accent{232, 205, 128, 255}, text{235, 237, 240, 255}, dim{170, 177, 190, 255};
        DrawRectangle(0, 0, width, height, Color{0, 0, 0, 150});
        DrawRectangle(x, y, panelWidth, panelHeight, Color{22, 25, 31, 245});
        DrawRectangleLines(x, y, panelWidth, panelHeight, accent);
        int top = y + 12;
        auto label = [&](const std::string &value, Color color) {
            // Do not expose preference paths, truncate into another panel or
            // silently clip the setting label to fit a narrow window.
            const int available = panelWidth - 24;
            int size = font;
            while (size > 10 && MeasureText(value.c_str(), size) > available) --size;
            DrawText(value.c_str(), x + 12, top, size, color); top += line;
        };
        label("PC video settings - restart required", accent);
        label("This run requested: " + scaleText(model_.runRequest()), dim);
        label("Effective GL scale: not observed by this menu", dim);
        label("Saved for next run: " + scaleText(model_.saved().scale), dim);
        top += 6;
        const std::string rows[Rows] = {
            "Internal scale: " + scaleText(model_.draft()) + (model_.draft() != model_.saved().scale ? " *" : ""),
            "Save for next launch", "Reload saved preference (discard draft)", "Close (discard unsent draft)"};
        for (int n = 0; n < Rows; ++n) {
            if (row_ == n) DrawRectangle(x + 6, top - 3, panelWidth - 12, line, Color{255, 255, 255, 18});
            label((row_ == n ? "> " : "  ") + rows[n], row_ == n ? accent : text);
        }
        top += 6;
        label(message(), accent);
        label("Arrows: select/change   Enter: action   R: use INI", dim);
        label("F2/Esc: close   F1 controls are separate", dim);
        label("No live scale, FPS or simulation change is applied.", dim);
    }

private:
    static constexpr int Rows = 4;
    Model model_;
    Hooks hooks_;
    int row_ = 0;
    std::string status_;
    bool refreshPending_ = false;

    static bool sizeFits() noexcept { return GetScreenWidth() >= 480 && GetScreenHeight() >= 360; }
    static std::string scaleText(Scale value) { return value ? std::to_string(*value) + "x" : "runtime INI"; }
    void step(int direction) {
        int current = static_cast<int>(model_.draft().value_or(0));
        current = (current + direction + 9) % 9;
        model_.edit(current == 0 ? Scale{} : Scale{static_cast<uint32_t>(current)});
    }
    void save() {
        const auto request = model_.save();
        if (!request) return;
        status_.clear();
        try {
            const auto result = hooks_.submit(*request);
            if (result == Submission::Rejected) model_.reply(request->id, Reply::Rejected);
            else if (result == Submission::Unknown) model_.reply(request->id, Reply::Unknown);
            else if (result != Submission::Queued) model_.reply(request->id, Reply::Unknown);
        } catch (...) {
            model_.reply(request->id, Reply::Unknown); // may have committed; don't label it NotSaved
        }
    }
    void receive() {
        if (!model_.pending()) return;
        const auto id = model_.pending()->id;
        try {
            const auto response = hooks_.receive(id);
            if (response) {
                if (model_.reply(response->id, response->result, response->committed)) status_.clear();
                else status_ = "Ignoring an unrelated storage reply";
            }
        } catch (...) {
            model_.reply(id, Reply::Unknown);
        }
    }
    void refresh() {
        if (refreshPending_ || model_.pending()) return;
        try {
            const auto submission = hooks_.refresh();
            if (submission == Submission::Queued) { refreshPending_ = true; status_.clear(); }
            else status_ = "Cannot reload; displayed preference may be stale";
        } catch (...) { status_ = "Reload failed; displayed preference may be stale"; }
    }
    void receiveRefresh() {
        if (!refreshPending_) return;
        try {
            const auto reply = hooks_.receiveRefresh();
            if (!reply) return;
            refreshPending_ = false;
            if (reply->result == ReadStatus::Ready && model_.refresh(reply->snapshot)) status_.clear();
            else status_ = "Reload unavailable; displayed preference may be stale";
        } catch (...) { refreshPending_ = false; status_ = "Reload outcome unknown; displayed preference may be stale"; }
    }
    std::string message() const {
        if (model_.phase() == Phase::AwaitHold) return "Waiting for acknowledged game hold; editing disabled";
        if (refreshPending_) return "Waiting for a verified saved-preference snapshot";
        if (model_.phase() == Phase::AwaitReply) return "Waiting for storage acknowledgement; not yet saved";
        if (!status_.empty()) return status_;
        switch (model_.notice()) {
        case Notice::SavedForRestart: return "Saved for the next launch; current run unchanged";
        case Notice::ReloadRequired: return "Preferences changed externally; reload before saving";
        case Notice::NotSaved: return "Request refused before commit; preference not saved";
        case Notice::OutcomeUnknown: return "Save outcome unknown; reload before retrying";
        case Notice::LimitReached: return "Request limit reached; close and restart the launcher";
        default: return "Only saved startup settings change; restart to apply";
        }
    }
};
} // namespace godhand_pc_video
