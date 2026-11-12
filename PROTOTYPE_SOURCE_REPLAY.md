# Fresh prototype inputs and a normal-mode effects regression

12 November 2026. Follow-up to the [interactive prototype workbench](PROTOTYPE_INTERACTIVE.md).
The full developer-tools goal stays active. This increment removes some cached
source dependencies experimentally; it does not turn the adopt-only launcher
into a complete ISO-only installer or establish a retail debug backend.

## Fresh source inputs, not copies of generated game C++

Two separate ignored trials read the personal prototype and retail discs
read-only and verify their whole-file SHA-256. The bounded original ISO-root
reader obtains fresh original ELFs; their hashes equal the qualified profiles.
The prototype BIN really has 2048-byte ISO sectors, not an assumed raw-sector
layout. Neither original disc nor original ELF is edited.

Original public [prototype_inputs.py](prototype_inputs.py) creates a separate
discovery input. It clears 40 non-.text section EXECINSTR flags, while preserving
all PT_LOAD file bytes and every other byte. It refuses malformed/overlapping
tables, a wrongly mapped .text section, virtual-range wrapping and any metadata
edit inside a load segment. Invented ELF fixtures exercise these invariants;
there are no game bytes in the tests. This is a metadata discovery policy, **not
an opcode repair, runnable patched game or complete instruction-discovery proof**.

The identity-pinned recompiler generates 9,792 discovery C++ units plus two
headers freshly. All 9,794 files equal the preserved discovery outputs
byte-for-byte. The later BOOT profile regenerates 9,816 C++ units plus two
headers, all 9,818 files also equal the preserved outputs byte-for-byte. No old
generated C++, object or game library is an input to these generation steps.

Generation still reports **one error and 1,450 warnings**, even with exit zero.
The diagnostic is retained unchanged, not stubbed, hidden or declared harmless.
Source-byte repeatability is not original guest-PC coverage or runtime fidelity.
There is **no newly compiled/linked executable** in this source replay.

Recompiler executable SHA-256:
`506cffa76fb5eeff58ee86e08fcec1a1d79e911d9fb23565a89f088f4bb80ec4`.
Runtime checkout: `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`.
Private retail naming/bounds metadata checkout:
`193076584e277c95644dcbbb4a6922c3a59ca2b8`.
These frozen inputs are not a claim to have tested newer upstream revisions.

## Replaying SDK candidates without an old address-map input

The retained normalized-span/CFG algorithms run on the NEW ELF/discovery inputs.
Names/bounds come from the frozen private GPL checkout; no raw table or game
source is republished. There are 107 candidate functions, initially 102 with
unique full-span matches. Original [finite-domain consistency](prototype_call_graph.py)
checks known direct targets without inventing a choice when ambiguity remains.

The resulting **103 selected bindings, 152 static known-direct-target checks and
two rejected targets exactly reproduce the earlier selected evidence**. Fifty-nine
selected bindings have no such outgoing check: do not mistake the total for
coverage of every function. Twelve ambiguous no-outgoing candidate targets remain
unselected. Incoming constraints narrow two static context anchors, but do not
silently enable two additional HLE bindings. The first incomplete anchor model
found the same binding identities but missed checks in 13 records; its failed
exact-evidence assertion is preserved, not reported as a passing replay.

The newly rendered binding text equals the previous text after the explicit
Windows CRLF/LF distinction. The original bytes/hash are retained, not rewritten.
This is **static identity/consistency replay**, not recovered source, new SDK-name
or ABI qualification, observed runtime call coverage, hardware or effect proof.

The fresh prototype ELF's own SNR2 metadata supplies 502 relocation records;
298 instruction-relocation records reproduce the old CSV exactly in original
table order. A first address-sorted attempt had the same set but failed exact
ordering before generation; it remains preserved. No retail address is reused.
The final BOOT generation still explicitly consumes **24 previously qualified
private seed ranges**. They are checked against fresh mapped ranges, not freshly
discovered or passed off as an ISO-only dependency closure. Selected modules,
VU programs and generic libraries remain separate setup dependencies.

## Current executable versus newly generated source

