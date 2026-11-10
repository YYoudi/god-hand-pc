// Original invented menu/editor events. No game, raylib, graphics or native integration.
#include "video_menu_model.hpp"
#include <cassert>
#include <iostream>
#include <string>

using namespace godhand_pc_video;

int main() {
    const std::string a(64, 'a'), b(64, 'b'), c(64, 'c');
    Model menu(3u, {2u, a});
    assert(!menu.open(false, true));
    assert(!menu.open(true, false));
    assert(menu.open(true, true));
    assert(!menu.open(true, true));
    assert(menu.phase() == Phase::AwaitHold);
    assert(!menu.edit(4u) && !menu.save()); // requested/visible is NOT acknowledged
    menu.close(); // cancellation before acknowledgement must work
    assert(menu.phase() == Phase::Closed && !menu.save());
    assert(menu.open(true, true));
    menu.observeHold(true);
    assert(!menu.edit(0u) && !menu.edit(9u));
    assert(menu.edit(4u));
    menu.observeHold(false);
    assert(!menu.edit(5u) && !menu.save()); // losing the hold disables edits/save
    menu.observeHold(true);
    auto request = menu.save();
    assert(request && request->id == 1 && request->scale == 4u && request->expectedRevision == a);
    assert(menu.phase() == Phase::AwaitReply && !menu.edit(6u) && !menu.save());
    assert(!menu.reply(2, Reply::Saved, {4u, b}));
    assert(!menu.refresh({5u, c}));
    bool invalid = false;
    try { menu.reply(1, Reply::Saved, {4u, a}); } catch (const std::invalid_argument &) { invalid = true; }
    assert(invalid && menu.pending());
    invalid = false;
    try { menu.reply(1, Reply::Saved, {5u, b}); } catch (const std::invalid_argument &) { invalid = true; }
    assert(invalid && menu.pending() && menu.saved().revision == a);
    menu.close(); // stop/close does not pretend an in-flight request was cancelled
    assert(menu.pending() && menu.reply(1, Reply::Saved, {4u, b}));
    assert(menu.saved().scale == 4u && menu.saved().revision == b && menu.runRequest() == 3u);
    assert(menu.notice() == Notice::SavedForRestart);
    assert(!menu.reply(1, Reply::Saved, {4u, b}));
    assert(menu.open(true, true));
    menu.observeHold(true);
    assert(menu.edit(std::nullopt));
    request = menu.save();
    assert(request && request->id == 2 && !request->scale);
    assert(menu.reply(2, Reply::Stale));
    assert(menu.reloadRequired() && !menu.save() && menu.saved().revision == b);
    assert(menu.refresh({7u, c}) && menu.draft() == 7u);
    assert(menu.edit(1u)); request = menu.save();
    assert(request && menu.reply(request->id, Reply::Unknown));
    assert(menu.notice() == Notice::OutcomeUnknown && !menu.save());
    assert(menu.refresh({7u, c}));
    assert(menu.edit(2u)); request = menu.save();
    assert(request && menu.reply(request->id, Reply::Rejected));
    assert(menu.notice() == Notice::NotSaved && !menu.reloadRequired());
    assert(menu.save()); // retry only after a known no-commit refusal

    Model discard(2u, {2u, a});
    assert(discard.open(true, true)); discard.observeHold(true);
    assert(discard.edit(8u)); discard.close();
    assert(discard.draft() == 2u && discard.saved().revision == a);

    Model bounded(std::nullopt, {std::nullopt, a});
    assert(bounded.open(true, true)); bounded.observeHold(true);
    for (uint32_t n = 1; n <= Model::MaxRequests; ++n) {
        assert(bounded.edit(n % 2 ? Scale{1u} : Scale{2u}));
        const auto out = bounded.save(); assert(out && out->id == n);
        assert(bounded.reply(n, Reply::Saved, {out->scale, n % 2 ? b : a}));
    }
    assert(bounded.edit(3u) && !bounded.save() && bounded.notice() == Notice::LimitReached);
    assert(!bounded.runRequest());
    for (auto revision : {std::string("../outside"), std::string(64, 'A'), std::string(63, 'a')}) {
        invalid = false;
        try { Model bad(1u, {1u, revision}); } catch (const std::invalid_argument &) { invalid = true; }
        assert(invalid);
    }
    std::cout << "ownership hold cancellation restart stale unknown bounded: PASS\n";
}
