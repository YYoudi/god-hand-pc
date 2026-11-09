# Audio ownership at the experimental controls hold

9 November 2026. **The forced native race is reproduced; a separately checked,
opt-in audio-v2 variant now excludes the admitted consumer.** This is not an
audible-output or full-machine result. The public v1 controls-pause variant
and default Original executable remain preserved. This concerns our opt-in host
extension, not an assertion that LasVola's unmodified port has this pause bug.

## Source observation and falsifiable hypothesis

Audited the privately fetched GPL host/runtime source at upstream14e956a and
our installed derived sourceec1e2f83. No generated game instructions/functions
were changed or newly inspected. The callback zeroes its destination, checks
the atomic paused state, then locks the PCM queue and consumes it. An admitted
callback can pass that check just before the executor acknowledges the hold.
The initial hypothesis was that it can still consume host audio after the acknowledged boundary,
even though the previous guest field/cycle/RAM checks remain stable.

The actual native controls below now reproduce that interleaving. A screenshot
or stable guest RAM digest cannot establish host queue ownership. Do not infer audible glitches
or a normal-run occurrence rate from a deliberately forced race.

The audited IOP flush joins current worker work and completes pending cycles;
PCM submission/reset routes through that subsystem. This supports a producer
drain hypothesis, not an all-device theorem. Teardown and state-load ownership
must be reviewed separately. No raw PCM/game audio is a public or CI fixture.

## Acceptance before native integration

1. Use original invented threaded fixtures to distinguish a naked paused-state
   check from activity admission. Reproduce the old interleaving deliberately;
   refuse freeze while an admitted consumer remains, deny new consumers during
   a scoped freeze, and verify move/release/resume and concurrent exclusion.
2. Reproduce the interleaving in the **actual native callback** with explicitly
   guarded private diagnostics: delay one already-admitted callback before its
   PCM lock, request a hold, and observe queue counters before/after it runs.
   Retain a bounded timeout; never rely on a hung callback or fabricated audio.
3. Trial the original admission barrier in a separate private native revision.
   Acquire its freeze only after IOP/guest/VU/GIF readiness, before the Gate can
   acknowledge. Keep its token across the hold and release on cancellation,
   resume and stop. Do not hold the admission mutex across callback work or the
   entire pause; do not introduce a Gate/PCM lock-order inversion.
4. In the same forced control, prove the earlier callback finishes **before**
   acknowledgement; then compare actual queue/read/request/production state
   across a hold. Also run without forced diagnostics and verify normal stop,
   responsive controls and original scene controls. No audible-quality claim.
5. Preserve both installed variants, operational source/executable/PDB and ISO.
   This research must not silently change the existing installer fingerprint.
   A public recipe update needs a separately reviewed, reversible version/
   upgrade path before old installations are replaced or declared fixed.

The original [activity barrier](adapter/audio_activity.hpp) is a generic
consumer-admission primitive, wired only into the explicitly selected audio-v2
recipe, **not silently into v1 or the Original baseline**.
It does not drain producers, stop a device, prove machine quiescence or decide
the runtime's correct safe-point. Those remain caller/native acceptance gates.

## Actual results and retained failed controls

All tests use the same pinned upstream14e956a and read-only personal USA retail
ISO. Forced diagnostics are private host-only changes, not edits to generated
game functions. Only title/start and upstream controls self-tests are injected;
there are no attacks, level-beating loops or save imports. Native output is muted.

| Control | Observed result |
| --- | --- |
| v1-style callback, deliberately forced interleaving, 240s | An already-admitted callback runs after acknowledgement: queued samples6144→5186, read8192→9150, requested output frames+480, produced frames unchanged. Guest counters/RAM digests and held original PNGs remain stable. UI3 checks pass; hold7685ms. |
| Corrected callback, same forced diagnostic, 240s | Freeze is refused while the earlier consumer holds its lease. That callback completes with parked0, then the hold acknowledges. The nonempty queue2314 and all tracked read/request/production/priming/fade/gap counters remain equal across7699ms. UI3 and original-scene controls pass. |
| Corrected callback, no forced callback schedule, 240s | Hold/resume/UI3 and original-scene controls pass; queue counters remain equal across7689ms. **The queue is empty at this hold.** The extra nonempty-buffer assertion correctly fails and is retained; this is NOT unforced nonempty-queue proof. |
| Later corrected callback, ordinary earlier hold, 100s | With no forced callback schedule or guest-pad progression, the hold acknowledges at field1003. The queue has7196 samples; all tracked counters remain equal across7839ms. UI3 and held-original equality pass. This is a separate early, black-background control, not a rerun of the failed first-fight nonempty assertion or an audible-output result. |
| Exact installed public audio-v2, 240s | Actual17-file public recipe builds and runs; UI3 passes, hold7692ms, guest counters/RAM digests stable, two held originals byte-identical. Bare field4741 PNG equals the preserved baseline. No private audio diagnostic code is installed. |
| Exact public audio-v2 stop-open, 25s | Native deadline124 exits an acknowledged hold without closing controls first or forcibly killing the process. The retry control holds24676ms with probe0; no RAM-digest claim in that mode. |
| Public audio-v2 + strict named pack, 220s | Correct version/executable selected; the original diagnostic texture renders. Field4741 PNG equals the earlier enabled-pack original byte-for-byte. Mutating probes remain disabled despite stale inherited variables. |
| Subsequent public Original and default-v1 starts, 30s each | Each selects its own preserved executable/source and renders opening captures without relinking. These are startup rollback checks, not fresh full-scene/campaign coverage. |

