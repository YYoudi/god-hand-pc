"""Original GPL bounded reference expansion for the experimental host upload.

Format provenance: the preserved MIT lab's specs/tm3-tim3-v1.md. No engine or
game code is copied. Unlike resources.py's metadata planner, this explicitly
reads original texture bytes into private memory: never publish its outputs.
This module is not a public HD installer, general texture decoder or asset tool.
"""
import struct
import resources


def transfer_address(x, y):
    """128x128 PSMT4 view of one64x32 PSMCT32 stored transfer, byte/shift."""
    resources.require(type(x) is int and type(y) is int and 0 <= x < 128 and 0 <= y < 128,
                      "Only the128x128 transfer contract is supported")
    xb = lambda bit: (x >> bit) & 1
    yb = lambda bit: (y >> bit) & 1
    bits = [yb(1), xb(3), xb(4), xb(0), yb(0), xb(1), xb(2)^yb(1)^yb(2),
            yb(2), yb(3), yb(4), xb(5), yb(5), xb(6), yb(6)]
    nibble = sum(value << bit for bit, value in enumerate(bits))
    byte = nibble >> 1
    px = sum(((byte >> bit) & 1) << n for n, bit in enumerate([2, 4, 5, 8, 10, 12]))
    py = sum(((byte >> bit) & 1) << n for n, bit in enumerate([3, 6, 7, 9, 11]))
    return (py * 64 + px) * 4 + (byte & 3), 4 * (nibble & 1)


def expand(payload):
    """Raw palette alpha is preserved; do not invert presentation normalization."""
    resources.require(type(payload) is bytes and len(payload) == 8256, "Unsupported stored reference length")
    out = bytearray()
    for y in range(128):
        for x in range(128):
            at, shift = transfer_address(x, y)
            index = (payload[at] >> shift) & 15
            out.extend(payload[8192+4*index:8196+4*index])
    return bytes(out)


def read_reference(disc, target):
    """Caller must verify the personal retail profile before using this reader."""
    selected = resources.resolve_texture(disc, target)
    resources.require((selected.width, selected.height, selected.index_bits, selected.storage, selected.size)
                      == (128, 128, 4, 6, 8256), "Unsupported reference metadata")
    return selected, expand(disc.read(selected.offset-disc.offset, selected.size))


def envelope(reference, rgba, width, height):
    resources.require(type(reference) is bytes and len(reference) == 128*128*4, "Reference must be raw128x128 RGBA")
    resources.require(type(width) is int and type(height) is int and 128 < width <= 2048 and
                      128 < height <= 2048 and width & (width-1) == 0 and height & (height-1) == 0,
                      "Unsupported external dimensions")
    resources.require(type(rgba) is bytes and len(rgba) == width*height*4, "External raw RGBA length differs")
    return b"GHHD001\0" + struct.pack("<6I", 128, 128, width, height, 128*128, width*height) + reference + rgba


def example_rgba():
    """Original512x512 grid/checker diagnostic; no game data is read or copied."""
    out = bytearray()
    for y in range(512):
        for x in range(512):
            if x % 64 == 0 or y % 64 == 0:
                color = (255, 255, 255, 128)
            elif (x // 8 + y // 8) % 2:
                color = (24, 180, 225, 128)
            else:
                color = (240, 48, 160, 128)
            if x % 128 == 1:
                color = (255, 235, 0, 128)
            if y % 128 == 2:
                color = (12, 12, 12, 128)
            out.extend(color)
    return bytes(out)
