// Original invented host/hold traces, not real input, audio, scheduling or game rendering.
#include "video_menu_host.hpp"
#include <cassert>
#include <iostream>

using namespace godhand_pc_video;
namespace fake = invented_host;

int main() {
    const std::string a(64, 'a');
    Hooks hooks{
        [](const Request &) { return Submission::Rejected; },
        [](uint32_t) -> std::optional<Response> { return {}; },
        [a]() -> std::optional<Snapshot> { return Snapshot{2u, a}; }};
    Host host(3u, {2u, a}, hooks);
    fake::keys = {KEY_F2}; godhand_pc_pause::on = false;
    host.tick(true); assert(!host.overlaysOpen() && !fake::overlay);
    godhand_pc_pause::on = true;
    host.tick(false); assert(!host.overlaysOpen());
    host.tick(true);
    assert(host.overlaysOpen() && fake::overlay && godhand_pc_pause::gate().requested());
    assert(host.view().model().phase() == Phase::AwaitHold);
    assert(!ps2x::controls::lastDrawable && ps2x::controls::ticks == 3);
    fake::keys = {KEY_RIGHT}; host.tick(true);
    assert(host.view().model().draft() == 2u); // request is not acknowledgement
    godhand_pc_pause::gate().held = true;
    host.tick(true); assert(host.view().model().draft() == 3u);
    assert(!ps2x::controls::lastDrawable); // F1 still ticks, cannot steal the owner
    fake::keys = {KEY_ESCAPE}; host.tick(true);
    assert(!host.overlaysOpen() && !fake::overlay && !godhand_pc_pause::gate().requested());

    // Existing controls own the screen; F2 cannot replace or release them.
    ps2x::controls::open = true; fake::overlay = true;
    fake::keys = {KEY_F2}; host.tick(true);
    assert(!host.view().isOpen() && host.overlaysOpen() && fake::overlay);
    assert(ps2x::controls::lastDrawable && godhand_pc_pause::gate().requested());
    host.shutdown();
    assert(ps2x::controls::shutdowns == 1 && !host.overlaysOpen() && !fake::overlay);
    assert(!godhand_pc_pause::gate().requested());

    std::cout << "host F1 tick exclusivity requested-vs-held close shutdown: PASS\n";
}
