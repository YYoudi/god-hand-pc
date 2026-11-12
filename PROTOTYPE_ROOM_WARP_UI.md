# Room Jump and Player Warp through the F2 workbench

12 November 2026. These are actual prototype-native UI experiments, not a retail
feature, complete debug-menu release or public personal-disc setup. The original
menu and original game actions run; our host controls submit finite controller
requests. No game position, health, readiness or debug flag is written by them.

## Room Jump, without a scripted jump

A fresh run of the previous executable
`837ee7ec3153925d8855e02a9b13423ef1554571f7576acf64b1fe051af6905d`
uses only declared movie/difficulty input at fields 900/1200. There is **no** shared
F2 probe or scripted room selection. Actual software F2 opens the original menu;
mouse Circle/Right/Down/Down/Right selects **Stage 1 / Room 00 / Point 1**, and Circle
confirms it. The original r100/Event modules load and the original scene renders.
Actual mouse Start skips the introduction; Gene and the normal HUD appear at
Point 1, facing the green facade.

The same actual UI then selects Player Warp, enters it with Circle, leaves with
Start and closes its parent with Cross. Five read-only in-mode samples have
actual-player/cached/target vectors equal; the original camera manager and normal
HUD return. **No stick request occurs in this first run**, so it does not prove
movement. It exits0 by normal Alt-F4 after 290.704 seconds, not its 600-second watchdog.
The public host headers match 6235f99/f59fde6; the exact old executable and headers
remain preserved.

Initial owned-window backend captures were white while native GS PNGs showed the
actual difficulty screen. An actual F2 on that identified native window produced
the expected visible menu/panel. No coordinate click was made on white pixels;
the failed originals remain private and their cause is not diagnosed. This is
not a renderer repair or evidence that the game itself rendered white.

## Explicit left-stick requests

`ControlSet::DigitalV1` retains the nine digital controls and original layout.
The separately selected `LeftStickV2` adds four left-stick direction buttons in
another host row. Each requests 200 ms through the existing controller FIFO;
digital and stick actions share one pending/busy gate and a 300 ms request interval.
F1/focus/profile/bindings/stale/resize/writer-failure rules remain shared. The
controls still request input, **not** successful game-action acknowledgements.

The private harness selects these with `PROTOTYPE_DEV_PANEL=controller-v1` or
`controller-v2`. This is **not** a new public `pc.py` installation/launch option.
No analog keyboard latch or unknown-scancode alias is added. Right-stick axes,
analog magnitudes and the full PS2 controller surface are not exposed here.

The exact new public headers, compiled unchanged in the new native candidate,
are committed at `0c4165b4613b7e00c364802ff04dee336ba41c26`. At capture time they
were uncommitted additions to public base f59fde6; the later matching commit does
not change that chronology. Native executable SHA-256:
`cb4d8dc54897b88683e441cac2fd3be08c3e041b23f06762966b51219b59dc85`.
Private source/file chain SHA-256:
`964e8ea74b1917f0ba8b9de171f091fd6471fb5c3abe816c28010533e91440a4`.

Compile-main, compile-guard and link return 0. The new host uses 9,821 objects and
prototype libraries from the fresh source build, not the old 9,793 prototype
objects; five pinned generic libraries remain reused. All 9,846 retained file
hashes and eight source input hashes agree. Four actual native refusals—unknown
version, missing shortcut prerequisite, unqualified other pad and wrong input
size—return 34/35/36/27 before runtime/output creation. Original discs are unchanged.

## What the Warp experiment proves

Two fresh runs use the **same** new binary and declared Point 1 bootstrap, then
actual F2/mouse navigation to Player Warp. Only the move run adds one actual
mouse **LS right** request; neither run has a scripted Warp or external FIFO
writer. No player attack or autonomous level-completion loop is involved.

The attempted **matched-start fresh-pair interpretation is rejected**: manual
entry occurs at different guest fields/poses. No position reset, refit or camera
normalization is used. Do not call the two fresh runs a matched causal/image pair.

A separately prospective **within-session idle → pulse → idle** control was
written before the move run and before any stick request:

- The no-stick run has 30 in-mode samples at one unchanged player/cached/target
  position.
- Within the move run, 12 samples have one unchanged player/cached/target position
  **after construction and before the stick**. This excludes the constructor's
  own placement shift from the movement measurement.
- After one 200 ms LS-right request, 16 samples share the changed position, with
  player/cached/target still equal. The observed displacement is about
  **0.23942 original world units**, not assumed to be metres.
- Actual mouse Start exits Warp, Cross closes its parent and Hide removes the
  host controls. The original lifecycle tail restores the camera manager while
  retaining the final in-mode player-vector bits. The ordinary room/HUD returns.
- Later ordinary-play samples are not bit-identical: their distance from this
  run's own pre-stick baseline ranges 0.22270–0.29643 units. The shift is not undone,
  but exact coordinate persistence forever or the cause of later drift is not
  established.

The retained `pad=` words contain buttons, **not complete analog state**. Zero
button words are not proof of all-neutral sticks or analog-wire conformance.
The evidence is one finite ordinary request and observed settled actor/target
behavior. It is not a physical-controller or arbitrary-axis test.

Actual F1 opens in the new binary; F2 is refused while it owns input, and closing
F1 returns gameplay with no deferred panel. This test starts with the panel
already hidden; broader simultaneous focus/held/ownership transitions remain open.
A separate actual `controller-v1` run shows the original nine controls without
the stick row, and Cross restores the original difficulty screen. This is scoped
compatibility, not native pixel identity or full menu coverage.

All three new-candidate runs exit0 through normal Alt-F4. They do not run to their
600-second watchdogs. No owned compiler/test job overlaps these native runs; no
whole-machine, GPU-isolation or performance claim is made.

## Evidence and remaining work

The journal keeps selected unchanged owned-window originals for Room Jump,
before/after stick, normal restoration and v1/v2 selection. They use the explicit
reviewed native-host JPEG profile: original backend compression, title/border,
hashes and capture-completion times remain intact. Comparisons are **unmatched**,
not PS2 fidelity references or lossless pixel-parity tests.

Warp still shows a detached cloak-like fragment, and a narrow yellow line is
visible between the host boxes. Both are retained in the originals; causes are
not isolated and no rendering fix is claimed. The earlier strict VU1 comparison remains failed and unrepaired; these runs do not rerun it.

The earlier [original no-death ON/OFF/death proof](PROTOTYPE_CONTROLLER_PANEL.md)
belongs to executable 837ee7ec, not a new no-death regression on cb4d8dc5. These
exact-build scopes remain separate. The next release gates are a checked
personal-disc prototype workflow, normal visible launch versus bounded probes,
current-candidate no-death regression, controlled focus/held/repeat cases and
coverage/refusals for more options/rooms. No movement undo, complete menu, game
Save/Load, hardware/audio/campaign or retail debug feature is claimed.

The original host additions and invented-input tests are GPL continuation code,
not recovered game source. Generated prototype code/modules, discs, ELFs, dumps,
assets, raw maps, saves and executables remain private. Game imagery is not
GPL/MIT or authorized by a repository license. The full goal stays active.
