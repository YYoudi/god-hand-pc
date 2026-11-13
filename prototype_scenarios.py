"""Original GPL-3.0-only bounded scenarios for qualified PRIVATE prototypes.

Not a builder, semantic room API, retail backend or ordinary interactive launch.
Only original finite controller inputs are delivered. Exit0 is not room success.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

import prototype_workbench as workbench

ROOT = Path(__file__).resolve().parent
BUILDS = ('scheduler-control-v1', 'scheduler-candidate-v1', 'source-v1')
SCENARIOS = ('prototype-scheduler-room-cycle-v1',)
BUTTONS = ('start', 'cross', 'circle', 'up', 'down', 'left', 'right', 'l2', 'r3')


def validate(plan):
    if (type(plan) is not dict or set(plan) != {'schema', 'profile', 'name',
            'builds', 'seconds', 'developer_probe_field', 'pad_script', 'fields',
            'expected_route', 'limits'} or type(plan['schema']) is not int or plan['schema'] != 1 or
            plan['profile'] != 'prototype-june-2006' or plan['name'] not in SCENARIOS or
            plan['builds'] != list(BUILDS)):
        raise ValueError('Unqualified scenario schema/profile/builds')
    if type(plan['seconds']) is not int or not 10 <= plan['seconds'] <= 600:
        raise ValueError('Scenario budget must be 10..600 seconds')
    field = plan['developer_probe_field']
    if type(field) is not int or not 1 <= field <= 42000:
        raise ValueError('Invalid developer probe field')
    fields = plan['fields']
    if (type(fields) is not list or not 1 <= len(fields) <= 100 or
            any(type(x) is not int or not 1 <= x <= 42000 for x in fields) or
            fields != sorted(set(fields))):
        raise ValueError('Capture fields must be ordered, unique and bounded')
    if type(plan['pad_script']) is not str or len(plan['pad_script']) > 4096:
        raise ValueError('Invalid finite input script')
    prior = 0
    steps = plan['pad_script'].split(',')
    if not 1 <= len(steps) <= 64:
        raise ValueError('Invalid finite input count')
    for step in steps:
        match = re.fullmatch(r'([0-9]{1,5})v:([a-z0-9]+):([0-9]{1,3})', step)
        if not match:
            raise ValueError('Expected bounded original vblank input')
        tick, button, duration = int(match[1]), match[2], int(match[3])
        if not prior < tick <= 42000 or button not in BUTTONS or not 1 <= duration <= 120:
            raise ValueError('Unqualified input order/button/duration')
        prior = tick
    if any(type(plan[k]) is not str or not 1 <= len(plan[k]) <= 1000
           for k in ('expected_route', 'limits')):
        raise ValueError('Explicit bounded route/limits required')
    return plan


def environment(parent, case, plan):
    env = {k: v for k, v in parent.items()
           if not k.upper().startswith(workbench.PREFIXES)}
    env.update(TEMP=str(case / 'tmp'), TMP=str(case / 'tmp'),
        PROTOTYPE_EXECUTION_PROFILE='diagnostic-v1', PROTOTYPE_PROBE_VISIBLE='0',
        PROTOTYPE_PROBE_SECONDS=str(plan['seconds']), PROTOTYPE_MODULE_CONTROL='enabled',
        PROTOTYPE_VU1_AOT='1', PROTOTYPE_DEVELOPER_SHORTCUT='1',
        PROTOTYPE_WINDOW_SHORTCUTS='edges-v1', PROTOTYPE_DEV_PANEL='controller-v2',
        PROTOTYPE_DEVELOPER_PROBE_FIELD=str(plan['developer_probe_field']),
        PS2X_SIO2_PAD_STATUS='per-port-v1', PS2X_FAKE_PADS='0', PS2X_AUDIO_MUTE='1',
        PS2X_PAD_SCRIPT=plan['pad_script'], PS2X_SCREENSHOT_DIR=str(case / 'frames'),
        PS2X_SCREENSHOT_FIELDS=','.join(map(str, plan['fields'])),
        PS2X_FRAME_TIMES=str(case / 'presents.csv'), PS2X_FRAME_HASH='0',
        PS2X_SIF_DMA_LOG='0', **{'PS2X_PAD' + str(i): '0' for i in range(2, 9)})
    return env


def require_idle():
    # Read-only inventory, no process termination or localized tasklist parsing.
    query = ("@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match "
             "'^(prototype-native|godhand|gdb|cl|link|cmake|ninja|pcsx2-qt|gs_replay|probe)\\.exe$'} "
             "| Select-Object Name,ProcessId) | ConvertTo-Json -Compress")
    raw = subprocess.check_output(['powershell', '-NoProfile', '-Command', query], text=True)
    if json.loads(raw.strip() or '[]'):
        raise ValueError('An owned native/build/debug process is live; finish that handle first')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=SCENARIOS, required=True)
    parser.add_argument('--build', choices=BUILDS, required=True)
    for arg in ('exe', 'elf', 'disc', 'session'):
        parser.add_argument('--' + arg, required=True)
    parser.add_argument('--controls-seed', type=Path,
                        help='Optional read-only ordinary controls file, cloned into fresh scratch data')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args(argv)
    try:
        if os.name != 'nt':
            raise ValueError('Qualified native scenarios require Windows')
        source = ROOT / 'scenarios' / (args.scenario + '.json')
        workbench.ordinary(source)
        plan = validate(json.loads(source.read_text(encoding='utf8')))
        build = workbench.build_profile(args.build)
        exe = workbench.verify(args.exe, build['sha256'])
        elf = workbench.verify(args.elf, workbench.ELF[1], workbench.ELF[0])
        disc = workbench.verify(args.disc, workbench.DISC[1], workbench.DISC[0])
        case = workbench.private_path(ROOT / '.local', 'prototype-scenarios', args.session)
        if case.exists():
            raise ValueError('Scenario session already exists; preserve it and choose a NEW name')
        seed = args.controls_seed
        if seed:
            if not 0 < workbench.ordinary(seed).st_size <= 100000:
                raise ValueError('Controls seed must be bounded')
            controls = seed.read_bytes()
        else:
            controls = workbench.CONTROLS.encode('utf8')
        if b'\0' in controls:
            raise ValueError('Binary/NUL controls seed refused')
        controls.decode('utf8')
        if args.check_only:
            print('Scenario input/identity checks pass; no files or native process created.')
            return 0
        require_idle()
        if shutil.disk_usage(ROOT).free < 4 * 1024**3:
            raise ValueError('Scenario requires at least4GiB free; no files created')
        inputs = {str(p): workbench.digest(p) for p in
                  [exe, elf, disc, source, ROOT / 'prototype_scenarios.py',
                   ROOT / 'prototype_workbench.py'] + ([seed] if seed else [])}
        case.mkdir(parents=True, exist_ok=False)
        for name in ('tmp', 'frames', 'userdata'):
            (case / name).mkdir()
        local_controls = case / 'userdata/controls.ini'
        local_controls.write_bytes(controls)
        env = environment(os.environ, case, plan)
        command = [str(exe), str(elf), str(disc), str(case), 'sdk']
        now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
        record = {'started_at': now(), 'build': args.build, 'scenario': plan,
            'command': command, 'inputs_before': inputs,
            'controls_before_sha256': workbench.digest(local_controls),
            'environment': {k: v for k, v in env.items() if k.startswith(workbench.PREFIXES)
                            or k in ('TEMP', 'TMP')},
            'scope': 'Explicit hidden diagnostic, original finite input only. No success inferred from exit0, '
                     'request ACKs or PNG existence; inspect actual scenes/module lifecycle. Not ordinary '
                     'interactive mode, retail, physical input, source generation or default adoption.'}
        receipt = case / 'receipt.json'
        def save():
            receipt.write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')
        save()
        start = time.monotonic()
        with (case / 'runtime.log').open('xb') as log:
            process = subprocess.Popen(command, cwd=case, env=env, stdout=log, stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            record['pid'] = process.pid
            save()
            print('Scenario native PID:', process.pid, 'Receipt:', receipt, flush=True)
            while True:
                try:
                    record['native_exit'] = process.wait(timeout=120)
                    break
                except subprocess.TimeoutExpired:
                    record.setdefault('observation_expiries', []).append(now())
                    save()
                    print('Same native handle still live; no restart/kill:', process.pid, flush=True)
        record.update(ended_at=now(), seconds=time.monotonic() - start,
            inputs_after={p: workbench.digest(Path(p)) for p in inputs},
            controls_after_sha256=workbench.digest(local_controls),
            captures=[{'name': p.name, 'sha256': workbench.digest(p), 'bytes': p.stat().st_size,
                'export_filemtime': datetime.datetime.fromtimestamp(p.stat().st_mtime,
                    datetime.timezone.utc).isoformat()} for p in sorted((case / 'frames').glob('*.png'))])
        save()
        if record['inputs_before'] != record['inputs_after']:
            raise ValueError('Original input bytes changed; preserve receipt and investigate')
        print('Native exit:', record['native_exit'], 'Original PNGs:', len(record['captures']),
              '(not a scene-success verdict)', flush=True)
        return 0 if record['native_exit'] == 0 else 1
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf8')
    sys.stderr.reconfigure(encoding='utf8')
    raise SystemExit(main())
