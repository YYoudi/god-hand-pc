# Bounded prototype metadata inventory

Date: 9 November 2026. Scope: read-only, offline discovery on the owner's saved
prototype and separately identified retail ELF. No new native boot, debug-menu
operation, gameplay patch, instruction disassembly or decompilation was performed.

## Inputs and method

The prototype is the previously profiled June 2006 image, boot SLPM_665.50;
the retail comparison is SLUS_215.03. The unchanged prototype ELF is 3,450,144
bytes and the retail ELF is 3,607,008 bytes. Both match their prior SHA-256
profiles. The original prototype image also matches its prior complete digest.
The saved TCRF HTML was parsed locally, not replaced with a current web page.

Ordinary Python inspected ELF32 little-endian MIPS section metadata and stored
NUL-terminated ASCII in allocated, non-executable PROGBITS sections. This excludes
executable-flagged data sections, other encodings, overlays and runtime strings;
the counts below are **bounded keyword matches**, not all strings/functions.
REA tools were absent in the session; the read-only CLI doctor reported missing
Codex registration. No configuration was changed. These are ordinary local byte
inspection results, **not REA Evidence** or a disassembler's function analysis.

## Observations

| Bounded selection | Prototype | Retail |
| --- | ---: | ---: |
| Distinct stored-string records matching selected categories | 464 | 317 |
| Debug/menu category matches | 44 | 10 |
| Camera category matches | 48 | 35 |
| Rendering category matches | 47 | 28 |
| Timing category matches | 29 | 15 |

Categories overlap; they must not be summed as unique coverage. There are 284
exact common selected texts. Prototype-only diagnostics include room selection,
camera tools, collision-related labels, light/fog toggles and lighting-loader
diagnostics. Their presence is useful for choosing investigations, not proof
that a menu, resource format or runtime flag is usable in retail.

**An important correction to “stripped means no names”:** neither input has a
normal ELF symbol table, but both retain an allocated metadata section containing
function-like names and repeated name-pointer/code-address candidate records.
A conservative probe accepts only contiguous runs of at least ten 12-byte-spaced
records, bounded name pointers, restricted printable names and aligned targets
inside that input's text section:

- Prototype: 659 candidate records; longest accepted run: 53.
- Retail: 743 candidate records; longest accepted run: 73.
- Exact common names in accepted records: 556; prototype-only: 103, retail-only: 187.

These are **inferred registry associations**, not 659/743 understood functions,
full symbol recovery or recovered C++. Nonaccepted records are not evidence of
missing functions. The third word and registry consumers are not decoded.
Different builds have different addresses: no map was transplanted to retail.
Three invented-data tests check record stride, isolated-pointer rejection and
invalid name/target rejection; they do not validate game semantics.

## Useful next investigations, not implemented features

1. Verify one name/address association against a bounded actual runtime call
   before using it as a function-replacement boundary; handle overlays and ABI.
2. Use camera/light diagnostic vocabulary to focus private format and subsystem
   investigation rather than guessing a new renderer API.
3. Preserve a terminology trap: **FPS in camera labels can mean first-person**,
   not frames per second. No variable-frame-rate mechanism was discovered.
4. The HTML's room-jump/debug controls remain reported leads. Static labels do
   not bypass the separately reproduced native prototype syscall-0x7a blocker.

## Provenance and publication

Private scripts, exact file/VA ranges, raw strings, candidate maps, input digests
and the saved-page text remain in ignored research storage. No extracted text
table, address map, game code, program image, screenshot or asset is published
with this report. Only aggregate observations and methodological limitations are
public. Metadata/name exposure is explicitly recorded; this work is not being
passed off as a newly clean-room implementation. No Rust feature was changed.
