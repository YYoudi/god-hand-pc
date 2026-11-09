# Native pack bridge contract, version 1

Status: locally built and rendered on 6 November 2026. Three separate 220-second
hidden runs verify enabled replacement, disabled original assets and invalid-pack
original-asset fallback. This is a bounded same-size texture MVP, not a remaster.

## Commands

After the successful personal-disc setup, install the original bridge and relink:

```powershell
python pc.py install-packs --workspace-name retail-setup
python make_example_pack.py --output .local/example-pack
python pc.py run --workspace-name retail-setup --iso "G:\path\God Hand (USA).iso" --profile enhanced --pack .local/example-pack/pack.json
```

Installation checks and backs up the baseline first, then creates a private
`codex/named-resource-packs` source revision with exactly nine reviewed host/bridge
paths. No generated game code is committed. Existing source or failed installer
attempts require inspection, not a silent reset/retry. Repeating a successful
unchanged installation verifies its receipt without rebuilding. Use a fresh
workspace for the clean setup recipe after creating this derived runtime revision.

Run without `--pack` for original assets. By default an invalid pack warns and
falls back to original assets; `--strict-pack` refuses launch instead. Invalid
disc/source/binary identity always refuses launch, even without strict-pack mode.
Inherited legacy/runtime override environment variables are removed.

Game cards persist under the workspace's ignored `userdata/memcards`; this is not
a claim that real game Save/Load is validated. Quick snapshots are scoped to the
runtime source revision and are not automatically imported from old experiments.
For a bounded hidden test use `--headless --seconds 220 --capture --fresh-user-data`.
This keeps test cards separate and mutes audio. Optional `--pad-script` is an
upstream input-test string, not a physical-controller test or an instruction to
attempt autonomous combat completion. Captures/logs stay private per run.

Pack runs now require explicit `--profile enhanced`; the default Original policy
refuses packs before runtime/disc checks. See [profile policy](PROFILES.md). This
is launch isolation, not a new in-game menu or certified accuracy mode.

## Scope and provenance

Install original GPL bridge code only into the isolated, successfully built
retail workspace. Preserve the exact baseline executable before any relink.
Require pinned upstream source and reviewed file hashes; reject unrelated edits.
Do not touch the adopted earlier evaluation checkout or prototype experiment.
Keep a private source revision, commands, binary hashes and failed logs.

The integration covers three positively identified full-disc read paths: the CD
image reader, raw ISO IOP host streams, and the EE SDK sector-read fallback. It
does not modify generated game functions, guest instructions or rendering state.
Source file edits are a small original integration recipe against exact upstream
file hashes; the upstream program is fetched privately, not vendored here.

## Loading and fallback

The launcher must verify the personal retail ISO and the installed binary/source
receipt, then resolve the existing named pack schema. Pack JSON never supplies
absolute disc offsets. Freeze validated original replacement bytes in a new
ignored per-run directory; never modify the ISO or publish extracted pixels.

The native bridge accepts only a complete launcher protocol: retail profile,
payload filename, resolved offset/length and expected SHA-256. It checks bounds,
exact payload length and actual payload digest before any write to a read buffer.
The digest uses the pinned upstream's existing generic SHA-256 implementation,
not copied game code. Configured data is immutable for that process.

No pack means original assets. Invalid/missing/mutated pack data must warn and
leave original read bytes unchanged, not throw into the game's reader. Invalid
ISO, source or binary identity must refuse launch, not bypass the disc gate.
Native raw-parameter environment variables are an internal protocol, not a
supported alternative to named/profile-verified packs. This is not a sandbox
against an owner deliberately altering their own executable or environment.

## Acceptance

- Original synthetic overlap/bounds/overflow/canary tests, malformed decimal,
  profile, file length and digest-callback tests; no game bytes in CI.
- Exact integration preimages and derived file hashes, path containment, no
  concurrent/unexplained installer job, baseline backup before relinking.
- Actual native build and bounded fresh enabled/disabled/invalid-pack runs;
  retain logs and unretouched same-subject original comparisons.
- Public source allowlist review, dependency attribution, CI and existing free
  Pages updates. Keep GPL tooling separate from the paused MIT lab.

One same-size native pixel/CLUT replacement only. No HD resizing, decoded RGBA
import, new material API, hot reload, prototype compatibility, physical-input,
full-game persistence or general remaster-fidelity claim follows from this MVP.

## Reproduced result and limits

Pinned upstream `14e956a1274332440273845fbab2c1f1e30c4a5a`, original integration
recipe and the personal retail ISO produced private runtime source revision
`193076584e277c95644dcbbb4a6922c3a59ca2b8`. The native bridge relink completed
with exit 0; the original executable was backed up first. All three fresh
220-second runs ended at the runtime deadline (124), not a crash or a playthrough.
The enabled run logs application through the EE sector reader and visibly changes
the ground. With the pack omitted or its SHA-256 deliberately invalid, the
selected original field-4741 PNG is byte-identical to the preserved fresh baseline.
The same invalid pack with `--strict-pack` refuses before spawning (exit 1);
a wrong prototype disc also refuses (exit 1), never a fallback around ownership.

`make_example_pack.py` writes an original uniform magenta diagnostic payload and
manifest into a new/empty directory. It reads no game assets and will not overwrite
an existing file. Its output matches the tested 8,256-byte payload exactly; this
is synthetic proof of replacement, not remaster artwork. Full-resolution
unchanged captures and provenance are in the
[English journal](https://yyoudi.github.io/god-hand-rs/dashboard/).

The original synthetic suite now has 81 tests, including a real portable C++
compile/run of 608,256 overlap/canary cases and malformed configuration checks.
The unit digest callback is a test double; the actual native bridge uses the
pinned runtime's SHA implementation and accepted the original diagnostic payload.
No game material is in tests or CI.

Known upstream capture padding is retained: original PNGs are 800x600 with
640x480 visible content. Generation still reports one unresolved error despite
exit 0. Neither this experiment nor a compiled binary proves complete translation,
real-time speed, hardware fidelity or full-game stability.
