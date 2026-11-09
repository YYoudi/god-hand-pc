# Translation diagnostics: retain the error, test reachability

A successful generation process is not proof that every instruction translated
or every runtime path is valid. Preserve the original diagnostic log and counter.
Never replace an unexplained instruction with a NOP/stub to make the build green.

## Scope of the current investigation

Private inspection of the retained retail diagnostic identifies a fail-fast
statement in generated C++ after a function return. This is a hypothesis about
that translated body until independently checked; it is not an ISA interpretation,
a game fix, complete code coverage or proof of original hardware behavior.
The [dated compiler/entry audit](https://github.com/YYoudi/god-hand-rs/blob/main/docs/translation-diagnostic-2026-11-09.md)
records the independently checked current C++-body result and its limits. The
original reported error remains present; do not convert that bounded result into
a blanket clean-translation claim or an instruction patch.

Validate using the exact source, compiler flags/version and registered entries,
plus invented controls. In particular, a branch/label can reach code physically
after a return. The presence of a return, a compiler warning elsewhere, or one
successful game scene does not establish that a particular failure is dead.
MSVC [C4702](https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4702?view=msvc-170)
reports compiler-detected unreachable code; keep its exact source location and
exception/optimization configuration, and do not generalize it to the PS2 program.

## Original game-free controls

```powershell
python translation_fixtures.py --output .local/translation-fixtures
```

This writes three original minimal ELF32/MIPS inputs, explicit function maps,
recompiler configs and expected runtime outcomes. They contain no game bytes,
names, addresses or assets. Outputs are local-only, even though invented. An
existing destination is refused, not overwritten; the CLI only accepts a child
of this repository's ignored .local directory.

- **Return tail:** a known return followed by a deliberately unsupported word.
- **Reachable fault:** the unsupported word is reached from the entry.
- **Branch ingress:** an early branch can reach the unsupported tail despite a
  preceding return elsewhere. The zero and nonzero inputs must differ.

The word is deliberately unsupported by the pinned translator, not claimed to
have a universal ISA meaning. All functions are explicitly bounded; normal and
delay-slot instructions are invented. Synthetic unit tests check file structure,
namespace, branch target arithmetic, expected outcomes and safe output handling.

The original local integration runs these files through the pinned recompiler,
compiles the resulting synthetic functions and checks return/fault controls:

```powershell
python translation_probe.py --workspace-name retail-setup-v2 --vsroot "G:\Tools\portable-msvc-research\msvc"
```

Use an already built private Windows workspace and your explicit existing MSVC
root. This command does not generate or run God Hand. It creates a fresh ignored
UUID directory, records exact tool/source hashes and process outcomes, and never
relinks or overwrites the game's executable. The native harness calls synthetic
functions directly; it does not validate dispatcher, scheduler or hardware paths.
Each deliberately faulty input must retain its one reported translation error;
the test passes only when the four return/throw outcomes match expectations.
Do not label those integration gates passed merely because fixture tests pass.
CI uses only original synthetic source/data and never reads the owner's ISO,
ELF, translated functions, private logs or resulting game executables.

## Publication and provenance

Our public fixture builder/tests are original GPL continuation tools. Native
generated files, actual game translations, compiler objects, raw mappings and
private address/label evidence are not published. Source exposure is recorded;
this continuation is not presented as a clean-room game implementation. The
MIT independent lab remains paused and receives no game-derived code.
