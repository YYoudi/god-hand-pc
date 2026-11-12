// Original GPL-3.0-only Windows input verification. No game contents or addresses.
#include "locked_input_file.hpp"
#ifndef _WIN32
#error "LockedInputFile requires Windows file-sharing semantics"
#endif
#include <windows.h>
#include <array>
#include <utility>

namespace godhand_pc::inputs {
struct LockedInputFile::State {
    HANDLE handle = INVALID_HANDLE_VALUE;
    ~State() { if (handle != INVALID_HANDLE_VALUE) CloseHandle(handle); }
};
LockedInputFile::LockedInputFile() = default;
LockedInputFile::~LockedInputFile() = default;
LockedInputFile::LockedInputFile(LockedInputFile&& other) noexcept { moveFrom(other); }
LockedInputFile& LockedInputFile::operator=(LockedInputFile&& other) noexcept {
    if (this != &other) { state_.reset(); moveFrom(other); }
    return *this;
}
void LockedInputFile::moveFrom(LockedInputFile& other) noexcept {
    state_ = std::move(other.state_);
    status_ = std::exchange(other.status_, InputStatus::Empty);
    error_ = std::exchange(other.error_, 0);
    digest_ = std::move(other.digest_);
}
LockedInputFile LockedInputFile::fail(InputStatus status, uint32_t error) {
    status_ = status; error_ = error; state_.reset();
    return std::move(*this);
}
namespace {
bool sameFile(const BY_HANDLE_FILE_INFORMATION& a, const BY_HANDLE_FILE_INFORMATION& b) {
    return a.dwVolumeSerialNumber == b.dwVolumeSerialNumber &&
        a.nFileIndexHigh == b.nFileIndexHigh && a.nFileIndexLow == b.nFileIndexLow &&
        a.nFileSizeHigh == b.nFileSizeHigh && a.nFileSizeLow == b.nFileSizeLow &&
        a.ftLastWriteTime.dwHighDateTime == b.ftLastWriteTime.dwHighDateTime &&
        a.ftLastWriteTime.dwLowDateTime == b.ftLastWriteTime.dwLowDateTime;
}
} // namespace
LockedInputFile LockedInputFile::verifyStream(const std::filesystem::path& path,
    uint64_t expectedSize, std::string_view expectedDigest,
    const std::function<void(const void*, size_t)>& consume,
    const std::function<std::string()>& finish) {
    LockedInputFile result;
    if (!expectedSize || expectedDigest.size() != 64) {
        result.status_ = InputStatus::InvalidExpectation; return result;
    }
    for (char c : expectedDigest) {
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) {
            result.status_ = InputStatus::InvalidExpectation; return result;
        }
    }
    result.state_ = std::make_unique<State>();
    auto& handle = result.state_->handle;
    handle = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ,
        nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_SEQUENTIAL_SCAN, nullptr);
    if (handle == INVALID_HANDLE_VALUE) return result.fail(InputStatus::OpenFailed, GetLastError());
    BY_HANDLE_FILE_INFORMATION before{};
    if (GetFileType(handle) != FILE_TYPE_DISK) return result.fail(InputStatus::NotRegularDiskFile);
    if (!GetFileInformationByHandle(handle, &before)) {
        return result.fail(InputStatus::MetadataFailed, GetLastError());
    }
    if (before.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) return result.fail(InputStatus::NotRegularDiskFile);
    const uint64_t size = (uint64_t(before.nFileSizeHigh) << 32) | before.nFileSizeLow;
    if (size != expectedSize) return result.fail(InputStatus::SizeMismatch);
    std::array<unsigned char, 65536> buffer{};
    uint64_t consumed = 0;
    while (consumed < expectedSize) {
        const auto remaining = expectedSize - consumed;
        const DWORD request = static_cast<DWORD>(remaining < buffer.size() ? remaining : buffer.size());
        DWORD count = 0;
        if (!ReadFile(handle, buffer.data(), request, &count, nullptr)) {
            return result.fail(InputStatus::ReadFailed, GetLastError());
        }
        if (!count || count > request) return result.fail(InputStatus::ReadFailed);
        consume(buffer.data(), count); consumed += count;
    }
    BY_HANDLE_FILE_INFORMATION after{};
    if (!GetFileInformationByHandle(handle, &after)) {
        return result.fail(InputStatus::MetadataFailed, GetLastError());
    }
    if (!sameFile(before, after)) return result.fail(InputStatus::ChangedDuringRead);
    result.digest_ = finish();
    if (result.digest_ != expectedDigest) return result.fail(InputStatus::DigestMismatch);
    result.status_ = InputStatus::Verified;
    return result;
}
} // namespace godhand_pc::inputs
