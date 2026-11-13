# Two-room regression on the scheduler variants

14 November 2026. This tests the isolated scheduler correction with a natural
prototype room cycle. It is not a new game translation, renderer improvement,
complete port, fresh ISO-only installer or default-profile promotion.

## Actual route

The finite original controller route is **Stage1/Room01/Point0 -> Room00/Point0
introduction -> Room01/Point0**, without restarting the native process. The first
interior/Gene/enemies/HUD is observed at3100, Room00 selection at6500, exterior
introduction at8400, and returned interior/Gene/enemies/HUD at11000. All originals
are unchanged; different actor poses are retained. The scenario does not directly
edit health, position, guest PC, readiness, instructions or menu flags to force
an outcome. No attacks or
autonomous level-completion loop occurs.

The same prototype's already-qualified selected-source capsule contains the
required Room01/BOOT bindings. No retail function map or address is transplanted.
The original runtime and candidate differ only in the generic scheduler unit
documented in SCHEDULER_RETIREMENT_CANDIDATE.md.

## Reproducible original scenario CLI

`prototype_scenarios.py` is original GPL tooling. It verifies the exact existing
private executable, personal prototype ELF/disc, scenario schema and fresh
private session before launch. It creates separate scratch controls/cards and
retains commands, inputs, source fingerprints, observation expiries, native
exit and original exports. It does not generate or distribute a game.

`scenarios/prototype-scheduler-room-cycle-v1.json` explicitly selects the new
480-second budget and the earlier finite route. The earlier290b experiment had
a300-second budget: its result is not inherited by the e677-based scheduler
variants. Missing fields would remain missing; no live deadline is extended.

With the qualified private setup and your own prototype inputs:

```powershell
python prototype_scenarios.py `
  --scenario prototype-scheduler-room-cycle-v1 `
  --build scheduler-candidate-v1 --exe "$Candidate" `
  --elf "$PrototypeElf" --disc "$PrototypeDisc" `
  --controls-seed "$ReadOnlyControlsSeed" --session candidate-room-cycle
```

Use `scheduler-control-v1` with its exact original-control executable for the
counterpart; `source-v1` explicitly selects the preserved frozen e677 build.
There is no automatic detection or fallback. `--check-only` creates no session
or process. Do not reuse a completed or partial session name. The normal
interactive workbench still strips diagnostic inputs and is not this command.

The native diagnostic capsule also writes raw module/RAM observer files into
the **private** session. Never publish the session directory wholesale. Only
reviewed original PNGs and aggregate findings belong in the public journal.
This CLI is a finite original-input workflow, not a semantic room API, retail
debug backend, physical-key test or generally qualified arbitrary scenario.

## New results, not transferred old acceptance

| New run | Native exit | Elapsed | Original PNGs |
| --- | --- | --- | --- |
| Initial private candidate, 13 November | 0 | 484.219s | 13 |
| Public-source CLI original-control, 14 November | 0 | 484.531s | 13 |
| Public-source CLI candidate, 14 November | 0 | 484.062s | 13 |

The two14November CLI runs have all13 corresponding PNGs byte-identical; they
also equal the initial private candidate samples. Every original input and
cloned controls fingerprint agrees before/after. The source that actually ran
is exactly the committed CLI blob, SHA-256
`9ddcd088dfb4f696772740228cf8a0428f3daf90564e4d353415b38ba445d201`.
Actual read-only CLI checks return0 for the candidate,2 for the wrong frozen
selector, and2 for an existing session, creating no sessions or overwrites.

The six selected module registrations show Room01 installation/clear, Room00
and Event installation/clear, then Room01 installation again in the **same
process**. The two15,206-byte Room01 linked snapshots use the same observed
base and equal each other and the previously qualified own-disc linked input.
All six new module snapshots equal the prior qualified cycle's private images.
Those earlier files are comparison oracles only, consulted after new capture,
not producer inputs. No raw module bytes, RAM, maps or addresses are published.

This establishes one named same-base return, not variable-base loading, every
retired lookup, transactional installation, all callbacks or cleanup ownership.
The sampled PNG identity is not every-frame, ISA, GS or full-game fidelity.
Different final present fields and elapsed times are not a performance test.
Known renderer/translation/installation limits remain; no diagnostic is hidden.

### Retained failures and interruption

The original-control completed this cycle. That **does not erase** its earlier
9.219s and55.391s access violations in the original catch VU0 read, nor prove the
old lifetime defect absent. The guarded synthetic failures and native retirement
observations remain separate evidence; absence of a crash is not correctness.

An earlier13November public-CLI control has an incomplete receipt and no
recoverable native exit. Its processes were absent at resumption and Windows
had subsequently rebooted; the exact interruption cause is unknown. That case
is preserved, counted as neither pass nor diagnosed crash. Its candidate was
never launched. Fresh14November cases were started only after authoritative
idle/input checks, not because an observation wait expired.

## Tests, scope and next work

Ten new invented-data tests cover schema/budget/field/input bounds, inherited
environment removal, read-only refusal and no-overwrite behavior. No game data
or pixels are fixtures. After all native handles terminate, the full Windows
suite passes543 tests/four skips in101.947s.

Retail acceptance remains the separately dated native startup/first-scene,
retirement/VU0, UI-command and frozen rollback controls already reported; this
prototype route is **not** a retail level test. Real Save/exit/Load, hardware,
audible audio, broad campaign fidelity and PC enhancements remain separate gates.

Decision: keep the scheduler candidate **experimental**, with unchanged defaults.
The next gap is durable, explicit generic-runtime build/relink integration from
qualified source and inputs, not more copies of this completed room/menu test.
The restored retail source is not its cached continuation postimage; preserve
its pause/probe/audio additions and source/ABI/link provenance. Broader native
ordinary-transfer/sequence coverage remains bounded, not invented. The goal
stays active. No new Rust or delegation is used.

GPL covers our continuation tooling, not game imagery or rights to the game.