The normal-mode regression deliberately reuses unchanged native07
`0afc8392bcab3db0aeb2ef3c9d57d9530598a408c68fa707091db56ac195c2e6`
and the actual public launcher from `8be4cd64fe300be51acf0ac36df002c9f0946d45`.
It uses the freshly read prototype ELF from a new directory plus the personal
disc, not the old cached ELF/extraction directory. Visible/muted interactive mode
has no automatic input, game-health/Warp/pad observers or raw-memory exports.
The external observation deadline is not a native diagnostic timer or permission
to kill/restart the process. Software OS/mouse actions are not hardware tests.

The actual normal session ends **0 after 664.865 seconds**, via real Alt-F4
before the outer 900-second observation limit. Actual F2/mouse Room Jump selects
1/00/Point0, loads the original room and skips its introduction with Start. The
initial window-backend capture is white; F2 produces the correct visible menu.
That failed capture remains private, not a repaired renderer or a mouse target.

Actual original PL NO DEATH OFF -> ON, Cross/menu close and Hide are followed by
visible enemy attack/hurt animations and Gene still alive with a full health bar.
Two selected alive observations are 90.283 seconds apart. This is visual normal-
mode acceptance, **not the earlier native05 198-HP/refill-count experiment**; no
numeric HP, damage count, arbitrary lethal-hit or every-frame survival claim.

Actual F2/mouse enters original Player Warp. After two idle observations, one
finite 200-ms LSRight request changes the visible original Warp view; a later
post-request original is byte-identical to the immediate post-request image.
The two idle scene regions are NOT perfectly identical: private read-only
analysis finds 952 decoded-JPEG pixel differences in sceneROI x1..640/y31..335,
versus 193,787 after the pulse. This reads original lossy images and writes no
crop. It is a scoped visual response, **not numerical actor-vector displacement,
full-machine pause or matched PS2 fidelity**. Native05's stronger vector proof
remains separate. Start/Cross/Hide restores the normal room camera/HUD; ordinary
enemy attacks and camera motion then resume. This is not position undo or exact
pose retention. The detached-cloak-like artifact is still visible and unchanged.

The original option still reads ON when revisited. Actual Left restores OFF;
Cross/close/Hide is followed by visibly reduced health and the original Continue
screen. The same `memory leak size 0x480` warning appears on the first Cross
after OFF, then the next observed parent/menu and game/death continue. It now
**reproduces with game observers disabled**; its cause, duration and whether the
PS2 prototype reference also produces it remain unverified. No suppression, fix
or memory-safety certificate is claimed.

Only the operational log, finite actual-input FIFO and launcher receipt appear
in the native session directory. No scripted bootstrap, automatic health/camera
writes, diagnostic command file or raw exports are present. Controls bytes are
unchanged. A private memory-card file exists; this is not game Save/exit/Load.
Cross/Circle are finite ordinary inputs used at observed original menu states;
no deliberate fighting script, autonomous level completion or imported save.

The aggregate receipt and selected unchanged native-window originals retain
exact timestamps, executable/input provenance, before/after/restoration and
limitations. New source-replay helpers are not silently described as part of
this unchanged executable.

Final full synthetic suite: **280 tests pass**, three Windows symlink skips,
69.834 seconds after journal/media preparation. The earlier280-test source
run67.916s remains retained; these are not additional unique tests. No owned
compiler/tests overlap the native run. The [aggregate
receipt](docs/evidence/prototype-source-replay-2026-11-12.json) records scope and
limits without private maps or generated source.

## Remaining boundaries

Complete prototype setup still needs reproducible seed/module/VU qualification,
a fresh full build and its own native acceptance. Normal-mode visual observations
do not inherit earlier native05 numerical health/vector evidence. Wider options,
invalid states, focus/held/repeat, physical keyboard/controller, audible audio,
genuine Save/exit/Load and campaign coverage remain open. Earlier strict VU1
failure and rendering artifacts remain unrepaired. Prototype evidence is not a
retail implementation; any retail action needs its own identity/ABI/lifetime proof.

Public code here is original GPL host tooling and invented fixtures only. No game,
ELF, extracted asset, raw map, dump, save, generated game code or binary is published.
Selected unchanged native-window images show actual action states, never the
journal page; game imagery is not GPL. The historical MIT Rust lab stays intact.
