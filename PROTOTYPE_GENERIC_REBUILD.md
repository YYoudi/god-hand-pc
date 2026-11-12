# Rebuilding the prototype's five generic libraries

12 November 2026. Follow-up to [fresh VU source replay](PROTOTYPE_VU_REPLAY.md).
This separate private build replaces the five historical generic archives with
newly compiled runtime, IOP and GUI/graphics libraries. It is not a new debug
feature, a graphics fix, a full personal-disc installer or normal-profile adoption.

## Source qualification

The historical 6 November snapshot sidecar is found **beside**, not inside, the
snapshot folder. It records the five library hashes and source revision
`1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`. This is useful retained provenance,
not a retroactive fresh-build result. The existing snapshot bytes still match.

The new build reads clean, exact pinned source trees:

- Runtime/IOP: `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`.
- raylib: `c1ab645ca298a2801097931d1079b10ff7eb9df8`.
- Dear ImGui: `b1bcb12a624af7509894c8e77dd47416997777fa`.
- rlImGui: `118221c8a532501a3c2c236b62950877cbefc2b4`.

The runtime repository carries GPLv3; the inspected dependency notices retain
their separate zlib-style raylib/rlImGui and MIT Dear ImGui terms, including
embedded dependency notices. This is not a blanket relicensing or rights-holder
authorization for God Hand. No third-party source is mirrored in our repository.
The original configuration helper and invented tests are GPL-3.0-only.

All 1,630 tracked source-input files selected by the private qualification are
hashed before and after. Existing source trees, build caches, snapshot libraries,
game inputs and normal executables are not edited. The existing source checkouts
are reused **as source**, not newly fetched or independently bootstrapped here.

## Original, disconnected configuration

[prototype_generic.py](prototype_generic.py), source revision
`46a09e9308818b157e7da723db75772bbe809879`, emits an original generic-only CMake
project from explicitly supplied, prequalified runtime and dependency directories.
It rejects relative/traversal paths and CMake command fragments. The configuration
uses disconnected FetchContent source overrides, no downloads, recompiler,
generated game directory or old `.lib` as a producer input.

Eight invented-data tests include an actual CMake/Ninja build of five invented
empty-library targets. They test configuration plumbing, not the real runtime,
game ABI, compiler equivalence or graphics. The explicit target list is
`ps2_runtime ps2_iop imgui rlImGui raylib`; MSVC output paths are expectations,
not an assertion that a build has succeeded.

The actual configuration retains **RelWithDebInfo**, `/MD` and the pinned
runtime's existing flags. It does not silently select that runtime's different
Release fast-math/AVX2 profile. FFmpeg/SDL input remain disabled as in the parent;
this does not remove or resolve the existing audible/input acceptance limits.

The first preflight stops on 21 differing GLFW build-include paths. It is retained
as a failed strict check, not called an unchanged-command pass. Read-only inspection
finds only CMake install/package metadata in those two build directories, no C/C++
headers or source. After **only that explicitly inspected include-path remap**
and object/PDB output-path exclusion, all 126 selected source/command profiles
match the retained cache. No general include/define/optimization differences are
ignored. Three CMake warnings and 67 compiler warnings remain in the logs:
65 D9025 inline-flag overrides and two C4005 Windows macro redefinitions
(`MAX_PATH`/`APIENTRY`). They are not suppressed or called a warning-free build.

## Actual compilation and link

In a new private build directory, MSVC 19.44.35229.0 compiles **126 translation
units** and five new archives with two jobs. Configure, library build and the
separate native link return zero. The old objects/archives are not producer
inputs to those five library targets. All five archives have newly recorded
identities; byte-identical archives or an explanation of every binary difference
is not claimed.

The link replaces exactly five generic archives in the prior VU-replay capsule.
All 9,843 inventoried parent inputs are preserved; the qualified BOOT/module,
VU and prototype host/IOP/menu continuation objects remain explicit dependencies.
In particular, rebuilding generic IOP does not discard the retained prototype
input-transport continuation or turn it into a new retail feature.

The new private executable is
`9c0e316c83b85bbffab7920f59701f899566f8363567b814c7030cd1a1ae00ba`.
It is **not** adopted by default native07 or explicit `room01-v1`.

The measured old target object/archive footprint is used for a G:-only capacity
review before the new build; no old work is removed or moved. This is not blanket
capacity approval for a new large whole-game compilation.

## New native controls

Two **new** sequential controls use the same finite original Room Jump route,
prepared scratch inputs, AOT1 and requested fields. Only executable and per-case
paths change. Both prospective watchdogs are300seconds: parent0ef exits0 after
**303.938seconds**, and new9c exits0 after **303.907seconds**.
Both actually register five VU callbacks and all five are called. All nine requested
640x480 original PNGs exist, and every same-filename pair is byte-identical.

The actual new menu at1560 and room/Gene/HUD at4501 are directly inspected. The
journal keeps separate before/after build identities and capture times even when
identical original bytes share one download. No crop, normalization or screenshot
of the journal stands in for native pixels. Existing artifacts remain visible.

Elapsed-time watchdogs end on different CSV fields; nine identical samples do not
prove every-frame fidelity, speed or identical whole execution. The bounded logs
have no missing-target or unimplemented-string match; this does not erase earlier
translation diagnostics or prove all instructions. This is not a new physical-key,
normal-mode F1/F2/Warp/no-death or PS2-reference validation.

## Remaining work

The full local suite passes **352 synthetic tests**, with three Windows skips,
in **63.047seconds** after both native controls are terminal. The focused eight
configuration tests also pass. No game-derived data or pixels are CI fixtures.
No owned compiler, generation, suite or emulator overlaps either native GPU run.

This closes the five historical generic-archive producer boundaries for these
qualified sources. It does **not** rebuild the compiler toolchain, freshly fetch
all sources, regenerate/compile every game/module/host input in one new setup, or
provide a complete public prototype installer. Those assembly/source-bootstrap
and new normal-mode acceptance gates remain explicit.

The earlier normal F1/F2, Room01/Warp and no-death/OFF/death results stay scoped to
their exact earlier executables. StrictVU failure, retained BOOT error/warnings,
cloak/interface artifacts, loading differences, original accounting warning,
partial-install/failure recovery and general ABI/lifetime remain open. No new
performance, PS2-reference, hardware, audio, genuine Save/exit/Load or campaign
certificate follows from this source rebuild.

The journal and [aggregate receipt](docs/evidence/prototype-generic-rebuild-2026-11-12.json)
publish only original continuation tooling, reviewed aggregates and selected
unchanged native originals. Discs, ELF, assets, raw maps/dumps, generated game/VU
source, objects, archives, native binaries and cards remain private. Game imagery
is not GPL. The goal remains active; no Rust or delegation is involved.
