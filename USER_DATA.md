# Launch lifetime and persistent controls contract

## Required behavior

An interactive `run` without `--seconds` must explicitly request native time
limit **0** (unlimited). It must not inherit the pinned runtime's generated
`godhand.ini` diagnostic default of 120 seconds. Explicit deadlines remain
10..600 seconds; hidden public runs still require a deadline. Unlimited is not
an FPS, simulation-timing or stability claim.

The existing upstream F1 controls screen is reused, not copied or presented as
our new menu. Its file must live in the selected workspace's ignored
`userdata/controls.ini`, beside but distinct from game cards and quick states.
Normal launches reuse that file. If it is absent, copy an existing native
`controls.ini` byte-for-byte once, without modifying the source; if no source
exists, let upstream create defaults. Do not guess/normalize its syntax or erase
unknown settings/comments. Record the operation and hashes, not file contents.

Fresh diagnostic user data never adopts or edits the persistent controls file.
It receives its own controls pathname and native defaults in the new per-launch
directory. Never delete an owner's preferences, cards or states to clean a test.

Reject oversized/non-regular controls files, symlink/reparse targets, hardlinked
destinations and resolved paths outside the owned user-data directory. Copy with
exclusive creation; refuse a concurrent destination instead of overwriting it.
The launcher explicitly sets GODHAND_CONTROLS_FILE after cleaning inherited
private environment variables, and records controls metadata before/after exit.
Normal launches explicitly disable the mutating upstream controls self-test,
including an accidental INI setting. Native UI tests require a separate guarded
private driver and scratch file, never the player's preferences.

## Evidence gates and limits

Synthetic tests use only invented text preferences and temporary files.
Native checks must retain the exact source/executable/ISO identity and original
preferences, exercise the existing controls UI's edit/save/new-process reload
in isolated files, and verify timer behavior separately from visual/input claims.
Upstream's guarded self-test injects UI commands: it is not physical keyboard or
controller evidence. Controls persistence is **not in-game Save/Load**.

This contract isolates input preferences only. General video/runtime INI still
belongs to upstream; no complete settings UI, audio usability, widescreen, FPS
unlock or full-game fidelity follows. Actual cards use the native IOP/SIO2 image
path; an HLE mc0 directory or a quick state does not establish game persistence.
