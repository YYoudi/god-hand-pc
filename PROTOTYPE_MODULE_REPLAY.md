# Regenerating the selected prototype modules

12 November 2026. Follow-up to [prepared native controls](PROTOTYPE_PREPARED_CONTROLS.md).
The developer-tools goal remains active. This removes another dependency on
cached generated game source; it is not a prototype installer or a full port.

## What is now reproducible

The original public [module adapter](module_emit.py) consumes fresh read-only
disc bytes, the prototype's own boot ELF and explicit qualified module bases.
It uses the existing public ISO/FST/AFS and source-envelope readers, then calls
the privately fetched GPL SNR2 parser, static linker and ELF writer from the
frozen upstream revision `193076584e277c95644dcbbb4a6922c3a59ca2b8`.
Those dependencies are not copied into this repository.

The adapter prefers the backend's function extent. Only if that returns no
extent does it try the original narrow fallback for a module-relative jump to
an already known earlier start. A delay slot, forward-branch bound and successor
condition are required. This is **not** full CFG, instruction, indirect-call,
alias, ABI or lifetime qualification. It never replaces unknown instructions.

Four selected prototype modules are emitted afresh without reading their old
REL files, linked images, ELF files, function maps, relocation maps, RAM dumps
or generated C++ as producer inputs. Their load bases remain explicit previously
observed qualification inputs. The boot registry is read from the prototype's
own ELF, not transplanted from retail.

Before opening old outputs as a comparison oracle, the new emission hashes are
recorded privately. All four emitted ELFs, linked images and both CSV inputs per
module equal the preserved originals byte-for-byte. JSON metadata values also
equal; the new JSON uses LF while the old Windows text has CRLF. This distinction
is recorded, not normalized away or counted as byte equality.

The exact recompiler with SHA-256
`506cffa76fb5eeff58ee86e08fcec1a1d79e911d9fb23565a89f088f4bb80ec4`
then generates **720 C++/header files**, all byte-identical to the old raw outputs.
All four processes return zero; **82 warnings and zero errors** are retained.
The older BOOT generation's separate error and warnings are not resolved by this.

## A separate compile and executable

All 708 translated function units from these new outputs are mechanically
namespaced; all 712 wrapped function/header files equal their old counterparts.
All four module libraries are compiled in new build directories, without old
module objects or libraries. The nine configure/build/link steps return zero.

The four existing original host registration wrappers and their qualified tables
remain explicit dependencies. So do 9,832 BOOT/host/VU/generic link inputs from
the previous capsule. No full-source build or generic/VU source closure is
claimed. All old link inputs remain unchanged. The new private executable is:

`79c88f1eed19e2c187ff15d5b69fd3518f115c617156749a57027226478b05fd`.

The normal07 launcher and executable are unchanged. The new capsule is not
silently promoted, nor does it inherit normal07's actual-key, mouse, Warp or
no-death survival evidence.

## Native observation

A new 450-second bounded diagnostic exits zero after 453.781 seconds, producing
all 23 requested original PNGs with no export failures. The last present counter
is 9885. The log records installation of all four selected modules; this does not
prove all calls, ABI or every module-lifetime path.

Direct original-image inspection shows the original main menu, the selected room,
PL NO DEATH ON then OFF labels, the existing `memory leak size 0x480` warning and
the normal room/Gene/HUD afterward. This is the finite software-controller/shared
F2 sequence, **not a new OS-key, mouse, Warp displacement or survival test**.
The warning and detached-cloak-like artifact remain visible.

Against the prior separate candidate27 run, all 21 common actual-filename PNGs
are byte-identical. Two filenames differ: the new run exports2900/5360 where the
old run exports2901/5361. No files are renamed. Filename counters do not prove
identical presented source or guest state; this is not a controlled timing pair
or all-frame/PS2 fidelity proof. The earlier loading-screen mismatch remains
unexplained and publicly retained; these samples do not resolve it.

The journal includes the actual new-build endpoint, original option states and
warning. Original files, timestamps, hashes and exact executable provenance are
preserved. Identical images may share a media file while retaining separate run
metadata; this does not turn an old capture into a new observation.

## Tests, limits and next steps

Nine original invented-data tests cover the narrow tail fallback, guard failures,
CSV quoting/filtering, preference for the backend extent, analysis refusal and
emission dispatch. Mock backend tests verify adapter control flow, not the
third-party linker. The four actual module replays above are separate evidence.

The full source suite passes **314 tests**, with three Windows symlink skips,
58.295 seconds, after native execution has ended. No owned compiler or synthetic
suite overlaps this native run. The final local publication suite also passes314tests/3skips in57.460s;
343explicit public paths and107reviewed original images pass the staged index
and journal/navigation checks. These are not additional unique tests.

Remaining work includes qualification inputs and registration-source closure,
VU and generic source reproduction, a fresh full build and its own native
acceptance. Wider UI/input behavior and the original-reference warning sequence
remain open. The existing memory warning, strict-VU1 failure, rendering artifacts,
retail backend, physical input/audio, game Save/exit/Load and campaign coverage
are not fixed by this source replay.

No game files, extracted assets, raw maps, dumps, saves, binaries or generated
game code are published. All emitted files returned by the adapter are private
game-derived outputs. Public source here is original GPL host tooling and
invented fixtures, not an independent clean-room engine or recovered game source.
Selected native screenshots retain their separate game-imagery rights and exact
build/time/hash provenance. The historical MIT Rust lab remains untouched.
