# Code-backed BOOT entries and a new native source capsule

12 November 2026. Follow-up to [the direct-import entry replay](PROTOTYPE_ENTRY_REPLAY.md).
This is an experimental source/build regression, not a replacement for normal07,
complete prototype setup or a validated retail debug backend. The goal is active.

## Deriving entries without the historical seed CSV

The read-only local-use recognizer scans the fresh prototype ELF's 659,964
instruction words and fresh discovery boundaries. It terminates tracked regions
at known direct branch targets, fresh entries, control transfers, delay slots
and unsupported instructions. It does not assume a callee preserves registers,
interpret an unknown instruction as NOP, or edit original game code.

This is limited R5900 low-word metadata analysis, **not general CFG/ISA
verification or execution**. The pinned official [PCSX2 opcode
tables](https://github.com/PCSX2/pcsx2/blob/v2.8.2/pcsx2/R5900OpcodeTables.cpp)
and [interpreter](https://github.com/PCSX2/pcsx2/blob/v2.8.2/pcsx2/R5900OpcodeImpl.cpp)
were consulted privately for the EE profile; a generic MIPS64 decoder misidentifies
some EE instructions. No third-party source is vendored here.

The corrected scan finds 17 local uses across five code-backed pointer prefixes:
indexed loads reaching JALR, and indexed pointer loads stored by a candidate
callback-construction path. An initial alignment check was too strict: a byte-offset mask
already cleared the low two bits even with scale1. That first rejected scan is
retained; this was a host analysis issue, not a game fix.

Original [prototype_table_candidates.py](prototype_table_candidates.py), revision
`7d3ce40adbd95dd0ff09965722b555ee94c62566`, unions all supplied entry fences.
Overlapping subarrays must not independently propose contradictory longer bodies.
Its eight invented-data tests contain no game symbols, addresses or bytes. The
ELF-decoding/integration experiment remains private research code, **not an
already published ISO-only generator**.

There are 21 unique indirect candidates, including the 18 historical entries and
three new ones. Each candidate span ends with a terminal JR RA/delay pair,
optionally one padding NOP, and has no decoded non-call transfer outside its span.
These are bounded checks, **not complete function/ABI, index-domain, callback-
alias, memory-immutability or overlay-lifetime proof**. A finite pointer prefix
does not prove every masked index valid or recover an entire runtime table.
The historical map is a later comparison oracle, never an entry/bound input to
the new selector. The 18 old starts/ends agree; new entries do not inherit old tests.

Combined with six fresh direct-import ranges, the new recipe consumes 27 fresh
ranges with **no historical seed CSV input**. The first generation exits0 but
changes 12 host-generated MPEG label spellings by hex-letter case: 15 added,
12 removed and three changed files. It is retained, not called byte-identical
or repaired by renaming outputs. A separate second generation applies our stable
host-label convention upfront. It produces **9,821 files**: 9,819 C++ units and
two headers. Relative to the old 9,818 files, 9,815 are byte-identical, three are
added and three change. **One generation error and 1,450 warnings remain**,
unchanged and visible. No guessed opcode, NOP, stub or warning suppression.
Stable host labels are ours, not recovered game-source symbols.

## What is actually linked

The new private capsule compiles five generated BOOT units and links, preserving
the old variants. The old split owner's original instruction-comment coverage
equals the union of its new pieces: **70 original PC/word checks**, matching the
ELF. The private generated-header delta is only three additional forward declarations.
All other generated files associated with reused objects are equality-checked.

This is an **incremental link**, not a fresh full source build: 9,821 object
inputs, the frozen07 host/main/file guard and selected module/VU/generic libraries
are reused; two old BOOT objects are replaced by five. Executable SHA-256:
`e1115bb6e58ed1a5cbd6a70324c15faa3ab5a4e4b3b17c138da0987d69a43f25`.
The normal launcher still adopts earlier07; it does not silently switch.

## Actual native evidence, with the failed capture gate retained

Both fresh native processes exit0 under the declared 330-second diagnostic
policy, after 333.703 and 335.843 wall seconds including startup/shutdown.
The **first paired attempt is NOT a full passing visual control**:

- Baseline07 reaches logged field8121 but has **zero PNGs**. All 23 exports fail
  because the new output directory was not prepared. The actual FILEIO failures
  remain; creating the directory late does not recover or relabel those images.
- A host-only watcher prepares the next fresh27 output directory before its first
  successful export. This changes host output preparation, not guest state.
  The new case produces **21 actual PNGs**, with no export failure. Requested1560
  arrives as actual filename1561. Last requested7301/7401 are not captured before
  stopping; last logged field is7265. Neither process is killed or restarted.

This is not a complete pair, image-parity, speedup or slowdown attribution. No
owned compiler/synthetic suite overlaps the native runs; whole-machine/GPU
isolation is not claimed. Original discs and scratch controls remain unchanged.

Directly inspected unchanged renderer originals from the **new executable** show
the original main menu after shared F2 input, the selected Point1 room/Gene/HUD,
the original warning after an empty option visit, PL NO DEATH ON, restored OFF,
and normal room/HUD return at7100. The two empty-visit warning originals are
byte-identical. OFF before/after is also exact; a partial-looking tool preview
is rejected using the original/decoded bytes, not reported as a game defect.

These are finite **software controller/shared-handler diagnostics**, not new
actual-key F1/F2/mouse or survival/refill/restored-death tests. The existing scoped
07 effects proof remains separate; the three new indirect candidates have no
observed execution coverage. The original0x480 warning is **not fixed** and its
prototype-reference comparison remains open. No arbitrary combat or imported save.

Source suite: **297 synthetic tests**, three Windows symlink skips, 65.209s,
all non-skipped tests pass. A separate final publication run is retained locally.
The [aggregate receipt](docs/evidence/prototype-indirect-replay-2026-11-12.json)
and selected journal originals retain exact build, export-time, hash and scope.

## Remaining boundaries

Fresh BOOT-entry provenance is not full prototype setup: selected module/VU and
generic-source dependencies, a fresh full build, broader input/menu coverage and
the reference warning comparison remain open. A new correctly prepared longer
native control is still needed to close the missed capture endpoints. No new
hardware/audio, game Save/exit/Load, campaign fidelity or retail menu acceptance.
The strict VU1 failure and visible rendering artifacts are not fixed.

Public content is original GPL host models, invented fixtures, aggregate findings
and selected unchanged native screenshots only. No game, ELF, raw map, dump,
save, generated game C++, extracted asset, third-party checkout or executable is
distributed. Game imagery has separate rights, not GPL coverage. No Rust/delegation.
