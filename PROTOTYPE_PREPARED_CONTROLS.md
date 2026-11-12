# Prepared native controls and reusable module inputs

12 November 2026. Follow-up to [the incremental source capsule](PROTOTYPE_INDIRECT_REPLAY.md).
These are new experiments, not extensions of the failed/partial330s runs.
The adopted normal07 executable is unchanged; the full goal remains active.

## The missing capture endpoints are now observed

Two fresh controls use the same frozen executables as before: baseline07
`0afc8392bcab3db0aeb2ef3c9d57d9530598a408c68fa707091db56ac195c2e6`
and candidate27
`e1115bb6e58ed1a5cbd6a70324c15faa3ab5a4e4b3b17c138da0987d69a43f25`.
There is **no new native compilation or guest generation** in this increment.

Each uses a new scratch directory, fresh controls/cards, an empty renderer-output
directory prepared **before spawning**, the same finite original controller
script, and a prospectively chosen **450-second native watchdog**. Original
Room Jump selects1/00/Point1, followed by two empty option visits, a third ON/OFF
visit and original exits. No attacks, imported save, desktop input, readiness,
health, heap, position or program-counter writes. This remains software/shared-
handler diagnostics, not a new actual-key or mouse trial.

Both processes exit0 and produce **23 unchanged640x480 PNGs each**, with no export
failure. Both final requested filenames7301and7401 are present. Last logged
fields9493/9731 demonstrate later progress, not game FPS. Each run takes about
453.766 wall seconds including startup/shutdown; this is not a speed comparison.
Original discs, controls and the old330s receipts/images remain unchanged. No
process is killed or restarted, and no owned compiler/synthetic suite overlaps
either run. Other applications, GPU and driver state are not isolated.

Deferred filenames are retained literally: baseline requests2900/5100 export
as2901/5101; candidate requests2900/5360 export as2901/5361. No files are renamed
to manufacture alignment. Among **21 common actual filename fields,20 originals
are byte-identical**, including7301and7401. Direct inspection confirms the final
candidate room/Gene/HUD original. This closes the scoped output-preparation and
missing-endpoint gates, **not full image parity or original-game fidelity**.

## One loading-screen difference remains

The common filename2901 differs by **17,300 decoded RGBA pixels**. Both originals
show GOD HAND / Now Loading. The read-only difference bounds are x8..609/y15..446;
maximum channel differences are101/83/53/0. No crop, repaint, normalization or
derived replacement image is written. Both unretouched originals are published,
not hidden behind the later equal room endpoint.

The present CSV contains no valid per-present image identity in this window.
Baseline records repeated2899 presents, no2901row, then2903; candidate also records
2901. Same export filename therefore does not certify identical presented source
or guest state. These observations **do not identify a timing, capture, renderer
or source-change cause**. No performance attribution or silent candidate promotion.
The old missing-directory failure and candidate330s missed endpoints stay recorded
as failures/incomplete coverage; they are not retroactively marked passing.

## Reading fresh module inputs through public tooling

The existing public ISO/FST/AFS readers already support the actual prototype
metadata. Rather than write another parser or override a private third-party
`Disc` method, original [module_inputs.py](module_inputs.py) reuses them. Its source
revision is `dcc303e1963cc8e47efaf6e5208dba2bcfe03551`.

The new read-only API checks a bounded immutable SNR2 source envelope, declared
size, alignment and table extents, then returns a private-use REL descriptor/hash.
It requires the supported bijective FST/AFS mapping. Only catalog metadata and
selected REL extents are requested; physical payload aliases are not certified.
It verifies **neither** symbol/relocation semantics, code bounds, constructors,
compact streams, guest addresses, ABI, loading nor lifetime. The caller must
verify its exact disc/profile; Window detects length changes, not adversarial
same-size writes. No output file or asset extraction is performed by the API.

Eight invented-data tests exercise source size/signature/alignment/table bounds,
catalog integration, case-insensitive REL selection, missing catalogs, aliasing
FST ordinals and malformed sources. No original game bytes/instructions are tests.

A fresh exact-profile prototype audit obtains **1,078 bijective file/archive
entries and76SNR2 modules**. The76source modules total985,929bytes; their raw
bytes, source offsets and paths all agree with the previous private reader.
The public-reader result is recorded before importing that old reader as an
oracle. The source headers contain13,761 relocation records and5,052 symbol
records, not that many verified functions or recovered C++ routines. Original
disc SHA-256 is unchanged. Raw names, offsets and module bytes stay private.

This replaces one private input-reading dependency experimentally. It does
**not** generate/relocate/compile the modules, publish game code, close module/VU/
generic-source dependencies or deliver an ISO-only prototype installer.

Source validation: **305 synthetic tests**, three Windows symlink skips,57.878s;
all non-skipped tests pass after both native controls are terminal. A separate
final publication suite is retained. An initial read-only audit script had a
syntax error before analysis; it is preserved separately, not a native failure.
The [aggregate receipt](docs/evidence/prototype-prepared-controls-2026-11-12.json)
records the real outcomes without public game maps or dumps.

## Still open

The loading mismatch remains unexplained. Investigate actual source/present
identity or repeatability before attributing it to the new BOOT entries. Complete
module/VU/generic-source setup and a fresh full build with its own acceptance.
The original0x480 warning/reference comparison, strict VU1 failure, rendering
artifacts and broader input/menu coverage remain open. Earlier07key/health/Warp
proofs are separate; this is not a new survival, physical input, audible audio,
Save/exit/Load, campaign, retail or complete prototype release.

Only original GPL tooling, invented fixtures, aggregate results and selected
unchanged native screenshots are public. Game imagery is not GPL. No ISO, ELF,
module/asset extract, raw map, dump, save, generated game C++, third-party source
or executable is published. No new Rust or delegation.
