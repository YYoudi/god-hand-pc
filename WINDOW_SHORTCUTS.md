# Short host-key events: experimental input edge preservation

12 November follow-up: [fresh source build and actual F1/F2](PROTOTYPE_SOURCE_BUILD.md).
One real shortcut round trip passes; ordinary keyboard navigation/close remain open.
The earlier dated results below are preserved, not relabeled.

11 November 2026. Prototype-native research follow-up, **not a verified F1/F2
release** or a retail launcher change.

## What the new observation establishes

The separate native14 Windows trial records both the GLFW F2 press and release
callbacks. The prior Raylib callback is retained and chained. Neither the
Raylib `IsKeyPressed` observation nor our F2 request handler reports a press.
This narrows the earlier failure: at least this F2 event reached the windowing
callback; it was not a disconnected PS2 controller or a missing debug menu.

The retained [Raylib source at c1ab645](https://github.com/raysan5/raylib/blob/c1ab645ca298a2801097931d1079b10ff7eb9df8/src/rcore.c)
derives `IsKeyPressed` from previous/current key levels. Its
[GLFW callback](https://github.com/raysan5/raylib/blob/c1ab645ca298a2801097931d1079b10ff7eb9df8/src/platforms/rcore_desktop_glfw.c)
updates the current level on press and release. A complete tap processed between
two level samples can therefore be missed. This is the working explanation for
the observed F2 failure; the retained trace does not timestamp every internal
poll boundary. [GLFW's input guide](https://www.glfw.org/docs/latest/input_guide.html#input_key)
distinguishes events from polled key state and recommends callbacks for retaining
state changes. These sources are not evidence of our game's input behavior.

## Original, narrowly owned event model

The original GPL [PressEdges component](adapter/window_shortcut_edges.hpp) stores
one pending press for Controls, Developer or Back. Release does not erase a
pending short press. Repeats do not create another activation. Taking an event
also consumes it when legacy polling detects the same press, avoiding a delayed
second activation. Losing focus clears pending events.

Invented C++17 tests cover short/held taps, repeat, coalescing, legacy/event
duplication, focus loss, invalid keys/actions and consumption order. F1's owner
must run first; the caller refuses F2 while that overlay is open rather than
deferring it until later. The model is not an input owner or a pause oracle.

A separate private candidate compiles this exact header into its generic host
bridge and a copied generic controls unit. The native executable must explicitly
select `PROTOTYPE_WINDOW_SHORTCUTS=edges-v1`; absent selection keeps the previous
key policy. The callback still chains the original Raylib callback. The later
candidate also chains focus events, clears queued edges on focus loss and restores
its callbacks at owned shutdown. F3 remains the existing FPS shortcut; it is not
intercepted or repurposed. No guest functions or flags are invoked from the UI
thread. Existing retail executables and launcher defaults are unchanged.

## Acceptance still open

The original model's synthetic test passes, and the native candidate links.
Neither proves an actual F1/F2 key round trip after the change. The owner stopped
Computer Use with Escape during the earlier trial. No further desktop input was
sent; subsequent work is headless. Keep real-key F1 open/F2 refusal/F1 close/F2
menu access and focus-loss behavior unverified until a renewed authorized test.

Prototype pad scripts can still exercise the original game menu in bounded
private runs; those are not Windows-key tests. Do not relabel the earlier failed
key trials, or count no-death option display as survival behavior. Player Warp,
no-death effects/restoration, checked prototype setup and any retail equivalent
remain part of the active full goal.

Only our original host component/tests and reviewed build evidence are public.
No game translation, raw map, asset, dump, save, disc, executable or copied
third-party implementation is included in this repository.
