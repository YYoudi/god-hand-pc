# Observed-field-span profiling

10 November 2026. One pilot and one four-run block are now terminal. This is
diagnostic tooling and a scoped measurement, not a frame-rate unlock or
gameplay-frame counter. **This block does not establish a reliable speedup.**

The pinned LasVola host runtime already writes `PS2X_FRAME_TIMES` CSV from its
native present loop (`ps2_runtime.cpp`, `Ps2Runtime::run`). No native rebuild is
needed. The existing file contains steady-clock time, an EE field sampled after
the host swap, source sequence/revision, and host interval/submit/swap durations.
Host presents can repeat fields; a shared display source can differ from the EE
field. Submit includes presentation and diagnostic screenshot work, not just
the HD matcher. These are wall intervals, not CPU-busy or isolated GPU timings.
The native text timestamps have limited precision. Logging also has overhead.

Original GPL `frame_spans.py` reads this exact schema with file/row budgets,
finite nonnegative timings, unsigned bounds, flag consistency and monotonic
field/time checks. It rejects unknown schemas and incomplete trailing lines;
it never rewrites or silently trims a private measurement file. Tests use only
invented numbers, not game CSV, hashes, assets or saves.

```powershell
python frame_spans.py "G:\private\presents.csv" --from-field 4500 --to-field 4740
```

Selection uses the first row crossing each requested bound and reports the
**actual** bounds and overshoots. Comparisons require identical actual bounds,
scenario, settings, input and verification images. Present counts are not game
FPS, and mismatched workloads must not be normalized away.

## Native protocol actually executed

Clean public tooling `281aefb39d13a94e7370d8986142b9dac47bca44` analyzed unchanged
installed HD v1 and GPU v2,
not new measurement binaries. The hook was audited in baseline host source
`193076584e277c95644dcbbb4a6922c3a59ca2b8`; its runtime is tracked in that tree,
not an unidentified separately updated submodule. No game instructions or
generated functions were inspected, and nothing was relinked or regenerated.

| Variant | Private native source revision | Executable SHA-256 |
| --- | --- | --- |
| HD v1 | `8dec4950b15f7fffe5e97b580dcc10fb758c8503` | `f17d67d6fc5efc1796176da3bb862dd7e3482f9361650d1f695005f6de3e809e` |
| GPU v2 | `953ea26336227e92455dbea1d4d791dd18b5159c` | `5d27048f688e0264123d733826d8399a4e619af75852fe267100c92409001b02` |

- Personal retail USA ISO verified read-only before/after; exact profile in
  [upstream.json](upstream.json). Fresh scratch cards, quick-state path and
  controls preferences each run; no imported save or runtime snapshot.
- Same private reference-bearing HD envelope, SHA-256
  `d39f6e2b0e1ebe052f59df44afe394498a97fe5d9bd5ea5ae688097a4baed5cd`.
  Original-authored 512x512 grid over one 128x128 ground source; original game
  reference pixels in this envelope stay private. This is not Original artwork
  versus more expensive HD artwork: both variants use the same replacement.
- Both `godhand.ini` files are identical, SHA-256
  `68d601196e0094017c26b49a2a3302bb197d65623e3467d4b1cbafd3a51f0258`.
  Native renderer, internal-resolution setting 3, headless/muted, FPS overlay off.
  Inherited `GODHAND_`/`PS2X_` variables cleared by the existing public helper.
  Controls self-tests/probes and dumps disabled; no forced callback or timing
  queries. This direct diagnostic route is **not a new public launch flag**.
- Native command: `<selected godhand.exe> --iso <personal ISO> --headless
  --time-limit 300`. Explicit `PS2X_FRAME_TIMES`, `PS2X_GS_SHADER_CACHE_DIR`,
  screenshot/output/user-data paths and the same valid HD file/hash/profile.
  Pad script: `1800v:start:20,2100v:cross:20,2400v:cross:20,4200v:start:20,4800v:start:20`.
  Title/start/pause only, no attacks or autonomous level completion. This is a
  first-fight diagnostic with Start inputs bracketing the window, not a verified
  active-combat throughput test or proof that the game accepted every input.
- Requested screenshot fields 4400/4800 produce actual 4401/4801. Both are outside
  requested timing 4500..4740, whose actual crossings are 4501..4741 throughout.
  No screenshot is requested inside the measured interval.
