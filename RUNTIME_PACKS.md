# Native pack bridge contract, version 1

Status: implementation/validation in progress. The metadata planner is already
tested; this document does not claim that the new public bridge runs yet.

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
