// Original GPL-3.0-only local IPC I/O. Cooperative ownership, not a hostile-FS sandbox.
#include "video_menu_io.hpp"
#include "video_menu_protocol.hpp"
#include <stdexcept>
#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace godhand_pc_video::message_io {
namespace {
void check(bool ok, const char *message) { if (!ok) throw std::runtime_error(message); }
void filename(const std::string &name) {
    check(!name.empty() && name.size() <= 40, "Invalid message name");
    for (char c : name) check((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '-', "Invalid message name");
}
#if defined(_WIN32)
struct File {
    HANDLE handle = INVALID_HANDLE_VALUE;
    ~File() { if (handle != INVALID_HANDLE_VALUE) CloseHandle(handle); }
};
std::optional<std::string> readFile(const std::filesystem::path &path) {
    File file{CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING,
                          FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_SEQUENTIAL_SCAN, nullptr)};
    if (file.handle == INVALID_HANDLE_VALUE) {
        const auto error = GetLastError();
        if (error == ERROR_FILE_NOT_FOUND || error == ERROR_PATH_NOT_FOUND) return {};
        throw std::runtime_error("Cannot open message");
    }
    BY_HANDLE_FILE_INFORMATION info{};
    check(GetFileInformationByHandle(file.handle, &info) && GetFileType(file.handle) == FILE_TYPE_DISK,
          "Message metadata unavailable");
    check(!(info.dwFileAttributes & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)) &&
          info.nNumberOfLinks == 1 && info.nFileSizeHigh == 0 && info.nFileSizeLow <= wire::Limit,
          "Message must be a bounded ordinary unaliased file");
    std::string raw(info.nFileSizeLow, '\0'); DWORD got = 0;
    check(ReadFile(file.handle, raw.data(), static_cast<DWORD>(raw.size()), &got, nullptr) && got == raw.size(),
          "Incomplete message read");
    char extra = 0;
    check(ReadFile(file.handle, &extra, 1, &got, nullptr) && got == 0, "Message grew during read");
    return raw;
}
void writeFile(const std::filesystem::path &path, std::string_view raw) {
    // Empty ready markers are published by creation alone. A live write handle
    // would conflict with an immutable consumer read on Windows. Payloads remain
    // exclusive writes and are fully flushed/closed BEFORE marker creation.
    File file{CreateFileW(path.c_str(), raw.empty() ? GENERIC_READ : GENERIC_WRITE,
                         raw.empty() ? FILE_SHARE_READ : 0, nullptr, CREATE_NEW,
                         FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, nullptr)};
    check(file.handle != INVALID_HANDLE_VALUE, "Cannot exclusively create message");
    size_t done = 0;
    while (done < raw.size()) {
        DWORD wrote = 0;
        check(WriteFile(file.handle, raw.data() + done, static_cast<DWORD>(raw.size() - done), &wrote, nullptr) && wrote > 0,
              "Incomplete message write");
        done += wrote;
    }
    if (!raw.empty()) check(FlushFileBuffers(file.handle), "Cannot flush message");
}
#else
struct File { int fd = -1; ~File() { if (fd >= 0) ::close(fd); } };
std::optional<std::string> readFile(const std::filesystem::path &path) {
    File file{::open(path.c_str(), O_RDONLY | O_NOFOLLOW | O_CLOEXEC)};
    if (file.fd < 0) { if (errno == ENOENT) return {}; throw std::runtime_error("Cannot open message"); }
    struct stat info{};
    check(fstat(file.fd, &info) == 0 && S_ISREG(info.st_mode) && info.st_nlink == 1 &&
          info.st_size >= 0 && static_cast<uint64_t>(info.st_size) <= wire::Limit,
          "Message must be a bounded ordinary unaliased file");
    std::string raw(static_cast<size_t>(info.st_size), '\0'); size_t done = 0;
    while (done < raw.size()) {
        const auto got = ::read(file.fd, raw.data() + done, raw.size() - done);
        if (got < 0 && errno == EINTR) continue;
        check(got > 0, "Incomplete message read"); done += static_cast<size_t>(got);
    }
    char extra = 0; check(::read(file.fd, &extra, 1) == 0, "Message grew during read");
    return raw;
}
void writeFile(const std::filesystem::path &path, std::string_view raw) {
    File file{::open(path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600)};
    check(file.fd >= 0, "Cannot exclusively create message");
    size_t done = 0;
    while (done < raw.size()) {
        const auto wrote = ::write(file.fd, raw.data() + done, raw.size() - done);
        if (wrote < 0 && errno == EINTR) continue;
        check(wrote > 0, "Incomplete message write"); done += static_cast<size_t>(wrote);
    }
    check(::fsync(file.fd) == 0, "Cannot flush message");
}
#endif
}

void validateDirectory(const std::filesystem::path &directory) {
    check(directory.is_absolute() && directory.lexically_normal() == directory, "Message directory must be absolute/normalized");
#if defined(_WIN32)
    const auto drive = directory.root_name().wstring();
    check(drive.size() == 2 && drive[1] == L':', "UNC message directories are unsupported");
#endif
    auto part = directory.root_path();
    for (const auto &name : directory.relative_path()) {
        part /= name;
#if defined(_WIN32)
        const DWORD attributes = GetFileAttributesW(part.c_str());
        check(attributes != INVALID_FILE_ATTRIBUTES && (attributes & FILE_ATTRIBUTE_DIRECTORY) &&
              !(attributes & FILE_ATTRIBUTE_REPARSE_POINT), "Message directory alias/reparse point refused");
#else
        struct stat info{};
        check(::lstat(part.c_str(), &info) == 0 && S_ISDIR(info.st_mode), "Message directory alias refused");
#endif
    }
}
void publish(const std::filesystem::path &directory, const std::string &name, std::string_view payload) {
    validateDirectory(directory); filename(name); check(payload.size() <= wire::Limit, "Message output too large");
    writeFile(directory / (name + ".txt"), payload);
    writeFile(directory / (name + ".ready"), {}); // never remove/replace an older attempt
}
std::optional<std::string> readReady(const std::filesystem::path &directory, const std::string &name) {
    validateDirectory(directory); filename(name);
    const auto marker = readFile(directory / (name + ".ready"));
    if (!marker) return {};
    check(marker->empty(), "Nonempty message ready marker");
    const auto payload = readFile(directory / (name + ".txt"));
    check(payload.has_value(), "Ready message has no payload");
    return payload;
}
} // namespace godhand_pc_video::message_io
