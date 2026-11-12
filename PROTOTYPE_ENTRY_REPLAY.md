# Deriving BOOT entry candidates from original module calls

12 November 2026. This is a source-reproducibility follow-up, **not a new native
menu release**. The normal07 executable, its adopted launcher and the previously
observed F2/mouse actions are unchanged. The developer-tools goal remains active.

## What was actually reproduced

A new private, read-only audit verifies the personal prototype disc and fresh
ELF identities, then reads all **76 original modules**. It joins original J26
import-relocation records whose original opcode is JAL to the fresh BOOT export
registry. The registry address comes from this ELF's explicit `.sndata` section,
not a retail default or an old address map. Discovery ranges come from the fresh
generation described in [the earlier replay](PROTOTYPE_SOURCE_REPLAY.md).

The audit records **6,487 original import-call uses**; two cannot resolve against
this BOOT-only registry. Seven other import J26 sites contain a jump rather than
JAL and are retained separately, not silently counted as direct calls. Later
module overrides and actual call-path execution are not established by this scan.

The entire module catalog leads to **25 missing exported-entry candidates**, not
just the six needed by the existing four-module room/introduction profile. Thus
"scan imports" is not by itself a recipe for selecting the previous six.
Explicitly restricting the profile selects **six candidates with nine original
call-site references**. Nineteen other candidates are not enabled or presented
as working rooms. No historical seed CSV is read before recording this selection.

Original GPL [prototype_entry_candidates.py](prototype_entry_candidates.py) is
the host-side selection model, at revision
`fbd18869fd291edb6b054f6bead70ea70812b848`. It takes parsed ranges, registered
entries, resolved direct-import uses and an explicit module scope. It refuses
overlap, unmapped exports, unregistered import targets, duplicate sites and an
unknown scope. Other exported entries remain span fences even when not selected.
Eight invented-data tests cover this model; it contains no game data, address
table, instruction decoder or third-party source.

Each selected candidate ends with an original JR RA/delay pair, optionally
followed by one padding NOP. This narrow check and a proposed span are **not full
CFG/ISA, function ABI, ownership, overlay lifetime or runtime-effect proof**.
Only afterwards does a separate historical-map comparison find that the six
starts and ends agree. Agreement is a regression result, not the selection input.

## Generation with explicit remaining dependencies

Two separate new generation trials combine these freshly selected six ranges
with **18 retained private indirect-entry ranges**. The second consumes the exact
final public model, after grouping its use records and tightening an input-shape
refusal. Both trials exit zero and reproduce **all 9,818 C++/header files** of the
preserved BOOT generation byte-for-byte: 9,816 C++ units and two headers.
The ELF's own 298 instruction-relocation records are derived freshly again.

Generation still reports **one error and 1,450 warnings**. They are retained,
not repaired, suppressed or declared harmless. No old generated C++/object/library
is a generator input, but the 18 old indirect ranges remain an explicit dependency.
This removes the six historical export bounds from the recipe, **not all private
seed/module/VU/generic-source dependencies**. It is not an ISO-only public setup.

There is no new compilation, executable, F2 action test, performance result or
PCSX2 warning comparison in this increment. Source equality does not inherit
native acceptance from another binary or prove full original guest-PC coverage.
The existing menu accounting warning and earlier strict VU1 failure remain open.

Source validation: **289 synthetic tests pass**, three Windows symlink skips,
71.486 seconds. A later publication check is recorded separately. The failed
CP1252 console summary is retained; it occurred after the focused eight tests
passed and did not change the journal. Subsequent commands use UTF-8 explicitly.

Preservation checks rehash **39,379 file identities**, including the old generated
sources, both new outputs, retained executables, original discs and four historical
MIT WIP files. All match. No owned native/emulator/compiler job overlaps the
synthetic suite; this is not whole-machine isolation or a performance claim.

## Next checks

Qualify the remaining indirect entries from code-backed table uses and bounded
control-flow evidence, rather than treating all raw data-pointer runs as valid
function tables. Complete module/VU/generic-source closure before a fresh full
build and its own native acceptance. Separately finish the original prototype
reference's empty-menu warning comparison and wider input/menu coverage.

The [aggregate receipt](docs/evidence/prototype-entry-replay-2026-11-12.json)
contains counts and provenance only. Raw names/address maps, module bytes,
generated game code, discs, ELFs, dumps, saves and executables remain private.
No new visual result is invented for this source-only work; the earlier native
menu/warning/action originals remain available in the journal. Game imagery is
not GPL, and this prototype evidence is not a validated retail debug backend.
