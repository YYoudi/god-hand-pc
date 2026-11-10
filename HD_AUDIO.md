# Explicit HD + audio-v2 composition

10 November 2026. **The exact additive recipe now builds and passes sampled
native hold/render/stop/rollback controls.** It remains experimental, not a
default upgrade or a complete PC/remaster result. Old HD/control combinations
remain refused unless the new exact version and both capabilities are selected.
Original stays unchanged.

The additive `gpu-audio-v3` HD version composes existing GPU-v2 and audio-v2
recipes over the same pinned named-pack baseline. Six modified host files and
eight original helper copies have disjoint destinations; no fuzzy overlapping
edits, guest function changes or game regeneration. Component and joint
fingerprints are checked separately. The old component recipe bytes, source,
binaries, pointers and fingerprints retain their existing meanings.

```powershell
python pc.py install-hd-textures --workspace-name retail-setup-v2 --version gpu-audio-v3
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --hd-textures --hd-textures-version gpu-audio-v3 --controls-pause --controls-pause-version audio-v2 --hd-pack .local/second-surface-example/pack.json --strict-hd-pack
```

The [original second-surface example](SECOND_RESOURCE.md) needs no game pixels
to author its external image. Its runtime envelope includes a private personal-
ISO source reference; never publish that envelope. Omit `--hd-pack` for the
same combined binary's original assets. Without all composite selection flags,
incomplete/old-version combinations refuse before filesystem/disc/process.
Same-size+HD composition remains unsupported. Normal launches disable mutating
controls self-tests and probes; no acknowledged hold or visible replacement is
inferred merely from requested flags or upload/submission logs.

## Exact build and identities

Clean public tooling: `6e9c2761956eb45b6368cb3625746038c1de4e38`.
Pinned upstream: `14e956a1274332440273845fbab2c1f1e30c4a5a`.
Private native source: `6ae2aafe8c19e00a67d6f026450341a900e09af0`.

- Composite fingerprint: `72ceaf2309cd86aedbc1d9f122f36464bf3a65a82874a69594aad65f86ea8fa9`.
- GPU-v2 component: `37018376887e83eac9f3356f528f062811ac152f6715131abae2a4875e1cbcb5`.
- Audio-v2 component: `1b1202fc25b238017c9c6b02b1e297855b8f18c928bfaf173e994e3e8a5b5624`.
- Executable: `eff438b141b3c928aef92819cd57751cd2704a5feb25aec61b3d1fb8d1b861d9`.
- New PDB: `6671cc3c8229118292c8f40a38b955c1a8ca6bc9f9019b50363730014e810e54`.

Actual public CLI configure0/build0,22-file composite source manifest. Ninja
compiles six host units (five runtime units plus our HD bridge) and links; no
game regeneration or new clone. MSVC retains its `/Ob1` overridden by `/Ob2`
warnings, not a warning-free claim. Original source/executable/prior PDB restored
before the additive pointer is published; the prior PDB is not asserted to match
the old executable's symbols. Old five variant pointers/binaries/fingerprints
remain verified. Shared object/CMake caches now describe the composite, not the
restored baseline: reconfigure/force affected units before any future relink.

