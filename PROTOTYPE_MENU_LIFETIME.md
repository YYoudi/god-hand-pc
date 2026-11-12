# Investigating the prototype menu's memory warning

12 November 2026. Follow-up to [normal prototype sessions](PROTOTYPE_SOURCE_REPLAY.md).
This is a diagnostic result, **not a cleanup fix or a new retail debug menu**.
The normal native07 workbench and its checked launcher are unchanged.

## What was reproduced

A separate native04 executable opens and closes the original DEBUG OPTION menu
three times. The first two visits change no options. The third requests ON then
OFF before closing. All three closes display the original `memory leak size
0x480` warning and return to the original room. The message is therefore not
dependent on enabling no-death. The final OFF menu original is byte-identical
to the first OFF original; no image is repaired or normalized.

These trials use the original controller-input path with an explicit finite
field-indexed script, including a declared Room Jump Point1 bootstrap. They
are **not another actual-OS F2/mouse or no-death combat test**. The earlier
normal07 F2/mouse, Warp, survival and restored-death observations remain separate.
No attacking or level-completion script, imported save or direct guest flag edit
is used. A physical keyboard is not required for these software-input trials.

## Where the warning comes from

Read-only inspection of the fresh personal prototype ELF locates the literal
and its original menu-close accounting check. The close path invokes the child
destructor, compares an original three-pool accounting sum with its saved
baseline, displays the warning on inequality and subsequently refreshes that
baseline. The inspected generated instruction comments agree with 1,035 original
ELF words across 13 relevant units. This is exposed-source GPL port research,
not recovered source or the historical MIT independent implementation.

Private read-only native observations now show:

- Each option visit returns 12 distinct entry allocations. The actual two menu
  vectors contain exactly those pointers: ten plus two entries.
- Each observed entry header records a 96-unit block, and consecutive entry
  returns reduce the original accounting sum by 96. The entry helper's original
  request is 48 bytes; this is not an invented host allocation.
- During each selected original close scope, the custom pool-release entry is
  observed for the child object, but **not for any of its twelve entry pointers**.
  The destructor increases the accounting sum by 260, leaving a difference of
  1,152 (`0x480`) at each actual comparison.
- The candidate small-vector link total remains 1,600 after every close while
  that accounting loss repeats. A simple one-time vector-cache warm-up does not
  explain the repeated result. Complete links are not proof of free ownership.
- Warning-entry to baseline-refresh observations are 60 guest VSync fields
  apart each time. This is a routine-stage interval, not continuous text
  visibility, wall-clock duration or a PS2 timing claim.

This evidence points to **unreleased option-entry records in the observed native
close path**. It does not establish every possible release path, later lifetime,
memory safety or whether the unmodified prototype under PCSX2/PS2 behaves the
same. No pointer is freed by the observer, no heap flag is guessed, and neither
the warning nor an original instruction is suppressed. Reference reproduction
is the next experiment before treating this as an original-console bug or a
port-specific regression.

## Controls and preserved failures

The first native03 reader hit its 512-event limit because a common epilogue
hook also ran on ordinary menu ticks. Its later lifecycle metrics are missing,
not passing coverage. Both native03 processes still finish normally with 76
original PNGs each; all 73 shared actual-field files are byte-identical. Three
requested captures land on different actual fields. This trial is preserved.

Native04 moves that hook strictly after the actual child store and adds scoped
factory/allocation/release observations without changing original statements.
Both SAME-executable read/no-read control processes finish normally at the
explicit field stop, with 76 PNGs each. The reader records 82 events without
exhaustion; the control body returns before those reads/logs. **75 of 76 common
actual-field originals are byte-identical**. The title image at field850 differs
in 304,035 decoded pixels; it is retained and unexplained. This is not complete
determinism, instrumentation absence or every-frame fidelity.

Native04 SHA-256:
`856d90ed45fd286017c0293de810acaf5fd936b4cd694eed1b534f51a7b190cb`.
It reuses 9,810 fresh-build objects and retained module/generic libraries,
replacing eleven selected objects plus main; fourteen compilations and linking
finish zero. This is a separate diagnostic relink, **not a fresh ISO-only build**.
Runtime checkout remains `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`.
Original host helper source is `e2f8a68518bdbc36ffd9b54c4390dc0fcc4dc95a`;
the private capsule is identified separately by the executable/hash receipt.

Both capsules reject six invalid/unbounded/wrong-profile inputs before creating
runtime output. Earlier preparation failures are retained. All four native
processes are terminal before synthetic tests; no owned compiler/test overlaps
these native runs. Retained native07 inputs, older binaries, discs and four MIT
WIP files are unchanged. No full-machine isolation or performance claim.

The only new public code is an original, game-free bounded opaque-link reader
and invented C++ fixtures. Its complete result means links reached zero, not
deallocation or a successful guest action. Source-stage suite: 281 tests pass,
three Windows symlink skips, 59.156 seconds. Final post-media suite: 281 tests pass, three skips, 59.080 seconds.
Publication checks are recorded in the [aggregate receipt](docs/evidence/prototype-menu-lifetime-2026-11-12.json).

## What remains

The warning is **diagnosed more narrowly, not fixed**. Compare the same empty-menu
sequence with the prototype reference before designing an optional cleanup.
Remaining private BOOT seed/module/VU/generic-source dependencies, fresh full
setup/build acceptance, wider original options, focus/held/repeat, physical
devices, audible audio, genuine Save/exit/Load and campaign coverage stay open.
Prototype observations do not qualify retail addresses or a retail debug menu.

A suspected partial preview was rejected during review: the original files and
decoded pixels prove the OFF images identical, including their left labels.
That unsupported preview interpretation is not published as a game defect.

Selected journal comparisons are unchanged native renderer PNGs with exact
executable, capture-export timestamps and hashes. They show menu/warning/return
states, not PS2 parity. No game input, generated code, raw map, dump, save or
binary is public. Game imagery is not GPL and the owner's publication request
is not rights-holder permission. The full developer-tools goal stays active.
