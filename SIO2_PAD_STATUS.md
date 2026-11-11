# Prototype input repair and the original debug menu

11 November 2026. Follow-up to [native bootstrap](PROTOTYPE_BOOTSTRAP.md).
The full developer-tools goal remains active. This is not a completed prototype
port, a retail debug backend or an accuracy certificate.

## The input failure was below the game menu

A new run of the unchanged earlier executable records real PADMAN DMA transfers
to both expected EE buffers. Their frame counters advance, but the input length
and connection state stay zero. This contradicts the missing-DMA hypothesis.

The original controller driver sends one batch with two ordinary pad commands.
Port 0 acknowledges; the unconnected port 1 does not. The retained generic SIO2
implementation collapses that into a missing-device value whose error bit refers
to port 0. The original driver consequently rejects the connected controller.

Primary-source inspection informed the experiment:

- [PS2SDK padData, revision 0c36f32](https://github.com/ps2dev/ps2sdk/blob/0c36f32d9a6f45b99894faaf54d35af088bd79b1/iop/input/padman/src/padData.c)
  checks separate response-error bits when consuming a batch.
- [PCSX2 Sio2, revision c8081bf](https://github.com/PCSX2/pcsx2/blob/c8081bf5d63b1b83b77112632e1113a25b81058c/pcsx2/SIO/Sio2.cpp)
  and its [register definitions](https://github.com/PCSX2/pcsx2/blob/c8081bf5d63b1b83b77112632e1113a25b81058c/pcsx2/SIO/SioTypes.h)
  distinguish missing controller ports and account for the commands processed.

These references are not a hardware oracle. In particular, the SDK reader uses
transfer positions, while that PCSX2 implementation describes physical-port
bits. Our actual native evidence concerns the canonical port-0-then-port-1 batch.
Synthetic tests of other orderings check the chosen model, not physical PS2
behavior. Do not claim general packet-order or multitap conformance.

## An explicit generic SIO2 candidate, not forced ready flags

The original [PadBatchStatus component](adapter/sio2_pad_status.hpp) preserves a
separate missing bit for each controller. It never marks an unanswered port as
present. It refuses empty, repeated-port, unknown and mixed/card/multitap batches;
the private integration retains the previous policy for unqualified transfers.

A new private native build compiles the exact unchanged public header into a
copied generic GPL SIO2 unit. `PS2X_SIO2_PAD_STATUS=per-port-v1` explicitly selects
the candidate; absent selection preserves the prior implementation. It does not
replace game instructions, SDK return values, game input flags or debug flags.
Original controller negotiation still runs in the IOP. The frozen runtime archive,
game objects, existing retail variants and original discs are not overwritten.
The generic source files are identical in our retained upstream revisions
1646d885 and 19307658; no claim about current upstream master is made.

### Actually reproduced controls

Same new executable, fresh private scratch data, hidden/muted 20-second cases.
All eight hardware-binding configurations are disabled; only explicitly counted
virtual diagnostic pads are connected. These are not physical-controller tests.

| Candidate | Virtual pads | Original port 0 state | Original port 1 state |
| --- | --- | --- | --- |
| Disabled | One | Disconnected | Disconnected |
| Enabled | None | Disconnected | Disconnected |
| Enabled | Both | Negotiates, then stable | Negotiates, then stable |
| Enabled | One | Negotiates, then stable | Disconnected |

All four cases stop 0 after the watchdog requests shutdown, not campaign success.
With the candidate enabled, the original title consumes ordinary Start/Cross
input and advances. With it disabled, the reproduced input failure remains.
Sampled disabled originals at fields 120, 850, 950 and 1000 equal the preserved
old executable byte-for-byte; field 900 differs. That discrepancy is retained,
not described as complete baseline parity or silently normalized.

## The original debug menu now executes

The shared native F2 handler's explicit diagnostic path sends the original
L2/R3 chord. The game itself draws Room Jump, Flag Edit, DEBUG OPTION, Player Warp
and SHOOTING MODE. No replacement menu is drawn by the host.

An actual native sequence opens Room Jump with Circle, moves its selection with
Down, returns to the parent menu with Cross, then closes that menu with Cross.
Original captures show the difficulty screen restored. A second sequence changes
the original Room Jump target from Stage 0 / Room 20 to Stage 1 / Room 00.

The exact key-event path and F1 coexistence still need dedicated native UI
verification; a diagnostic handler invocation is not a physical F2 keypress.
The unchanged runtime still ticks and draws its existing F1 controls separately.
The public shortcut refuses a request while F1 owns input.

The first confirmed Room Jump request loads the prototype's actual r100 module,
then requests Event. These are private original-disc translations, not a retail
room map. R100 has 32 functions/1,190 dispatch entries and its whole linked file
equals the native load observation. Event has 291 functions/2,374 entries: its
code equals the native observation, but 12 symbol-registration flag bytes differ
from the BOOT-only static registry. Those differences are qualified and retained;
whole-file equality is not claimed for Event.

The next retained trials expose missing original BOOT entries, rather than an
asset or input failure. Six real export entries required by the observed modules
and two entries in an observed original dispatch table are qualified against the
original instructions and terminal return pairs. The new translation replaces
48 old BOOT units and adds 24 entries in total, including the earlier MPEG work;
3,149 recorded instruction words are checked. No opcodes or return stubs are
invented. The original unresolved diagnostic and 1,450 warnings remain.

The resulting native11 build executes Stage 1 / Room 00 / Point 0 and renders the
original western room and Gene's in-engine introduction. This is a real loaded
3D scene, not the title's pre-recorded attract movie or a synthetic scene. The
180-second diagnostic ends at captured field 3360, before the scheduled field
4000 second chord. This does **not** establish free gameplay or usable speed.

Player Warp, no-death effects and reversal, in-scene debug access, further rooms,
retail equivalence and general fidelity remain unfinished acceptance gates.
Do not enable public Developer switches on the strength of their menu labels.
The full goal remains active. The [reviewed native evidence](docs/evidence/prototype-pad-menu-2026-11-11.json)
records the exact builds, actions and unchanged originals.

## Reproducibility and publication boundary

The public component and its test use invented inputs only. Private generated
game bodies and stored names were inspected; this is the GPL continuation, not
an independent clean-room engine. Dispatch-entry counts do not prove arbitrary
guest-PC coverage or readable decompilation.

The exact private build identity, actions, selected unchanged originals and
limits accompany the journal comparisons. The public installer still targets
retail; there is no source-complete prototype installer or downloadable game.
No disc, ELF, asset extraction, dump, save, binary, raw address map or generated
game code is published. Game imagery is neither MIT nor GPL; the owner's selected
publication request is not rights-holder permission.

## Synthetic validation for this milestone

`python -m unittest discover -s tests -v`: 261 tests, exit 0, three Windows
symlink skips (85.614 seconds). The new C++17 model test passes with invented
packet outcomes. These tests do not execute the game or establish hardware,
menu-action, controller/audio or general SIO2 conformance.
