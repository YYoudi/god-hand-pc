# Native prototype bootstrap and the remaining input boundary

11 November 2026. Follow-up to [the first debug investigation](PROTOTYPE_DEBUG.md).
This is actual native startup progress, **not a working debug-menu release**.
The public installer still targets retail. No installed retail executable or
Original-mode policy has been changed.

## What now runs

A separate private prototype executable displays the original memory-card check,
**PRESS START** title screen and pre-recorded attract movie. Movie footage is not
proof of interactive prototype gameplay, a reconstructed scene or a working cheat.
The journal publishes selected unchanged build captures, not screenshots of itself.

The original prototype disc and ELF are unchanged. This experiment uses frozen
LasVola runtime/IOP/GUI libraries from revision
`1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a` and private, prototype-specific
translation inputs. Static SNR2 tooling comes from pinned GPL upstream revision
`193076584e277c95644dcbbb4a6922c3a59ca2b8`. There is no retail function-map,
overlay-base or debug-address transplant. Retail SDK routines were comparison
anchors, not addresses to reuse in the prototype.

The changes are more than labels or a successful linker exit:

- Qualify SDK routines by complete address-normalized instruction spans and call
  relationships, then route coherent SIF/filesystem/CD boundaries through existing
  native handlers. Do not fabricate readiness or successful replies.
- Observe the prototype's real McPort and r020 modules at load time. Their complete
  statically linked original files equal their native pre-constructor images.
  Generate private native modules: McPort has 355 functions/2,853 dispatch entries;
  r020 has 30 functions/432 entries. Identity-gated installation and unregister/
  overlapping-load cleanup are required; this is not general relocatable support.
- Recover the prototype's own boot relocations instead of baking in unlinked
  imports. Preserve all 9,793 original object files and earlier executables.
- Recover sixteen actual MPEG routine entry boundaries missed by the earlier
  discovery pass. Their instructions were already inside an overmerged routine,
  but indirect calls could not enter them. Regenerate 42 changed old units and
  16 new units. Cross-check 2,491 recorded instruction words against the original
  ELF; do not edit opcodes, insert NOPs or fake movie completion.

These checks establish input identity, not an ISA/ABI correctness certificate.
The retained unresolved original translation diagnostic and 1,450 warnings remain
visible in the generation receipt. Generation exit 0 is not a clean translation.
Initial module-table API and mixed MPEG-HLE/original-feed mistakes, black outputs,
and failed controls are retained privately rather than relabeled as successes.

## F2 is a real input path, not an implemented debug action

The original [host sequencing component](adapter/prototype_debug_shortcut.hpp)
requests L2, waits, then requests R3 with bounded release times. It refuses an
open F1 controls overlay, overlapping requests, writer failure, reversed time
or a missed chord window. It contains no game addresses, instructions or assets.
A C++17 invented-input test covers those cases. The exact unchanged header is
compiled into the private native executable.

The native F2 handler and an explicit diagnostic request use the same component.
The diagnostic is **not a physical F2-key test**. Its logs acknowledge only input
submission and expiration, never that the game opened a menu. No guest function
is invoked from the host UI thread, and no guessed debug flag is written.
F1 remains the existing controls screen. The prototype shortcut is not installed
as a retail F2 command or enabled in normal public launches.

## The current blocker

A targeted original Start request reaches the frontend and the IOP controller
wire. The game nevertheless remains at PRESS START and then enters its attract
movie. Cross and the L2/R3 sequence do not establish a debug action either.
Read-only guest-thread observations find the title consumer's held/edge values
still zero during the requests. SDK port-open calls return success, but the
original port0/port1 state queries return0; the port1 read remains empty.
Those SDK roles are inferred from original call/packet consumption, not recovered
source; port0 never progresses to its read phase.

This narrows the next investigation to the original libpad / IOP-to-EE status and
packet boundary. It does not yet identify the faulty instruction, DMA operation
or driver behavior. Do not force a ready state, synthesize button flags in game
memory, or call this a functioning prototype/debug port.

An earlier timing hypothesis was tested: a second Start was sent after an actual
observed return to the title, not just during a movie. It still did not advance
the title. Earlier hidden probes also exposed unconfigured host key activity;
they are not clean no-input controls. A separate same-executable trial explicitly
disables all hardware bindings and keeps only a virtual diagnostic pad. Both isolated90s cases stop0 through the watchdog;
OFF is idle, ON carries exactly the requested Start/Cross/L2/R3 values. Seven
preselected OFF/ON frame originals are byte-identical, and the title input values
remain zero. These results and exact build identity are recorded in the linked
evidence, separately from the earlier observations.

## Acceptance still required

1. Find and fix the verified original input/status boundary, with invented-data
   regression tests and clean no-input/input controls. Preserve the failure.
2. Observe the original debug menu through the native F2 path, then a functioning,
   reversible action with original before/action/restore captures.
3. Validate Room Jump/resource lifetime, Player Warp, no-death versus no-damage,
   and the remaining options independently. A visible label is not acceptance.
4. Expose only validated actions in the appropriate PC F2 Developer backend.
   Retail equivalents need retail identities/contracts; prototype evidence is
   not retail fidelity. Keep scratch saves and Original mode unchanged.

The broad faithful-PC objective remains unachieved. Hardware input/audio, genuine
retail Save/exit/Load, campaign coverage and general performance remain separate
open gates. No autonomous combat/level-completion loop was used.

## Publication and provenance

The [build/evidence receipt](docs/evidence/prototype-bootstrap-2026-11-11.json)
identifies the local executable, source-input snapshot, commands, captures and
limits. The executable and complete game-derived source are intentionally not
public. This is a research harness, not a source-complete prototype installer.
Generated game source was inspected privately for the GPL continuation; the
work is not presented as an independent clean-room engine.

No disc, ELF, extracted asset, raw map, dump, save, binary or generated game code
is published. Our original continuation code is GPL-3.0-only. Game imagery is
neither MIT nor GPL; the owner's publication request is not rights-holder
permission or legal certification. Originals are downloadable byte-for-byte.
