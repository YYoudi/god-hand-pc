# Prototype workbench: visible sessions and current no-death regression

12 November 2026. Continuation of the [Room Jump / Warp workbench](PROTOTYPE_ROOM_WARP_UI.md).
This is still a **private-build prototype workbench**, not a complete prototype
installer, a retail debug backend or a finished PC port. The full goal stays active.

## No-death rechecked on the stick-panel build

The unchanged native05 executable (`cb4d8dc54897b88683e441cac2fd3be08c3e041b23f06762966b51219b59dc85`)
compiles the public `0c4165b4613b7e00c364802ff04dee336ba41c26` controller headers.
The new test explicitly boots Point0 with declared controller-field input; it is
not a new UI-only Room Jump claim. Subsequent cheat changes use actual F2/mouse
actions, with no external input-file writer, attacks, movement or game-state writes.

Actual original PL NO DEATH OFF -> ON, menu close and Hide are followed by **19
matched selected damage calls totaling 198 HP**, against maximum 100. The original
positive-health refill site runs 22 times. Gene stays alive. Actual F2/mouse restores
OFF, closes the original menu and hides the host panel; 15 subsequent selected
damage calls lead to HP zero, collapse and the original Continue screen. There
were seven selected OFF calls before enabling the option. Normal Alt-F4 ends the
830.554-second process with native exit 0, before the prospective 900-second limit.

These are cumulative multi-hit/refill observations, **not no-damage or arbitrary
one-shot immunity**. All selected ON pre-clamp values remain positive: the separate
lethal-floor branch is not exercised. The selected function is not every HP writer;
refills include an existing deficit and other writers, not one refill per attack.
The alive screenshot is during the ON interval, not necessarily the final damage
event. Counts come from private read-only matched observations, not the image alone.

**Unresolved original warning:** the first Cross after disabling the option shows
`memory leak size 0x480`. The next observation shows the original parent menu,
then normal play/death/Continue. Both warning and follow-up originals are retained
below. Its cause and exact duration are not isolated; no memory-safety/fix claim.

## A separate visible interactive launch

Native07 is a NEW executable:
`0afc8392bcab3db0aeb2ef3c9d57d9530598a408c68fa707091db56ac195c2e6`.
Compile-main, compile-guard and link finish 0; 9,850 retained inputs and ten source
inputs match. Native06's failed `_get_environ` compile remains preserved. Native07
enumerates its initial `main` environment before runtime instead of guessing an
internal CRT getter. Old binaries, private generated sources/objects and discs
are not overwritten or regenerated in this increment.

Original public [execution policy](adapter/prototype_execution_policy.hpp), source
revision `8be4cd64fe300be51acf0ac36df002c9f0946d45`, requires explicit
`interactive-v1`, visible mode, no deadline, qualified SDK mode and a persistent
user-data path. A small case-insensitive environment allowlist rejects automatic
input, state-load, dump and unknown future diagnostics before runtime. Ten actual
direct-native negative controls exit 38 without creating output.

Interactive mode has **no watchdog thread**, scripted bootstrap, external command
poll, game pad/Warp/health observers or raw module/RDRAM export. Required qualified
module installation/unloading remains. Operational host key/focus/controller-request
and changed-button logs remain; this is not a claim of no logging. The native
personal-disc/ELF hash and read-sharing guards still run before hooks/runtime.

The actual visible, muted, unscripted session lasts **197.783 seconds**, exceeding
the old diagnostic 90-second default. Real F2 opens the original menu and panel;
F1 closes an already open panel, F2 is refused under F1 and does not activate later.
Actual mouse Room Jump selects 1/00/Point1, loads the original scene and Start skips
the introduction. The normal Gene/HUD appears. Actual in-scene F2, Cross and Hide
return to that room; normal Alt-F4 ends with native 0. Controls bytes are unchanged.
Only runtime log and the finite user-driven controller FIFO are produced by the
session, apart from separately recorded Computer Use evidence. Controls and a
memory-card file live in the persistent private user-data folder. This is **not
genuine game Save/exit/Load validation**.

A separate SAME07 hidden, 30-second control with execution profile **unset** keeps
the old bounded diagnostic path, deliberately produces private diagnostic exports
and stops normally with native 0. Interactive mode is not a silent legacy upgrade.

## Checked local launch, not an ISO-only installer

[prototype_workbench.py](prototype_workbench.py) adopts only this exact local native07
executable and the exact personal prototype disc/ELF. It fetches/builds nothing.
Example, from this GPL repository (replace the three input paths):

```powershell
python prototype_workbench.py --exe "G:\private\guarded-workbench.exe" --elf "G:\private\SLPM_665.50" --disc "G:\private\prototype.bin" --session first-session --check-only
python prototype_workbench.py --exe "G:\private\guarded-workbench.exe" --elf "G:\private\SLPM_665.50" --disc "G:\private\prototype.bin" --session first-session
```

Session names must be fresh. Preferences/cards remain under ignored
`.local/prototype-workbench/userdata/`; sessions/logs under its `sessions/` sibling.
Original keyboard-only defaults are created only if controls are missing. Existing
controls/cards are not overwritten. F1 edits controls; the panel refuses unsupported
live controller bindings rather than forging a device. Physical hardware tests
remain separate. Close the visible window normally; ordinary launches have no timer.

The exact public source `8be4cd6` is actually run with inherited invented diagnostic
flags: they are stripped, native F2/Cross/Hide works during the opening movie and
actual Alt-F4 exits 0. Persistent controls/card hashes equal the previous run.
This separate startup check is not another Point1 gameplay proof. Check-only,
existing-session, invalid-name, wrong-executable and missing-ELF refusals create no
new session or native process. The missing-ELF test is not a retail-ELF digest test;
earlier native input-identity controls remain separate evidence.

An initial CLI transcript reader fails on localized Windows CP1252 stderr. That
failure is retained; the launcher now explicitly writes UTF-8, an invented-path
regression passes and a distinct five-control repeat decodes cleanly. Computer Use
also briefly returns another application and one stale screenshot ID during the
exact-source run: no input/save is applied to the wrong image; fresh activation and
observation precede the successful actions. No whole-machine isolation is claimed.

Final complete synthetic validation: **272 tests pass**, three Windows symlink
skips, 58.576 seconds, after the UTF-8 fix and journal preparation. Invented
inputs only; no owned compiler/tests overlap the native trials. The earlier
source-suite run and first failed observations remain preserved.

## Remaining work

- Reproduce qualification/generation of private prototype SDK/module/VU inputs
  from personal discs; the public launcher is **adopt-only**, not source-complete setup.
- Broader original options/rooms, invalid-state refusals, focus loss, held/repeat
  and physical keyboard/controller acceptance; do not extrapolate from single taps.
- Investigate the original memory warning, retained detached-cloak/interface artifacts
  and earlier failed strict VU1 comparison. No new renderer fidelity/performance claim.
- Retail debug functions need their own identity/ABI/lifetime qualification; no
  prototype addresses or results are transplanted.
- Audible audio, genuine game saves and campaign coverage remain open.

The [aggregate receipt](docs/evidence/prototype-interactive-2026-11-12.json) and
journal contain reviewed, unchanged native-window JPEG originals with full hashes,
capture times and exact executable provenance. Pairs show named action states,
not matched-camera PS2 fidelity. Game imagery is not GPL; no game, extracted asset,
dump, save, binary or generated game code is distributed.
