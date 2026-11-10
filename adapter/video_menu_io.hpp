// Original GPL-3.0-only exclusive immutable message I/O, no game dependency.
#pragma once
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>
namespace godhand_pc_video::message_io {
void validateDirectory(const std::filesystem::path &directory);
void publish(const std::filesystem::path &directory, const std::string &name, std::string_view payload);
std::optional<std::string> readReady(const std::filesystem::path &directory, const std::string &name);
}
