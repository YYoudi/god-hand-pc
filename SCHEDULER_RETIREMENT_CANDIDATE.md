# Experimental scheduler retirement candidate

13 November 2026. This makes the previous synthetic experiment reproducible
from public original tooling. It does **not** install a correction into the game.
Original and current launch profiles, executables and F1/F2 remain unchanged.

## Published source

- `scheduler_retirement_candidate.py`: original, hash-gated transformation of
  one **generic GPL runtime** source file, not generated game code.
- `tests/probes/scheduler_context_lifetime.cpp`: the exact original synthetic
  probe already tested privately, SHA-256
  `b8071f03f4558b956a8141f290126546a7ce318b20634171b817243f073c459a`.
  Invented functions/addresses only; no disc, ELF, game assets or source needed.
- `tests/test_scheduler_retirement_candidate.py`: thirteen invented-data tests
  for guarded edits, source/output fingerprints, explicit CRLF bytes, private
  output confinement and no-overwrite behavior. No third-party/game fixture.

The pinned `EeScheduler.cpp` is byte-identical in the inspected prototype
runtime checkout1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a and retail
checkout193076584e277c95644dcbbb4a6922c3a59ca2b8. Both remain clean.
This is actual common source identity, not similar-engine inference or proof
that either game now runs with the candidate. No game addresses are transferred.

Expected source SHA-256:
`80297ca782b38abfefc3a1e53059dab8b6e05dcf3b2d136266f13cf65b88da4f`.
Candidate SHA-256:
`eef04f79134fc139de2876274b028dbaee88e25496bb6707ff22eb7329b197a7`.
These fingerprints identify the inspected Windows/CRLF bytes, not every checkout
configuration of those Git revisions. Unknown inputs are refused, not converted
to evade the source gate. Output CRLF is explicit on every host.

## Generate a separate candidate

From the public checkout, with Python and the existing pinned runtime available:

```powershell
New-Item -ItemType Directory .local\scheduler-candidate
python scheduler_retirement_candidate.py `
  --source "$Runtime\runtime\ps2xRuntime\src\lib\Kernel\EeScheduler.cpp" `
  --output .local\scheduler-candidate\EeScheduler.cpp
```

`$Runtime` is a locally inspected checkout, not supplied game code. The output
directory must already exist; output must be a NEW `.cpp` under this checkout's
ignored `.local`. The source, existing output, runtime libraries and launcher
profiles are never overwritten. This command does not compile or adopt anything.
Do not stage the generated private runtime copy or turn this into a game-source
distribution step. The upstream runtime's GPL attribution/license still apply.

## Synthetic native build and actual results

The exact public probe and exact public-command output were newly compiled with
MSVC14.44.35207 x64, `/O2 /EHsc /GL /MD /std:c++20`, and linked against the
previously pinned generic `ps2_runtime`, `ps2_iop`, `raylib` and GS-reference
libraries. Candidate builds put the new scheduler object before those libraries.
Baseline builds omit that object. No generated EE/VU/game object is linked.

Use the same frozen headers, compiler definitions and generic-library build:
runtime/include, runtime/src/lib/Kernel, IOP/include, raylib/src and its GLFW
include directory. Definitions are WIN32, _WINDOWS, GRAPHICS_API_OPENGL_33,
PLATFORM_DESKTOP, PS2X_ENABLE_IOP_RPC_TRACE=1 and PS2_RUNTIME_LOGS=1.
The local link uses console/x64, embedded manifest, LTCG, no incremental link,
and the usual Windows SDK libraries: glu32, winmm, opengl32, gdi32, kernel32,
user32, winspool, shell32, ole32, oleaut32, uuid, comdlg32 and advapi32.
This describes the evaluated existing-library setup, not a fresh-build installer.

With the resulting standalone probe, execute separately:

```powershell
.\probe.exe guarded keep
.\probe.exe guarded delete
.\probe.exe ordinary delete
.\probe.exe guarded keep nested
.\probe.exe guarded keep sequence
```

The earlier unchanged-runtime controls crash on guarded deletion, nested growth
and sequence growth. The NEW build from public sources returns0 in all five
cases. Its surviving observer checks all four lanes of shared VU0 random state,
then another ordinary dispatcher transfer's state. The allocator deliberately
decommits freed large allocations so stale reads cannot hide behind heap reuse;
this is diagnostic instrumentation, not a production allocator or game patch.
All compilation/link steps return0. The thirteen Python tests pass; the full
Windows suite passes526 tests with4 skips in74.069s, after the helper terminates.

The first recipe command refused a mismatched output fingerprint because its
LF serialization differed from the actual CRLF candidate. It wrote no output.
The corrected explicit-byte recipe reproduces the candidate exactly. A separate
private build-driver path contained an accidental tab and failed before compile;
the new corrected trial is recorded separately. Neither is a passing relabel.

