# Restart-required native video preferences

This is a small pre-launch preference boundary, **not an in-game graphics menu**.
RM03 remains in progress. It reuses the pinned runtime's internal-scale option;
there is no new renderer, FPS unlock, widescreen or resolution-independent HUD.

## Source audit

The evaluated host source193076584e277c95644dcbbb4a6922c3a59ca2b8 descends from
LasVola14e956a1274332440273845fbab2c1f1e30c4a5a. Its `src/main.cpp` reads only
the executable-directory `godhand.ini`; there is no alternative-config CLI.
Recognized CLI values precede existing environment values, which precede INI
defaults. We do not edit that INI or invent a config-path argument.

`ps2_game_menu.cpp` gates F2 on an active PCSX2 GS backend. That is **not a
working native-GS graphics menu**. F1 is the existing, separately tested controls
screen, not a full video settings screen.

`gs_gpu_backend.cpp` reads `PS2X_GS_SCALE` at startup and clamps it1..8. It then
reduces the scale if the sample-plane buffer would exceed the reported OpenGL
storage-block limit. A requested scale is **not necessarily the effective one**.
Internal sampling scale is not output framebuffer size, window resolution or an
accuracy certificate. Native initialization logs the effective value when >1;
absence of that line alone does not prove1x or successful initialization.

Vsync, simulation timing, alternate backends and fullscreen/window flags are not
exposed here. In particular, disabling vsync is not a safe FPS-unlock proof.

## Commands

After setting up an existing `retail-*` workspace:

```powershell
python pc.py video-settings --workspace-name retail-setup-v2 --internal-scale 2
python pc.py video-settings --workspace-name retail-setup-v2
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --video-settings
python pc.py video-settings --workspace-name retail-setup-v2 --reset
```

`--internal-scale` accepts integer1..8, the source-audited range, **not eight
locally verified hardware modes**. Restart the process to apply a change.
`--reset` records a new immutable revision and supplies no video override on the
next explicitly selected run. It returns to upstream INI behavior, not a
hardcoded value or claimed original PS2 settings. No history is deleted.

Without `run --video-settings`, the launcher does not load this store at all.
Default Original and previous Enhanced commands retain their old meaning.
Original plus the flag refuses before workspace/disc/native-process work; use Enhanced
explicitly. Selecting missing, corrupt or locked preferences refuses native
spawn rather than silently choosing a different configuration.

The flag is independent of the existing explicit pack/controls version flags;
it does not install, select or upgrade a native variant. It does not make old
unsupported HD/controls combinations valid. `--fresh-user-data` still isolates
input preferences/cards/states; when the video flag is supplied it deliberately
snapshots the selected workspace's video revision, rather than guessing a fresh
video default. It never edits native INIs or a player's controls.

## Storage and receipt contract

Ignored `userdata/video/` contains a small `current.json` pointer and immutable
SHA-256-named JSON revisions. Each revision has exactly `schema:1`,
`native_scale` (integer1..8 or null for reset), and `previous` (hash or null).
The previous hash retains the chain of settings/reset operations. An exclusive
writer lock prevents cooperative writers from overwriting each other; stale
locks require inspection, not automatic stealing. Pointer replacement is atomic.
Interrupted writes leave old/current or pending evidence for review. This is not
a guarantee against malicious concurrent filesystem mutation or power loss.

Reject duplicate/unknown keys, wrong types/bounds, nonfinite/malformed JSON,
tampered hashes, symlinks/reparse points, hardlinked files and metadata >4096
bytes. No arbitrary runtime environment key, native INI fragment, dump, self-test
or generated game code is accepted through this schema.

The launch freezes the selected original revision bytes into its private
directory, records their hash and requested value, and sets only native renderer
and scale for a non-reset selection. The receipt deliberately leaves effective
scale unproven: inspect actual native initialization/rendering separately.
Later preference changes cannot retroactively relabel the launch snapshot.

The Python writer also accepts an optional keyword-only `expected_revision` for
a future editor/menu. It compares that immutable identifier under the existing
writer lock, before writing a new revision. Explicit null means create only while
absent; a stale identifier refuses without overwriting newer preferences.
Omitting it preserves current CLI behavior. This prerequisite has invented-data
and real-thread tests only: no native menu, request/ack bridge or new in-game
save action is integrated by this change.

`adapter/video_menu_model.hpp` is a separate original, game-free state model for
that future surface. Portable tests cover hold-before-edit, exclusive opening,
close with an in-flight request, reply identity/selection, stale and unknown
write outcomes, bounded requests and immutable current-run intent. A caller's
hold Boolean is not runtime readiness evidence. There is no drawn overlay,
native input owner, IPC implementation or new runtime acceptance from this model.
The later [native view and host-binding source](NATIVE_MENU.md) now uses actual
host APIs but remains unlinked/uninstalled, with no concrete storage transport.
Its portable doubles and real-header syntax checks are not a new game result.

