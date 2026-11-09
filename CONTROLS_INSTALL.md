# Checked experimental controls-pause variant

9 November 2026. **Locally built and observed, experimental and opt-in.** The
exact clean public recipe now reproduces the bounded host-pause experiment in a
separate variant, while preserving the operational baseline. Earlier private
evidence is retained in [CONTROLS_PAUSE.md](CONTROLS_PAUSE.md). Neither portable
tests nor these sampled native controls prove a full machine or campaign.

## Explicit installation and launch

Version selection is additive: existing commands and installed receipts continue
to mean **v1**. Its fingerprint, source, executable and private directory are
preserved. The new **audio-v2** recipe has synthetic coexistence/refusal controls;
its exact public build/runtime validation is still pending at this implementation
boundary. Do not call a private diagnostic build an installed audio-v2 result.

```powershell
python pc.py install-controls-pause --workspace-name retail-setup-v2 --version audio-v2
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --controls-pause --controls-pause-version audio-v2
```

audio-v2 lives in `controls-audio-v2/`, with a separate pointer, source worktree,
executable/PDB and composite **17-file** manifest. v1 remains in `controls/` with
its original 16-file manifest, including older receipts without a version field.
No pointer or previous variant is overwritten. Omitting the pause flag selects
the baseline; omitting the version while requesting pause still selects v1.
A version argument without `--controls-pause`, or any pause with Original, is
refused before runtime/disc access. See [the audio contract](AUDIO_HOLD.md).

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
ordinary host/input/focus polling. These tests use no game inputs.

## Reproduced native controls

The exact clean installer tooling revision was
`691388c6555b98109c447b4a8b0da0d7030d3307` (later tests/docs do not change its
native recipe). Pinned upstream remains `14e956a1274332440273845fbab2c1f1e30c4a5a`;
the preserved operational pack-bridge source is
`193076584e277c95644dcbbb4a6922c3a59ca2b8`. The new private derived host source is
`ec1e2f83a6c2f372f96172ce67b81b3767841c98`, executable SHA-256
`9f5a5f36c9575c5a0d950906b1e39461c3db086396ba243281b3f7913cbb4068`.
These identifiers are provenance, not downloadable game source/binaries.

Both public configure/build steps return zero. The separate 16-file source
worktree and executable pass composite verification. The original source,
executable **and prior PDB bytes** are restored; the ISO and baseline INI/controls
are unchanged. This uses existing private generation/build inputs, not a fresh
generation or a claim that the restored older PDB matches the baseline exe.

| Actual control | Observed result |
| --- | --- |
| Same new variant, host pause disabled, 240-second bound | No host hold; the background continues. Guarded upstream UI rebind/save/live/release checks pass. Bare field-4741 PNG equals the preserved original baseline byte-for-byte. |
| Same variant, host pause enabled, 240-second bound | A 7,740 ms acknowledged first-fight hold at field 4801; field/cycle counters stable, EE/IOP RAM digests equal, two held original PNGs byte-identical. UI checks pass and fields advance after close. Bare field-4741 PNG also equals the original baseline. |
| Stop while controls remain open, 25-second bound | A 24,593 ms hold at field 2 escapes through native stop/time-limit, exit 124 without forced kill; counters and diagnostic RAM digests remain equal. |
| Diagnostic hashing and field delay disabled, 30-second bound | An early 7,428 ms hold/resume completes with responsive injected UI and byte-identical held PNGs, then native deadline124. Log explicitly records probe0: no RAM-digest equality is asserted in this mode. |
| Actual public Enhanced + controls-pause + strict named pack, 220-second bound | Launcher selects the verified variant, explicitly disables all mutating probes despite stale inherited values, and renders the original magenta diagnostic. Field-4741 PNG equals the earlier enabled-pack original byte-for-byte. No F1/self-test is injected in this public run. |
| Subsequent actual public default Original, 220-second bound | Launcher selects the preserved baseline, requests no host pause/probe/pack, and reproduces the preserved original field-4741 PNG byte-for-byte without relinking. |

Every listed native process ends at its intended deadline (124); both public
launchers return zero, with no forced process termination. The long targeted
tests use only title/start inputs, not attacks or autonomous level completion.
RAM checks are noncryptographic digests, not every device/register's exact bytes.
Hash diagnostics and reused warm private shader cache are not performance/audio
evidence. Screenshots in the new [comparison](https://yyoudi.github.io/god-hand-pc/comparisons.html#2026-11-09-checked-controls-install)
are actual unretouched 800x600 originals, same-landmark rather than same-frame;
known black padding is retained. The controls UI itself remains upstream work.

## Remaining acceptance

The checked build, sampled controls, baseline restoration and public opt-in/
default selection gates above pass locally. Additional focus/held physical input,
audible audio/queue transitions, peripherals,
more scenes and genuine game Save → exit → Load remain open. This is not a full
PC settings menu, HD support, FPS unlock or full-game accuracy claim.
