# Named texture plans, version 1

This is a metadata planner, not yet a public launcher or an HD texture API.
It resolves a named resource from the owner's verified retail US ISO without
reading or exporting its original texture pixels/palette. The existing private
runtime experiment accepts one resolved read-overlay range; connecting this
planner to that adapter is a separate validation gate.

## Pack contract

Create an original native-format pixel/CLUT payload and a UTF-8 JSON manifest:

```json
{
  "schema": 1,
  "profile": "retail-us-slus-21503",
  "replacements": [
    {
      "target": {"path": "st1/r100.dat", "scp": 3, "bank": 0, "image": 0},
      "payload": "original.raw",
      "sha256": "REPLACE_WITH_THE_64_CHARACTER_PAYLOAD_SHA256"
    }
  ]
}
```

`path` is a case-sensitive FST path; `scp` is the **outer DAT section ordinal**,
not the occurrence number of an SCP tag. `bank` is the inner DAT section ordinal;
`image` is a TM3 image ordinal. Tags must match SCP and TM3 exactly. The example
selects a locally verified 128x128, 4-bit stored-layout texture with 8,256 bytes
of pixel indices plus palette. No absolute game offsets belong in the pack.

```powershell
python pc.py resource-plan --iso "G:\path\God Hand (USA).iso" --pack "G:\my-pack\pack.json"
```

The command verifies the complete ISO hash, then resolves ISO9660 root catalogs,
FST path / AFS ordinal, outer DAT / SCP, inner DAT / TM3 and TIM3 header.
It writes a new uniquely named metadata plan under ignored `.local/plans/`.
Plans contain local paths and resolved ranges: do not publish them automatically.
The ISO is opened read-only; no disc extraction, patching or game execution occurs.

Only one replacement is supported. Its size must equal the original stored
pixel-plus-CLUT span; its own SHA-256 must match. The payload path must resolve
inside the pack directory. Unknown/duplicate fields, unsafe paths, wrong profiles,
malformed metadata and unsupported texture formats fail without producing a plan.
There is no silent retry with a guessed offset. Run without a pack for original
assets; automatic in-game fallback/reloading is not implemented by this planner.

Supported TIM3: version 4, one picture, 48-byte picture header, no mipmaps,
RGBA32 CSM1 palette, 4/8-bit indices, linear selector 0 or the bounded native
selector 6 profile. Payloads are stored bytes, **not decoded RGBA**. This does not
support larger dimensions, new materials, arbitrary pack execution or prototype
discs. Original format contracts are linked in `resources.py`; this is an original
parser implementation. Synthetic tests contain only invented bytes, never game
assets. Game ownership does not grant redistribution rights to game data.
