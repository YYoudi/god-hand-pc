# Prototype F2: actual mouse navigation of the original menu

12 November 2026. This is a scoped prototype result, not a full debug-menu release,
a retail backend, a keyboard fix or a finished port. The original menu remains
the game menu; the new panel only submits ordinary controller input requests.

## What changed

An explicitly selected `controller-v1` host surface appears after an accepted F2.
It has Debug chord, Up/Down/Left/Right, Circle, Cross, Start and Hide buttons.
It does not replace the original options or pretend to know the current guest
menu. Circle confirms and Cross goes back. Hide hides **only** the host panel.
The host panel does **not** pause the running game.

This is additional PC UI, not a workaround silently changing keyboard semantics.
A separate read-only trace identifies the automated Down tap as GLFW_UNKNOWN
(-1, scan256), not Down. An earlier K tap lasted62 microseconds within one poll.
Neither observation proves a physical keyboard fault; no keyboard was required
from the absent owner and no unknown scancode was remapped.

The new original GPL code is in `adapter/prototype_controller_panel.hpp`,
`prototype_controller_view.hpp` and `prototype_controller_native.hpp`. The
native trial compiled these exact headers, now committed at
`6235f99fea14563463c6636d90289678d10cf64e`. At capture time they were uncommitted
additions to public base `fac575f7789192ed2533cfc5c787a20438a1e275`; the matching
post-test commit does not change that chronology. The private host integration
and generated prototype inputs still prevent claiming a public ISO-only setup.

## Safety and ownership

- Exact original prototype ELF/disc size and SHA-256 are checked and read-only
  handles retained before runtime/hooks, as in [the source build](PROTOTYPE_SOURCE_BUILD.md).
- Explicit opt-in only. Pad1 must have keyboard-only live bindings; other pad
  slots are explicitly disabled for this experiment. Pointer/controller/chord
  bindings disable the panel instead of being silently rewritten.
- The existing GLFW mouse callback is chained. One press edge retains its
  coordinates/size/time; stale, resized, unfocused and F1-owned clicks are dropped.
- Requests use the existing finite controller FIFO:200ms button with a300ms
  minimum request interval. The original debug chord retains its longer sequence.
  There are no game flag/HP/register writes, UI-thread guest calls or fake ACKs.
- F1 closes the panel and cancels pending clicks. It cannot undo an already sent
  bounded pulse. Writer failure means delivery-unknown and disables further
  panel/chord requests for that run. No automatic retry or success claim.

## Actual native trial

Executable SHA-256:
`837ee7ec3153925d8855e02a9b13423ef1554571f7576acf64b1fe051af6905d`.
Private source/file chain:
`ab42ef077b5c6cd8f6b12898c83f17d565af63b9851f9a193742061c35cb392a`.
The new host unit linked9,821 objects and prototype libraries from the **fresh**
source build, not the old9,793 prototype objects; five pinned generic libraries
remain reused. Compile-main, compile-guard and link return0. Three direct
invalid-version/prerequisite/other-pad refusals return34/35/36 before creating
runtime output.9,841 retained file hashes and eight source input hashes agree.

The visible run starts07:25:32 UTC and exits0 at07:33:27 UTC, after475.175seconds.
It has a900second watchdog, but was closed normally with actual Alt-F4 **after**
the observed Continue prompt. It did not run900seconds or need a forced kill.
No owned compiler/test job overlapped this native run.197 native GS PNGs remain
private, with selected unchanged host-window originals reviewed for publication.

| Observation | Evidence and boundary |
| --- | --- |
| Bootstrap loads original1/00/Point0 room | Declared field script plus shared field1400 debug request; **not** actual keyboard/mouse Room Jump. |
| Actual F2 opens original menu and host panel | Software OS F2, original Room Jump/DEBUG OPTION/Player Warp labels visible. |
| Actual mouse Down then Circle | Original cursor moves to DEBUG OPTION, then original option list appears. No external FIFO writer after bootstrap. |
| Actual Right selects PL NO DEATH ON | Original OFF/ON displays; mouse Cross twice restores the actual room/HUD. |
| Actual F1 then F2 then F1 | F1 controls screen owns input; F2 request refused; closing F1 returns gameplay without a deferred panel/menu. |
| Later actual F2, mouse Down/Circle/Left | Original option ON becomes OFF; Cross twice restores gameplay; Hide removes only the host surface. |
| Real ON/OFF effect | Three selected ON damage calls reduce25HP total and five original positive-HP refill-site events restore maximum. After menu OFF,14selected damage calls accumulate to HP0 at field10728; visible collapse and Continue follow. |

One additional selected OFF hit occurs **before** ON;15OFF calls in the whole
trace must not be described as15after deactivation. Selected damage calls are
not all health writers. This trial demonstrates original refill behavior and
restored death, **not** a lethal-total survival test while ON:25is below100maxHP.
The earlier [native22 lethal-total/no-death proof](PROTOTYPE_NO_DEATH.md) is a
different executable, with its own unchanged evidence. No attacks, autonomous
level-completion loop, save import or health writes were used.

## Images and publication

The journal shows the actual native menu/panel, OFF/ON, normal return, F1 owner
and OFF/Continue states. These are **unchanged original JPEGs returned by the
owned-window capture backend**,642x512 including the native title/border. JPEG
is lossy; these are not lossless renderer captures, pixel-parity comparisons or
PS2 references. Dates are recorded capture-completion observations, not claimed
guest-frame timestamps. Different states/times are labeled **unmatched**.

A new explicit `native-host-jpeg-v1` comparison publication profile checks source,
unchanged-original/lossy declarations, hash, bounded baseline JFIF envelope and
dimensions. It rejects EXIF/comments, progressive/multiscan data and trailing
bytes. This structural check is not a full JPEG decoder or fidelity test. The
old PNG profile stays unchanged. Native JPEGs use the comparison registry under
`docs/media/`; none are misclassified as journal screenshots. Synthetic neutral
JPEG fixtures, callback stubs and an autocrlf checkout test use no game pixels.
Game imagery is not covered by our source license or rights-holder permission.

## What remains

The original menu is now navigable and closable via this additional mouse UI,
but only the named original no-death option is exercised through it here.
Room Jump through the new panel, Player Warp controls/effect/exit through it,
other options/invalid states, repeated focus/held-input acceptance and a checked
personal-disc prototype setup remain open. The panel does not yet expose analog
stick requests. Existing Warp evidence does not silently qualify this UI.
Strict VU1 comparison still fails; hardware/audio/save/campaign and retail debug
claims remain separate. The full developer-tools goal stays active.
