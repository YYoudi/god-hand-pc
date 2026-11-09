# Audio ownership at the experimental controls hold

9 November 2026. Investigation and acceptance contract, **not a shipped audio
fix or an audible-output result**. The checked public v1 controls-pause variant
and default Original executable remain preserved. This concerns our opt-in host
extension, not an assertion that LasVola's unmodified port has this pause bug.

## Source observation and falsifiable hypothesis

Audited the privately fetched GPL host/runtime source at upstream14e956a and
our installed derived sourceec1e2f83. No generated game instructions/functions
were changed or newly inspected. The callback zeroes its destination, checks
the atomic paused state, then locks the PCM queue and consumes it. An admitted
callback can pass that check just before the executor acknowledges the hold.
**Hypothesis:** it can still consume host audio after the acknowledged boundary,
even though the previous guest field/cycle/RAM checks remain stable.

This is an interleaving argument until reproduced. A screenshot or stable guest
RAM digest cannot establish host queue ownership. Do not infer audible glitches
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
consumer-admission primitive, **not wired into the current public installer**.
It does not drain producers, stop a device, prove machine quiescence or decide
the runtime's correct safe-point. Those remain caller/native acceptance gates.

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