- One cold HD-v1 pilot primes a 56-file, 21,759,290-byte private shader-cache seed.
  Then sequential **v1 / v2 / v2 / v1**, each starting from a separate identical
  snapshot of that seed. All 55 compiled `.glbin` files stay unchanged afterwards;
  only the runtime's `hw_keys.txt` index changes. This does not control the
  driver's private caches, clocks, thermal state or OS file cache.
- Runtime reports NVIDIA RTX 5080, OpenGL 3.3.0 NVIDIA 621.01. No owned compiler or
  test suite runs during the block, but other desktop activity is not isolated.
  Native 124 at all five normal deadlines, observers 0, no forced termination,
  missing boundaries, truncated CSV or shader errors.

Private receipts and raw originals: `G:\God-Hand-PC\.local\present-field-spans-2026-11-10\`.
The block ran 00:02:04..00:22:06 UTC, 10 November 2026 (01:02..01:22 Europe/Paris).
The analyzer is public; the native driver/CSV, cache binaries, scratch user data
and screenshots are deliberately not uploaded or supplied to CI.

## Observed results

Every row below covers **actual 4501..4741**, 121 distinct observed field values.
Repeated host presents explain why interval counts differ. All selected rows
use the copy path (`shared=0`), with no valid per-present image hashes: CSV
metadata alone cannot prove identical rendered content throughout the window.

| Order | Variant | Field-span wall seconds | Host-present intervals | Submit wall sum ms | Swap wall sum ms |
| --- | --- | ---: | ---: | ---: | ---: |
| Pilot, cold/priming only | HD v1 | 30.723 | 711 | 3714.638 | 885.596 |
| A1 | HD v1 | 29.871 | 697 | 4110.036 | 671.320 |
| B1 | GPU v2 | 29.678 | 703 | 4002.653 | 385.260 |
| B2 | GPU v2 | 29.792 | 708 | 3792.352 | 474.832 |
| A2 | HD v1 | 33.810 | 764 | 4186.316 | 631.275 |

Native text rounding means these sums and differences need not agree exactly;
do not infer sub-millisecond precision. Submit/swap exclude other work and waits
in the host loop. They are neither a CPU/GPU cost breakdown nor time that can be
subtracted to predict game FPS.

Both outside-window PNG originals are byte-identical across the pilot and all
four block runs, including actual field names and sizes:

- field 4401, 714,732 bytes, SHA-256
  `407d7bcf4f7638fe10f09d61d5db5dddd2c6683f731423ebb95440d529c4343d`;
- field 4801, 761,377 bytes, SHA-256
  `c1a64e2c18348880e10b0eebd1523423025cc630bc0da63ef5ad906b9593de00`.

These are endpoint controls, **not every-frame identity or overall fidelity**.
V1 logs full-source matches; GPU v2 logs submitted work/counts-unread, not zero
matches or inferred visible application. No new public picture pair is invented
for this nonvisual measurement; older approved originals/provenance are untouched.

## Decision and remaining work

The measured span and endpoint checks now pass, but **no dependable performance
benefit is established**. The two GPU-v2 observations are close to the first
v1 observation; variation between the two v1 observations is much larger than
that early difference. Do not hide A2, choose only a favorable pair, convert
present counts to game FPS, subtract the older readback/GPU scopes, or advertise
a percentage improvement. Two observations per variant in one sequential block
cannot establish statistical significance or isolate the classifier change.
Different logging/binaries, unisolated system/driver scheduling and a scripted
single-scene workload are additional limits.

Keep GPU v2 explicit and Original/no-version HD defaults unchanged. Do not add
a persistent cache or change game timing to chase this result. Wider scenes,
drivers/backend/state and invalidation tests, and separately designed repeated
performance experiments remain open. The full PC goal, true SaveExitLoad,
physical input/audible audio, HD+controls composition, campaign fidelity,
prototype kernel, widescreen/FPS/lighting and multiplayer are not complete.

Earlier **different scoped** matcher measurements remain in
[HD_TIMING.md](HD_TIMING.md); sampled GPU-v2 functional/build controls remain in
[HD_GPU_RESULTS.md](HD_GPU_RESULTS.md). This report supersedes neither result
and makes no new installed-native or engine feature claim.