All listed native processes finish at their intended deadline124. Public
launchers return0. The first public policy attempt failed **before its new native
launch**, with a UTF-8 decoding error in preflight; its preceding stop control
passed. Both failed attempts above remain in private evidence, not overwritten
by a successful retry or counted as successful nonempty/launch controls.

### Follow-up: one ordinary buffered hold

A later, separate100s run uses the **unchanged private corrected diagnostic**
`313e55ff1aa5e01fc7bda19c91f2a87a1b32c89d`, executable SHA-256
`e5caf086973fa60425320edaa1559d07e73be69a89b3924e3e21a4752ae92123`.
It does not relink or replace the exact installed public audio-v2 executable.
The activity header remains byte-identical to the checked public implementation.

The guarded controls test requests the earlier field1001 rather than4800:
`GODHAND_PC_CONTROLS_PROBE=1`, `GODHAND_PC_CONTROLS_PROBE_FIELD=1001`,
`GODHAND_PC_AUDIO_AUDIT=1`, **`GODHAND_PC_AUDIO_FORCE=0`** and an empty
`PS2X_PAD_SCRIPT`. Native arguments are `--iso <personal-disc> --headless
--time-limit 100`. The existing injected UI rebind/save/live/hold checks use
fresh scratch preferences/cards, not owner data. The run is muted; it reuses
the private shader cache and provides no performance measurement.

The hold acknowledges and resumes at field1003/cycle4934847807 after7839ms.
Both passive boundary snapshots report read3044, queued7196, requested798240,
produced799744, primed1, fade128 and gap0. No forced callback delay, injected
queue data or readiness condition is used to manufacture a nonempty queue.
All three UI checks pass; the two held PNG originals are byte-identical, and
the diagnostic EE/IOP digests stay equal. The native process ends at deadline124,
the validation driver returns0 and no forced termination is needed.

This establishes one naturally buffered boundary in that **earlier** retail run,
not all scenes or a natural race occurrence rate. The observed controls background
is black; no specific cinematic or gameplay identity is asserted. The snapshots
do not inspect PCM content, nonzero samples or a device's already queued output:
the buffer may contain digital silence. Audible output and click-free transitions
are still unverified. The earlier first-fight empty-queue failure is preserved,
not relabeled as this successful case. No visual comparison is invented for a
queue-counter result; its new captures remain private.

Source provenance:

- Unfixed private diagnostic: `ba5f73fa7cc5823bceefc1d378f6a8c3fff2dd89`.
- Corrected private diagnostic: `313e55ff1aa5e01fc7bda19c91f2a87a1b32c89d`.
- Clean exact public recipe tooling: `27c06d9782c5b556f38bd8ac37be0df205414f8c`.
- Installed public native source: `1ded3f337a7e9a711cf24521e81eeca10ce7abb4`.
- Installed public executable SHA-256: `0b2d0ca78d8a8127fbef0fb3136bb56a368e64ece723ea9c8ca36e33a570cd2f`.
- Shared original activity-header SHA-256: `15b275932b63c3d0070cdfae90764e2a735f9521d35218637627b6d0f9ec5f19`, byte-identical in the private corrected experiment and public implementation.
- Clean public launch-policy tooling: `4141e569802e9ff0e7ab34d2671a071fcbf77953`.

These are provenance identifiers, not public game source/binaries. The original
operational and v1 source/executable/PDB bytes are preserved. audio-v2 has its
own17-file source manifest, private executable/PDB and installed pointer. See
[versioned installation and rollback](CONTROLS_INSTALL.md). No visual before/after
pair is invented for this nonvisual ownership change; existing original scene
controls remain unchanged and the actual journal is captured separately.

## UTF-8 process guard and its scope

An actual public preflight returned an invalid-UTF-8 byte error before creating
its launch receipt. The process-preservation guard now requests CSV and inspects
native bytes for the ASCII image name, without decoding localized memory/text
columns. Unknown/NUL-containing output and command failures refuse safely.
Invented byte fixtures cover invalid UTF-8 and case-insensitive active names.
An actual second UTF-8-mode launch is refused while the owned native game runs,
before creating a second launch receipt or native process. Terminal native
handles are released in the private driver before its next startup check.

The exact transient invalid-byte output was not reproduced by a later live
table query (that output decoded correctly). Do not assert a measured occurrence
rate, a precise formatter/timing cause or that every Windows encoding mode is
fixed. The original error log is retained; the raw-byte guard and native refusal
are the bounded reproduced controls.

## Focus and held-input scope

The existing upstream controls code handles focus transitions and binding
cancellation. Its input hold has a two-second cap; a passed diagnostic
`holdcheck` means the overlay/hold flags cleared, not proof that arbitrary
physical keys cannot leak after a long hold. Scripted guest-pad inputs also
have a separate merge path. Preserve these distinctions; do not replace source
observations or synthetic button tests with a hardware/focus certificate.

Genuine game Save/Load, hardware input, audible output, later scenes and the full
campaign remain open. No new Rust work, game assets, generated game code, native
binaries, raw PCM or private traces are published by this investigation.
The one ordinary nonempty-buffer result above does not establish already queued
device-buffer ownership, audible transitions, broader producer/peripheral
ownership or other scene coverage. Those remain separate gates; neither the
earlier empty control nor the forced schedule silently satisfies them.