## Validation status

Original invented-data tests cover history/reset/reload, exact frozen bytes,
strict parsing, metadata/path limits, aliases, locks, atomic replacement failure,
CLI routing, policy refusal, safe environment and unselected defaults.

## Actual runtime controls — 10 November 2026

Clean tooling8b6456de8bfe4b61cfe7dcace97ca79ca869ae18 launched the first
unselected baseline. The later controls use0d9fb76714f72567633bda8149c789e0d5f46d81:
that second commit only clarifies the policy receipt text and its assertion,
not the environment, preference parser or native executable. Each private launch
receipt records its exact tooling revision; none is relabeled as a later build.

Unchanged baseline source193076584e277c95644dcbbb4a6922c3a59ca2b8,
executable SHA-256
`eaed174f4d0c1df5530e5a65b2d53611a14d3037c9e01a3e0aa02c8d6a0d4e53`.
The separate combined control retains source6ae2aafe8c19e00a67d6f026450341a900e09af0,
executable SHA-256
`eff438b141b3c928aef92819cd57751cd2704a5feb25aec61b3d1fb8d1b861d9`.
No native compilation, clone, game generation or INI edit was needed.

All six target-complete public launches return launcher0/native124 (normal
requested deadline), without forced termination or observed shader errors:

| Control | Limit | Observed native scale | Original field4741 PNG |
| --- | --- | --- | --- |
| Original, before storing settings |220s|3x|`9bd97cff...`|
| Enhanced, explicitly select saved2 |220s|2x|`591f0fcf...`|
| New process, same saved revision2 |220s|2x|exactly the same `591f0fcf...`|
| Original, ignore active saved2 |220s|3x|exactly the same `9bd97cff...`|
| Explicit reset, later300s trial |300s|3x|exactly the same `9bd97cff...`|
| Explicit HD/audio-v2 composite, saved2 |360s|2x|`ac70765c...`|

Effective values come from native initialization lines, not just our receipt's
request. Both3x and2x originals remain640x480. The composite logs a512x512 upload
at scale2 and the unchanged original renderer export visibly contains the authored
green/orange diagnostic on the right wooden surfaces. Counts remain unread;
neither a planned pack nor log submission alone is treated as application proof.
No controls UI/hold or new audio-device behavior is inferred from this launch.

Full selected original hashes:

- INI3x: `9bd97cff522321767ad5e101e11989751131ca32c2a2a7e76d55d6e80ab6e5be`.
- Saved2x: `591f0fcf7bf24af22c68002578a5d53d3d527f4ee0f3e2dd2332d0ecff5ef199`.

The journal comparison preserves full unchanged PNGs, actual UTC capture times,
native and tooling identities. This is a same-field PC scale comparison, **not
PS2-reference fidelity, a quality improvement, an artwork upgrade or a benchmark**.

Additional actual public CLI controls refuse malformed duplicate-key preferences
and Original plus the flag (exit1, no native spawn). The malformed pointer existed
only temporarily in this experiment's newly created store; both original pointer
files were preserved and the valid pointer restored. Final reset leaves a new
null-scale revision and retains every earlier revision. Native/player INIs and
controls were not edited. Ordinary runs still disable injected UI probes and
clear inherited private runtime variables.

Two nonpassing target observations are retained separately:

- An initial no-flag control lost its observer and native process handles around
  a context interruption. Its receipt remains running without a terminal exit;
  it is **not** counted as passed or inferred124. Completed earlier cases were
  not rerun. Only the unfinished controls resumed after process absence was checked.
- The first220s reset returns normally and logs3x, but its last requested export
  is4621, not4741. That target check fails; it is not hidden, cropped or relabeled.
  The separate300s reset reproduces the baseline4741 PNG. There is no diagnosis of
  slowdown, hardware isolation or reliable performance gain from this.

Private receipts/logs/originals remain under the ignored dated experiment;
`validation.json`, `resumed-validation.json`, `final-validation.json` and the
separate driver logs preserve the sequence. Only the explicitly reviewed3x/2x
pair is published, not a media sweep or the private asset-envelope contents.
All six installed source/executable/INI/PDB identities, original ISO and the
historical MIT lab's four WIP hashes were reverified unchanged. Preserving the
older baseline PDB is not a new matching-symbol claim. The preexisting
shared native object cache remains composite, not a baseline cache. About5.4GB
free remains on G:; review capacity before another native build/clone, never
delete retained evidence automatically.

221 invented-data tests run in the active tree and an actual separate checkout
of0d9fb76 with an asserted import root:218pass/three Windows symlink-privilege
skips. CI receives invented fixtures only. These native controls cover2x/3x on
the evaluated machine and two retained variants, not every scale/variant/GPU.
Broader graphics UI/usability, physical input/audio, genuine Save/exit/Load and
campaign fidelity remain open. RM03 and the full faithful-PC goal stay active.
