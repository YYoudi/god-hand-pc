# Point1 reference and a scheduler lifetime defect

13 November 2026. New reference and diagnostic results. No corrected game build
or retail regression result is claimed. The existing native executable remains
unchanged; the candidate below is a private synthetic experiment, not adopted.

## An actual reference for the retained ground artifact

PCSX2 v2.8.2, official source fd9d310ccbb6b8b62c976da8886a3c8fd3a10ff3,
uses the same untouched prototype and isolated configuration as
PROTOTYPE_EMULATOR_REFERENCE.md. The private Room Jump snapshot is our own,
not a game save or downloaded state. The MTVU snapshot warning remains.

From that selector snapshot, Down100, Down200, Right300 and Circle400 target
Stage1/Room00/Point1. The first run ends on Olivia's introduction, not the desired
gameplay reference. A transition warning containing “memory leak” is retained;
its numeric value and cause are not qualified, nor equated with the native warning.
That process closes normally after200.188s within its240s operator budget.

A separate prospective recording adds Start1500..1511 and ends at4000.
Actual2627,3273 and4000 show Gene/HUD beside the green wall. F8 is requested
while playback is running; the unchanged827x620 display PNG is exported at
02:23:26.828393 UTC. Its exact guest frame is unknown. Normal exit0/203.625s,
within240s. No player attacks, movement, health flags or level-completion loop.

A NEW run of the unchanged native e677f789 executable records GS operations
around4500. It exits0 after303.734s against a300s native watchdog; all six sampled
PNG originals equal the retained same-filename originals byte-for-byte.
The gallery uses this run's actual4501 original, not a newly improved renderer.

Both images show the green wall and Gene. A lower-ground ghost-like shape is
visible in native output. “Detached cloak” remains an observational description,
not a diagnosed cloth bug. Different pose, health, capture scale and game time
prevent a pixel-error or same-frame comparison. No image is resized or corrected.

## GS-only investigation: no GPU fix demonstrated

The pinned generic factory defaults to CPU GS rasterization unless overridden;
the upstream retail main explicitly enables GPU, whereas the inspected prototype
host does not. This is source evidence, not by itself a logged backend-selection
certificate. OpenGL presentation does not identify the GS rasterizer.

The private recording has4959 operations, including3819 draws, initial state4501
and End4503, but NO Field operation. The upstream comparison observer stops at
End before presenting: it could otherwise report success with zero compared
frames. A private observer correction compares End and refuses zero comparisons;
it is not a game/runtime correction. Original recording bytes remain unchanged.

- Standard CPU replay: exit0, final recorded VRAM byte-identical.
- Standard GPU replay: exit1,55781 differing VRAM bytes at End.
- Corrected paired observer: one actual512x448 presentation, zero differing RGB
  pixels but44221 differing VRAM bytes AFTER presentation; exit1.

These are different checkpoints, not contradictory byte counts. Both displayed
replays retain the ground artifact and may present an inherited initial buffer.
This short recording cannot identify its cause or establish GPU rendering parity,
optimization, native frame rate or a safe default switch. Raw GS/state data and
offline replay binaries stay private. A CPU rounding self-check also passes;
it is not game-fidelity evidence.

## New startup crash, then an actual generic-runtime counterexample

A separate longer-recording trial crashes BEFORE its recording window: field162,
8.140s, access violation0xC0000005, no PNG and an empty recording. Last module-clear
messages are chronology, not proof of the cause. The original executable, ELF,
disc and controls hashes are unchanged. This failed trial is not a longer trace.

The existing Windows crash dump is preserved privately. Local matching PDB
analysis identifies EeScheduler::run's dispatcher-transfer catch at line699,
saveSharedVu0Random(context). Its native instruction reads the saved context's
VU0 random field through an invalid pointer. This is ordinary local DbgHelp/dump
analysis, not REA Evidence. No network symbol server or system setting is changed.
The dump does not reconstruct the exact earlier context-invalidation call path.

An original synthetic harness links the unchanged pinned GPL generic runtime,
without a disc, ELF, generated game code, window, GPU or audio. Its own allocator
decommits freed large allocations so stale reads cannot silently survive heap
reuse. Actual scheduler APIs execute invented main/child/observer functions.

| Actual synthetic case | Unchanged runtime | Private candidate v2 |
| --- | --- | --- |
| Guarded exit, thread record retained | exit0 | exit0 |
| Guarded exit and deletion | access violation | exit0 |
| Ordinary allocator, exit and deletion | exit0, does NOT disprove stale read | exit0 |
| Guarded nested invocation growth | access violation | exit0 |
| Guarded nested invocation-sequence growth | access violation | exit0 |

The first candidate fixes only exit retirement and still FAILS nested growth;
that failed candidate and the first fixture/build failures remain preserved.
Candidate v2 saves shared VU0 random state BEFORE exit/invocation mutation and
marks the dispatched context retired, avoiding its later stale read in the catch.
Each passing final case also checks all four lanes of an invented random value,
then a separate ordinary dispatcher transfer with another value. This checks that
the retirement marker does not suppress the next live context's state update.
No guest-ready status, unknown instruction, return stub or game flag is forced.

This proves concrete lifetime defects in the generic scheduler, and a candidate
passes these synthetic controls. It does NOT prove which path caused the earlier
game crash, all context-lifetime correctness, or a corrected native game.

## Reproduction and next acceptance

The exact frozen runtime source is LasVola1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a.
Local compilation uses MSVC14.44.35207, one new observer/test object and reused
hash-pinned generic libraries; candidate trials additionally compile ONE copied
scheduler unit. Original sources/libraries and native executables are not patched.
There is no CMake configure, guest generation or full-game compilation here.
Structured aggregate results and hashes: scenarios/prototype-point1-runtime-v1.json.
Raw dumps, maps, recordings, private game inputs and generated code are not public.

1. Retain and review the candidate, including other context-retirement paths.
2. Integrate it in an isolated build variant only after the native link capacity
   preflight passes. Current G: space is roughly4GiB, below the whole-build11GiB
   and configure8GiB floors; the3GiB small-probe gate is NOT a waiver.
3. Reproduce prototype startup/room transitions and exercise retail native
   regression controls. Keep the old executables and failures for rollback.
4. Only after those actual results, decide adoption/upstream contribution and
   return to a longer GS window for the still-unresolved ground artifact.

The common-runtime milestone remains IN PROGRESS, not complete. Physical input,
audible audio, genuine game Save/exit/Load and human campaign validation remain
separate gates. Selected original game imagery has separate rights; the owner's
publication request is not rights-holder permission. No game is distributed.
