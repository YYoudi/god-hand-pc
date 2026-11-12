# Public entry-input production for the prototype

12 November 2026. Follow-up to [the SDK producer](PROTOTYPE_SDK_PRODUCER.md).
Original GPL source revision `989b65a34c42b827e7e473ec0d7fa3964223ba08` adds
[prototype_entries.py](prototype_entries.py) and
[prototype_entry_inputs.py](prototype_entry_inputs.py). The import-use,
local-pointer-table and entry-span stages no longer execute our three private
selector scripts. Game bytes, populated maps and generated game code stay private.

## Inputs and dependency provenance

The CLI reads a hash-qualified personal prototype disc, its original ELF, and
qualified discovery sources from the earlier selected-source setup. It requires
the disc's named BOOT file to equal the supplied ELF and checks the disc hash
before and after production. There is no disc extraction, game translation,
compilation or native launch in this increment.

It explicitly uses the GPL upstream SNR2 registry metadata model from
LasVola/godhand-recomp revision `193076584e277c95644dcbbb4a6922c3a59ca2b8`.
That dependency is based on upstream reverse engineering, not a newly independent
engine or independent SDK/ABI proof. Its content is **not copied** into our repo.
The prototype's **own `.sndata` section address** is passed explicitly; the
upstream retail default is never used.

Dependency source must match pinned Git bytes or the explicitly checked LF→CRLF
checkout postimage. Both identities/policies are recorded. Only those verified
source bytes are executed as the named tool dependency, not an existing unchecked
Python bytecode cache, private selectors or generated game functions. Registry
flags are host-side static symbol metadata, **not controller-ready status or
writes to guest RAM**. This does not qualify all loader, ABI or lifetime behavior.

## Actual private production

The new command scans all 76 cataloged prototype modules, observing 6,487 original
import JAL uses. Two uses remain unresolved; 25 missing-entry candidates are
recorded and seven import relocations whose original words are not JAL are
rejected. None is guessed or turned into a stub.

The conservative local scan considers 659,964 text words. Unknown instructions,
control transfers, branch targets, fresh entries and delay slots are metadata
flow barriers. There are 23,619 unknown-barrier occurrences, 17 locally code-backed
uses and five pointer-table candidates. These are not complete CFG/ISA coverage,
executed callbacks, complete valid-index domains or ownership/lifetime proofs.
Stored-pointer uses are explicitly not proven later callback loads.

The explicit five-module scope yields 12 direct and 21 indirect entry ranges.
Known catalog modules with no missing direct import do not become “unknown” and
do not cause a fallback to a different scope: only three of the five contribute
to direct selection here. Unknown selected modules are still refused.

Direct spans retain their terminal-pair check. Indirect spans use the existing
union-fence model, terminal pairs and known non-call outgoing-transfer checks.
Those bounded checks do not prove full function boundaries, entry reachability,
arbitrary branch/call behavior, return semantics or ABI. Generated labels are
ours, not recovered game function names.

Fresh reports and their manifest precede older-oracle reads. All import/local-scan
record fields and selected entry records agree; only the old prose-only scope
field is excluded from table-provenance comparison. Both actual native consumer
inputs are **byte-identical**: the 1,786-byte entry CSV and 4,083-byte runtime
instruction-relocation CSV, containing 298 records in original table order.
Only the declared instruction-relocation type subset is emitted; no general
SNR2 linker completeness is claimed.

This connects the new public producer to the existing source-built executable
`e677f789c9f51400ba054b5a72ab7807f363a5bd4c099ba10f5c2c07edcc8e34`.
That executable and its earlier [normal debug-action evidence](PROTOTYPE_WHOLE_INTERACTIVE.md)
are unchanged. No new game run, rendering fix, menu-option coverage or native
profile adoption is claimed.

## Real controls and retained failure

The first actual check-only attempt fails its dependency-source guard: the local
Windows checkout is CRLF while Git stores LF. Its source, failure receipt and
empty output state are preserved. It is not relabeled as a passing run or game
bug. A separate new run accepts **only** the exact LF→CRLF postimage (or exact
Git bytes), not arbitrary CR removal or other source changes.

That new seven-command block gives exits 0/2/2/2/2/0/2 for check-only, wrong ELF,
wrong disc, wrong discovery, unsafe session, new production and stale session.
Two separate actual controls also refuse the wrong registry revision and an
unknown selected module with exit2. All eight non-production controls leave the
private output tree unchanged. No old selected map is a producer input.

The full suite passes **442 synthetic tests**, with three Windows skips, in
**61.764seconds**. Thirty-eight new invented-data tests exercise the models,
source/dependency guards, own-section argument, local barriers, R5900 MULT/U
destination handling, module scope, private outputs and exact CSVs. CLI IO-only
mocks are identified as such, not substituted for the real-disc command above.
All 45,676 retained identities match, including old inputs/native objects,
original screenshots, earlier failures and MIT lab WIP. No game fixtures enter CI.

## Running this stage

This remains one source-production stage, **not a public ISO-only installer**.
The original ELF and qualified discovery tree must already exist privately, and
the pinned registry source checkout must be available. Supply independently
recorded identities; hashing an arbitrary folder does not qualify its provenance.

```powershell
python prototype_entry_inputs.py --disc $PrototypeDisc --disc-sha256 $DiscHash --elf $PrototypeElf --elf-sha256 $ElfHash --boot-name SLPM_665.50 --discovery $Discovery --discovery-sha256 $DiscoveryHash --registry-source $PinnedSource --module mcport.rel --module r020.rel --module r100.rel --module event.rel --module r101.rel --session entries-first --check-only
```

Omit check-only to create a **new ignored** session under this repository's
`.local/prototype-entries/sessions/`. Reports, word/address maps and CSVs are
private outputs; never publish them. Existing sessions, input identity failures,
unignored outputs and aliased output paths are refused. The discovery digest
uses the same sorted `basename\0fileSHA256\n` convention as the SDK producer.

## Next work

The SDK and entry-selector production paths are now public and separately
reproduced. Remaining source-setup work is the qualified original host/main/IOP
continuation, its qualification profiles and whole-build orchestration, followed
by a fresh setup with its own native acceptance. Do not repeat these completed
static stages or the earlier exact-e677 named actions as missing tests.

The full debug/port goal remains active. Wider original options/rooms/input,
reference/ABI/lifetime/failure recovery, translation diagnostics, strictVU,
render/loading/accounting0x480, hardware/audio, genuine Save/exit/Load and campaign
fidelity remain open. No prototype result establishes a retail debug backend.
No new Rust or delegation is used. GPL covers our continuation source, not game
rights; no ISO/ELF, asset, dump/card, populated map, generated game/VU code or
binary is published. The [aggregate receipt](docs/evidence/prototype-entry-producer-2026-11-12.json)
contains reviewed results without the private tables.
