# Normal F1/F2 acceptance on the combined prototype build

12 November 2026. Follow-up to the [Room01 return](PROTOTYPE_ROOM_TRANSITIONS.md).
The unchanged private executable is
`4acf41e7d0495dbb883629dc9a12b15dc7e0b33b6bee10ea6a97bbeef8f047f7`.
Native attachment tooling remains `97b774547230976d1536f7fe32d3f27cf3271c48`;
the qualified generated inputs and retained objects/libraries are described in
[the Room01 report](PROTOTYPE_ROOM01.md). There is no new native compilation or
game translation in this increment.

## Actual normal-mode sessions

Two separate fresh `interactive-v1` sessions use real Windows F1/F2 and actual
mouse actions on the host controller panel. There is no native watchdog,
scripted bootstrap, external diagnostic command reader, game-memory observer,
snapshot or raw game export. Each ends through normal Alt-F4, with native exit 0.
Software OS/mouse input is not physical keyboard/gamepad hardware acceptance.

The first session lasts **512.922 seconds**:

- Actual F1 opens controls. F2 is refused while F1 owns input, does not activate
  after F1 closes, and a fresh F2 opens the original menu and host panel.
- Actual mouse Room Jump selects Stage1 / Room01 / Point0. Its real interior,
  Gene, enemies and HUD render; the panel can be hidden without closing the game.
- Original PL NO DEATH changes OFF -> ON. Closing options shows the retained
  `memory leak size 0x480` warning, then the original parent menu.
- Original Player Warp displays its axes. One bounded 200 ms left-stick Right
  request changes the scene/camera view. Start exits Warp; Cross closes the
  original parent. The normal camera and HUD return.
- F1 closes an already open F2 panel; another F2 is refused under F1 and is not
  deferred. A fresh later F2 still works. The original no-death option is observed
  still ON, restored to OFF, closed and followed by the normal scene/HUD.

This Room01 trial alone is **not a damage-survival proof**: the inspected enemies
remain idle. Its Warp comparison is a visual response, not a numeric world vector
or undo. Read-only analysis of original lossy JPEG scene regions finds 1,007
differing pixels in the idle pair, 193,926 after the pulse and 1,742 in the later
settled pair. No crop is saved, no camera is refitted and no perfect idle equality,
full-machine pause or PS2-fidelity claim follows from these numbers.

Initial owned-window captures in this first session are white. The exact live
process/window is verified before a single F1-only visibility diagnostic; its
later actual controls/game pixels are observed before guest navigation. The white
originals are preserved privately, cause unisolated. Occasional accessibility-tree
unavailability is also retained; current correct owned-window screenshots remain
available. No input or screenshot is taken from another application.

## A separate no-death effect and restoration control

The second normal session lasts **546.406 seconds**, on the same executable with
fresh controls/cards. Actual F2/mouse selects Stage1 / Room00 / Point0, the original
introduction is observed and ordinary Start skips it. Actual Gene/HUD/enemies
appear before opening the original options.

Original PL NO DEATH is enabled, the original menus close and the host panel is
hidden. With **no player input** between observations, original enemy attack,
hurt and knockdown poses are visible. Gene is alive with full-looking health at
the two inspected endpoints **110.004 seconds apart**. These are selected original
snapshots, not an uninterrupted recording, numeric HP, cumulative damage/refill
counts, no-damage or arbitrary one-shot-immunity proof.

Actual F2 reopens the menu; the option is still ON and is restored to OFF. The
existing 0x480 warning is visibly retained on this close, then the parent and
ordinary game return. With no further player input, successive originals show
reduced health, a later collapse and the original **Continue? Yes / No** screen.
Exact death time, total damage and every HP writer are not measured. The earlier
native05/native07 numerical/visual observations are separate, not inherited here.

## Explicit local launcher selection

Original launcher source `ab9990646bf5a9865861506a77bed88c796ae935` adds an explicit
`--build room01-v1`. It still **adopts an already built private executable**:
it downloads, generates and distributes no game. A personal supported June-2006
prototype disc and its qualified ELF remain required; retail inputs are not
interchangeable.

```powershell
python prototype_workbench.py --build room01-v1 --exe "G:\private\guarded-workbench.exe" --elf "G:\private\SLPM_665.50" --disc "G:\private\prototype.bin" --session first-room01 --check-only
python prototype_workbench.py --build room01-v1 --exe "G:\private\guarded-workbench.exe" --elf "G:\private\SLPM_665.50" --disc "G:\private\prototype.bin" --session first-room01
```

Replace the three private input paths. Session names must be fresh. The default
remains **native07**, with its old exact hash and `prototype-default` user-data
name. The new explicit profile uses a separate `prototype-room01` default so old
preferences/cards are not silently shared. Existing files are never overwritten;
`--user-data` remains an explicit owner choice. Cards/preferences are not a
validated in-game Save/exit/Load result.

An actual exact-source public-CLI startup lasts **62.547 seconds** and ends with
launcher/native 0: real F2 opens the original five-choice menu/panel; actual
Cross/Hide close them and normal Alt-F4 exits. Deliberately inherited invented
automatic-input/probe/screenshot variables are stripped. Runtime reports normal
mode, no watchdog/raw exports/game observers; the forbidden screenshot directory
and diagnostic request/module-export files are not created. This startup-only
source check is distinct from the two full room/effect sessions above.

Seven actual preflight controls pass without changing the output tree or old
user-data bytes: new and old default check-only positives, default refusing the
new binary, new profile refusing the old binary, unknown profile, missing ELF
and invalid session refusals. Native07 remains an explicit supported old choice,
not an automatic fallback for a bad executable.

The source suite passes **336 synthetic tests**, three Windows symlink skips,
in 60.247 seconds after the two first native sessions end. Six new invented-file/
environment tests cover build selection and output-free check-only behavior.
No game data or screenshots are synthetic fixtures. Final publication validation
is recorded separately, after the exact-source native trial ends.

## Still open

The full goal remains active. Prototype VU/generic source closure, a fresh complete
personal-disc setup, wider original options/rooms, focus/held/repeat/hardware
input and full ABI/lifetime/failure-recovery coverage are not finished. The
retained translation diagnostic, strict VU1 mismatch, cloak/interface artifacts,
loading differences and original accounting warning are not repaired here.
Audible audio, true game Save/exit/Load and campaign fidelity remain separate.
No prototype address or result establishes a retail debug backend.

The [aggregate receipt](docs/evidence/prototype-combined-interactive-2026-11-12.json)
and journal identify the unchanged full native-window JPEG originals, their exact
builds and limitations. JPEGs are lossy backend originals, not renderer PNGs or
PS2 captures; their title/border and bytes are preserved. Game imagery is not GPL.
No game, extracted asset, dump, save, binary or generated game code is published.
