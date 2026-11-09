# Bounding a retained translation diagnostic without hiding it

Date: 9 November 2026. This investigates one retained retail boot-generation
diagnostic, not a newly fixed gameplay bug. The original source, error counter,
native executable, personal disc and paused Rust work remain unchanged.

## Observed result and exact scope

The retained log reports one unhandled-instruction error although generation
exits zero. Upstream's emitter produces a fail-fast C++ exception for such a
site; it does not silently turn it into a NOP. Private inspection found this
particular failure in a straight-line tail after a function return.

That appearance alone is insufficient. We checked the exact emitted function,
its initial resume switch and all six registered aliases. The aliases match the
normal entry plus switch entries, with no entry into the failure tail. A separate
compiler probe then compiled the unchanged private translation unit, redirecting
objects/debug output to new research paths rather than touching the game build.

Using the existing MSVC 14.44.35207 toolchain and its original optimization and
exception configuration, both default and strict-return analysis variants report
unreachable code in the same straight-line block before the fail-fast statement.
There are no intervening labels or control-flow statements that could provide
ingress. Both probes deliberately return compiler error 2 because C4702 is
promoted to an error; there are no other compiler errors. This is an **expected
analysis result**, not a failed game rebuild. Microsoft documents
[C4702 as compiler-detected unreachable code](https://learn.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4702?view=msvc-170).

**Conclusion:** this failure is compiler-unreachable in the inspected generated
C++ body. This does not establish every possible original guest-PC path, the
meaning of the untranslated word, hardware behavior or complete game fidelity.
We did not identify an ISA operation, remove bytes, shorten a game function,
patch an instruction, insert a stub or suppress the diagnostic. Warnings and the
original reported error remain visible. Other compiler/source revisions require
their own checks.

## Counter-controls, not just a successful build

Three original C++ control bodies distinguish a dead throw from a reachable
throw and a labeled ingress after a return. With the same compiler reachability
check, only the deliberately dead control is diagnosed. This avoids the false
rule that anything physically after a return must be unreachable.

We also authored three original, minimal ELF32/MIPS programs, explicit function
maps and recompiler configs. They contain no copied game bytes, symbols or maps.
The pinned real recompiler reports **one deliberate error and exit zero for each**.
Their translated functions are then compiled and executed natively:

| Invented input | Native observation |
| --- | --- |
| Return followed by an unsupported tail | Returns the invented value 37. |
| Unsupported instruction reached from entry | Throws at the expected synthetic PC. |
| Early branch into a tail, input zero | Returns through the other path. |
| Same branch example, input nonzero | Reaches the tail and throws. |

These four outcomes pass. This harness calls generated **synthetic** functions
directly; it does not exercise the game dispatcher, scheduler, renderer or game
instructions. It demonstrates why generation exit codes and source layout alone
cannot be treated as coverage or correctness certificates.

## Reproduction and actual failures retained

The original public GPL fixture builder and native probe live in
[god-hand-pc](https://github.com/YYoudi/god-hand-pc/blob/main/TRANSLATION_DIAGNOSTICS.md).
The verified clean tooling revision is
`8132cc495623fd14531fb4eda31df9d02659985a`; upstream base remains
`14e956a1274332440273845fbab2c1f1e30c4a5a`, and evaluated private host source
remains `193076584e277c95644dcbbb4a6922c3a59ca2b8`.

From an existing private Windows setup:

```powershell
python translation_probe.py --workspace-name retail-setup-v2 --vsroot "G:\Tools\portable-msvc-research\msvc"
```

This creates a new ignored UUID directory and records source/tool hashes, source
cleanliness, exact commands, owned PIDs, logs, error counts and native outcomes.
The clean committed rerun completes nine steps with exit zero: three generations,
four single-unit compilations, a link and native execution. Expected translation
errors remain recorded; passing means that the controls behave as specified.
The command never relinks or overwrites the game and does not read the ISO.

A first environment probe failed on Windows command quoting; its failed script
and result remain private. A combined public compiler invocation later exceeded
its 180-second bound during code generation without a source-error diagnostic.
It was stopped and retained, not treated as success or blindly restarted.
The corrected recipe compiles one unit at a time to private object paths, then
links, with bounded per-step waits. A synthetic recipe test prevents silently
returning to a combined/multiprocess compile. No system security or privilege
settings were changed.

## Publication and remaining gates

Public code contains only original fixture/probe tooling and invented tests.
Actual translated game source, raw addresses/maps, private compiler logs, ELF
inputs, generated files, objects and executables remain private. Source exposure
to the translated unit is explicitly recorded; this is not presented as a
clean-room game implementation. No game-derived code enters the MIT lab.

This is nonvisual evidence: no fake renderer comparison is added. The journal
capture shows the actual report entry, not a manufactured gameplay milestone.
The retail generation warning set, genuine game Save/exit/Load, physical input,
audible audio, later-stage validation and campaign fidelity remain open. The
owner has no personal save available; no downloaded save or quick state is used
as a substitute. Next host work remains safe settings pause/resume and input
boundaries, not a duplicate menu or a whole-engine rewrite.
