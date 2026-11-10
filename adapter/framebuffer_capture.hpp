// Original GPL-3.0-only host readback extent. No game pixels, timing or viewport changes.
#pragma once
#include "raylib.h"
#include "rlgl.h"
#include <cstdint>

namespace godhand_pc_capture {
inline bool validExtent(int width, int height) noexcept {
    return width > 0 && height > 0 && width <= 16384 && height <= 16384 &&
           static_cast<int64_t>(width) * height <= 64 * 1024 * 1024;
}
// Only the current default-window framebuffer, at the host capture point.
// The caller retains Image ownership and must UnloadImage. Do NOT multiply
// logical dimensions by monitor DPI; that is not the allocated framebuffer.
inline Image readWindow() {
    const int width = GetRenderWidth(), height = GetRenderHeight();
    if (!validExtent(width, height)) return {};
    rlDrawRenderBatchActive();
    void *pixels = rlReadScreenPixels(width, height);
    if (!pixels) return {};
    return Image{pixels, width, height, 1, PIXELFORMAT_UNCOMPRESSED_R8G8B8A8};
}
} // namespace godhand_pc_capture
