# Experimental host pause while editing controls

Follow-up: [the checked opt-in variant contract](CONTROLS_INSTALL.md) describes
the new public integration and its separately reproduced native controls. The
original private observations below are historical, not silently relabeled.

Date: 9 November 2026. **Initial private research result, not an installation claim.**
`pc.py run` still uses the preserved evaluated native executable. Its existing
F1 controls overlay keeps the game running. The sampled experiment below uses
a separate private host-runtime build, not a new release or a Rust engine.

## Observable contract

Opening controls requests a cooperative executor hold; it does not inject Start
or suspend arbitrary OS threads. Report **waiting**, not paused, until an
executor boundary acknowledges readiness. Drain pending IOP work and require no
pending RPC, guest handler/completion, runnable VU/GIF work or GS SIGNAL stall.
While acknowledged, keep host drawing, UI commands and quit responsive, with
game pads neutral. On close, retain upstream's release-before-input behavior.
Rebase host pacing/deadline anchors, not guest cycle deadlines; do not count the
hold as game time to catch up. Stop must escape a hold without requiring close.

The original GPL [Gate](adapter/host_pause.hpp) is a small coordination primitive,
not a quiescence oracle. Its caller must establish readiness, own the executor
boundary and rebase the correct anchors. Its portable test uses only invented
ticks, blockers and clocks: cancellation, held executor/clock, repeated entry,
resume and stop. Passing that test alone does not establish native correctness.
The current public installer does **not** wire this primitive into upstream.
Entry/rebase callbacks run under the Gate mutex. They must not re-enter its
`now`/`request` methods or wait on another thread that needs that mutex. Readiness
is checked before taking it. Lock-order safety in future integrations still
requires review; this primitive is not a general-purpose pause-any-thread API.

## Actual native evidence

Upstream base: `14e956a1274332440273845fbab2c1f1e30c4a5a`, with the previously
tested original GPL pack bridge. Initial private host-pause source:
`67ac6a3544a8167786342960bd74d467fd8d46aa`. First-fight diagnostic source:
`4d7ebfceb28c7bba1558d4e4dbe83e96cd469b4f`. The public tooling baseline was
`bbb302bf6e55136bc86ede1fe0f4948be03af7e0`. These private runtime revision
identifiers are provenance, not public mirrors of generated game functions.
Only host files and original helper code were changed; guest functions and
instructions were not patched or newly inspected for this experiment.

| Control | Observed result |
| --- | --- |
| Early-scene enabled, 70-second bound | Two holds of 7,423 and 2,188 ms; field/cycle counters stable, EE/IOP RAM digests equal, injected UI sequence completes. Two originals from the first hold are byte-identical. |
| Stop with controls still open, 25-second bound | A 20,660 ms hold exits through the native time-limit/stop path with code 124, not a forced process kill. Field/cycle counters and RAM digests remain equal. |
| First-fight disabled, 240-second bound | No host hold; the two controls screenshots differ as the background continues. Rebind/save, live preference and input-release checks pass. |
| First-fight enabled, 240-second bound | One 7,709 ms hold at field 4,801; field/cycle counters stable and EE/IOP RAM digests equal. Two held originals are byte-identical. UI rebind/save and input-release checks pass, then fields advance again. |
| Bare first-fight control before either UI experiment | Both selected field-4,741 original PNGs equal the preserved baseline PNG byte-for-byte, including existing capture padding. |

The presentation trace for the held first-fight field contains 155 host presents
with one GS-image hash. That field's trace can include boundary presents, not
just the exact acknowledged interval; it is not an FPS or wall-time fidelity
measurement. RAM checks use noncryptographic digests, **not** exact comparisons
of every emulated device/register. Exact byte equality above applies separately
to the actual PNG originals.

Both first-fight processes finish at their intended deadline, code 124. Each
guarded UI script reports three successful file/live/hold checks; this is not a
new-process preference reload test, hardware keyboard/controller use or game
Save/Load. The existing upstream controls screen is reused, not authored here.
Only title/start inputs are scripted; there are no attacks or level-beating
loops. Warm private shader cache is reused, not presented as a fresh installer.
Original disc, operational executable/preferences and generated logic are kept.

## Retained failures and methodological correction

The first cold disabled 60-second trial reaches only part of its planned UI
script before the deadline. It is retained and is **not** called a complete UI
test pass. The later field-targeted disabled control completes all three checks.

A first field-delay variant linked, but would have skipped the whole host
controls tick, including chord/focus handling. It was rejected before runtime.
The tested revision delays only injected self-test steps; normal host/input
polling continues. No missing observation was replaced by a fabricated capture.

## Publication and remaining work

The journal publishes only two explicitly reviewed, unretouched original native
controls screenshots, with exact hashes, timestamps, runtime/revision and
same-landmark limitations. Their backgrounds/actors are not the same frame.
Neither is Bevy or PS2 hardware. Raw logs, RAM digests, runtime binaries, ISO,
ELF/cache data, generated game code and all other captures stay private.

Public code contains the original generic primitive and synthetic tests only.
The integration is experimental and **not shipped by the ISO setup/launcher**.
Next: make the checked host integration reproducible without modifying generated
code, preserve the baseline/disable path, then test focus, held physical input,
audio transitions and additional scenes before choosing a default policy.
Diagnostic hashing itself adds overhead; no timing/audio quality is certified.
An open menu can still be waiting for readiness, so do not equate a request with
an acknowledged pause. Full campaign/peripheral fidelity, actual game Save/Load,
HD resources, widescreen, FPS changes and multiplayer remain separate gates.
