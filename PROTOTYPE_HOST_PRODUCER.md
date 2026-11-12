# Original prototype host source production

12 November 2026. Source `dd5b061ac6ef0bb8922af7b275d93461b5aefa49` publishes the original GPL
[host main template](adapter/prototype_host_main.cpp.in), original window bridge,
[host integration recipe](adapter/prototype_host_integration.json), and
[private-output producer](prototype_host_sources.py). This follows the public
[SDK](PROTOTYPE_SDK_PRODUCER.md) and [entry](PROTOTYPE_ENTRY_PRODUCER.md) producers.

## What is now public

The host main handles file identity checks, execution policy, module attachment,
SDK dispatch, F1/F2 callback chaining, the controller panel and optional read-only
diagnostic observers. It contains our original host statements, **not translated
game function bodies**. Its 516 lines are parameterized: 57 numeric-literal
spellings and ten include paths remain typed private inputs. Some are ordinary
bounds/masks, not game addresses; this is not a count of recovered functions.
No populated address map or local research path is published.

The three override files are produced from separately fetched GPL host source at
LasVola/godhand-recomp `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`.
Only our reviewed edits are published (2 header, 6 IOP implementation, 7 F1 screen
edits), not full upstream files. Upstream attribution/licenses remain applicable.
The IOP addition observes actual per-port acknowledgements through the existing
public PadBatchStatus helper; it does not force libpad ready or write guessed
menu/game flags. F1 uses the same host edge ownership already tested with F2.
This is continuation work with disclosed source exposure, not clean-room MIT.

The four generated game functions containing original observer insertions stay
private. They are **not** templates or source inputs to this publication. The
insertion-only reconstruction helper and its separate qualification boundary
remain described in [the whole-source report](PROTOTYPE_WHOLE_SOURCE.md).

## Source identity and output rules

Dependency checkout bytes must equal the pinned Git blob or exactly its LF→CRLF
postimage; both identities and the policy are recorded. The original templates
have explicit LF checkout attributes, exercised with real Git checkout machinery
and `core.autocrlf=true`. Private output EOL is separately specified. Numeric
parameters accept a single unsigned 32-bit hex literal, not C++ expressions;
include parameters cannot insert directives or parent traversal. Parameters,
output names and complete output SHA-256 identities must match exactly.

All five sources are planned and verified before creating a new ignored output
session. The upstream checkout and previous tested host files are never edited.
A private profile is data only; the producer does not execute it or compile any
source. It requires previously qualified prototype values and **does not derive
or certify their game identity, ABI, lifetime, module bases or correctness**.
The SDK binding include and generated module headers remain separate private
outputs of their own stages, not embedded game code in this tool.

## Actual result, connected to the native build

The new private source manifest was saved **before** reading the old postimage
oracle. All five produced files equal the actual tested host sources byte for
byte: main, window bridge, IOP header/implementation and F1 screen. Sizes and
SHA-256 identities are in the [aggregate record](docs/evidence/prototype-host-producer-2026-11-12.json).

Their consumer is the unchanged executable
`e677f789c9f51400ba054b5a72ab7807f363a5bd4c099ba10f5c2c07edcc8e34`.
Its [earlier normal-action observations and original screenshots](PROTOTYPE_WHOLE_INTERACTIVE.md)
remain dated evidence of F1/F2, original Room01, one Warp movement/normal-camera
return, and separate no-death ON/OFF/health loss/Continue. This increment is source
production, **not another native run or a new visual result**. It neither promotes
that executable nor changes existing normal07/room01-v1 launch profiles.

Nine actual commands return the expected `0/2/2/2/2/2/2/0/2`: check-only, wrong
private-profile identity, wrong typed value, wrong complete postimage, C++
expression refusal, wrong upstream revision, unsafe session, fresh production,
and stale-session refusal. All eight non-production output trees stay unchanged.
The exact-source suite passes **465 tests, four Windows skips, 72.245 seconds**;
23 new tests use invented source/profile fixtures, never game/vendor fixtures.
45,676 previously retained file identities match. The earlier 464-test invocation
preceded the final checkout-contract test; it is retained, not mislabeled as the
final source run. No owned native/compiler process ran during these validations.

The new CLI is a source stage, not a launch command:

```powershell
python prototype_host_sources.py --source <pinned-private-upstream> `
  --profile <qualified-private-profile.json> --profile-sha256 <profile-sha256> `
  --session <fresh-private-name> --check-only
```

Without `--check-only`, outputs go only under ignored
`.local/prototype-host/sessions/<fresh-private-name>`. Never publish that profile,
its populated parameters, generated outputs, game sources, discs, cards or binary.

## What still blocks a complete public setup

Private profile derivation/qualification and whole-build orchestration still need
public original tooling and their own fresh personal-disc setup/native acceptance.
This publication closes the opaque **original host-source** dependency, not those
remaining data dependencies. No new whole compile is attempted with less than
10 GB free on G:; capacity must be rechecked first, without deleting old evidence
or moving research to C:.

The retained translation error/warnings, strict VU1 and rendering/loading limits,
0x480 accounting warning, wider original debug options/rooms, variable-base and
failure/lifetime coverage, physical input/audio, genuine game Save/Load and human
campaign acceptance stay open. Prototype is not retail. No FPS, graphics or
full-menu-completion claim is made; the full goal remains active.
