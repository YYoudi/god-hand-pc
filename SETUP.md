# Personal-disc Windows setup

The original orchestrator follows the pinned retail generation pipeline. It
does not download a game, bypass disc checks, install a compiler or publish outputs.
The complete fresh build is **under local validation**, not yet a verified installer.

## Prerequisites and command

- Windows x64, Python 3.11+, Git, CMake, Ninja and an MSVC x64 environment.
- Visual Studio 2022 / Build Tools with C++ and a Windows SDK, or an explicitly
  supplied compatible local toolchain root containing `VC/Auxiliary/Build/vcvars64.bat`.
- A checkout path without spaces/cmd metacharacters, such as `G:/God-Hand-PC`.
  The pinned upstream's nested batch calls are not certified for other paths.
- The supported personal USA retail ISO and enough free space for the private
  disc copy, dependency sources, generated C++ and compiler outputs.

```powershell
python pc.py setup --iso "G:\path\God Hand (USA).iso" --vsroot "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools" --jobs 2
```

Use `--prepare-only` to verify/fetch prerequisites and create the private disc
copy without generating or compiling game code. `--jobs` defaults to two; child
builds run hidden and below-normal priority. Setup does not launch the game.

## What happens locally

1. Verify the exact complete ISO size and SHA-256 before generation.
2. Fetch upstream and eight dependency repositories at exact commit hashes under
   ignored `.local/retail-setup/`. `dependencies.json` also records license hashes;
   upstream and dependency notices remain in those private checkouts.
3. Create a separate, verified, read-only private ISO copy in the sibling `disc/`
   path required by upstream's overlay emitter. Never hardlink or change attributes
   on the original. A partial/mismatched existing copy is refused, not overwritten.
4. Generate the boot program, extract all 81 overlays, link their inputs, generate
   their C++ packs, then build the native executable. The `snr2 --iso` option is
   deliberately before `extract`; upstream's README order does not parse at this pin.
5. Check the extracted boot identity, overlay count/hashes, generated pack presence,
   source status and executable hash. Reverify the owner's original ISO afterward.

The existing adopted evaluation checkout is not replaced or rebuilt. All new
source/build outputs stay in this distinct workspace. No old evidence is deleted.
Dependencies are explicitly fetched; CMake's implicit downloads remain disabled.
Optional SDL3, prebuilt FFmpeg and PCSX2 graphics builds are not enabled here.

## Evidence, interruption and limits

Each invocation creates a new private `runs/<id>/receipt.json`, per-step logs,
child PIDs, exact tooling hashes, dependency versions and retained generation logs.
An exclusive `setup.lock` refuses a concurrent or unexplained interrupted build.
After an interruption, inspect the recorded parent/child processes before any
manual lock recovery. An observation timeout is not permission to restart a job.
Do not share the entire private workspace or logs automatically.

The recompiler can exit zero while reporting errors. Setup records its warning,
error and unhandled-instruction counts separately and warns explicitly; it does
not silently remove instructions or substitute successful stubs. A compiled binary
is labeled **built, not runtime validated**, not a clean translation or fidelity pass.
The earlier tested retail generation log itself reports one unresolved instruction;
that does not erase the limited gameplay observations, or prove all paths work.

Fresh executable boot/scene/input testing is a separate gate. This recipe does not
yet install the private external-texture adapter, validate real game Save/Load,
support prototype discs or promise bit-identical compiler output across toolchains.
Nothing generated from the game belongs in this public repository or CI.
