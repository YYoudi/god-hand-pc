# Explicit normal launch of the selected-source prototype

13 November 2026, Europe/Paris. Original launcher source
`25889a821b5f7ba62d5a78e9fa85a854e0883a0d` adds an explicit
`--build source-v1` choice to [prototype_workbench.py](prototype_workbench.py).
It adopts the already-built private executable
`e677f789c9f51400ba054b5a72ab7807f363a5bd4c099ba10f5c2c07edcc8e34`.
**It does not compile, download or distribute a new game executable.**

## Why this change

The goal/evidence review found a practical gap: this exact source-built binary
already had its own [normal Room01, Warp and no-death ON/OFF observations](PROTOTYPE_WHOLE_INTERACTIVE.md),
but the public normal launcher could select only the older native07 and
room01-v1 executables. More source-helper proofs would not close that delivery
gap. The new choice exposes the tested binary through the existing strict
input/environment policy, without changing the binary or old defaults.

| Explicit choice | Private executable identity | Default private data name |
| --- | --- | --- |
| native07 (still default) | Existing native07 pin, unchanged | prototype-default |
| room01-v1 | Existing combined pin, unchanged | prototype-room01 |
| source-v1 | Exact e677 pin above | prototype-source |

There is no automatic detection, fallback or silent upgrade. The new default
data name keeps previous controls/cards separate. Existing files are never
overwritten; `--user-data` remains an explicit owner choice. Controls preferences
and a blank card file are not verified in-game Save/exit/Load.

## Normal command

The user must already have the qualified private build and personal original
June-2006 prototype inputs. This is adopt-only, **not a public ISO-only installer**.

```powershell
python prototype_workbench.py --build source-v1 `
  --exe <qualified-private-e677-executable> --elf <personal-prototype-ELF> `
  --disc <personal-prototype-disc> --session <new-private-session>
```

Add `--check-only` to verify identities/paths without creating output or launching.
Every real run needs a fresh session name. The normal policy is visible/muted,
with native watchdog zero, no automatic input/bootstrap, game-memory observers,
snapshot loading, diagnostic command reader or raw exports. F1 controls and
F2 original debug-menu/controller requests retain their previous meanings.
Ordinary interactive play has no forced time limit; close the window normally.

## Actual exact-source delivery check

Eleven real preflight controls preserve the complete existing workbench tree:
new source check-only, old default/explicit native07 and room01-v1 positives;
default/combined refusing e677, source-v1 refusing both old executables, unknown
profile, unsafe session and missing ELF refusals. No native process is started
by these controls and no old user data is changed.

The first private test invocation stops **before** preflight/launch: it selected
a different historical local executable for the old room01 comparison. Its
hash guard refuses. The previous authoritative normal receipt identifies the
correct 4acf path; that corrected test uses the same public pins/source. The
first script and refusal remain preserved, not relabeled as a native failure.

The exact committed public launcher then starts e677 with deliberately inherited
invented script/probe/snapshot/key-trace/screenshot flags. The child reports
`interactive-v1`, no watchdog, no raw exports and no game-memory observers; the
forbidden output paths are not created. Its session contains only launch.json,
runtime.log and the ordinary developer-input FIFO. All 18 pre-existing workbench
files and the original executable/ELF/disc remain byte-identical afterward.

Actual Windows OS/mouse observations on the identified native window show:

- F1 opens controls; F2 is refused while F1 owns input.
- Closing F1 creates no deferred debug panel. Fresh F2 opens the original
  five-choice debug menu and host controller panel.
- A mouse Cross request initially has a pending image. A later observation
  actually shows the original menu closed; the pending image is not called a
  closure result. Hide then closes the host panel.
- Normal Alt-F4 closes the window; both native and launcher exit zero.

The background is the original opening/attract movie, **not newly observed live
combat or an autonomous gameplay loop**. Earlier named room/Warp/no-death effects
retain their own dated exact-e677 receipts; they are not repeated or inferred
from this startup trial. An early white-window original is retained; later F1,
movie and original-menu rendering appear without any build change. Its cause
is not isolated and no rendering fix/parity claim follows.

The actual native duration is **205.781 seconds**. The planned 180-second operator
observation budget is exceeded by 25.781 seconds. That overrun is retained,
not presented as a passing deadline or termination guarantee. Normal mode has
no native watchdog; the observed exit is the actual manual close.

## Original screenshots and time provenance

Eight original backend JPEGs, 642×512 including title/border, are decoded and
hash-checked. Four individually reviewed originals are selected for the journal;
no crop, resize, conversion, compositing or artificial scene is used. These are
lossy native-window originals, not renderer PNGs, PS2 captures or Bevy output.

The saving helper recorded its **artifact-save time after observation**, not
the exact backend capture-completion time. Publication uses a separate
`recorded_at` field/basis and labels it accordingly. It does not invent a guest
frame, input latency or precise capture timestamp. The earlier raw metadata
field label is retained privately with this explicit correction; image bytes
and action ordering are unchanged. Legacy capture-time records remain unchanged.

The paired UI states are intentionally unmatched: the movie changes between
observations. They show input ownership and closure, not visual fidelity,
performance or a before/after graphics improvement. Game imagery retains
separate rights; the repository license is not rights-holder permission.

## Validation and remaining work

The launcher/source identities, actual commands, budget overrun, UI provenance
and preserved-file audit are in the [aggregate record](docs/evidence/prototype-source-launch-2026-11-13.json).
The final suite passes **507 tests, four Windows skips, 69.417 seconds** after the native session ends; four launcher and two timestamp controls are new. Earlier505tests/73.257s remain their own receipt. Of45,676 prior file expectations,45,675 paths remain unchanged; the intentionally changed launcher has its exact old bytes/Git history retained. Only original launcher/tests/publication code and selected reviewed screenshots
are public. No ISO, ELF, asset, dump, card, binary or generated game code is added.

source-v1 is now an explicit local normal-launch option; native07 remains default
and room01-v1 retains its old identity. This is not a new native build, fresh
ISO-only setup, all-menu/room or retail-debug acceptance. The source/data/project
stages remain separately documented; end-to-end orchestration, fresh registration
qualification and a new full build/native acceptance still need work and enough
free G: space. Wider focus/held/repeat/hardware input, reference/ABI/lifetime,
failure recovery, translation/VU/render/loading/accounting warnings, audible
audio, genuine Save/Load and human campaign testing remain open. Goal active.
