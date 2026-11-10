# Native video menu: source preparation, not a shipped screen

Work on `codex/native-video-menu`, 10 November 2026. **The retained game builds
do not contain this screen.** No factory, storage transport, checked variant or
launcher flag installs/enables it yet. RM03 and the full PC-port goal remain open.

## Implemented original source

- `video_menu_model.hpp` separates current-run intent, saved-next-run preference,
  draft, requested hold and acknowledged hold. A submitted write is not a save.
- `video_menu_view.hpp` uses the existing host Raylib/input APIs for an F2 screen,
  original text/primitives and four keyboard rows: scale, save for next launch,
  reload and close. It does not change the renderer's live scale or game timing.
- `video_menu_host.hpp` binds that view to the existing F1 lifecycle and our
  audio-v2 pause Gate. It requests the union of both screen owners, samples the
  acknowledgement afterward and updates the union again after Escape closes it.
- The existing Python preference writer can compare an expected revision under
  its writer lock, preventing a stale future menu from overwriting a newer edit.

The view labels **this run's request**, **saved for next run**, and **effective GL
scale not observed by this menu** separately. Reset means upstream INI, not an
invented hardware-accurate value. Save acknowledgement must contain the requested
selection and a new valid revision. Unknown outcomes require reload, not a blind
retry or a misleading “not saved” message. These are video preferences, not game
memory-card saves.

## Host integration details that matter

The pinned host F1 screen has no generic native panel API. Its overlay input
state is a shared Boolean with release quarantine, not independent ownership for
multiple menus. Native F2 must not open while F1 owns the screen. F3 is already
the FPS-overlay shortcut; it is not reassigned. F8 is a private dump shortcut,
not a settings action.

**Still tick F1 with `drawable=false` while video owns the screen.** Skipping F1
entirely would leave its raw Back+Start/focus history stale. The source binding
therefore continues that tick without allowing F1 to open over video. Drawing is
after the game image, before native capture. A window too small to show the menu
does not acquire input ownership; shrinking an open screen disables edits and
shows a resize/close message. Focus loss never changes a draft.

The existing audio-v2 patch requests hold from F1 only. A new visible screen or
idle pads do not automatically pause the guest. The binding must replace that
old F1-only request, not leave it running afterward and silently releasing a
video hold. A public native experiment must still prove this boundary; a Boolean
in a portable test is not readiness or audio-device evidence.

The tested parent `gpu-audio-v3` has disjoint HD/audio edits. A new menu touches
`ps2_runtime.cpp`, already changed by audio-v2. Extending it requires **ordered
postimage/preimage review** over the exact parent, not weakening the current
overlap refusal or changing old component fingerprints.

## What was actually checked

Original portable tests compile the exact public view/binding against invented
host, draw-call, controls and Gate doubles. They exercise ownership, hold gating,
queued versus acknowledged writes, unrelated/bad replies, close with a pending
write, refresh, focus, small windows and shutdown. They do **not** render pixels,
open a game window or verify physical input, actual chord/quarantine behavior,
audio, guest memory or scheduler quiescence.

Separately, MSVC14.44.35207 `/Zs` accepts the source against the **actual retained
host/Raylib/input/F1 declarations**, plus the actual owned Gate from parent
`6ae2aafe8c19e00a67d6f026450341a900e09af0`. These are syntax-only probes: no game
objects, PDB, executable, link, new launch or rendered integration. Logs and exact
source hashes remain private. No guest instructions/functions or generated game
code were inspected for this source preparation.

## Remaining acceptance

1. Implement a bounded concrete request/ack transport to the sole Python writer,
   with strict schema, immutable request identity, conditional commit, no arbitrary
   environment/path input and explicit stale/unknown handling.
2. Add the native factory and reviewed ordered host integration. Keep all old
   variants/pointers/fingerprints and default Original unchanged; no mutating
   self-test in ordinary launches.
3. Build a separately checked variant after disk-capacity review. Preserve all
   earlier source/binaries/PDBs/INIs/discs/evidence. No automatic deletion or
   weakening of containment checks to work around low space.
4. Observe the **real retail-backed** overlay, acknowledged hold, edit/save ACK,
   invalid/stale refusal, close/resume, stop, new-process reload and original/
   old-version rollback. Do not substitute a standalone menu demonstration.
5. Publish selected unchanged native originals and accurate scope only after
   review. No mock pixels or fabricated comparison for the current non-rendered
   source work. Hardware/audio, genuine Save/exit/Load and campaign gates remain.
