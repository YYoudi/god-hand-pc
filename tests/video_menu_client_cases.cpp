// Original separate-process IPC fixture. Invented settings only, no window/game.
#include "video_menu_client.hpp"
#include <iostream>
#include <thread>

using namespace godhand_pc_video;
static Response waitSet(Client &client, uint32_t id) {
    const auto end = Client::Clock::now() + std::chrono::seconds(8);
    while (Client::Clock::now() < end) {
        if (const auto reply = client.receive(id)) return *reply;
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    throw std::runtime_error("Fixture observation deadline, no restart");
}
static ReadResponse waitRead(Client &client) {
    const auto end = Client::Clock::now() + std::chrono::seconds(8);
    while (Client::Clock::now() < end) {
        if (const auto reply = client.receiveRefresh()) return *reply;
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    throw std::runtime_error("Fixture read observation deadline");
}
static void require(bool value, const char *message) { if (!value) throw std::runtime_error(message); }
static int run(const std::string &mode, const std::filesystem::path &directory) {
    std::cout << std::unitbuf;
    if (mode == "raw-config") {
        const auto raw = message_io::readReady(directory, "config");
        require(raw.has_value(), "Config not ready"); wire::config(*raw);
        std::cout << "RAW-OK\n"; return 0;
    }
    Client client(directory, mode == "timeout" ? std::chrono::milliseconds(60) : std::chrono::milliseconds(1500));
    std::cout << "INIT " << wire::scale(client.config().runRequest) << ' ' << wire::scale(client.config().saved.scale) << '\n';
    if (mode == "initial") return 0;
    const Request first{1, mode == "stale" ? Scale{3u} : Scale{4u}, client.config().saved.revision};
    require(client.submit(first) == Submission::Queued, "First request not queued");
    std::cout << "QUEUED\n";
    const auto one = waitSet(client, 1);
    if (mode == "timeout" || mode == "bad-reply" || mode == "lost-reply") {
        require(one.result == Reply::Unknown, "Uncertain outcome not Unknown");
        require(client.submit({2, 6u, client.config().saved.revision}) == Submission::Unknown,
                "Write was not blocked after uncertainty");
        std::cout << "UNKNOWN-NO-RETRY\n"; return 0;
    }
    if (mode == "stale" || mode == "uncertain") {
        require(one.result == (mode == "stale" ? Reply::Stale : Reply::Unknown), "Expected stale/unknown result");
        require(client.submit({2, 6u, first.expectedRevision}) == Submission::Unknown, "Blind retry permitted");
        require(client.refresh() == Submission::Queued, "Read not queued");
        const auto read = waitRead(client);
        require(read.result == ReadStatus::Ready && read.snapshot.scale == (mode == "stale" ? Scale{5u} : Scale{4u}),
                "Read did not reconcile current preference");
        require(client.submit({3, 6u, read.snapshot.revision}) == Submission::Queued, "Reconciled set refused");
        require(waitSet(client, 3).result == Reply::Saved, "Reconciled set not acknowledged");
        std::cout << "RECONCILED-SAVED\n"; return 0;
    }
    require(mode == "roundtrip" && one.result == Reply::Saved && one.committed.scale == 4u, "First save not verified");
    require(client.submit({2, std::nullopt, one.committed.revision}) == Submission::Queued, "Reset not queued");
    const auto reset = waitSet(client, 2);
    require(reset.result == Reply::Saved && !reset.committed.scale, "Reset not verified");
    require(client.refresh() == Submission::Queued, "Snapshot read not queued");
    const auto read = waitRead(client);
    require(read.result == ReadStatus::Ready && !read.snapshot.scale, "Read/reset mismatch");
    require(client.config().runRequest == 3u, "Current run intent changed");
    std::cout << "ROUNDTRIP-RESET-READ\n"; return 0;
}
#if defined(_WIN32)
int wmain(int argc, wchar_t **argv) {
    try {
        require(argc == 3, "Fixture arguments"); const std::wstring wide(argv[1]);
        return run(std::string(wide.begin(), wide.end()), std::filesystem::path(argv[2]));
    } catch (const std::exception &error) { std::cerr << error.what() << '\n'; return 3; }
}
#else
int main(int argc, char **argv) {
    try { require(argc == 3, "Fixture arguments"); return run(argv[1], std::filesystem::path(argv[2])); }
    catch (const std::exception &error) { std::cerr << error.what() << '\n'; return 3; }
}
#endif
