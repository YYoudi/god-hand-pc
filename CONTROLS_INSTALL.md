# Checked experimental controls-pause variant

9 November 2026. **Implementation awaiting native validation of this exact public
recipe.** Earlier private evidence is in [CONTROLS_PAUSE.md](CONTROLS_PAUSE.md).
Portable tests are not a native runtime, full-machine or campaign proof.

## Explicit installation and launch

Prerequisite: a successful personal USA retail ISO setup and `install-packs` in
the same workspace, with the pinned source and recorded executable unchanged.
Windows/MSVC and the previously recorded setup environment are required.

```powershell
python pc.py install-controls-pause --workspace-name retail-setup-v2
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --controls-pause
```

This is opt-in. The default Original launch still selects the original installed
pack-bridge executable, without a host pause. Original refuses `--controls-pause`
before accessing the disc/runtime. Enhanced without the flag also retains that
baseline. Closing F1 controls requests resume; the UI says waiting until an
executor-owned safe-point acknowledges a hold. It does not inject Start or
arbitrarily suspend Windows threads. Packs remain separately opt-in.

Ordinary launches explicitly set pause to zero unless requested, set diagnostic
probe and field delay to zero, and disable upstream mutating controls self-tests.
This overrides native INI pass-through as well as inherited environment settings.
A launch receipt records a request, not proof of an acknowledged hold.

## Source and preservation contract

The original GPL integration selects four exact normalized open-source host-file
preimages and three original additions. No game addresses, generated guest
functions, resource bytes or instructions are patched. The public Gate is the
same generic primitive used in the earlier private trial. Caller readiness checks
remain conservative, sampled evidence, not an all-device quiescence proof.

The installer:

1. Takes an exclusive workspace setup lock and controls-layer lock; refuses live
   games, an active pack install, a previous unfinished attempt or source drift.
2. Verifies the existing nine-file pack bridge, executable and original ISO.
   Copies the operational executable **and any existing PDB** separately before
   relinking. An older PDB is preserved, not asserted to match that executable.
3. Creates a private derived branch, applies only the reviewed host edits, and
   commits them. Reconfigures, explicitly invalidates the four host source units,
   then rebuilds using the existing private generated inputs/object cache.
   This is not a fresh game-generation/installer proof.
4. Copies the derived executable, PDB and one initial general INI snapshot to a
   separate per-run `controls/runs/<id>/native/` folder. Creates a separate clean
   source worktree. It does not copy game research into this public repository.
5. Preserves relinked outputs, restores the original source revision/branch,
   executable and PDB, re-verifies the base and unchanged ISO, then records the
   installed-variant pointer. General INI is a private initial snapshot, not a
   continuously synchronized or reset settings file. Workspace controls/cards
   retain their existing ownership; first adoption reads the baseline controls.

Every requested variant launch rechecks the original base, adapter fingerprints,
the composite 16-file source manifest, clean derived source and derived executable.
Changed upstream/preimages, regeneration drift or a changed executable are
refused, not silently adapted. Returning to a normal launch requires no relink.

## Failure and recovery

Never delete a lock or retry solely because an observer timed out. Check the
receipt's exact child PID/process and logs. A live child/interrupted build retains
locks and evidence. A terminal build failure restores only a clean, exactly owned
derived checkout, retains all output/attempt evidence and refuses automatic retry.
Unrelated source edits are never reset; inspect and preserve them manually.
No `git reset --hard`, recursive cleanup or original-disc changes are performed.

Synthetic invented Git/source/executable fixtures verify source planning,
separate variant identity, byte restoration (including PDB/INI), repeated-install
verification, terminal failure, live-child interruption, unrelated-edit
preservation, fingerprint/source/executable drift and default policy refusal.
Actual C++ controls verify that field-delay routing requires both a diagnostic
flag and a nonzero self-test script; only injected test steps are delayed, never
ordinary host/input/focus polling. Native integration must still be built/run.

## Remaining acceptance

Build this exact clean public recipe, run disabled/enabled/stop controls, compare
the original sampled scene, and verify baseline restoration/normal launch.
Additional focus/held physical input, audible audio/queue transitions, peripherals,
more scenes and genuine game Save → exit → Load remain open. This is not a full
PC settings menu, HD support, FPS unlock or full-game accuracy claim.
