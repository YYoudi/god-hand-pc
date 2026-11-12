# Prototype Room Jump: a same-process return

12 November 2026. Follow-up to [the additional Room01 scene](PROTOTYPE_ROOM01.md).
This is new native evidence on the **unchanged** combined executable
`4acf41e7d0495dbb883629dc9a12b15dc7e0b33b6bee10ea6a97bbeef8f047f7`,
not a new game translation, promoted launcher or completed prototype port.
Its attachment tooling remains revision
`97b774547230976d1536f7fe32d3f27cf3271c48`; qualified private inputs and reused
objects/libraries are exactly those described in the preceding report.

## What was actually exercised

A fresh, hidden, muted diagnostic session first selects the original
**Stage1 / Room01 / Point0** route. The actual interior, Gene, enemies and HUD
appear. The original in-scene L2/R3 chord reopens the debug menu; Room Jump
initially displays those same values, rather than assumed defaults.

Finite normal-controller requests change Room01 to Room00, keeping Stage1 and
Point0. The original Room00 exterior introduction then renders. One Start skips
that introduction. An explicit diagnostic request for the shared F2 handler is
submitted while the loading logo is still visible; the later original five-choice
menu proves delivery. It is **not an actual Windows F2 key test** or evidence of
an already visible ordinary Room00 Gene/HUD at submission.

The original selector is observed again as Stage1 / Room00 / Point0. Finite
requests change it back to Room01 and confirm. The actual Room01 interior,
Gene, enemies and HUD return **without restarting the native process**.
No character position, health, menu flag, guest PC or input-ready status is written.
There are no attacks, imported saves or autonomous level-completion loops.

The eleven interactive diagnostic requests are bounded, recorded and each
preceded by an exact live executable/PID/creation-time check. They are ordinary
finite pad pulses or one original-chord request, not effect acknowledgements.
There are only two destination confirmations after the initial bootstrap.

## What the module observations establish

The retained native log shows the following selected lifecycle:

1. r101 is installed for the first Room01 entry, then cleared on departure.
2. r100 and Event are installed for the Room00 introduction. Event is cleared
   after Start; r100 is cleared on the return jump.
3. r101 is installed again for the returning Room01 scene.

Both r101 registrations use the **same observed base**. Their complete 15,206
linked bytes are identical to each other and to the preceding own-disc qualified
static link. The other four module observations equal the retained, previously
qualified native observations byte-for-byte. No new address or cleanup guess is
introduced to make the transition work.

This proves one observed same-base return sequence. It does **not** prove
variable-base loading, absence of every retired function lookup, all callback/ABI
paths, allocation ownership, transactional installation or failure recovery.
Existing ignored install returns and partial-install limitations remain.

## Correction: the missing-label interpretation is rejected

The first version of this report (commit c183aa5) described missing selector
labels based on partial-looking inspection previews. Checking the actual full
original PNGs disproves that claim: actual5100 and actual10200 are byte-for-byte
identical to the full original selector at actual2300, SHA-256
`ea8a09470d738c82a95bb52ce0c03691006481cda923fad38bd69b0af2ff2c18`.
The unchanged label region also has identical decoded RGBA bytes in all six
inspected originals2300/3900/5100/6500/9700/10200. No cropped/converted file is
written or substituted. The original downloads and their provenance are kept.

There is **no demonstrated native missing-label defect or rendering fix** here.
This explicit correction preserves the earlier commit/history rather than
silently replacing the images. It does not establish all-menu rendering fidelity
or explain unrelated retained loading differences. The prior option-accounting
warning was not exercised or fixed in this sequence.

## Validation and remaining limits

The declared 480-second native watchdog ends normally with exit 0 after
483.828 seconds. There are **171 original PNGs**, through actual filename15700.
The three requested late fields15800/15900/16000 are not reached and remain
missing. The run is not relabeled as a complete capture-target pass, extended
or restarted. Room01 return is directly observed at actual11300 before that
boundary. No missing-function target message is observed.

The unchanged source suite passes 330 synthetic tests with three Windows
symlink skips in 67.893 seconds, after the native process ends. There is no
new game translation or host-source modification in this increment.

All 10,142 inventoried retained file identities match, including 260 old/new
original PNGs and the historical lab's four WIP hashes. Native disc/ELF guards
and before/after digests agree; the original inputs and old variants are unchanged.
No owned compiler, game generation, emulator or synthetic suite overlaps this
native run. This is not whole-machine isolation or a performance measurement.

Next: normal-mode F1/F2 and named-action acceptance on this combined build before
any launcher promotion; additional qualified loading/lifetime and variable-base
evidence; prototype VU/generic source closure and a fresh source-complete setup.
Broader options, original-reference comparisons, hardware input, audible audio,
genuine game Save/exit/Load and campaign fidelity remain separate gates. The
adopt-only public launcher still uses the old exact normal07 executable.

The [aggregate receipt](docs/evidence/prototype-room-transitions-2026-11-12.json)
and journal contain only reviewed aggregates and selected unchanged native
originals. No game, extracted asset, raw module/dump, save, binary or generated
game code is published. Game imagery has separate rights and is not GPL.
