"""Original GPL-3.0-only configuration glue for a pinned generic-runtime build.

No third-party source, generated game code or program/address map is embedded.
This emits a Windows/MSVC build configuration, not an installer or ABI proof.
The caller must independently qualify the source trees and the resulting build.
"""
from pathlib import PurePosixPath, PureWindowsPath

TARGETS = ('ps2_runtime', 'ps2_iop', 'imgui', 'rlImGui', 'raylib')
DEPENDENCIES = ('raylib', 'imgui', 'rlimgui')


def _absolute_literal(value):
    if not isinstance(value, str) or not value or any(c in value for c in '$;"\r\n\0'):
        raise ValueError('Expected a literal absolute source path, not CMake syntax')
    normalized = value.replace('\\', '/')
    if '..' in normalized.split('/') or not (
            PureWindowsPath(normalized).is_absolute() or PurePosixPath(normalized).is_absolute()):
        raise ValueError('Absolute path without parent traversal required')
    return normalized.rstrip('/') or '/'


def cmake_project(runtime_source, dependency_sources):
    """Emit only generic targets using explicitly supplied, prequalified sources.

    RelWithDebInfo is selected by the caller: the pinned runtime's Release
    profile has different math/ISA flags and must not be silently substituted.
    No generated game directory or historical .lib is a producer input here.
    """
    runtime = _absolute_literal(runtime_source)
    if not isinstance(dependency_sources, dict) or set(dependency_sources) != set(DEPENDENCIES):
        raise ValueError('Exactly raylib, imgui and rlimgui source directories required')
    deps = {name: _absolute_literal(dependency_sources[name]) for name in DEPENDENCIES}
    lines = [
        '# Original GPL-3.0-only generic-runtime configuration glue.',
        'cmake_minimum_required(VERSION 3.21)',
        'project(PrototypeGenericReplay LANGUAGES C CXX)',
        'set(CMAKE_CXX_STANDARD 20)',
        'set(CMAKE_CXX_STANDARD_REQUIRED ON)',
        'set(CMAKE_EXPORT_COMPILE_COMMANDS ON)',
        'set(URBAN_BUILD_RECOMP OFF)',
        'set(URBAN_BUILD_TOOLS OFF)',
        'set(PS2X_ENABLE_DEBUG_UI ON CACHE BOOL "" FORCE)',
        'set(PS2X_ENABLE_FFMPEG OFF CACHE BOOL "" FORCE)',
        'set(PS2X_ENABLE_SDL_INPUT OFF CACHE BOOL "" FORCE)',
        'set(PS2X_ENABLE_AGRESSIVE_LOGS OFF CACHE BOOL "" FORCE)',
        'set(PS2X_ENABLE_RUNTIME_LOGS ON CACHE BOOL "" FORCE)',
        'set(PS2X_ENABLE_IOP_RPC_TRACE ON CACHE BOOL "" FORCE)',
        'set(PS2X_ENABLE_SCCACHE OFF CACHE BOOL "" FORCE)',
        'set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "" FORCE)',
    ]
    lines += [f'set(FETCHCONTENT_SOURCE_DIR_{name.upper()} "{deps[name]}" CACHE PATH "" FORCE)'
              for name in DEPENDENCIES]
    lines += [f'add_subdirectory("{runtime}" runtime EXCLUDE_FROM_ALL)', '']
    return '\n'.join(lines).encode('utf-8')


def msvc_library_outputs(build_directory):
    """Expected five MSVC archive paths; not a claim that the files exist."""
    base = _absolute_literal(build_directory).rstrip('/')
    return {
        'ps2_runtime': base + '/runtime/ps2xRuntime/ps2_runtime.lib',
        'ps2_iop': base + '/runtime/ps2xIOP/ps2_iop.lib',
        'imgui': base + '/runtime/ps2xRuntime/imgui.lib',
        'rlImGui': base + '/runtime/ps2xRuntime/rlImGui.lib',
        'raylib': base + '/_deps/raylib-build/raylib/raylib.lib',
    }
