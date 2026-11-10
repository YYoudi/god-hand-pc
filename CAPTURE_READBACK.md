# Native capture diagnosis, with a retained scene-comparison failure

10 November 2026. **This is evidence and candidate source, not a new main release
or improved game graphics.** The tested v1 menu and default Original remain the
active main implementation. The readback-v2 candidate stays on
[`codex/native-capture-readback`](https://github.com/YYoudi/god-hand-pc/tree/codex/native-capture-readback).
The full faithful-PC goal and RM03 remain open.

## A current readback defect, not just the historical report

The6November report already reproduced a DPI screenshot issue in a DIFFERENT
private checkout. We preserve it unchanged. This new experiment uses the actual
Raylib library in the current checked-build cache and original invented colors:

| Hidden window | Logical | Render | Queried GL viewport | Old read | Direct read |
| --- | --- | --- | --- | --- | --- |
| Normal | 640x480 | 640x480 | 0,0,640,480 | 800x600, padded | 640x480, correct markers |
| HIGH_DPI | 640x480 | 800x600 | 0,0,800,600 | 800x600 | 800x600, identical PNG bytes |

Both report monitor scale1.25 and queried GL read/draw framebuffer0. Unlike the
older probe, these viewport/FBO values were actually queried. This is synthetic
GPU evidence, not game execution. The first compile used an absent pinned API;
the corrected probe uses the actual GLFW entry point. Both attempts are kept.

The pinned Raylib screenshot function multiplies logical size by monitor scale.
Our original bounded helper reads `GetRenderWidth/Height` through the same
readback library instead. No new viewport, window, DPI policy, game scale or
existing image is changed. The source checks allocation arithmetic and returns
an empty image for invalid extents. It is for the default-window capture point,
not arbitrary render textures or a guarantee for every backend/driver/window.

## Checked candidate build — not silently upgraded v1

Clean candidate tooling: `da084f0d3273acfad325e24846401f0ab1b96e80`.
Upstream stays pinned to `14e956a1274332440273845fbab2c1f1e30c4a5a`.
The additive33-file recipe patches exact v1 postimages at host field capture,
F1 diagnostic capture and F2 diagnostic capture, with one new original header.
It preserves v1 fingerprint `75278aea...` and all older versions/defaults.

Actual configure0/build0; private source `ac62f7afce10349dcb00f9ea49845824d6f2d51c`;
native executable SHA-256 `2cf30a275b23ff8c2dce68afe997c2632a46de0f5284233a58b17a1413694751`.
The helper is [public original source at the tested revision](https://github.com/YYoudi/god-hand-pc/blob/da084f0d3273acfad325e24846401f0ab1b96e80/adapter/framebuffer_capture.hpp).
No guest regeneration, new clone, ISO edit, new Rust or third-party vendoring.

The first exact candidate300s native run exits124. Its F2 view exports640x480,
acknowledges a scratch save, holds/resumes and reaches laterfield5001. BUT the
driver then fails its historical3x image assertion: current640x480 SHA
`346e96c69777eb837c3d85c76c0ba7711f2ba068e4d6b55652880b9fcea1a50e`
differs from `9bd97cff...` at298,188 pixels across the whole frame. The camera/
actor pose visibly differs. This is **not just PNG metadata or black padding**.
The driver is FAILED; its planned2x and stop cases never start. No edited image,
camera fit or easier replacement assertion is used to label that block passed.

## An actual same-host-draw control

To avoid guessing inter-run alignment, a separate PRIVATE34-file diagnostic
adds only legacy-before / exact-public-helper / legacy-after reads at the same
host capture point. It is NOT the unchanged public candidate executable.
Private source `37035065dd5547816febcdd6606e9528b5cf4a38`, executable SHA-256
`8f70b36581f06a6492c6a99d3386adb2cf1906aa2ba37a0eca0e7ad61aba02d4`. The public helper's bytes are unchanged.

This distinct300s retail run exits124, completes actual F2 save ACK/hold/resume,
and reaches laterfield5001 (present CSV last5177). It reports logical/render
640x480 and DPI1.25 at capture. Five actual native triples cover field4741,
two acknowledged held UI captures, the saved UI and field5001:

- All five legacy-before/after PNG files are byte-identical within their triple.
- All1,536,000 valid render pixels agree with the direct read. The row mapping
  follows readback origin and vertical flip, not fitted image registration.
- Direct originals are640x480; legacy originals are800x600. No derived/cropped/
  resized/repainted game PNG is written. The two direct held UI originals agree.

**Native viewport/FBO were NOT queried in this diagnostic**; those measurements
belong to the separate synthetic probe. New probes compute no EE/IOP digests or
PCM/device evidence. Stable framebuffer pixels do not certify full-machine hold.
This proves the sampled readback defect and valid-pixel preservation, not full
rendering, campaign, input, audio or game Save/exit/Load accuracy.

## Later controls narrow the failure; they do not erase it

Two separate normal PUBLIC CLI300s runs disable mutating UI probes:

| Exact binary | Native result | Actual4741 original |
| --- | --- | --- |
| Preserved v1 (`b0105b94...`) | CLI0/native124 | 800x600, old `fd53182e...` exactly |
| SAME candidate (`2cf30a27...`) | CLI0/native124 | 640x480, old `9bd97cff...` exactly |

The candidate therefore does not always produce the different pose. These are
not a controlled single-variable A/B: the first failed diagnostic has different
probe, CSV and screenshot scheduling from the normal public launches. Cause of
the earlier inter-run scene mismatch remains UNKNOWN. Same global field does
not by itself establish the same game state or camera. The private paired run
also reproduces9bd directly, but is not substituted for the candidate binary.

**Decision:** keep readback-v2 isolated as a candidate rather than declaring
cross-run fidelity or quietly promoting it on main. Only the capture defect is
bounded by same-draw evidence. Next establish a stronger repeatability/scene
alignment contract: controlled same-executable diagnostics/input timing and, if
used, independently checked snapshot compatibility. A magic/version header or
a runtime snapshot is not genuine game saving/loading. New candidate2x/HD,
F1 hardware/focus, broader scenes and general renderer parity are not verified.
The patched F1 diagnostic capture call is source-reviewed, not exercised by
this increment's native runs (which cover field capture and F2).

## Controlled same-executable follow-up — 10 November 2026

This is a new experiment, not a relabeling of the earlier failed300s check.
Tooling at start: `1d3723d03c8ad20a53edecc031c7ab6788a7d89a` on the isolated
candidate branch. No rebuild or game-code generation was performed. All cases
use the SAME candidate executable
`2cf30a275b23ff8c2dce68afe997c2632a46de0f5284233a58b17a1413694751`
and INI `68d601196e0094017c26b49a2a3302bb197d65623e3467d4b1cbafd3a51f0258`.

The fixed order is OFF / ON / ON / OFF: F2 selftest `0` versus `scale2`.
Each new process has identical fresh scratch video/control files and the same
broker, script, CSV and screenshot schedule. Recorded environments match after
substituting isolated output paths and the ONE selftest mode. Canonical owner
preferences and original ISO are untouched. Both conditions explicitly disable
the application's shader binary cache through the actual pinned runtime option;
independent driver cache, OS/background scheduling and thermal conditions are
not controlled. No owned compiler, synthetic test or GPU probe overlaps the block.

Exact common arguments: `--iso <personal retail ISO> --headless --time-limit 480`.
Common diagnostic settings include:

```text
PS2X_PAD_SCRIPT=1800v:start:20,2100v:cross:20,2400v:cross:20,4200v:start:20
PS2X_SCREENSHOT_FIELDS=4740,5000
PS2X_FRAME_TIMES=<isolated-case>/presents.csv
PS2X_GS_SHADER_CACHE=0
GODHAND_PC_CONTROLS_PAUSE=1
GODHAND_PC_CONTROLS_PROBE=0
GODHAND_PC_VIDEO_MENU_SELFTEST_FIELD=4800
GODHAND_PC_VIDEO_MENU_SELFTEST=0 or scale2
```

Muted, fake-pad diagnostic input only; no attacks, imported state or game save.
The requested4740 screenshot is actually named field4741 in these runs, BEFORE
the requested4800 UI open. All four480s processes exit at native deadline124;
there is no forced kill or retry of a live process.

| Case | Pre-menu field4741 | Later field5001 | Last CSV field | Broker saves |
| --- | --- | --- | --- | --- |
| OFF1 | `9bd97cff...` | `b1812e8f...` | 7071 | 0 |
| ON1 | `9bd97cff...` | `b1812e8f...` | 6959 | 1 acknowledged |
| ON2 | `9bd97cff...` | `b1812e8f...` | 7005 | 1 acknowledged |
| OFF2 | `9bd97cff...` | `b1812e8f...` | 6891 | 0 |

Each set of four is **byte-identical raw PNG files**, not normalized images:

- field4741: `9bd97cff522321767ad5e101e11989751131ca32c2a2a7e76d55d6e80ab6e5be`
- field5001: `b1812e8f00c5e0b22b4ea70579c8b7c04680e3c7190bc57c238f03dfe21eed25`

Both ON cases park/resume at field4801, cycle23621128446, acknowledge the
restart-only2x preference, and continue to field5001. Their two held UI originals
match `37c94a34...` exactly; saved-for-restart originals match `a2e1b8b...`.
These are UI preferences, NOT game saves. Probe0 records no EE/IOP state digests;
zero diagnostic placeholders are not equality evidence. Later screenshots happen
to agree across ON/OFF as well, but neither that nor equal sampled frames proves
full-machine hold, determinism, accurate PS2 behavior or campaign fidelity.

Two preparation failures are retained: the first harness correctly refuses a
scratch video directory outside the owned launch root before any native launch;
a corrected300s OFF case reaches only CSV field4240 and produces neither requested
screenshot. Its observer assertion fails. The subsequent480s block is prospectively
specified, uses FOUR fresh cases and does not count the short run as passing.
No cause is assigned to that different progress/deadline.

**Conclusion:** the previously different pose (`346e96c6...`) does NOT recur in
this block. The tested selftest toggle does not produce different sampled images
under THESE conditions. This does NOT explain or erase the first failure, isolate
all timing factors, establish a speedup or justify a blanket fidelity claim.
Keep its original unmatched comparison and provenance visible. Main remainsv1,
with no candidate promotion/default change. Next exercise fresh saved2x, HD
combination and F1 diagnostic captures with explicit schedules. Physical input,
focus, audible audio, genuine Save/exit/Load and human campaign stay separate.
Stronger state-compatible fixtures remain necessary if later comparisons diverge;
runtime snapshots are not game saves.

All nine saved source/executable/INI/PDB sets, ISO, canonical preferences and
historical MIT lab WIP are verified unchanged. Private evidence remains under
`G:/God-Hand-PC/.local/scene-repeatability-2026-11-10/`: `block-owned-launches.json`
(short run), `block-480.json` (complete block), `preservation-after.json` and
`new-variants-after.json`. No additional game media needs publication: selected
field4741 and held UI originals already have these bytes. Old capture records
are not rewritten with new dates or substituted for this experiment's provenance.


## Remaining capture paths exercised — 10 November 2026

This later experiment uses the SAME isolated33-file candidate, source
`ac62f7afce10349dcb00f9ea49845824d6f2d51c`, executable
`2cf30a275b23ff8c2dce68afe997c2632a46de0f5284233a58b17a1413694751`,
clean tooling `81fc65bcbba4bbf193901cb4b2b0683a39713a25`. No rebuild, private
pair substitution, game generation, camera fitting or image repair occurred.
These are newly executed cases, not completion/relabeling of the earlier
aborted driver. The full faithful-PC goal remains active.

The three long cases have480s deadlines, fresh owned scratch data, the same
four Start/Cross opening pulses and screenshot requests4740/5000, plus native
presentCSV. Application shader cache is explicitly disabled; no owned builds,
tests or GPU probes overlap. Driver/OS/background/thermal state is not isolated.
All cases are headless/muted, with no attacks, imported states or game saves.

| New case | Actual internal scale | Last CSV field | Observed result |
| --- | --- | --- | --- |
| Fresh saved2x process,480s | 2x | 6814 | Reads prior ON1 scratch choice, seeds fresh store; proper640x480 field4741 equals prior2x `591f0fcf...`. F1/F2 tests OFF. |
| HD plus F2,480s | 3x | 6273 | Original authored512x512 source4 image uploads; field4741 equals prior HD `cce21397...`; F2 hold/saveACK/close and later5001 pass. |
| F1 diagnostic capture,480s | 3x | 6339 | Actual corrected upstream F1 capture call runs; original scene4741 equals `9bd97cff...`; controls edit/file/live/hold checks pass and later5001 is exported. |
| Stop with F2 open,30s | 3x | 180 | Both held originals agree; shutdown releases the acknowledged hold, no preference save requested. |

All four native processes exit at their own deadline124, without forced kills.
Internal2x/3x is observed in the actual `[gs-gpu] internal resolution` log line,
not inferred from a request or framebuffer size. The first observer filter
looked for the word "scale" and missed those initialization lines; the retained
supplemental parser fills that observation gap without rewriting native results.
The2x run reads a prior scratch preference, not a new public user-store CLI
option or an in-game graphics change. Canonical owner preferences and the source
scratch choice remain unchanged. Preference/controls persistence is NOT game saving.

The HD/F2 case holds and resumes at field4801/cycle23621128446 for1733ms, with
one real broker ACK. Current3x is unchanged;2x is saved for a later launch.
This case uses probe0: no EE/IOP digest or audible/device evidence. It exercises
the existing authored texture path, not a new HD feature, general asset support
or a claim about all scenes/aliases/performance.

The F1 case uses the existing upstream view and shared typed diagnostic commands,
not OS key injection. It holds field4801/cycle23621128446 for10896ms and reports
equal EE/IOP RAM digests at resume. The first two raw UI PNGs are byte-identical.
The third adds an alternate U binding to Combo/Square and visibly says **unsaved**
at that capture. Only the later Escape action and passing file/live assertions
establish saving. Do not caption the third image as already saved.

Selected first/third originals are both640x480, unchanged and downloadable.
Their13468 changed pixels lie within the observed panel; pixels outside it are
identical. This is a before/after **UI edit**, not better graphics, a new F1 menu,
Bevy/PS2 hardware output or a general pause certificate. EE/IOP RAM and two held
images do not establish complete SPU/GS/peripheral state or audible correctness.

### Separate actual public-launch controls

Four startup-only30s public CLI controls select candidate normal, candidate+HD,
preserved no-version v1 and Original. All launchers return0/native124, select the
expected existing executable and do not force a stop. Inherited mutating F2/F1
diagnostics and a stale state-load variable are deliberately injected into the
launcher environment: actual per-run records show both selftests/probe OFF and
the state variable removed. Brokers remain idle. These are startup controls,
not physical menu interaction or later-scene checks.

Five actual preflight refusals create no launch receipt: orphan readback version,
Original+menu, missing video selection, incompatible legacy hold, and unsupported
old default HD combination. Old version meanings and default behavior are intact.

### Decision and next direction

The scoped capture acceptance gaps for fresh2x, existing HD/F2 combination, F1
diagnostic exports and stop/startup rollback now have actual evidence. This is
not a new main release or full settings/fidelity acceptance. Keep the candidate
isolated, main runtimev1 unchanged, and the first different pose (`346e96c6...`)
visible and unexplained. Neither successful later checks nor the previous four
stable samples retroactively pass that failed comparison.

Do not keep adding display choices. Next audit one verifiable game function or
subsystem identity/ABI/overlay lifetime for readable extensions (RM01), and use
explicitly scoped captures for representative comparisons, not as a PS2-accuracy
oracle. No guest replacement should be installed merely from a prototype label.
Physical F1/F2/focus/controller, audible/device audio, genuine game Save/exit/Load,
broader DPI/window/backend coverage and human campaign gates remain open. No
autonomous fighting, new Rust features or delegation.

All nine source/executable/INI/PDB sets, ISO, canonical preferences and historical
MIT WIP are verified preserved. The shared object/CMake cache is STILL the earlier
private-pair build; no new link changed it. Evidence remains private under
`G:/God-Hand-PC/.local/readback-acceptance-2026-11-10/`: `native-cases.json`,
`supplemental-analysis.json`, `public-controls.json`, `preservation-after.json`
and `new-variants-after.json`. Only the explicitly reviewed original F1 pair is
added publicly. Game imagery is not GPL/MIT or rights-holder authorization;
ISO/ELF/assets/envelopes/generated game code/dumps/saves/executables remain private.


### Windows synthetic-test follow-up — 11 November local date

Keep both unsuccessful test observations. The first local full-suite log ends
without a summary; after the tool handle was missing, a fresh process inventory
confirmed no matching test job. It is incomplete, not passed. A subsequent full
265-test run under a deeper temporary root completes with TWO errors: Git cannot
create the synthetic readback fixture files because their names are too long.
This is not a native game failure or evidence that those two tests passed.

Without changing source, defaults, global Git options or Windows settings,
the same capture-version group passes7 tests under the shorter ignored temp
root `G:/God-Hand-PC/.local/t-ra11`. The full suite then passes265 in106.449s,
with three Windows symlink-privilege skips. No game data is a synthetic fixture.
This is a test-path workaround, not general arbitrary-path installer acceptance
or a performance comparison. Keep future nested synthetic worktrees under a
short G: temp root. The original native installations are unchanged.

Retained logs: `candidate-tests.log` (incomplete), `candidate-tests-retry-11.log`
(two path errors), `short-path-capture-tests.log` and `short-path-full-tests.log`.

## Preservation and reproduction boundaries

265 original synthetic tests pass on the candidate branch (three Windows
symlink-privilege skips locally; one Windows-only probe skip in Linux CI
42882379903). CI never receives game pixels as synthetic rendering inputs.
Main still has its separate257-test source; do not present branch tests as a
released main implementation. Native evidence and synthetic evidence are distinct.

Seven earlier installations, INIs/PDBs, the original ISO, canonical video store
and the paused MIT lab's four WIP files are verified unchanged. The two new
private source/executable/sidecar sets are preserved too. Operational baseline
source/executable/PDB are restored after linking; shared object/CMake cache is
now the PRIVATE PAIR variant and must be reconfigured/refreshed before a future
link. All build/research/evidence remains on G:; no automatic deletion/move.

Selected unchanged same-draw legacy/direct UI originals are registered with
their own time/source/binary provenance. Reused equal-byte media never rewrites
its old capture record. Imagery is neither GPL nor MIT; owner-selected
publication is not rights-holder permission. ISO/ELF/assets/generated game code/
dumps/saves/executables/PDB/private reference inputs remain private. Original
continuation code is GPL, separate from the paused MIT/Rust lab.

Private evidence directory: `G:/God-Hand-PC/.local/framebuffer-readback-2026-11-10/`.
Key receipts: `synthetic.json`, `installer.json`, FAILED `retail-driver.log` /
`retail-controls.json`, `pair-installer.json`, `paired-controls.json`,
`same-frame-analysis.json`, `old-v1-control.json`, `new-v2-control.json`,
`preservation-after.json`, `new-variants-preserved.json`.
