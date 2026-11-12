# A public SDK-input producer for the prototype build

12 November 2026. This follows the [source build](PROTOTYPE_WHOLE_SOURCE.md) and
its [own normal debug-action checks](PROTOTYPE_WHOLE_INTERACTIVE.md).

The original matching/qualification algorithms previously ran through three
private selector scripts. They now have public, parameterized GPL source:
[prototype_sdk.py](prototype_sdk.py) and
[prototype_sdk_inputs.py](prototype_sdk_inputs.py), revision
`08d92331b8fb6bc1e34c50075c0a72a41a8338b0`.
No private selector is executed by this new production path. No populated
address map, game body or upstream metadata table is included in these files.

## What the command actually does

It reads explicitly hash-qualified original prototype/retail ELF inputs, pinned
SDK/function metadata and the previously generated prototype discovery sources.
The retail input supplies **identity evidence**, not addresses transplanted into
the prototype. It searches the prototype's own text and uses bounded normalized
span/CFG/direct-target consistency models. Exact normalized matching is **not**
complete instruction semantics, independent SDK-name identification, function
boundary, live ABI, overlay-lifetime or runtime-effect proof.

The source has bounded ELF/metadata/CFG/search inputs, immutable byte models,
explicit output line endings and no execution of private scripts or source text.
Incoming context can narrow a candidate domain, but never enables an ambiguous
HLE candidate that has no outgoing known-anchor evidence. Unknowns remain open.

Outputs are private reports and an SDK-binding include, not a PC executable.
The command only writes a **new Git-ignored session** under this repository's
`.local/prototype-sdk/sessions/`; existing sessions and aliased paths are refused.
Check-only and identity/session refusals create no output. It does not extract
a disc, invoke a recompiler/compiler, launch a game or modify an original input.

## Actual reproduction and connection to the build

A new run uses the existing original personal-disc ELFs, frozen metadata from
revision `193076584e277c95644dcbbb4a6922c3a59ca2b8`, and the fresh discovery inputs
already produced in the earlier selected-source setup. It is **not** a new disc
extraction, translation, whole setup, native build or gameplay run.

The new public algorithms reproduce all107 initial/CFG candidate records and
all selected record fields after excluding the older prose-only scope field.
The selected103 bindings,105 context domains and152 known-direct checks agree;
two candidate targets are rejected and12 ambiguous targets remain unresolved. Of the
selected records,59 have no known-direct check: normalized identity alone must
not become a general ABI or execution-coverage claim.

Fresh results and their manifest are written **before** the earlier selected
maps are consulted as comparison oracles. With explicit CRLF, all3,422 binding
include bytes equal the actual input of the unchanged `e677f789…` native build.
The first LF version has the same103 logical lines but3,319 bytes; it is not
called byte-identical to that consumer input.

The exact-source public CLI separately passes six actual commands: check-only,
wrong ELF identity, wrong discovery identity, unsafe session, new production and
stale-session refusal, with exits0/2/2/2/0/2. Its five non-production controls do
not change the output tree. The new production equals the API result and the
retained native host input byte-for-byte. This is the build connection, not an
assertion that static matching itself proves the debug menu or game fidelity.

The executable remains exactly
`e677f789c9f51400ba054b5a72ab7807f363a5bd4c099ba10f5c2c07edcc8e34`.
Its linked native evidence remains the **earlier** normal sessions and originals;
no new rendering or gameplay result is claimed here. Native07/default and
explicit `room01-v1` profiles are unchanged; the new source build is not adopted.

## Retained failures and controls

- The first actual API run refuses the arbitrary100,000 registration-comment
  ceiling. Inspection finds136,956 word-slot comments within659,964 text words,
  not136,956 discovered functions. The corrected bound uses the actual text-word
  count and requires every comment address to be aligned and inside that text.
- The next run reproduces all candidate/domain results but fails the exact-byte
  include check because LF differs from the old CRLF file. That failure/output
  is preserved. A **separate new run** requests explicit CRLF and passes; no
  previous failed receipt is relabeled.
- An invented search control demonstrates that advancing four bytes after an
  unaligned occurrence can skip a later aligned match. Searching each byte and
  accepting aligned results fixes that stepping issue. Current real candidate
  outputs remain unchanged. This is not a newly observed native bug.
- An invented LD/address-origin control guards the distinct historical linear
  and CFG write policies. Sharing the wrong set would preserve a stale origin;
  the negative control demonstrates that difference. No full ISA claim follows.
- Sized reads keep a one-byte growth sentinel without reserving the24-MiB ceiling
  for every tiny source file. Both earlier and sized-reader CLI controls are
  retained; changed source has its own actual controls. This concerns setup
  file I/O only, **not native FPS or game optimization**.

The full suite passes **404 synthetic tests**, with three Windows skips, in
**61.728seconds**;44 new invented-data controls cover the producer/input CLI.
No personal/game bytes or pixels enter those fixtures.45,662 retained identities
match, including prior failures, original inputs, source/object variants and the
MIT lab WIP. The whole native build and normal launch profiles are unchanged.

## Using the producer

This is one reviewed stage, **not a public ISO-only prototype installer**. The
qualified original ELFs, frozen metadata and correctly generated discovery tree
must already exist privately. Supply their independently recorded identities;
hashing an arbitrary folder does not make it a qualified discovery result.

```powershell
python prototype_sdk_inputs.py --prototype-elf $PrototypeElf --prototype-elf-sha256 $PrototypeHash --retail-elf $RetailElf --retail-elf-sha256 $RetailHash --functions $FunctionCsv --functions-sha256 $FunctionHash --sdk-metadata $SdkMetadata --sdk-metadata-sha256 $MetadataHash --discovery $Discovery --discovery-sha256 $DiscoveryHash --session sdk-first --binding-line-ending crlf --check-only
```

Replace the variables with private input paths/qualified hashes. Omit check-only
to create a new ignored session; never publish its reports/include. The discovery
digest is SHA-256 of sorted UTF-8 `basename\0fileSHA256\n` records for every
immediate `.cpp`, including registration source. Default binding text is explicit
LF on every platform; CRLF must be requested for the existing consumer postimage.
No binary or game source is downloaded or distributed by this command.

## Remaining setup work

The SDK matching/qualification core and its input CLI no longer require the three
private selector programs. The **remaining** direct/indirect entry selectors,
original host/main/IOP continuation, qualification profiles and whole-build
orchestration still need their own provenance review and public packaging. A
fresh public setup must then compile and receive its own native acceptance.
Do not repeat the already observed exact-e677 named actions as if they were
missing, or infer that these static results finish the full debug menu.

Translation diagnostics, strictVU/render/loading/accounting0x480 limitations,
wider options/rooms/input/reference/ABI/lifetime/failure recovery, hardware/audio,
genuine Save/exit/Load and campaign fidelity remain open. The full goal is active.
No prototype result establishes a retail debug backend. Source exposure stays
GPL continuation work, not a new MIT/clean-room reimplementation. ISO/ELF/assets,
dumps/cards, populated maps, generated game/VU code and binaries remain private.

The [aggregate receipt](docs/evidence/prototype-sdk-producer-2026-11-12.json)
records the bounded results without publishing the private binding contents.
