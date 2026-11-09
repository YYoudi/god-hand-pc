# Measuring the experimental HD matcher

9 November 2026. Separate private host instrumentation of the checked
[hd-v1 workflow](HD_PACKS.md), **not an optimized release or a new installed
variant**. Original, controls-v1, audio-v2 and hd-v1 keep their prior identities.
No cache or sampler change is part of this experiment.

## What is measured

The original public [totals helper](adapter/hd_timing.hpp) is compiled into the
private trial, with invented invariant/overflow/reset tests. The hooks add:

- Steady-clock wall time inside HD preparation, including the existing result
  readback and timing-query retrieval, but excluding the later aggregate log.
- Wall time around the existing `GetBufferSubData` call only. This can wait for
  earlier queued rendering as well as the classifier; it is **not** an isolated
  classifier-cost measurement or a removable amount of frame time.
- Two GL timestamps around classifier dispatch and its barrier, read after the
  existing synchronous result readback. No extra `glFinish`. This is a command-
  stream interval, not shader-busy time or CPU latency. Timestamp units are
  nanoseconds, not a claim of nanosecond timer resolution; see the primary
  [Khronos timer-query specification](https://github.com/KhronosGroup/OpenGL-Registry/blob/main/extensions/ARB/ARB_timer_query.txt).
- Counts of preparation calls, states, CPU-eligible candidates, exact matches
  and timestamped dispatches. Each periodic window covers256 calls. A trailing
  partial window may be missing: native deadline shutdown did not reliably call
  the backend destructor in earlier runs. No fabricated final totals.

Timers, query commands, aggregation and logs perturb the process. A timing-off
run is an image/behavior control on the same trial binary, **not** an
uninstrumented FPS benchmark. The processes have different wall deadlines and
can complete different numbers of frames/batches. Do not infer a speedup from
their duration, CPU/GPU scope difference or the totals below.

## Reproduction and native provenance

The checked public installer is unchanged. This is a separately retained private
experiment over that host integration, using the existing private generated
inputs/object cache, not fresh game generation. Only original host hooks and the
public arithmetic helper are changed; no generated guest functions/instructions,
disc data, camera, internal scale or authored image are edited.

Clean public helper tooling: `f156b00947886ef6909ec9ac6a97d768fc8e62dc`.
Private native source: `2a2bb9180e6f7a35ba12e6c49cf68730a7e9ed40`.
Executable SHA-256:
`7d71ba86ab3923e8bec21e4c2ea69a660ab46294d696cf72e55aeb073fd2790b`.
Pinned upstream remains `14e956a1274332440273845fbab2c1f1e30c4a5a`.
Configure/build return0 using the existing Windows/MSVC14.44.35207 toolchain.
The first private build failed on a destructor-scope API name collision; that
source, log and outputs remain preserved. The correction changes that call,
not warnings or game behavior. All four installed variants and baseline PDB
bytes were restored/verified before starting the native controls.

Native runs use `godhand.exe --iso <personal-USA-ISO> --headless --time-limit N`,
with isolated scratch controls/cards, muted audio, captures and only the retained
title/start/pause script:
`1800v:start:20,2100v:cross:20,2400v:cross:20,4200v:start:20,4800v:start:20`.
`GODHAND_PC_HD_TIMING=1` is a **private diagnostic hook**, not a supported flag
in the installed public hd-v1 binary/launcher. The private build source,
commands, native logs and receipts remain under the local ignored
`hd-timing-2026-11-09` workspace. Do not mistake a public totals header for a
public profiling installer.

## Observations

Pending terminal native controls; no measured improvement or cache acceptance
is claimed by this document's initial implementation revision.

## Why not cache by texture address or epoch yet?

This is a source-backed dependency finding, **not** completed native cache-
invalidation validation. In the pinned primary
[GS backend](https://github.com/LasVola/godhand-recomp/blob/14e956a1274332440273845fbab2c1f1e30c4a5a/runtime/ps2xRuntime/src/lib/gs/gpu/gs_gpu_backend.cpp),
`resetBatch` reuses epoch0, `addState` records a batch-local epoch/CLUT slot,
copy-on-write remaps texture pages, and transfers/CLUT dispatches update GPU
storage. The primary
[sampler](https://github.com/LasVola/godhand-recomp/blob/14e956a1274332440273845fbab2c1f1e30c4a5a/runtime/ps2xRuntime/src/lib/gs/gpu/gs_gpu_shaders.cpp)
also resolves epoch page maps, CLUT and high-resolution planes. A repeated
address/state/epoch is not a persistent decoded-content identity. Identical
content aliases are another distinct ownership problem.

Before a persistent match cache, prove all relevant transfer, palette, copy,
render-target, reset/load and plane invalidation paths with invented mutation
controls and actual unchanged/reference-negative rendering. A more local next
experiment is to decouple the CPU diagnostic result readback from the GPU match
buffer while still classifying every batch. That needs its own native controls;
it is not implemented or a promised performance gain here.

True game SaveExitLoad, physical input/audible audio, wider resources/scenes,
filtering, campaign accuracy, HD/controls composition and prototype kernel
support remain open. No FPS unlock, widescreen, modern lighting or multiplayer
result follows from this measurement.
