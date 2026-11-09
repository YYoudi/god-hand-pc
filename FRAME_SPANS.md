# Observed-field-span profiling

10 November 2026, initial experiment contract. This is diagnostic tooling, not
a performance result, frame-rate unlock or gameplay-frame counter.

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

## Planned native check, not yet a result

Use the already installed explicit HD v1 and GPU v2 binaries, with the same
private original-authored 512x512 diagnostic pack and title/start/pause script.
First run one 300-second HD-v1 pilot, then, only if its schema/bounds/images
support the contract, a v1/v2/v2/v1 block with identical initial shader-cache
snapshots. Fresh scratch user data, headless/muted, no attacks or level beating.
Capture fields 4400 and 4800, outside the requested 4500..4740 measured span.
Do not run owned compilers/tests concurrently; no whole-machine/GPU/thermal
isolation is claimed. Keep raw CSV, reference-bearing pack envelopes, screenshots,
saves and native binaries private. No new generated game code or native relink.

Record every trial, including failed boundaries or images, before interpreting
any measured difference. One block cannot establish general performance,
backend/driver coverage or campaign fidelity. Earlier distinct scoped matcher
measurements remain in [HD_TIMING.md](HD_TIMING.md); sampled GPU-v2 functional
controls remain in [HD_GPU_RESULTS.md](HD_GPU_RESULTS.md).
