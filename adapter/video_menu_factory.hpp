// Original GPL-3.0-only opt-in native factory. No existing build/launcher calls it yet.
#pragma once
#include "video_menu_host.hpp"
#include "video_menu_client.hpp"
#include "video_menu_probe.hpp"
#include <cstdlib>
#include <cstring>
#include <memory>

namespace godhand_pc_video {
class Session {
public:
    Session(wire::Config config, Hooks hooks, const std::filesystem::path &directory)
        : host_(config.runRequest, config.saved, std::move(hooks)), probe_(config.scratch, directory) {}
    void tick(bool drawable, uint64_t field) { host_.tick(drawable); probe_.tick(host_, drawable, field); }
    bool overlaysOpen() const noexcept { return host_.overlaysOpen(); }
    void draw() { host_.draw(); probe_.capture(); }
    void shutdown() { probe_.shutdown(); host_.shutdown(); }
private:
    Host host_;
    Probe probe_;
};
inline std::unique_ptr<Session> fromEnvironment(bool nativeRenderer) {
    const char *enabled = std::getenv("GODHAND_PC_VIDEO_MENU");
    if (!enabled || std::strcmp(enabled, "0") == 0) return {}; // no channel filesystem reads
    if (std::strcmp(enabled, "1") != 0 || !nativeRenderer || !godhand_pc_pause::enabled())
        throw std::invalid_argument("Native video menu requires explicit native/audio-v2 capability");
#if defined(_WIN32)
    const wchar_t *path = _wgetenv(L"GODHAND_PC_VIDEO_MENU_DIR");
#else
    const char *path = std::getenv("GODHAND_PC_VIDEO_MENU_DIR");
#endif
    if (!path || !*path) throw std::invalid_argument("Missing owned video-menu channel directory");
    auto client = std::make_shared<Client>(std::filesystem::path(path));
    const auto config = client->config();
    Hooks hooks{
        [client](const Request &request) { return client->submit(request); },
        [client](uint32_t id) { return client->receive(id); },
        [client]() { return client->refresh(); },
        [client]() { return client->receiveRefresh(); }};
    return std::make_unique<Session>(config, std::move(hooks), std::filesystem::path(path));
}
} // namespace godhand_pc_video
