# Replaying the prototype VU source inputs

12 November 2026. Follow-up to [normal combined-build acceptance](PROTOTYPE_COMBINED_INTERACTIVE.md).
The public normal launcher profiles remain unchanged. This experiment removes
an inherited generated-source dependency from the **VU portion** of a separate
private build. It is not a rendering fix, strict VU-equivalence result or complete
personal-disc prototype installer.

## Fresh inputs, not the historical capture as a seed

The retained `4acf41e7` executable first runs a new, declared 450-second diagnostic
with the prototype's compiled-program registration disabled. Its five old counted
wrapper callbacks report zero calls. The actual original Room Jump route is
Stage1 / Room00 / Point1, followed by Start to skip the observed introduction.
No later attack/movement, health/PC/ready-flag edits or imported save is used.

This native run ends zero after **454.141 seconds**, with all nine requested
original PNGs, including the actual room/Gene/HUD. It records five fresh 16-KiB
microprogram images privately, 81,920 bytes in total. A fresh manifest is written
before consulting the old capture or old generated source as an oracle.

The new inputs match the historical image set and bytes. Each exact image is
bound by SHA-256 and its canonical filename is checked against the runtime's
byte-domain FNV-1a identity. FNV is **not cryptographic provenance**; these checks
do not authenticate the native runtime's program hash table or prove the console's
VU behavior. This is a fresh **native capture through an existing qualified
bootstrap**, not independent direct extraction from the ISO or a complete new
bootstrap source build. Existing port defects could still affect execution.

## Original metadata and counted-registration tooling

[prototype_vu1.py](prototype_vu1.py), source revision
`02de3050a5975e24ec43ef573a636b61f54bff37`, contains original game-free metadata
validation and host-wrapper emission. Private program identities are input data,
not a hard-coded public game map. The helper checks exact image size, filename,
FNV and explicit SHA-256; the emitter refuses duplicate/colliding IDs, source
fragments and unbounded profiles, and has explicit LF/CRLF behavior.

The emitted counted wrapper equals **all 3,472 original bytes** of the currently
linked host wrapper, including its CRLF line endings, callback forwarding,
registration order, atomic call counters and report format. It changes no guest
instruction, readiness state, game flag, heap cleanup or arithmetic behavior.
Eight invented-data tests include a compiled C++ callback/counter stub and an
integer hash oracle. Stub compilation is not real-runtime ABI/ISA validation.

## Two new generations and a new library

The existing pinned `vu1_recomp` tool is invoked twice into separate **new empty**
private directories, from only the five qualified fresh image files. Its SHA-256 is
`f30dab23ade5a9c9cb13be4a10fe67211c503e88c19a78b9582509d7ffe59d47`.
It is the same prebuilt tool as the historical generation. Its inspected source
matches pinned upstream revision `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`
after CRLF-only normalization; this is not a new toolchain bootstrap attestation.

Both generations produce the same 20 C++ files, byte-for-byte. Only after writing
those fresh results is the old generated directory consulted as an oracle: all
20 files match. No old generated C++ file is an input to either generation.
All source and diagnostics remain private. Byte equality is not a clean-translation
or VU-correctness certificate; the existing strict-comparison failure remains.

Twenty new VU translation units and a static library are compiled with MSVC
19.44.35229.0, followed by the regenerated host wrapper and a separate native link.
Both generations, configure, library compile, wrapper compile and link return zero.
All 9,843 inventoried parent link inputs remain unchanged; the old wrapper object
and VU library are replaced only in the new response file. Other BOOT/module
objects and five historical generic snapshot libraries are explicitly reused.

The new private executable is
`0ef156637d67835e4a956288985e6bdca83411ef5d7f696272a701ba55f21ef7`.
It is **not** adopted by either public normal-launch profile.

The source suite passes **344 synthetic tests**, three Windows symlink skips,
in 59.672 seconds after the capture and build end. No game program, image pixel,
dump or generated game C++ is a CI fixture. No owned compiler, game/VU generation
or synthetic suite overlaps a native GPU run. The final publication-tree suite also
passes all344 tests with three Windows skips, in67.032 seconds after both new
native controls are terminal.

## Native controls

Two **new** sequential AOT-enabled controls use the same finite original-menu
route, prepared scratch directories and nine requested screenshot fields. They
change only the executable and per-case output paths. Each native watchdog is
declared at 300 seconds; the retained parent exits zero after **303.906 seconds**,
and the fresh VU-source capsule exits zero after **303.844 seconds**.

Both report five registered compiled callbacks and **all five are actually called**.
The original menu at field1560 and the room/Gene/HUD at field4501 are directly
viewed from the new PNGs. All **nine same-filename original PNGs are byte-identical**
between the two runs, including loading/menu/scene samples. The selected menu and
scene pairs retain unchanged 640x480 downloads and separate per-run provenance,
even when identical bytes share one public filename. No image is cropped,
normalized, redrawn or replaced by a screenshot of this journal.

The recorded CSV endpoints differ (elapsed-time watchdogs do not stop on an equal
guest field); the nine samples do not prove every-frame identity or performance.
All actual requested PNGs exist. No missing-target or unimplemented-string match
is found in these two retained logs; this bounded check does **not** erase the
earlier translation error or certify complete instruction coverage. The prior
AOT-disabled capture is a different experiment, not an AOT1 before/after control.
Normal launch profiles and their private executable hashes remain unchanged.

## What remains open

Five generic snapshot libraries, other qualified BOOT/module/host inputs and the
existing bootstrap are still dependencies. This closes one replay boundary, not
the complete source/setup workflow, arbitrary VU program/room repertoire, CFG,
ABI, lifetime or failure recovery. The retained BOOT translation error and 1,450
warnings, strict VU mismatch, cloak/interface artifacts, loading differences and
original 0x480 menu warning are not repaired or hidden.

The actual normal F1/F2, Room01/Warp and separate Room00 no-death/OFF/death proofs
remain valid for `4acf41e7` only; no named effect or hardware acceptance is inherited
into this new capsule. Retail inputs/functions remain separate. Full menu, hardware,
audible audio, genuine Save/exit/Load and campaign-fidelity gates remain open.

The [aggregate receipt](docs/evidence/prototype-vu-replay-2026-11-12.json) and journal
contain reviewed aggregates and selected unchanged actual native originals only.
The five programs, raw hash/entry maps, generated C++, objects, libraries, binaries,
cards and original discs remain private. Game imagery is not GPL. The goal remains
active; no new Rust or delegation is involved.
