# A second named resource through the same boundary

10 November 2026. The unchanged checked HD v1 and explicit GPU v2 now render a
second distinct named resource with original external artwork. Same-binary
absent, invalid-pack and private interior-reference-negative controls restore
the current sampled original-assets image. **Same room, same format**, not a
second validated scene, unique texture ownership, general HD or full-game claim.

## Selection and provenance

Target: `st1/r100.dat / SCP3 / bank0 / image4`. The earlier ground was image0.
Both are128x128,4-bit selector6 with RGBA32 CLUT,8256 stored bytes; all16384 raw
alpha values in the selected source are128. The replacement is a new original
512x512 green/orange stripe pattern with yellow diagonal marks, not game art.

Read-only inventory of this one69-image bank finds14 compatible128x128 decoded
references, all distinct within that subset. A private source preview resembles
vertical planks; that was a hypothesis before intervention, not a renderer
binding. The new pattern is visible on the right raised porch/boardwalk, but
also affects facade pixels. **An isolated-porch-only interpretation is rejected.**
Shared uses and identical-content aliases elsewhere remain unclassified. No
source preview, palette, reference texture or asset sheet is published.

Actual public launcher tooling:
`4ae5d3311980604a546b3faee325015d5781d2f6`.
Pinned LasVola: `14e956a1274332440273845fbab2c1f1e30c4a5a`.

| Retained variant | Native source revision | Executable SHA-256 |
| --- | --- | --- |
| HD v1 | `8dec4950b15f7fffe5e97b580dcc10fb758c8503` | `f17d67d6fc5efc1796176da3bb862dd7e3482f9361650d1f695005f6de3e809e` |
| GPU v2 | `953ea26336227e92455dbea1d4d791dd18b5159c` | `5d27048f688e0264123d733826d8399a4e619af75852fe267100c92409001b02` |

No native relink, game regeneration, generated-function edit, new Rust work,
third-party import or ISO edit. Both installed versions, all older variants and
the baseline source/executable/PDB are preserved. The MIT lab and four pending
Rust files are unchanged. This is ordinary parser/runtime evidence, not REA
retained Evidence or a formally independent clean-room claim.

## Reproduce the authored pack

Run this original Python from the repository. The output directory must be new;
the artwork generator never opens a disc or copies source pixels.

```python
from pathlib import Path
import hashlib, json

out = Path('.local/second-surface-example')
out.mkdir()
rgba = bytes(c for y in range(512) for x in range(512) for c in (
    (245,235,45,128) if (x+y)%64 < 4 else
    (20,220,90,128) if x//32%2 else (235,90,20,128)))
(out/'authored.rgba').write_bytes(rgba)
manifest = {
    'schema': 1, 'kind': 'decoded-rgba-replacement',
    'profile': 'retail-us-slus-21503', 'replacements': [{
        'target': {'path':'st1/r100.dat','scp':3,'bank':0,'image':4},
        'image': {'path':'authored.rgba','width':512,'height':512,
                  'format':'rgba8-gs-alpha',
                  'sha256':hashlib.sha256(rgba).hexdigest()}}]}
(out/'pack.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
```

Authored image SHA-256:
`d447df477f423790ed96c56539484b5fa7bdf34aad9417bdbb925ea16d0b3ecd`.
Its1,048,576 bytes are our diagnostic artwork, not an extracted asset. Use the
existing [checked HD workflow](HD_PACKS.md), without rebuilding a variant:

```powershell
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --hd-textures --hd-pack .local/second-surface-example/pack.json --strict-hd-pack
```

Explicit GPU v2 additionally selects `--hd-textures-version gpu-v2`; no version
still means preserved HD v1. Omit the pack for that same HD binary's original
assets. Original refuses HD requests. HD+controls/same-size packs remain refused.
The native envelope includes a complete private source reference read from the
verified personal ISO; **never distribute that envelope or reference**. Strict
mode checks preflight, not whether the GPU will visibly apply a replacement.

## Executed controls

All long probes use fresh scratch cards/controls/quick-state paths, no imported
save or runtime snapshot, muted headless output and the same script:
`1800v:start:20,2100v:cross:20,2400v:cross:20,4200v:start:20,4800v:start:20`.
Native command uses `--headless --time-limit <seconds>` through the public
launcher except for the separately labeled reference negative. Capture requests
include4740; actual selected field is4741. No attacks or autonomous level
completion, no camera/object/internal-scale edit. This is not hardware input,
active-combat throughput, audio-quality or Save/Load evidence.