## Reviewed boundary and outstanding native acceptance

The candidate captures shared random state before current-thread retirement or
invocation-vector growth, then avoids rereading that retired dispatch context
while unwinding. The marker resets before the next actual dispatch. The first
exit-only candidate still failed nesting; it remains preserved, not adopted.

Other inspected mutations occur outside the guest call (including paths with
an immediate loop continuation before reusing a selected context), or affect
non-running thread records. Snapshot servicing is called at the outer loop
boundary. This source review is not an exhaustive lifetime/ABI proof,
and does not reconstruct the earlier game's precise invalidation path. See
PROTOTYPE_POINT1_RUNTIME.md for the preserved startup crash and visual findings.

The initial private native link preflight counted9842 resolved input files/682,643,584
bytes, plus24 unresolved SDK-library tokens. Preserving a candidate executable,
PDB and map gives a conservative budget LOWER BOUND of5,442,950,056 bytes under
the four-times-input/output-plus1GiB policy, before resolving those SDK tokens.
At that check G: had roughly4GiB free. No native game link was attempted. No diagnostics are
removed, originals deleted, or full-build/configure capacity gates weakened.

Next: complete native dependency/capacity preflight when space permits, integrate
in an isolated variant, and run prototype startup/transitions AND retail native
regression controls. Only those results can support adoption/upstream submission.
The ground artifact, full fidelity, game Save/Load, physical input, audible audio
and human campaign gates remain open. The previous Point1 comparison is retained;
this tooling step produces no new game screenshot or corrected before/after.

## Follow-up: the unchanged native game exercises the lifetime path

Later on13 November, two NEW bounded debugger runs use the same frozen e677f789
native executable, ELF, disc and scratch-controls identities. Neither contains
the candidate. Existing GDB18.1r3 uses native-runtime-only software breakpoints;
no game flags, register values, return values or on-disk program bytes are changed.
Debugger timing/heap perturbation prevents treating these runs as ordinary play
or as a deterministic reproduction of the earlier access violation.

The first diagnostic exits normally: debugger0/native0 after49.015s with the
existing45s native watchdog. It records two invokeCurrent entries, four
exitCurrent entries and six dispatcher-catch reads. A separately specified
second diagnostic records the actual before/after context relation, rather than
inferring it from those counts. It exits debugger0/native0 after49.031s.
Those wall times include debugger startup and native cleanup, not guaranteed
45s deadlines. No kills, timeout restarts, compiler, emulator or replay overlap.

In the paired run, all FOUR exit calls have the delete argument set. At each
subsequent catch, the original read uses the SAME saved context pointer as the
entry observation, while the scheduler's current-thread identifier is zero.
The inspected original exit implementation retires and deletes that non-main
thread before throwing the dispatcher transfer. Thus the native game actually
exercises the retirement/read pattern targeted by the synthetic candidate.
Readability of the freed storage under this debugger is not object lifetime.
The two invokeCurrent/unchanged-main-context pairs remain separate controls.
Six catch observations, no debugger errors or actual access violations.

This is evidence from the ORIGINAL native game, not candidate-game acceptance.
It does not prove which earlier invalidation caused the retained crash, nested
growth in this game run, candidate correctness on retail, or full scheduler ABI
safety. No room, combat, menu, frame-fidelity or performance result is inferred.
No new game screenshot is produced; the earlier Point1 images stay unchanged.

The preserved dump was also unwound offline through ten frames using matching
local images/PDB and serialized memory callbacks. The scheduler heap fields
needed to distinguish the earlier invalidation are NOT in that dump; missing
bytes are unknown, not zero. See Microsoft's
[StackWalk64 reference](https://learn.microsoft.com/en-us/windows/win32/api/dbghelp/nf-dbghelp-stackwalk64)
for the offline-callback interface. This is ordinary local dump/debugger work,
not REA Evidence; no network symbols or system settings are changed.

The first GDB driver refused an unsupported startup-with-shell option BEFORE
launching a native process; that failure remains. A first text-log audit also
mistook interleaved field-number digits for a frame endpoint. Its maxima are
rejected, not heuristically clamped: endpoint frame is UNKNOWN. The paired
lifecycle evidence is instead the debugger's serialized records. Raw stacks,
addresses, dumps, registers and recordings stay private; only aggregates publish.

The later dependency inspection resolves all24 SDK tokens:9866 inputs,
703,355,692 bytes, conservative reserve5,525,798,488 bytes, versus4,077,285,376
free at that check. This still FAILS the native link capacity gate. No native
game link or adoption is attempted, and the separate whole-build/configure
floors remain. Next acceptance is an isolated corrected build with actual
prototype AND retail regression, not another source-helper or menu-polish pass.
