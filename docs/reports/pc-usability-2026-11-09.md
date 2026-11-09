# Launch lifetime and existing PC controls

Date: 9 November 2026. Active continuation tooling:
`f770aa2844121acd1ca9f67bf8d6524d5872e203`.
Pinned upstream remains `14e956a1274332440273845fbab2c1f1e30c4a5a`;
private native source remains `193076584e277c95644dcbbb4a6922c3a59ca2b8`.
No native relink, generated function edits or new Rust features.

## A concrete launcher defect

The evaluated native `godhand.ini` contains a 120-second diagnostic time limit.
The old public interactive launcher selected `--window`, but omitted the native
time-limit argument when the owner supplied no `--seconds`. It could therefore
inherit that diagnostic timeout instead of remaining playable indefinitely.

The original launcher now explicitly passes `--time-limit 0` for an ordinary
unlimited session. Explicit limits remain 10..600 seconds; hidden public runs
still require a limit. This changes process lifetime, **not simulation speed,
frame rate or combat timing**. The runtime INI is not rewritten.

Two serial hidden native controls reproduce the timer boundary:

| Control | Observed result |
| --- | --- |
| No explicit limit; unchanged INI | Native deadline exit 124 at 120.14 seconds. |
| Explicit zero | Still alive after 132 seconds; intentionally stopped by the private owned-process watchdog (Windows exit 1). |

That second exit is an intentional diagnostic termination, not a crash or a
clean gameplay shutdown. It proves survival past the inherited deadline, not
indefinite stability. The normal-window CLI vector is synthetically tested;
these native timer controls are hidden, not a physical-window interaction test.

## Reuse the existing native UI

Source inspection and actual guarded upstream self-tests establish an existing
F1 controls screen. It would be wasteful to invent a replacement before auditing
it. A fresh hidden 50-second process edited a second keyboard binding, saved and
closed the screen; a separate 30-second process read **the same saved file** and
verified both serialized and live bindings. Each reports three successful checks.

A third 35-second process reads an exact snapshot of that saved file and captures
the reloaded screen without editing it. Published native originals show default
and reloaded bindings; the intermediate unsaved-edit original remains private.
The screen is upstream's implementation, not a newly authored PC settings menu.
Commands were injected through upstream's guarded diagnostic API: this is **not
proof of physical keyboard/controller input** or a game memory-card save.

The overlay says that the game keeps running and asks the player to pause first.
The intro background changes during the menu test. A safe pause/resume policy
for future settings needs its own experiment; do not assume this screen pauses
combat. The original screenshots retain background differences and known readback
padding; they are a controls-UI comparison, not matched game frames or fidelity.

## Our original continuation change

Input preferences now live at the selected ignored workspace's
`userdata/controls.ini`. If absent, an existing executable-local controls file
is adopted once byte-for-byte; it is never edited in place or silently replaced.
Fresh diagnostics use their own path and native defaults, not the owner's file.
Missing defaults are created by the runtime, not fabricated by the launcher.

The helper rejects oversized/non-regular files, aliased destinations and unsafe
links, preserves unknown bytes/comments and uses exclusive creation. Ordinary
launches disable the mutating upstream controls self-test even if an INI attempts
to enable it. Private guarded UI experiments use explicit scratch files only.
Receipts record preference operations and before/after hashes, not their contents.

The actual existing native controls file was adopted and reused in a separate
scratch directory, with exact bytes and an unchanged original. A fresh **public
launcher** 220-second native run then initializes its isolated preferences,
records self-test=0, ends at its configured deadline 124 and produces 40 captures.
Its selected field-4741 PNG is byte-identical to the preserved opening-scene
baseline: `fd53182e7a2982021e5c5008d2e5dbab4dbd907cf9dfe52edc520c9a5d02315e`.
No screenshot is cropped or repainted to obtain that equality.

## Tests, persistence and next work

The local Windows synthetic suite collects 102 tests: 101 pass and one real
symlink-creation test skips because the process lacks that Windows privilege.
No system privilege was changed to make it pass. Public Linux CI run 42614352536 passes all 102 tests, including that case,
without Windows' restriction.
Fixtures are invented preferences/Git/data, never game pixels, assets or saves.

Actual card-path source/boot observations distinguish raw IOP/SIO2 memory-card
images from the separate HLE mc0 directory. Controls-file persistence, raw card
existence and runtime quick states do not prove **game Save -> process exit ->
Load**. That gate remains open; no personal save is currently available. Keep this gate open for a future
legitimate play/test state, without downloaded-save substitution or autonomous
level-completion attempts.

Physical input, audible audio, later-stage fidelity, unresolved generation
diagnostics, HD dimensions, widescreen, simulation-safe FPS and multiplayer remain
open. The next host experiment should examine existing menu pause/resume and
input boundaries, not create a duplicate interface or silently change gameplay.

See the original continuation's
[user-data contract](https://github.com/YYoudi/god-hand-pc/blob/main/USER_DATA.md).
Exact native commands, process IDs, logs, input preference snapshots and receipts
remain private. The public comparison contains only two selected unchanged
renderer originals, not files from the game disc or raw technical dumps.
