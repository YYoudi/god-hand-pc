// Original GPL-3.0-only Windows read-only input guard. No game data or addresses.
#pragma once
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <string>
#include <string_view>

namespace godhand_pc::inputs {
enum class InputStatus {
    Empty, InvalidExpectation, OpenFailed, NotRegularDiskFile, MetadataFailed,
    SizeMismatch, ReadFailed, DigestMismatch, ChangedDuringRead, Verified
};
inline const char* statusName(InputStatus status) {
    switch (status) {
    case InputStatus::Empty: return "empty";
    case InputStatus::InvalidExpectation: return "invalid-expectation";
    case InputStatus::OpenFailed: return "open-failed";
    case InputStatus::NotRegularDiskFile: return "not-regular-disk-file";
    case InputStatus::MetadataFailed: return "metadata-failed";
    case InputStatus::SizeMismatch: return "size-mismatch";
    case InputStatus::ReadFailed: return "read-failed";
    case InputStatus::DigestMismatch: return "digest-mismatch";
    case InputStatus::ChangedDuringRead: return "changed-during-read";
    case InputStatus::Verified: return "verified";
    }
    return "unknown";
}

// Owns a non-inheritable read handle. Share-read permits the runtime's own
// reader, but does not grant write/delete sharing. This is a supported-profile
// check, not an adversarial path-resolution or general filesystem certificate.
class LockedInputFile {
public:
    LockedInputFile();
    ~LockedInputFile();
    LockedInputFile(const LockedInputFile&) = delete;
    LockedInputFile& operator=(const LockedInputFile&) = delete;
    LockedInputFile(LockedInputFile&& other) noexcept;
    LockedInputFile& operator=(LockedInputFile&& other) noexcept;
    [[nodiscard]] InputStatus status() const { return status_; }
    [[nodiscard]] uint32_t osError() const { return error_; }
    [[nodiscard]] bool verified() const { return status_ == InputStatus::Verified; }
    [[nodiscard]] const std::string& digest() const { return digest_; }

    // Hasher supplies update(const void*, size_t) and finishHex(). The native
    // caller must supply its audited SHA-256 implementation. An injected test
    // hasher establishes byte delivery/I/O policy, not cryptographic soundness.
    template<class Hasher>
    static LockedInputFile verify(const std::filesystem::path& path,
                                  uint64_t expectedSize,
                                  std::string_view expectedDigest, Hasher hasher) {
        // Synchronous callbacks only; the implementation never retains them.
        // Windows declarations stay in the .cpp to coexist with Raylib headers.
        return verifyStream(path, expectedSize, expectedDigest,
            [&hasher](const void* data, size_t size) { hasher.update(data, size); },
            [&hasher]() { return hasher.finishHex(); });
    }
private:
    struct State;
    static LockedInputFile verifyStream(const std::filesystem::path&, uint64_t,
        std::string_view, const std::function<void(const void*, size_t)>&,
        const std::function<std::string()>&);
    LockedInputFile fail(InputStatus status, uint32_t error = 0);
    void moveFrom(LockedInputFile& other) noexcept;
    std::unique_ptr<State> state_;
    InputStatus status_ = InputStatus::Empty;
    uint32_t error_ = 0;
    std::string digest_;
};
} // namespace godhand_pc::inputs
