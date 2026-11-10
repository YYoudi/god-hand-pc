// Original invented host/UI events. Stub draws are NOT pixels or native evidence.
#include "video_menu_view.hpp"
#include <cassert>
#include <iostream>

using namespace godhand_pc_video;
namespace fake = invented_host;

int main() {
    const std::string a(64, 'a'), b(64, 'b'), c(64, 'c');
    std::optional<Request> sent;
    std::optional<Response> incoming;
    std::optional<Snapshot> current = Snapshot{8u, c};
    bool readQueued = false;
    Hooks hooks{
        [&](const Request &request) { sent = request; return Submission::Queued; },
        [&](uint32_t) { auto out = incoming; incoming.reset(); return out; },
        [&]() { readQueued = true; return Submission::Queued; },
        [&]() -> std::optional<ReadResponse> {
            if (!readQueued || !current) return {};
            readQueued = false; return ReadResponse{ReadStatus::Ready, *current}; }};
    View view(3u, {2u, a}, hooks);
    fake::keys = {KEY_F2};
    view.pollToggle(false, false); assert(!view.isOpen() && !fake::overlay);
    view.pollToggle(true, true); assert(!view.isOpen() && !fake::overlay);
    fake::width = 320; view.pollToggle(true, false); assert(!view.isOpen());
    fake::width = 640; view.pollToggle(true, false);
    assert(view.isOpen() && fake::overlay && view.model().phase() == Phase::AwaitHold);
    fake::keys = {KEY_RIGHT, KEY_ENTER}; view.poll(false);
    assert(view.model().draft() == 2u && !sent);
    fake::keys = {KEY_RIGHT}; view.poll(true); assert(view.model().draft() == 3u);
    fake::keys = {KEY_DOWN}; view.poll(true);
    fake::keys = {KEY_ENTER}; view.poll(true);
    assert(sent && sent->scale == 3u && sent->expectedRevision == a);
    assert(view.model().phase() == Phase::AwaitReply && view.model().saved().scale == 2u);
    fake::keys.clear(); view.draw();
    assert(fake::has("Waiting for storage acknowledgement; not yet saved"));
    assert(fake::has("Effective GL scale: not observed by this menu"));
    incoming = Response{sent->id + 1, Reply::Saved, {3u, b}}; view.poll(true);
    assert(view.model().pending());
    incoming = Response{sent->id, Reply::Saved, {3u, b}}; view.poll(true);
    assert(view.model().saved().revision == b && view.model().runRequest() == 3u);
    fake::texts.clear(); view.draw();
    assert(fake::has("Saved for the next launch; current run unchanged"));
    fake::keys = {KEY_R}; view.poll(true); assert(!view.model().draft());
    fake::keys = {KEY_ENTER}; view.poll(true); assert(view.model().pending());
    fake::keys = {KEY_ESCAPE}; view.poll(true);
    assert(!view.isOpen() && !fake::overlay && view.model().pending());
    incoming = Response{view.model().pending()->id, Reply::Unknown, {std::nullopt, {}}};
    fake::keys.clear(); view.poll(false);
    assert(view.model().reloadRequired());
    fake::keys = {KEY_F2}; view.pollToggle(true, false);
    fake::keys = {KEY_DOWN}; view.poll(true); // save row
    fake::keys = {KEY_DOWN}; view.poll(true); // reload row
    fake::keys = {KEY_ENTER}; view.poll(true);
    assert(view.model().saved().scale != 8u); // queued read is NOT a completed refresh
    fake::keys.clear(); view.poll(true);
    assert(view.model().saved().scale == 8u && !view.model().reloadRequired());
    fake::width = 320; fake::keys = {KEY_R}; view.poll(true);
    assert(view.model().draft() == 8u); // shrink disables invisible editing
    fake::texts.clear(); view.draw(); assert(fake::has("Resize, or F2/Esc to close"));
    fake::keys = {KEY_ESCAPE}; view.poll(true); assert(!view.isOpen() && !fake::overlay);
    const auto releases = fake::releases;
    view.shutdown(); assert(fake::releases == releases); // does not release another owner's overlay

    fake::width = 640;
    View unavailable(3u, {2u, a}, {});
    fake::keys = {KEY_F2}; unavailable.pollToggle(true, false); assert(!unavailable.isOpen());

    View throwing(3u, {2u, a}, Hooks{
        [](const Request &) -> Submission { throw std::runtime_error("invented uncertain write"); },
        [](uint32_t) -> std::optional<Response> { return {}; },
        []() { return Submission::Rejected; },
        []() -> std::optional<ReadResponse> { return {}; }});
    throwing.pollToggle(true, false);
    fake::keys = {KEY_RIGHT}; throwing.poll(true);
    fake::keys = {KEY_DOWN}; throwing.poll(true);
    fake::keys = {KEY_ENTER}; throwing.poll(true);
    assert(throwing.model().notice() == Notice::OutcomeUnknown && throwing.model().reloadRequired());
    throwing.shutdown(); assert(!fake::overlay);

    incoming.reset(); sent.reset();
    View badReply(3u, {2u, a}, hooks);
    fake::keys = {KEY_F2}; badReply.pollToggle(true, false);
    fake::focused = false; fake::keys = {KEY_R}; badReply.poll(true);
    assert(badReply.model().draft() == 2u); // focus loss does not edit
    fake::focused = true; fake::keys = {KEY_RIGHT}; badReply.poll(true);
    fake::keys = {KEY_DOWN}; badReply.poll(true);
    fake::keys = {KEY_ENTER}; badReply.poll(true);
    assert(sent && sent->scale == 3u);
    incoming = Response{sent->id, Reply::Saved, {4u, b}};
    fake::keys.clear(); badReply.poll(true);
    assert(badReply.model().saved().revision == a);
    assert(badReply.model().notice() == Notice::OutcomeUnknown && badReply.model().reloadRequired());
    badReply.shutdown(); assert(!fake::overlay);
    std::cout << "view exclusivity hold ack close reload size unknown: PASS\n";
}
