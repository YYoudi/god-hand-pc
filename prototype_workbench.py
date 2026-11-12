"""Original GPL-3.0-only launcher for one qualified PRIVATE prototype build.

This adopts a local executable; it does not generate, fetch or distribute a game
or constitute a public ISO-only prototype installer. No diagnostic CLI options.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BUILD_SHA256 = '0afc8392bcab3db0aeb2ef3c9d57d9530598a408c68fa707091db56ac195c2e6'
ELF = (3450144, 'f9974f97a7c38a6f1d0fcdd66e0f9424bbe109ecca745493628b468d8ce5242e')
DISC = (1261928448, '5871f717ea7f3239cbc75e49790d5202c0b5041c392d1317e616ee1d344ceb7e')
PREFIXES = ('PS2X_', 'PROTOTYPE_', 'GODHAND_')
# Original keyboard-only defaults. Existing preferences are NEVER overwritten.
CONTROLS = '''# God Hand PC prototype workbench: original keyboard-only defaults.
[Pad1]
Type = DualShock2
Deadzone = 0
AxisScale = 1.33
ButtonDeadzone = 0
Up = Keyboard/Up
Right = Keyboard/Right
Down = Keyboard/Down
Left = Keyboard/Left
Triangle = Keyboard/I
Circle = Keyboard/L
Cross = Keyboard/K
Square = Keyboard/J
Select = Keyboard/Backspace
Start = Keyboard/Return
L1 = Keyboard/Q
L2 = Keyboard/1
R1 = Keyboard/E
R2 = Keyboard/3
L3 = Keyboard/F
R3 = Keyboard/G
LUp = Keyboard/W
LRight = Keyboard/D
LDown = Keyboard/S
LLeft = Keyboard/A
RUp =
RRight =
RDown =
RLeft =
LargeMotor =
SmallMotor =
'''


def ordinary(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or path.is_symlink() or getattr(info, 'st_file_attributes', 0) & 1024:
        raise ValueError('Expected an ordinary file: ' + str(path))
    return info


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(path, expected, size=None):
    path = Path(path).absolute()
    info = ordinary(path)
    if size is not None and info.st_size != size:
        raise ValueError('Unsupported input size: ' + str(path))
    if digest(path) != expected:
        raise ValueError('Unsupported input SHA-256: ' + str(path))
    return path


def private_path(root, *parts):
    # Refuse pre-existing aliases at every component before resolving; no moves,
    # deletion or write into owner-supplied arbitrary paths. Not an adversarial
    # filesystem/race certificate. Local .local root must already be trustworthy.
    root = Path(root).absolute()
    for name in parts:
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', name):
            raise ValueError('Private names use 1..64 lowercase letters/digits/hyphens')
    p = root
    for name in parts:
        p = p / name
        if p.is_symlink() or (p.exists() and getattr(p.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('Private path alias refused: ' + str(p))
    if not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('Private path escapes workspace')
    return p


def launch_environment(parent, user):
    env = {k: v for k, v in parent.items() if not k.upper().startswith(PREFIXES)}
    env.update(PROTOTYPE_EXECUTION_PROFILE='interactive-v1',
               PROTOTYPE_USERDATA_ROOT=str(user), PROTOTYPE_PROBE_VISIBLE='1',
               PROTOTYPE_PROBE_SECONDS='0', PROTOTYPE_DEV_PANEL='controller-v2',
               PROTOTYPE_DEVELOPER_SHORTCUT='1', PROTOTYPE_WINDOW_SHORTCUTS='edges-v1',
               PROTOTYPE_MODULE_CONTROL='enabled', PROTOTYPE_VU1_AOT='1',
               PS2X_FAKE_PADS='0', PS2X_SIO2_PAD_STATUS='per-port-v1',
               PS2X_AUDIO_MUTE='1', PS2X_VSYNC='0',
               **{'PS2X_PAD'+str(i): '0' for i in range(2, 9)})
    return env


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', required=True, help='Qualified private native07 executable; exact hash required')
    parser.add_argument('--elf', required=True, help='Personal June-2006 prototype ELF, read only')
    parser.add_argument('--disc', required=True, help='Personal June-2006 prototype disc, read only')
    parser.add_argument('--session', required=True, help='NEW private session name, never overwritten')
    parser.add_argument('--user-data', default='prototype-default', help='Persistent private preferences/cards name')
    parser.add_argument('--check-only', action='store_true', help='Verify inputs and paths without creating files or launching')
    args = parser.parse_args(argv)
    try:
        if os.name != 'nt':
            raise ValueError('This qualified executable requires Windows')
        exe = verify(args.exe, BUILD_SHA256)
        elf = verify(args.elf, ELF[1], ELF[0])
        disc = verify(args.disc, DISC[1], DISC[0])
        workspace = ROOT / '.local'
        if workspace.is_symlink() or (workspace.exists() and getattr(workspace.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('Aliased .local workspace refused')
        session = private_path(workspace, 'prototype-workbench', 'sessions', args.session)
        user = private_path(workspace, 'prototype-workbench', 'userdata', args.user_data)
        if session.exists():
            raise ValueError('Session already exists; choose a fresh name')
        controls = user / 'controls.ini'
        if controls.exists() or controls.is_symlink():
            ordinary(controls)
        env = launch_environment(os.environ, user)
        print('Qualified PRIVATE prototype build. Visible, muted; F1 controls / F2 original debug menu and mouse panel.')
        print('No deadline, automatic input, snapshots or game-memory export. Close the window to exit.')
        print('Existing controls/cards preserved; these are not verified game Save/Load or hardware tests.')
        if args.check_only:
            print('Checks pass; no output created or process launched.')
            return 0
        session.mkdir(parents=True, exist_ok=False)
        user.mkdir(parents=True, exist_ok=True)
        if not controls.exists():
            with controls.open('x', encoding='utf8', newline='\n') as stream:
                stream.write(CONTROLS)
        before = digest(controls)
        receipt = {'profile': 'interactive-v1', 'exe_sha256': BUILD_SHA256,
                   'elf_sha256': ELF[1], 'disc_sha256': DISC[1],
                   'controls_before_sha256': before, 'user_data': str(user),
                   'scope': 'Adopted private build; not ISO-only generation, retail or full menu/fidelity acceptance.'}
        receipt_path = session / 'launch.json'
        receipt_path.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
        with (session / 'runtime.log').open('xb') as log:
            process = subprocess.Popen([str(exe), str(elf), str(disc), str(session), 'sdk'],
                cwd=session, env=env, stdout=log, stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            receipt['pid'] = process.pid
            receipt_path.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
            print('Native PID:', process.pid, flush=True)
            receipt['exit'] = process.wait()  # Intentionally no timeout/kill in visible interactive mode.
        receipt['controls_after_sha256'] = digest(controls)
        receipt_path.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
        return receipt['exit']
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    # Windows redirected streams otherwise use the machine's locale (including
    # localized filesystem errors). Keep receipts/CLI readers deterministic.
    sys.stdout.reconfigure(encoding='utf8')
    sys.stderr.reconfigure(encoding='utf8')
    raise SystemExit(main())
