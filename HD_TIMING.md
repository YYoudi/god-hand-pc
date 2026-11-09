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

## Observed native controls

All four starts finish at native deadline124 with driver0 and no forced kill.
The two 300-second valid measurements and the timing-off220s control produce
the same unretouched field4741 PNG:
`c0720b6a89b05bed007fa76060029f8db542f69365df6270c4cedafff94428b2`.
The 300-second negative changes one interior byte of the **private source
reference**, not the disc/VRAM/authored image. It reports zero matches and
reproduces the original-assets PNG:
`fd53182e7a2982021e5c5008d2e5dbab4dbd907cf9dfe52edc520c9a5d02315e`.
Shader-error lists are empty; valid and negative inputs remain unchanged.

The first valid measurement overlaps our synthetic suites. It is retained with
that limitation, not silently presented as isolated performance evidence. A
separate later valid repeat starts after those suites are terminal, with no
concurrent owned compiler/unittest job. That is still **not** full-machine,
background-GPU, thermal or clock isolation. The native renderer reports an
NVIDIA GeForce RTX5080; one machine is not a portability/performance result.

These are sums of the **collected periodic windows only**, rounded to0.001ms.
The timings have different scopes and must not be added/subtracted as a frame
budget. Counts differ across processes; rows are not a comparative benchmark.

| Measurement | Calls / windows | Timestamped dispatches | Candidate states / exact matches | Prepare wall ms | Readback wall ms | GPU command interval ms |
| --- | --- | --- | --- | --- | --- | --- |
| Valid300s, synthetic suites overlap | 113408 /443 | 4759 | 48941 /1226 | 11852.337 | 11623.591 | 133.951 |
| Interior-reference negative300s | 113664 /444 | 4742 | 48941 /0 | 11642.697 | 11464.271 | 143.185 |
| Valid300s, owned tests/compiler idle | 114432 /447 | 4834 | 49841 /1277 | 12015.230 | 11829.474 | 139.371 |

The final collected window ends at uptime299195/299286/299295ms respectively;
the trailing partial window is not included. Timing-off has **no timing rows**,
not a measured zero cost. In the later valid repeat the largest observed single
readback wall interval is27.774ms; the largest GPU command interval is2.615ms.
Those maxima need not be from the same call, and are not latency percentiles.

The wall wait is much larger than the timestamped command interval in these
observations. **Inference:** investigate synchronous diagnostic readback before
introducing a persistent match cache. This does not establish how much time a
readback-free implementation would save: queued rendering and CPU scheduling
may simply move the wait elsewhere. No optimized binary, FPS gain or lower-
latency claim has been demonstrated.

The original header is tested with invented times only:178 tests locally and
in a fresh public autocrlf checkout,176pass/two Windows symlink-privilege skips.
Actual query creation/use and the unchanged native image controls are separate
runtime evidence. The first inventory regex was overescaped; its receipt is
retained and an exact tasklist-name/Python-command check is recorded separately.
Known owned test handles were already terminal before the later valid repeat.

Native build/source snapshots, all four original captures, inputs, logs, exact
commands and JSON window summaries remain private under `hd-timing-2026-11-09`.
The installed sources/executables/pointers, prior baseline PDB, personal ISO and
historical Rust WIP are preserved. No new image comparison is manufactured for
this nonvisual change: the fresh captures reproduce the already reviewed bytes.
The [existing checked-HD pair](https://yyoudi.github.io/god-hand-pc/comparisons.html#2026-11-09-checked-hd-workflow)
keeps its original timestamps/revisions; it is not relabeled as this trial.

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
buffer while still classifying every batch. The current original
[host adapter](adapter/hd_runtime.inc) reads those results for counters/logging;
the sampler consumes the GPU match buffer, not a CPU texture-choice decision.
That source finding does not prove a safe optimized implementation: preserve
ordering/binding/error behavior and test actual matched/unmatched rendering,
then measure without promising a gain. This is not implemented here.

True game SaveExitLoad, physical input/audible audio, wider resources/scenes,
filtering, campaign accuracy, HD/controls composition and prototype kernel
support remain open. No FPS unlock, widescreen, modern lighting or multiplayer
result follows from this measurement.