| Observed control | Result at actual field4741 |
| --- | --- |
| Public HD v1, valid source4 pack,300s | Complete source match logged; original512x512 pattern renders. PNG `cce213978ff1670d2b9ab8ef83f0e83d6eadf79325ec6eb1a60d0cf2b5002ea8`. |
| Same HD v1, no pack,220s | No HD upload. Current original-assets PNG `9bd97cff522321767ad5e101e11989751131ca32c2a2a7e76d55d6e80ab6e5be`. |
| Same HD v1, wrong authored-image hash,220s | Public preflight fallback clears HD input and reproduces that same original PNG. Not a native checksum test. |
| Public explicit GPU v2, same valid pack,300s | Upload and submitted/counts-unread logs; selected PNG equals the v1 enabled original byte-for-byte. No CPU match-count claim. |
| Direct same HD v1, one private reference byte changed,300s | Valid envelope/hash still uploads, no exact-match diagnostic, selected PNG equals absent/fallback. Only R at reference(47,59) changes; authored image and ISO are unchanged. This is not a public preflight control or zero-matches-throughout-game proof. |

All four public launchers return0 and natives124 at their normal deadlines;
direct-negative observer0/native124. No forced termination or shader errors.
Actual strict-invalid and Original+new-pack preflight refusals return1 without
native spawn. No stale inherited self-tests, timing queries or quick-state load
enter normal launches. Five installed variants, input snapshots and ISO verify.
Private receipts: `G:\God-Hand-PC\.local\second-resource-2026-11-10\`.
Runs span00:41:52..01:04:28 UTC,10November2026 (01:41..02:04 Europe/Paris).

## Original images and limits of alignment

The [selected comparison](https://yyoudi.github.io/god-hand-pc/comparisons.html#2026-11-10-second-named-resource)
uses the two new **same-binary** absent/enabled observations, both640x480, with
unchanged original bytes. The absent9bd97cff file equals an already reviewed
640x480 reference in the gallery; its bytes are reused without rewriting the
older observation's provenance. Capture times for this new pair are the Windows
last-write times of its native
PNG files (UTC), not fabricated replay times. Both new reference and output are
native LasVola continuation, not Bevy, PS2 hardware or remaster artwork.

Post-hoc RGB comparison finds6253 changed pixels, bounding box
`[204,198,640,378)` (exclusive maximum). Two proposed unaffected regions are
exact: upper sky/actor `[0,0,640,160)` and lower ground/HUD `[0,395,640,480)`.
The proposed mid-left facade `[0,160,430,330)` **fails**:1114 pixels change. The
initial analysis asserted all three regions unchanged and stopped; its source
and failure are retained. Corrected analysis reports the original boxes/results,
not smaller boxes chosen to hide changes. No edited difference image is published.

The older baseline PNG was800x600. These new640x480 originals are **not** its
byte-identical replay. A simple top-left640x480/padding hypothesis also fails;
it is not used to establish cross-run alignment. The reason for the capture-size
change was not established here and is not an implemented screenshot fix. Do
not resize, crop, overwrite or relabel the historical originals to hide this.
Acceptance above uses only the new same-size matched set. No overall original-
renderer parity or unchanged capture environment is claimed.

## Synthetic tests and next gates

195 original invented-data tests locally:193pass/two Windows symlink-privilege
skips. Two new tests use an invented two-image bank, prove nonzero selection
uses its own reference while authored pixels stay equal, and reject out-of-range
selection rather than falling back to image0. Initial fixture mistakes (stale
in-memory bytes,17-byte label in a16-byte span) are corrected and retained;
no production parser bounds/tolerance changed. No retail data enters CI.

PC04 remains in progress: a second resource in this room is now proven, but
another room, more formats/sizes/states and alias ownership are not. Broader
GPU/backend/driver performance/state, true SaveExitLoad, physical input/audible
audio, campaign fidelity and HD+controls composition remain open. The previous
[timing block](FRAME_SPANS.md) still establishes no reliable speedup. Widescreen,
simulation-safe FPS, modern lighting, multiplayer and the prototype kernel
remain separate work. The full PC/remaster goal is active, not complete.
