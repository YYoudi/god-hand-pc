# Prototype emulator reference: actual gameplay and debug menu

13 November 2026. New reference executions, not a native build or runtime fix.
The earlier native originals are reused with their original dates/provenance.

## Actual setup

Local PCSX2 v2.8.2 executable SHA-256
`982c7c62600a999cf15a25c18349426166c785e7867b2fcc5018d733245b71a3`.
Official source tag resolves to
`fd9d310ccbb6b8b62c976da8886a3c8fd3a10ff3`.
Personal prototype SLPM-66550 / CRC18E5A0CA. BIOS/configuration are private on G:;
owner originals and disc remain unchanged. No cards, saves or accounts copied.
CPU/GS settings selectively reuse the owner's configuration; this is not stock
PCSX2 or a hardware-accuracy certificate. Automatic D3D12, internal1x512x448,
display4:3, muted; compatibility patches disabled warning retained.

The actual data directory is the configured root plus `PCSX2/`. Earlier wrong
outer-directory setup/wizard and CUE/CDVD failures remain private evidence.
The original CUE names a different BIN; it was not edited. Direct original BIN
boot is the observed successful route.

## Finite input, not physical-key automation

The pinned [recording format](https://github.com/PCSX2/pcsx2/blob/fd9d310ccbb6b8b62c976da8886a3c8fd3a10ff3/pcsx2/Recording/InputRecordingFile.h)
and [controller decoding](https://github.com/PCSX2/pcsx2/blob/fd9d310ccbb6b8b62c976da8886a3c8fd3a10ff3/pcsx2/Recording/PadData.cpp)
were inspected, not assumed from master or screenshots. GPL upstream source is
not vendored into this repository. Original authored event metadata lives in
`scenarios/prototype-emulator-debug-reference-v1.json`; no binary recording,
BIOS, game input, state or generated game code is distributed.

In the running VM, Tools / Input recording / Playback opens the private `.p2m2`
file. This pin resets to power-on, initially paused; resume with System / Pause.
No fictional CLI playback switch is claimed. The original authored recording
uses no savestate, active-low controller bytes and finite events. Working files
actually append36bytes during the trial; immutable authored duplicates and hashes
were retained. The full authored bytes remain exact prefixes, not unchanged
working-file hashes. The append cause is not yet qualified.

## Results and rejected assumptions

| Attempt | Actual endpoint | Normal exit / seconds | Declared budget |
| --- | --- | --- | --- |
| Start control | New Game title selection | 0 /419.875 |180s, OVERRUN239.875s |
| Room sequence v1 | EASY difficulty, not Room01 |0 /178.485 |240s |
| New Game v2 | Exterior introduction, not debug |0 /186.360 |240s |
| Later skip v3 | Next introduction, not debug |0 /217.781 |240s |
| Second skip v4 | Gameplay/HUD, then original debug menu |0 /241.515 |270s |

The native room script includes a separate developer request at1400. A copied
controller sequence is therefore not an equivalent emulator route. This is a
rejected experiment, not a demonstrated native engine defect. The first Start
attempt's overrun and metadata-case warning are retained, not hidden successes.

Final v4 events: Start1800..1859; Cross2100..2129 and2600..2629;
Start5300..5311 and7000..7011; L2 8300..8379 and R3 8355..8366.
Two separate introduction skips are needed on this observed route. Actual7728
shows Gene/enemies/HUD;8134 shows changed pose/health under enemy attack.
There are no attack inputs, guessed game-state writes or level-completion loop.
At9000 the recording auto-pauses on the original Room Jump / Flag Edit /
DEBUG OPTION / Player Warp / SHOOTING MODE menu. This proves visible opening,
not every option's operation or physical controller acceptance.

All processes were closed through normal UI confirmation without resume snapshot;
no timeout kills, observation-expiry restarts or compiler/native overlap.
Original disc, owner BIOS and owner global configuration hashes are unchanged.

## Selected original images and comparison boundary

The new F8 PNG is827x620 display-sized, despite512x448 internal resolution.
It contains actual gameplay and no recording OSD. The request was near observed
8134; exact exported guest frame is not certified. Its timestamp is file export.
The menu original is a1052x698 full-window, lossy JPEG with title/borders/OSD;
its timestamp is artifact-save AFTER observation, not exact capture completion.
No originals are cropped, resized, converted or cosmetically corrected.

The gallery explicitly compares the new menu reference with the PREVIOUS native
reader-trial original900, executable290b321c, host reader/integration sourcee59c3a5.
A second pair shows new emulator gameplay versus the PREVIOUS native Room00
introduction8400. Different state, pose, camera, resolution and encoding mean
both pairs are **UNMATCHED**. The second documents scene coverage, not a fidelity
comparison. Native results are not newly obtained, and no pixel-error metric,
rendering correction or before/after improvement is claimed.

Game imagery retains separate rights; owner-requested documentation is not
rights-holder authorization. Original continuation GPL licensing is unchanged.

## Next falsifiable experiment

Qualify Room Jump in the emulator and capture a named scene comparable with the
native route, recording viewpoint/state limits. Diagnose one actual discrepancy,
then verify any common-runtime correction on BOTH prototype and retail. No new
menu polish is required. Save/exit/Load, physical input, audible audio, wider
ISA/ABI/overlay lifetime, human campaign and faithful retail gates remain open.
No new native executable, default adoption, retail result, remaster, optimization
or shared-runtime correction is delivered by this reference milestone.
