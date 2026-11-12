# Fresh prototype-source build and actual F1/F2 taps

12 November 2026. Follow-up to [original no-death](PROTOTYPE_NO_DEATH.md).
The full developer-tools goal is still active. There is no complete keyboard
debug-menu release or public prototype installer yet.

## Source build, not a pile of old objects

A new ignored build directory compiles all 9,816 selected BOOT units, the host
overrides, the four selected prototype modules and the selected prototype VU1
programs. Configure/build/link finish 0. None of the old prototype objects or
prototype libraries are linked; all 9,793 old objects remain unchanged.

Five identity-pinned **generic** runtime/IOP/GUI/graphics libraries are still
reused. The private generated sources are not regenerated from the ISO in this
experiment. The 103-row private SDK binding input can be rendered exactly from
the qualified private metadata, but that is not a fresh re-qualification from
two discs. These are explicit remaining setup dependencies, not a source-complete
public installer or proof that every function was decompiled into readable C++.

Frozen runtime revision: `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`.
MSVC 14.44.35207; separate fresh source-only executable:
`78c8101f1cc6a356b2e60ccc3db376c402b2339a26a8c351ed17dadb417e84ad`.
The source inventory records 10,739 source/header/build inputs. A successful
compile is not guest coverage, full gameplay, ABI or PS2 fidelity acceptance.

## Reject a wrong disc before installing prototype hooks

The earlier private native harness relied on its Python run driver to verify
the disc/ELF. Directly launching that executable could bypass those checks.
The new separate candidate checks exact size and whole-file SHA-256 **inside
the native process**, before scratch directories, runtime initialization or
prototype-specific hooks. The verified inputs remain open read-only.

Original GPL [LockedInputFile](adapter/locked_input_file.hpp) keeps Windows API
declarations in its [implementation](adapter/locked_input_file.cpp), not in the
public header. An actual retained-Raylib syntax probe exposed Rectangle/window
name collisions in the first inline design; the separated version passes.
No warning suppression or global `NOUSER` workaround is used.

The guard opens with share-read but without write/delete sharing, checks the
size and identity metadata, streams bytes to the existing pinned generic SHA-256
implementation and compares the expected digest. See Microsoft's
[CreateFileW sharing contract](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)
and [handle metadata API](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle).
This is a supported-profile check, not an adversarial path-resolution or general
filesystem security certificate. No game file is opened for writing.

Seven direct-native negative controls pass: retail ELF, retail disc, missing ELF,
missing disc, invented same-size wrong ELF, invented same-size wrong disc, and
an already-open writer on our **invented** ELF. All refuse before runtime/window
or scratch setup. Size-only acceptance is explicitly rejected by the two real
digest-mismatch controls. No writer is opened on an original game file.

The original Windows fixture uses invented bytes and a deliberately toy hasher
to test byte delivery, read sharing, write refusal, move/release and exceptions.
It is not SHA-256 validation. The actual native controls above use the retained
real SHA-256 backend. The corrected full synthetic suite passes 263 tests, three
Windows symlink skips, 68.579 seconds. Initial test-driver lint failures remain
preserved, not labeled passing.

## What the actual keyboard trial proves

After renewed owner permission, a visible, muted, bounded run uses scratch
keyboard-only preferences, no SDL bindings and **no fake pad**. It ends 0 via
its prospective 900-second watchdog. Original controls, ELF and disc hashes
are unchanged afterward. No owned compiler or synthetic suite overlaps it.

Initial Computer Use activation fails and one returned screenshot shows another
application. No keys are sent to that image, and it is not saved or published.
The owner later requests a retry. A fresh correct game-window observation is
obtained before the successful key actions.

While waiting for that recovery, a separately recorded diagnostic phase uses
controller-file requests to skip the movie and select original Room Jump
Stage 1 / Room 00 / Point 0. Each append checks the live native process handle,
executable path and creation time; a submitted request is still not delivery
proof. Original room/actor captures confirm the result. This bootstrap is **not
cold-start keyboard acceptance** and is not relabeled as actual Windows keys.

Then, in the same native process:

1. An actual Windows F1 action opens the original controls screen.
2. An actual F2 tap records press and release; the F2 request is refused while
   F1 owns input, and F1 stays visible.
3. An actual F1 tap closes controls; the normal room/HUD is visible. The refused
   F2 does not open later on its own.
4. A subsequent actual F2 tap is accepted and opens the original debug menu.
   The selected native PNGs below bracket this real-key action.

This verifies that scoped F1/F2 path, not all keyboard usability. **One brief Down
tap did not visibly move the original menu cursor**, even after settling. The
ordinary-key callback/level/IOP path is not traced yet, so its cause is unknown.
The later K/Cross close attempt encounters the watchdog-ended window and is not
close/resume proof. Do not confuse the normal watchdog exit with a successful key.

F1's original screen says the game keeps running. No acknowledged pause, controlled
focus-loss/pending-event test, held-key/repeat behavior or physical keyboard/
controller-device acceptance is claimed. OS-injected key events are not a human
hardware-peripheral test. F3 was not repurposed.

## Evidence and remaining work

Guarded native executable SHA-256: `1947fbd7bfe6368e55ec8c816356d0886f4bc0c05da6767141227de7966fd619`.
Private source/library/input chain snapshot: `bc71eec964b0bd407d43aca216339a25f92f05b9311bdf65285bdb052f4926a6`.
The [aggregate receipt](docs/evidence/prototype-source-build-2026-11-12.json)
records commands, inputs, scoped outcomes and limitations without publishing maps.

Selected unchanged GS-renderer PNGs show the original Room Jump destination and
the real F2 before/after. Dimensions change from 640×480 to 640×515 during the
foreground/window-interaction period; the cause is not isolated. No crop, resize,
normalization, widescreen fix or image-parity claim is made. Comparisons are
unmatched action evidence, not matched-camera fidelity tests.

Original native-window F1/F2 captures are backend JPEGs. They remain private
because the current reviewed comparison profile is PNG-only; they are not
converted, silently reclassified as journal screenshots or used to bypass it.
Only reviewed native PNG originals are published here, never screenshots of the blog.

Next: trace actual Down/K/L events, host levels and the original pad consumer;
verify normal-key navigation and close, then controlled focus/held/repeat cases.
Keep the earlier Warp and no-death proofs tied to their exact older executables;
they are not silently rerun or certified on this new candidate. Other options,
rooms, a fresh ISO-only workflow and any retail equivalent remain separate gates.

Private generated prototype source was inspected/compiled for this GPL continuation,
not an independent clean-room component. No ISO, ELF, extracted asset, raw map/log,
dump, save, executable, generated game source or third-party implementation is
published. Game imagery is neither GPL nor MIT; the owner's request is not
rights-holder permission. The historical Rust lab remains paused and untouched.
