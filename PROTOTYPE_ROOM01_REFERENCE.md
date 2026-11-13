# Room01: an actual emulator Room Jump reference

13 November 2026. New emulated prototype evidence; existing native evidence is
reused explicitly. No new native build, correction, retail result or adoption.

## Exact route

Same PCSX2v2.8.2/source/executable/disc profile and private CPU/GS configuration
as PROTOTYPE_EMULATOR_REFERENCE.md. The finite power-on route plus Circle9100
opens the actual Room Jump selector: Stage1/Room00/Point0, highlightStage, at9700.
The v5 process closes normally0 after296.750s, within300s operator budget.

A NEW private emulator snapshot is exported through System / Save state / Save
to file, without modifying the disc or importing user cards/saves. It is13,701,468
bytes, SHA-256`4c63d8655eeae6b0ae1ac6a35b4cd18462cfdda56a9cde05ec3807b027bd9a2e`.
It stays ignored/private onG:. This is not genuine game Save/exit/Load evidence.
The emulator explicitly warns that MTVU may make snapshots unstable; that warning
is not suppressed, and successful file creation is not treated as restoration.

The original pinned recording playback interface supports a from-state header
and adjacent `<recording>_SaveState.p2s`. A private byte-identical copy is supplied;
no state is patched. The new finite recording uses Down100..111, Right200..211,
Down300..311, Circle400..411, then neutral input through2400. See original event
metadata in scenarios/prototype-emulator-room01-reference-v1.json. No recording
binary, state, BIOS, ISO, game asset, code or dump is distributed.

## What actually happened

- Initial paused snapshot load0 renders BLACK, not a proven visible selector.
- Actual playback300 visibly shows Stage1/Room01/Point0 before Circle400.
  This later observation, not the load log, qualifies the selected destination.
- Actual2400 auto-pauses on the original interior: Gene, two enemies, carpet,
  arches, vases and HUD. PriorRoom00 attacks explain different starting health;
  no health equality or native health bug is inferred.
- F8 while paused schedules an export but does not produce the completed PNG.
  Resume allows the pending original capture, then normal UI shutdown follows.
  Closure observes2891; terminal recording header2892. Exact PNG guest frame
  is unknown. Do not label the F8 PNG as exactly2400.
- The resulting file has493additional complete pad-frame records. Port0 is
  verified neutral; disabledport1 is allzero. An initial generic two-neutral-pad
  assertion FAILED and is retained, rather than silently claiming all-port
  equivalence. Authored header/game-name and authored frame-data bytes remain;
  the working total-frame header and length change. Authored duplicate retained.
- v6 exits normally0 after212.860s. The180s operator budget is OVERRUN32.860s,
  not a deadline guarantee or a reason to kill/restart. No automatic fighting,
  guest-state flags, physical-key assumption or compiler/native overlap.

Original disc and owner BIOS/global configuration hashes remain unchanged.
The owned snapshot and its playback copy remain byte-identical after the test.

## Original comparison, not an accuracy certificate

The new F8 original is827x620 display-sized PNG, internal512x448/1x/4:3;
file-export UTC timestamp, no recording OSD or desktop. No crop, resize, color
adjustment, image registration, per-object/camera fit or asset substitution.

The retained native image is the PREVIOUS290b321c Stage1/Room01/Point0 entry3100,
from the earlier CLI room cycle,640x480, with its original runtime/revision/date.
The same carpet/arches/vases establish a named common subject, not equal camera
parameters, health, animation, time, simulation state or pixel correspondence.
The gallery is labeled SAME-LANDMARK, explicitly not SAME-FRAME. A native rendered
frame is not newly obtained just because a reference is now available.

Neither selected Room01 snapshot by itself establishes or repairs the retained
detached-cloak-like observation in another scene. No artificial defect is inferred
from resolution, pose or health differences. Game imagery retains separate rights;
owner-requested selected screenshots are not rights-holder authorization.

## Next useful test

Qualify a reference for one concrete retained discrepancy, beginning with the
Room00/Point1 detached-cloak-like case only after matching destination/view/state
well enough to avoid animation/camera confounds. Diagnose the actual layer; a
common runtime correction requires original before/after and native prototype
AND retail regression evidence. Do not resume a Rust rewrite, rebuild menus,
repeat completed input/helper proofs or claim remaster/optimization support.
