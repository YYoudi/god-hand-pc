# Prototype observer sources and native project assembly

13 November 2026, Europe/Paris. Source
`480b7e77887973fc8f7252f39667410981a5c6aa` adds original GPL
[observer-input assembly](prototype_observer_inputs.py), its
[reviewed insertion metadata](adapter/prototype_observer_inserts.json), and
[native CMake project emission](prototype_native_project.py).
This follows [host-profile derivation](PROTOTYPE_HOST_PROFILE.md).

The four observer outputs now reproduce the tested private source files without
our private instrumentation script/profile as a producer. An actual newly
configured CMake project matches the prior source/selected-flag inventory.
**No new game executable is compiled, linked, run or adopted in this increment.**

## Original additions only

The public insertion policy contains hashes, line positions, explicit EOL and our
original observer declarations/calls. It contains no game instructions, populated
addresses, original/observed game body, source filename map or capture. It was
authored from the previously separated original insertions; prior game-source
exposure and semantic qualifications remain disclosed GPL continuation work,
not clean-room independent-engine work or newly recovered game source.

Input raw and output instrumented game functions remain private. The producer
indexes a hash-qualified generated BOOT catalog and requires exactly one input
for each selected source identity. Missing/ambiguous identities refuse. The
existing insertion-only helper checks complete pre/postimage hashes. Original
PC/word comment sequences must also remain unchanged and in the same order.
These are text-production checks, not independent C++ read-only, CFG, ABI,
ownership, lifetime or instruction-execution proof.

## Actual four-source replay

The current private catalog has 9,825 C++ units, 167,218,399 bytes. New output
identities were recorded before reading the prior native postimage oracle.
All four bodies are byte-identical to the actual instrumented sources used by
the unchanged `e677f789c9f51400ba054b5a72ab7807f363a5bd4c099ba10f5c2c07edcc8e34`
executable. Their neutral output filenames are new, not recovered function names.

| Original observer role | Insertion positions | Preserved PC/word comments |
| --- | ---: | ---: |
| Damage observations | 5 | 118 |
| Refill observations | 3 | 1,141 |
| Warp creation observations | 2 | 71 |
| Warp destruction observations | 2 | 32 |

No game body is copied into this repository. Earlier
[normal F1/F2, Room01, Warp and no-death OFF/restoration observations](PROTOTYPE_WHOLE_INTERACTIVE.md)
and original screenshots remain **earlier** native evidence, not new captures
or new menu-option coverage from this source replay.

Eight actual CLI controls return expected `0/2/2/2/2/2/0/2`: check-only, wrong
catalog identity, missing directory, unsafe session, ambiguous selected source,
missing selected source, fresh production and stale-session refusal. All seven
non-production output trees stay unchanged. The two real-data identity-negative
folders are private controls, not synthetic fixtures or public/CI inputs.

```powershell
python prototype_observer_inputs.py --generated <private-generated-BOOT-directory> `
  --generated-sha256 <qualified-catalog-sha256> --session <fresh-private-name> `
  --check-only
```

Without `--check-only`, the CLI writes four private C++ files and a receipt only
under ignored `.local/prototype-observers/sessions/<fresh-private-name>`.
Those files contain game code and **must never be published**, even though the
inserted observer statements are original.

## Actual native project configuration

The public emitter receives explicitly qualified BOOT/host/module/observer/SDK
and VU source locations plus five generic-library paths. It emits configuration
text only. It does not itself fetch, generate, relocate, compile, run or qualify
those inputs. No existing guest object path is accepted as a source argument.

It retains the five named module order, override objects before generic archives,
explicit SDK include copy, MSVC/C++20 profile, selected `/O1` flags, byte-size
`/Od` exceptions, four observer PCH exclusions, corrected angle PCH spelling,
interpreter-bootstrap capability macro and separate VU `/O2` target. Without an
explicit VU directory, only the bootstrap target is emitted; this is not fake
compiled-program registration. Runtime refusal still needs its existing code.

An actual fresh project configures successfully with MSVC 19.44.35229.0 and Ninja.
CMake performs its normal compiler-ABI probe, **not a game build**. The project
uses existing qualified producer outputs and the five libraries previously
rebuilt in the selected-source experiment; they are not rebuilt again here.

The actual new and prior `compile_commands.json` inventories each contain
10,586 commands after excluding CMake's generated PCH source. Their multisets
agree by target, exact source-file bytes, selected optimization/CRT/EH flags,
PCH-use and bootstrap-macro classes. The four renamed observer files are checked
by content, not guessed filename correspondence. CMake exposes both bootstrap
and native targets, guest/host/VU groups and all five module groups.

This does **not** compare every include/preprocessor state or source path, prove
link/initialization order or binary/ABI equivalence, compile every command, or
establish new native/fidelity/performance acceptance. Changed paths and the new
graph require their own real build and native validation before adoption.

## Validation and remaining gates

The exact-source suite passes **501 tests, four Windows skips, 70.070 seconds**,
including 16 new invented-data controls. None supplies game/vendor bytes to CI.
All 45,676 retained native/source/disc identities match. Aggregate hashes,
control outcomes, source counts and configure scope are in the
[evidence record](docs/evidence/prototype-source-assembly-2026-11-13.json).

The original source-assembly stages and project emitter are now public. The
end-to-end orchestration, fresh native-registration acquisition/qualification,
complete fresh compilation and its own native acceptance remain. Five historical
registration capture pairs are still dependencies of the host-profile stage;
this is not yet a public ISO-only installer.

No whole compile is attempted with the current low free space on G:. The existing
capacity gate is unchanged; old evidence, original discs and paused Rust work
are not deleted or moved. Existing normal07/room01-v1 launch profiles and the
tested executable remain unchanged. Translation error/warnings, strict VU1,
render/loading and 0x480 accounting limits, wider menu/input/reference/ABI/lifetime,
failure recovery, audible audio, genuine Save/Load and campaign testing stay
separate. The full goal remains active; no Rust or delegation.
