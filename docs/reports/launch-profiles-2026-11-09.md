# Original/Enhanced launch-policy validation

Date: 9 November 2026. Original GPL continuation tooling revision:
`cc62cb780a703629c2ccc88b4ba53d9b59a4e8a3`. Pinned LasVola base:
`14e956a1274332440273845fbab2c1f1e30c4a5a`.
The private native source remains `193076584e277c95644dcbbb4a6922c3a59ca2b8`;
this Python policy increment does not relink or alter generated game functions.

## Reproduced checks

- All 89 original synthetic continuation tests pass on the evaluation machine;
  the public continuation CI passes at the same tooling revision. Eight new
  tests cover default/explicit policies, rejection before runtime/disc/process
  access, CLI forwarding and invalid choices. No game material is a fixture.
- An actual Original+pack CLI request returns 1 with a policy refusal, before
  native launch. An invalid pack is not silently ignored in Original mode.
- Two independent fresh hidden 220-second native starts use the same executable
  and title/start script, separate empty private user data, captures and explicit
  audio muting. Original has no pack; Enhanced requests the original diagnostic
  pack in strict mode. No attack/level-completion script or old snapshot is used.
- Both native processes end at their configured deadline (124); both launchers
  return 0 and finalize receipts. These are bounded controls, not hours of stable
  gameplay or performance measurements.
- Both selected actual full-resolution field-4741 PNGs were inspected unchanged.
  The Original PNG is byte-identical to the retained disabled/pre-adapter baseline;
  the Enhanced PNG is byte-identical to the earlier enabled magenta control.
  The bridge logs applying the original 8,256-byte payload.

Selected original SHA-256:
`fd53182e7a2982021e5c5008d2e5dbab4dbd907cf9dfe52edc520c9a5d02315e`.
Selected enhanced SHA-256:
`96a8c748aeca15e321ac53a61d36ab068325851fcec76c395d52d3d88020f809`.
These are the same image bytes already published with their historical capture
provenance in the [earlier comparison](https://yyoudi.github.io/god-hand-rs/dashboard/#comparison-2026-11-06-public-native-pack-bridge).
That old gallery record is not relabeled as a new capture. New originals and
their timestamps/commands/receipts remain preserved privately. Known 800x600
readback padding remains visible; no crop or recolor is used.

## Reproduction

Use the successful setup/bridge workspace, exact personal retail ISO and original
example pack described in the separate GPL repository:

```powershell
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --headless --seconds 220 --capture --fresh-user-data --pad-script "1800v:start:20,2100v:cross:20,2400v:cross:20,4200v:start:20,4800v:start:20"
```

For the second control add `--profile enhanced --pack .local/published-example/pack.json --strict-pack`.
Each launch verifies the original ISO, source and binary before starting, cleans
inherited GODHAND_/PS2X_ settings, and verifies the disc again after exit.
Do not copy private cards/states into CI or assume another workspace is equivalent.

## Limits and next gate

The profile names are policy, **not a PS2 fidelity certificate**. Both retain
upstream settings/timing and the previously built native runtime. This does not
implement an in-game settings menu, readable game-function replacement, HD
dimensions, widescreen, FPS changes, new lighting or multiplayer. Same-size
resource replacement and one sampled scene remain the only enhancement proof.

Genuine game Save/exit/Load, physical input, audible audio, later-stage behavior
and translation diagnostics remain explicit gates. Next audit existing upstream
PC settings and actual card persistence paths, rather than invent another menu
or attempting to beat levels. The prototype's native kernel blocker is unchanged.
