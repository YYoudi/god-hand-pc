# Point1: six GS checkpoints

13 November 2026. New original-game recording and GS-only replay evidence.
No scheduler candidate is installed, no game renderer is corrected or promoted,
and no retail, full-fidelity, remaster or game-performance result is claimed.

## New bounded original-native observation

A prospective run uses the unchanged native e677f789 executable, original
prototype disc/ELF, same finite Room Jump/Start script and new scratch outputs.
The earlier long-recording attempt's startup access violation remains a failure;
its dump and the subsequent lifetime investigation are not replaced by this run.
No debugger, compiler, test suite, emulator or offline replay overlaps this run.

The existing native watchdog is300s; normal exit0 occurs after303.890s including
startup/cleanup. Nine original PNGs are actually exported. Three overlapping
samples3300,4501,5001 equal the retained same-filename originals byte-for-byte.
That is sampled continuity, not all-frame, ordinary-play or full-state parity.
No attack loop, health flag, synthetic ready state or forced return is used.

The original recorder requests4500 plus12 ticks. Its ACTUAL closed window is
State4501, Field4503/4505/4507/4509/4511 and End4513: five Field checkpoints
plus End, rather than a comparison of only one possibly inherited front buffer.
The private file is42,229,278 bytes,29,686 records including initial State,
22,860 draws. The replay tool reports29,685 records after consuming that State.
Neither the recording, VRAM, extracted assets nor generated game code publishes.

Initial and4503 checkpoint payloads equal the earlier short recording, but the
command prefix is NOT byte-identical, even excluding MXCSR for classification.
Its first differing raw payload is a Submit record; semantic meaning is not yet
qualified. Do not call the complete recordings identical or discard differences
as harmless padding. All original bytes are kept and replayed without filtering.

## Actual sequential replay results

The existing pinned GPL GS-only helper is reused, including its previously
documented End-checkpoint observer correction. No EE/game function executes and
no new helper or game build is made. Runtime source remains LasVola1646d885;
helper SHA-2566b5f7fa3ca427e64430bfbc9cd873c28336e8caf82fbff843cef13c58ae2ba0a.
Observed GPU environment: NVIDIA RTX5080/OpenGL4.6/driver621.01, not a universal
GPU or driver certificate. All cases run separately after the native writer exits.

- Standard CPU replay returns0, recorded VRAM bit-exact at ALL SIX checkpoints.
- Standard GPU replay returns1 at the FIRST failed checkpoint4503:43,490 VRAM
  bytes differ. The original helper returns on this mismatch; its timing is NOT
  a completed six-checkpoint run or a game-FPS measurement.
- The paired CPU/GPU observer actually presents all six checkpoints, then
  returns1. Its first RGB image is identical, but subsequent images differ.

| Recorded tick | RGB pixels differing, CPU vs GPU | Maximum RGB-channel difference |
| --- | ---: | ---: |
| 4503 | 0 | 0 |
| 4505 | 124 | 3 |
| 4507 | 7,269 | 46 |
| 4509 | 7,525 | 52 |
| 4511 | 7,640 | 48 |
| 4513 | 7,624 | 50 |

These are512x448 RGB images from the same recorded presentation request.
They do not certify GS alpha/depth, game state, camera behavior or PS2 fidelity.
At4513 the paired observer also finds87,192 differing VRAM bytes AFTER its
presentation calls. Standard-replay and paired-observer checkpoints are distinct;
their byte counts must not be interchanged. PNG-only analysis independently
confirms7,624 changed RGB pixels/max50/mean absolute0.109437 at that final pair.

## Negative controls, not recommended settings

Two existing upstream diagnostic variants are actually replayed: disable the
texture-page cache; then disable both page cache and fast triangle setup. Both
still return1, with7,505 and7,472 differing final RGB pixels respectively.
The CPU original at each checkpoint is byte-identical across all three pairs.
This does not isolate a single cause, prove GPU repeatability, rank the variants
as improvements, or justify changing defaults. The CLI name `gpuoriginal` means
an upstream diagnostic option, not the original PS2 renderer or an accuracy mode.

## Reviewed originals and visible limits

The gallery publishes the unchanged CPU/GPU PNGs for the final recorded4513
checkpoint. They are originals from the OFFLINE replay renderer, not new full
native-game screenshots or an emulator reference. The same-frame label applies
only to this shared GS recording/presentation request. No crop, rescale, fitted
camera, asset replacement or color correction is used.

Both show Gene, the green wall and HUD, and both retain the lower-ground
ghost-like shape. Its cause is still not established as cloth, shadow, temporal
presentation or another layer. The new result is that the initial zero-RGB-diff
observation hid later differences; it is NOT a repaired artifact or GPU quick fix.
Selected game imagery has separate rights, not the repository's GPL license;
the owner's publication request is not rights-holder authorization.

Next: bound same-backend repeatability and, if runtime capacity permits, compare
qualified native CPU/GPU controls with the same original inputs. Diagnose the
actual state/command/presentation layer before changing defaults or materials.
The scheduler candidate still needs isolated prototype AND retail native
acceptance after its separate link-capacity gate passes. No Rust rewrite, menu
polish, guessed flags, deleting evidence or weakening the accuracy gates.
