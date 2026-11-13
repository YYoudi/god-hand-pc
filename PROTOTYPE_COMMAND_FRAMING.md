# Prototype command framing: private native trial

13 November 2026. This is a new host-reader trial, not a shared game-engine
correction, retail result, default upgrade or public ISO-only installer.

The original e677 command reader consumes a complete `open-debug` line once,
but an unterminated line produces480 attempts in the observed eight-second
window (10 accepted,470 refused). Its offset does not advance when EOF makes
`tellg` negative. Request acceptance is not evidence of a game effect.

The original bounded reader in adapter/command_line_reader.hpp commits only
LF-terminated records, retains partial data for the next poll, handles CRLF,
and latches malformed/oversized/truncated-stream faults. Its invented C++17
probe passes partial-write, repeated-EOF, exactly-once and boundary controls.

A separate private host main includes this exact helper. One new main object
and a new link reuse existing game/module/VU/runtime objects; no game generation
or full build occurs. New executable SHA-256:
`290b321c332d757b44d2e0c9f53535c65ce0f6a95fd5b88511ef259db86edce7`.
The first CMake link fails after response expansion with name-too-long; that
log remains preserved. A separate direct MSVC link succeeds, retaining the
response file and explicitly embedding the default manifest. Linker metadata
is not claimed binary-identical.

A NEW90-second diagnostic process exits0 after93.703 seconds including
shutdown. Complete, unterminated and later newline-completed records produce
1/0/1 request attempts. The actual original menu is inspected in the new900
renderer PNG. New900/1800/2400 equal the earlier900 PNG byte-for-byte; this is
sampled menu continuity, not every-frame equality or evidence of counts.

No automatic pad script or developer probe runs. Legacy diagnostic observers
remain enabled: this is not normal interactive/hardware acceptance. All
original exe/ELF/disc and inspected build preimages remain unchanged. Existing
launcher profiles still select their preserved executables. The original source/integration recipe is published for this scoped trial;
normal-launch adoption and wider native checks remain separate. No binaries, generated game code or raw logs are public.

## Reproducing the host source edit

Use the qualified private host emitted for the previous source-built prototype:

```powershell
python command_reader_source.py --input <private-qualified-host-main.cpp> --output <new-private-main.cpp>
```

The checked recipe is `adapter/command_line_reader_integration.json`; all edit
text is our original host glue, with exact whole-input/output SHA-256 checks.
Copy/use the exact `adapter/command_line_reader.hpp` in the host include path.
The actual CLI reproduced the compiled candidate main byte-for-byte after the
trial. This source command does not compile or run anything and is not a full
prototype setup recipe. Never overwrite generated guest functions or old builds.

Full validation: Ran 513 tests in 62.960s  OK (skipped=4)
