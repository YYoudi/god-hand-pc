# Prototype debug tools: investigation and PC integration

11 November 2026. This is an incomplete research milestone, not a debug-menu
release. The retail PC build and its default launch policy are unchanged.

## What we are trying to build

Keep F1 for the existing controls screen. Add a **Developer tools** section to
our explicit F2 extension only when a real backend has been validated. Initial
targets are room/stage selection, player warp and no-death mode. Later candidates
include enemy/display toggles and camera inspection. Screenshot labels alone do
not establish what each option does; these are targets, not available features.
In particular, preventing death is not necessarily preventing damage; test that
distinction before calling a flag invincibility.

Two possible backends remain open:

- Run the prototype's original debug functions in a separate native prototype
  build, generated locally from the owner's disc.
- Implement verified equivalents for retail, using that build's own function,
  state and resource contracts. Never copy prototype addresses or room IDs into
  retail, or assume the retail executable retains its debug UI.

Neither route requires a Rust/Bevy rewrite. Do not duplicate a complete engine
just to expose an existing game action.

## New observations

Private read-only inspection of the exact prototype ELF found the constructor
that registers **Room Jump, Flag Edit, DEBUG OPTION, Player Warp and SHOOTING
MODE**, together with their callback entries. The evidence now goes beyond
finding labels: the registration calls associate labels with callbacks.

Twelve selected generated bodies were cross-checked against 370 original ELF
instruction words recorded in their emitter comments. This checks input identity,
not instruction translation, calling-convention correctness or runtime effects.
Private generated code was inspected for this GPL continuation; this is not a
new clean-room implementation. No game source or raw address map is published.
Ghidra's generic MIPS language misinterprets some R5900 instructions and truncates
some decompilations. Its pseudocode is not recovered original source or an oracle.

A **new private native harness** links successfully using 9,793 unchanged
prototype object files and five frozen generic runtime/IOP/GUI libraries from
LasVola revision `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`. No retail game
library, function map or generated retail code is linked. This reuses the earlier
prototype translation and its unresolved diagnostic; it is not fresh generation
or a public prototype installer.

The harness routes two verified prototype SDK wrapper entries to the existing
SIF register handlers. It does not fabricate successful replies or set ready
flags. The syscall identities are documented by the open-source
[PS2SDK syscall definitions](https://github.com/ps2dev/ps2sdk/blob/0c36f32d9a6f45b99894faaf54d35af088bd79b1/ee/kernel/include/syscallnr.h).
A separate invented-value set/get/previous-value test passes against those
linked handlers; this is not a hardware-conformance test.

| Same executable, fresh scratch, hidden/muted 60-second run | Observed result |
| --- | --- |
| SDK routing disabled | The original unsupported `0x7a` diagnostic recurs; one black export at field 1. |
| SDK routing enabled | Four SIF reads and two writes; no `0x7a` warning. Execution subsequently waits for an RPC acknowledgement. Exports at fields 1, 60 and 120 are the same black image. |

Both processes exit 0 after the watchdog requests shutdown. **That is not a
successful game boot.** The final enabled-run PC lies in the selected SDK RPC
initialization wait, consistent with the analogous handshake in
[PS2SDK's implementation](https://github.com/ps2dev/ps2sdk/blob/0c36f32d9a6f45b99894faaf54d35af088bd79b1/ee/kernel/src/sifrpc.c).
No native title, scene, debug menu, invincibility or warp has been observed.
Scheduler field exports do not prove guest gameplay progress.

Local executable SHA-256:
`58d82c8b9e95c00332c27183daa7bbba2ce08bd53289d59a9917485b7dd3199c`.
Prototype ELF SHA-256:
`f9974f97a7c38a6f1d0fcdd66e0f9424bbe109ecca745493628b468d8ce5242e`.
MSVC 14.44 compiled the new host file and linked the existing objects. Original
prototype executable/libraries/objects, both discs, nine retail variants and
historical Rust WIP were preserved. There were no retail rebuilds or game inputs.
Initial Ghidra path/argument failures and a host-test macro compilation failure
are retained locally, not reported as passing attempts.
The unchanged public-main tooling suite passes 257 synthetic tests with three
Windows symlink-privilege skips. These tests do not execute the prototype.

## Integration gates and next experiment

1. Verify the prototype SDK/RPC boundary as a coherent group, or validate a
   specific retail equivalent. Do not force readiness or hide another blocker
   behind a return-zero stub. Static no-death labels still need flag consumers
   and actual behavior tests.
2. Establish exact disc identity, ABI, object initialization and overlay/resource
   lifetime for **one** action. Reject unsupported builds and unavailable states.
3. Execute typed requests at a verified guest-thread safe point, never call guest
   functions from the host UI thread. Preserve the existing F1/F2 input owner and
   acknowledged-hold protocol; define how an action completes before resuming.
4. Prove the action and its disable/restore control in native execution before
   drawing an enabled F2 control. Keep Developer mode explicit, Enhanced-only,
   with scratch preferences/saves and no automatic game-save writes.
5. Publish selected original before/after captures only for a genuine observed
   action, same build and viewpoint where meaningful. The owner's PCSX2 images
   remain private references, not a matched native success pair.

Next acceptance is **one functioning, reversible debug action**, not five
decorative switches. Genuine retail Save/exit/Load, hardware input/audio,
representative fidelity and campaign testing remain separate unfinished gates.
The unrelated readable-function WIP and isolated readback candidate are retained,
not silently merged or declared complete.