Private receipts: `G:\God-Hand-PC\.local\hd-audio-composite-2026-11-10\`.
No private game source, reference/envelope, executable/PDB or save is published.

## Actual native controls

All probes use the personal verified retail ISO, fresh scratch cards/controls/
quick-state paths, muted headless output and bounded deadlines. Long probes use
the retained title/start/Start script, no attacks, level completion or save import.
Normal public launches disable stale inherited self-tests and probes explicitly.
The selected source4 image/format and artwork are from [SECOND_RESOURCE.md](SECOND_RESOURCE.md).

| Control on the new exact executable | Observed result |
| --- | --- |
| Public composite + valid HD pack,300s | Uploaded/submitted counts-unread; actual field4741 PNG equals prior source4 enabled `cce21397…`. Controls pause requested, but no actual hold is inferred without opening controls. |
| Same binary, no pack,220s | Original-assets field4741 `9bd97cff…`. No HD upload; component identities retained. |
| Same binary, invalid image hash,220s | Public preflight fallback clears HD input; same `9bd97cff…` PNG. Not a native checksum test. |
| Guarded direct native UI/hold/resume,300s | UI3 checks pass, parked/resumed field4801/cycle23621128446; hold7685ms, EE/IOP digests agree and first two held originals are byte-identical. Normal pre-UI field4741 remains `cce21397…`. |
| Same executable, pause disabled,300s | UI3 passes without pause logs; first two UI originals differ. This is a flag control, not a different binary or hardware-input test. |
| Stop with controls still open,25s | Probe0/no digest assertion, acknowledged hold exits at normal deadline124 without closing controls or forcibly killing the process. Self-test intentionally does not reach its `done` step. |
| Direct native one-reference-byte negative,300s | Same authored image, valid envelope hash, source-reference R at(47,59) changed privately; GPU work submitted/counts-unread but sampled PNG equals absent/fallback. Not zero matches throughout the game. |

Eight public launchers0/natives124 include five **30-second startup-only** old
Original/controls-v1/audio-v2/HD-v1/GPU-v2 selection controls. These are not another
first-fight or campaign proof for those versions. Four actual strict-invalid,
Original, incomplete-composite and old-GPU+audio-v2 requests refuse before native
spawn. All four initial direct probes end124/observer0, no forced kill/shader error.

### Separate observation proving forward progress after resume

The first UI probe established a hold and a `resumed` message, but had no present
CSV or later-field export. That is weaker than observed forward simulation.
Retain it; do not relabel its evidence. A separate300s same-executable follow-up
adds only the existing `PS2X_FRAME_TIMES` hook and field4740/4800/5000 screenshot
requests, with the same input, UI script and source4 envelope, no relink.

It acknowledges/resumes at field4801/cycle23621128446 after7724ms; EE/IOP digests
agree, first two held PNGs are exact, all three UI checks pass. Afterwards the
CSV observes fields up to5485 and an original actual-field5001 PNG is exported.
Thus forward progress is observed, not inferred only from a log label. The CSV
is a host-present trace, **not game FPS**, CPU/GPU timing, every-frame fidelity or
proof of the audio device queue. Native124/observer0, no forced termination.

The UI checks exercise scratch binding edit/save, stored/live `Square=Keyboard/U`
and release of the overlay input hold. They are not physical keyboard/controller
or genuine game SaveExitLoad evidence. The audio-v2 admission helper is unchanged;
this composite contains no new PCM/nonempty-queue or audible-output proof.

## Selected unchanged originals and remaining gates

The comparison gallery records new combined original-assets/authored observations
at actual4741 using existing byte-identical640x480 files, with new source/time/
runtime provenance, not rewritten old observations. A separate UI pair shows
before rebinding versus the captured unsaved U binding while held at4801. Its
background field is fixed, UI state intentionally differs; no artwork/fidelity
improvement is implied. Capture times are native PNG filesystem UTC last-write
times; full originals are unretouched and downloadable. Older800x600 results
and failed alignment hypotheses remain unchanged. No source textures are uploaded.

205 invented-data tests locally:203pass/two Windows symlink-privilege skips. New
tests cover exact component union/identities, helper/source/pointer drift,
coexistence, failed/live build preservation, refusal before I/O and composite
launcher environment/receipts/CLI routing. Initial cross-pointer test wrongly
expected only ValueError; actual FileNotFoundError refusal is valid. Corrected
the test's exception contract, not production tolerance; retained failed log.

PC11's sampled build/hold/render/rollback scope now passes. Other scenes,
peripherals/focus, audible/nonempty-device audio and full-machine quiescence
remain unverified. Same-size+HD and all old unsupported combinations remain
refused; no new default, automatic component upgrade or persistent cache.

The full PC/remaster goal, genuine SaveExitLoad and campaign/PS2 fidelity remain
open. No performance gain, cache, widescreen/FPS/lighting/multiplayer or hardware-
audio claim follows from composing two previously sampled host extensions.
