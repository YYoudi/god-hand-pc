// Original GPL-3.0-only bounded preference wire. No game data or arbitrary paths.
#pragma once
#include "video_menu_model.hpp"
#include <functional>
#include <string_view>
#include <vector>

namespace godhand_pc_video {
enum class Submission { Queued, Rejected, Unknown };
struct Response { uint32_t id; Reply result; Snapshot committed; };
enum class ReadStatus { Ready, Unavailable, Unknown };
struct ReadResponse { ReadStatus result; Snapshot snapshot; };
struct Hooks {
    // Never wait for the other process. Concrete local I/O is metadata-bounded,
    // not a real-time OS/disk-latency guarantee. Queued is NOT Saved/ReadReady.
    std::function<Submission(const Request &)> submit;
    std::function<std::optional<Response>(uint32_t)> receive;
    std::function<Submission()> refresh;
    std::function<std::optional<ReadResponse>()> receiveRefresh;
};

namespace wire {
inline constexpr size_t Limit = 512;
inline constexpr uint32_t MaxSequence = 128;
inline bool nonce(const std::string &value) {
    return value.size() == 32 && validRevision(value + value);
}
inline std::string scale(Scale value) {
    if (!validScale(value)) throw std::invalid_argument("Invalid wire scale");
    return value ? std::to_string(*value) : "ini";
}
inline Scale parseScale(const std::string &value) {
    if (value == "ini") return {};
    if (value.size() != 1 || value[0] < '1' || value[0] > '8') throw std::invalid_argument("Invalid scale token");
    return static_cast<uint32_t>(value[0] - '0');
}
inline std::vector<std::string> fields(const std::string &raw, size_t count) {
    if (raw.empty() || raw.size() > Limit || raw.back() != '\n') throw std::invalid_argument("Invalid wire length/newline");
    std::vector<std::string> out(1);
    for (size_t i = 0; i + 1 < raw.size(); ++i) {
        const char c = raw[i];
        if (c == '\t') { out.emplace_back(); continue; }
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-'))
            throw std::invalid_argument("Invalid wire character");
        out.back() += c;
    }
    if (out.size() != count || out[0] != "GHPCV1") throw std::invalid_argument("Invalid wire schema");
    for (const auto &value : out) if (value.empty()) throw std::invalid_argument("Empty wire field");
    return out;
}
inline std::string join(const std::vector<std::string> &values) {
    std::string out;
    for (const auto &value : values) { if (!out.empty()) out += '\t'; out += value; }
    out += '\n';
    if (out.size() > Limit) throw std::invalid_argument("Wire output too large");
    return out;
}
struct Config { std::string session; Scale runRequest; Snapshot saved; bool scratch = false; };
inline Config config(const std::string &raw) {
    const auto f = fields(raw, 6);
    if (!nonce(f[1]) || !validRevision(f[4]) || (f[5] != "scratch" && f[5] != "persistent"))
        throw std::invalid_argument("Invalid channel config");
    return Config{f[1], parseScale(f[2]), {parseScale(f[3]), f[4]}, f[5] == "scratch"};
}
struct Operation { uint32_t sequence; bool read; Request request; };
inline std::vector<std::string> requestFields(const Config &c, const Operation &o) {
    if (!nonce(c.session) || o.sequence < 1 || o.sequence > MaxSequence) throw std::invalid_argument("Invalid wire identity");
    if (o.read) return {"GHPCV1", c.session, std::to_string(o.sequence), "read", "0", "-", "-"};
    if (o.request.id < 1 || o.request.id > Model::MaxRequests || !validRevision(o.request.expectedRevision))
        throw std::invalid_argument("Invalid set identity");
    return {"GHPCV1", c.session, std::to_string(o.sequence), "set", std::to_string(o.request.id),
            o.request.expectedRevision, scale(o.request.scale)};
}
struct Decoded { std::string status; Snapshot snapshot; };
inline Decoded reply(const Config &c, const Operation &o, const std::string &raw) {
    const auto f = fields(raw, 10), expected = requestFields(c, o);
    for (size_t i = 0; i < expected.size(); ++i)
        if (f[i] != expected[i]) throw std::invalid_argument("Reply identity/selection differs");
    if (f[7] == "ok") {
        if (!validRevision(f[8])) throw std::invalid_argument("Invalid committed revision");
        Snapshot current{parseScale(f[9]), f[8]};
        if (!o.read && (current.revision == o.request.expectedRevision || current.scale != o.request.scale))
            throw std::invalid_argument("Reply did not commit the requested preference");
        return {f[7], current};
    }
    if ((f[7] != "stale" && f[7] != "rejected" && f[7] != "unknown") ||
        (o.read && f[7] == "stale") || f[8] != "-" || f[9] != "-")
        throw std::invalid_argument("Invalid negative reply");
    return {f[7], {std::nullopt, {}}};
}
} // namespace wire
} // namespace godhand_pc_video
