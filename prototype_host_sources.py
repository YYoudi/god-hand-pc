"""Original GPL-3.0-only prototype host source producer, NOT a game generator.

Public inputs are original host templates and our edits against pinned GPL host
dependencies. Populated prototype parameters remain a PRIVATE qualification
dependency. Matching a prior source postimage is not ABI/native/accuracy proof.
This tool never compiles, runs, adopts a profile or edits an input checkout.
"""
import argparse
import json
from pathlib import Path
import re
import stat
import subprocess
import sys

from prototype_entry_inputs import dependency_checkout
from prototype_sdk import require
from prototype_sdk_inputs import digest, identity, ordinary_bytes, qualified_bytes
from runtime_packs import transform

ROOT = Path(__file__).resolve().parent
REVISION = '1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a'
OUTPUTS = {'main.cpp', 'window_shortcut_bridge.hpp', 'overrides/iop_sio2.h',
           'overrides/iop_sio2.cpp', 'overrides/ps2_controls_screen.cpp'}
TEMPLATES = {'adapter/prototype_host_main.cpp.in': 'main.cpp',
             'adapter/prototype_window_bridge.hpp.in': 'window_shortcut_bridge.hpp'}
OVERRIDES = {'runtime/ps2xIOP/src/emulator/devices/iop_sio2.h': 'overrides/iop_sio2.h',
             'runtime/ps2xIOP/src/emulator/devices/iop_sio2.cpp': 'overrides/iop_sio2.cpp',
             'runtime/ps2xRuntime/src/lib/ps2_controls_screen.cpp': 'overrides/ps2_controls_screen.cpp'}
TOKEN = re.compile(r'@@([A-Z][A-Z0-9_]{0,63})@@')
LIMIT = 256 * 1024


def canonical(blob):
    require(type(blob) is bytes and 0 < len(blob) <= LIMIT, 'Bounded template bytes required')
    try:
        text = blob.decode('utf-8')
    except UnicodeDecodeError as error:
        raise ValueError('UTF-8 template required') from error
    require('\r' not in text and '\0' not in text, 'Canonical LF template required')
    return text


def token_names(blob):
    text = canonical(blob)
    require('@@' not in TOKEN.sub('', text), 'Malformed template token')
    return set(TOKEN.findall(text))


def parameter(value, kind):
    require(type(value) is str, 'Literal parameter string required')
    if kind == 'u32':
        require(re.fullmatch(r'0x[0-9a-fA-F]{1,8}[uU]?', value) is not None,
                'Only one unsigned 32-bit hexadecimal literal is supported')
    elif kind == 'include':
        # Text substitution, not a C++ expression or arbitrary directive. These
        # qualified paths are not opened/executed by the template renderer.
        require(0 < len(value) <= 512 and
                re.fullmatch(r'[A-Za-z0-9_./: -]+', value) is not None and
                '..' not in value.split('/'), 'Invalid quoted include path')
    else:
        raise ValueError('Unknown parameter type')
    return value


def render_template(blob, parameters, kinds, *, output_sha256, line_ending):
    names = token_names(blob)
    require(type(parameters) is dict and type(kinds) is dict and
            names == set(parameters) == set(kinds), 'Exact typed parameter set required')
    values = {name: parameter(parameters[name], kinds[name]) for name in names}
    result = TOKEN.sub(lambda match: values[match[1]], canonical(blob))
    require(line_ending in ('lf', 'crlf'), 'Explicit output EOL required')
    if line_ending == 'crlf':
        result = result.replace('\n', '\r\n')
    result = result.encode('utf-8')
    require(len(result) <= LIMIT and digest(result) == identity(output_sha256),
            'Complete rendered source postimage differs')
    return result


def recipe(root):
    data = json.loads(ordinary_bytes(Path(root) / 'adapter/prototype_host_integration.json', LIMIT))
    require(set(data) == {'schema', 'version', 'upstream_revision', 'parameters', 'templates', 'overrides'} and
            data['schema'] == 1 and data['version'] == 'prototype-host-source-v1' and
            data['upstream_revision'] == REVISION, 'Unsupported host recipe')
    require(type(data['parameters']) is dict and 0 < len(data['parameters']) <= 256 and
            all(re.fullmatch(r'[A-Z][A-Z0-9_]{0,63}', key) and kind in ('u32', 'include')
                for key, kind in data['parameters'].items()), 'Invalid parameter schema')
    require(type(data['templates']) is list and len(data['templates']) == len(TEMPLATES) and
            {r['path']: r['output'] for r in data['templates']} == TEMPLATES,
            'Host template allowlist differs')
    require(type(data['overrides']) is list and len(data['overrides']) == len(OVERRIDES) and
            {r['path']: r['output'] for r in data['overrides']} == OVERRIDES,
            'Host dependency allowlist differs')
    return data


def input_templates(root, source, spec):
    """Read/qualify original templates and separately fetched host dependencies."""
    root, source = Path(root), Path(source)
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    require(actual == REVISION, 'Pinned host dependency revision differs')
    templates, inputs = {}, {}
    for row in spec['templates']:
        templates[row['output']] = qualified_bytes(root / row['path'], row['sha256'])
        inputs[row['path']] = dict(sha256=row['sha256'], provenance='Original GPL host template')
    for row in spec['overrides']:
        blob = ordinary_bytes(source / row['path'], LIMIT)
        git = subprocess.check_output(['git', 'show', REVISION + ':' + row['path']], cwd=source)
        policy = dependency_checkout(blob, git)
        templates[row['output']] = transform(blob, row)
        inputs[row['path']] = dict(checkout_sha256=digest(blob), git_blob_sha256=digest(git),
                                  checkout_policy=policy, provenance='Separately fetched pinned GPL host dependency')
    return templates, dict(upstream_revision=actual, inputs=inputs)


def plan_sources(root, source, private_profile):
    """Plan all five postimages before any output directory is created.

    The private profile is data, never Python/C++ executed here. It must retain
    separate evidence of disc/function/module/ABI qualification; this renderer
    does not create that evidence or assume supplied numbers are game addresses.
    """
    root, source = Path(root), Path(source)
    spec = recipe(root)
    require(type(private_profile) is dict and
            set(private_profile) == {'schema', 'qualification', 'parameters', 'outputs'} and
            private_profile['schema'] == 1 and type(private_profile['qualification']) is str and
            0 < len(private_profile['qualification']) <= 4096, 'Private qualification record required')
    values, expected = private_profile['parameters'], private_profile['outputs']
    require(type(values) is dict and set(values) == set(spec['parameters']) and
            type(expected) is dict and set(expected) == OUTPUTS, 'Private profile coverage differs')
    for key, kind in spec['parameters'].items():
        parameter(values[key], kind)
    for row in expected.values():
        require(type(row) is dict and set(row) == {'sha256', 'line_ending'} and
                row['line_ending'] in ('lf', 'crlf'), 'Explicit complete output identity/EOL required')
        identity(row['sha256'])
    templates, provenance = input_templates(root, source, spec)
    used = set().union(*(token_names(blob) for blob in templates.values()))
    require(used == set(values), 'Unused or undeclared private parameters')
    planned = {}
    for name, blob in templates.items():
        names = token_names(blob)
        planned[name] = render_template(blob, {k: values[k] for k in names},
                                        {k: spec['parameters'][k] for k in names},
                                        output_sha256=expected[name]['sha256'],
                                        line_ending=expected[name]['line_ending'])
    return planned, dict(**provenance, parameters=len(used),
                        private_qualification=private_profile['qualification'])


def private_session(name):
    require(type(name) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,63}', name),
            'Fresh session uses lowercase letters/digits/hyphens')
    p = ROOT
    for part in ('.local', 'prototype-host', 'sessions', name):
        p = p / part
        if p.exists() or p.is_symlink():
            info = p.lstat()
            require(stat.S_ISDIR(info.st_mode) and not p.is_symlink() and
                    not getattr(info, 'st_file_attributes', 0) & 1024, 'Aliased/non-directory output refused')
    require(not p.exists(), 'Session exists; preserve it and choose a fresh name')
    check = subprocess.run(['git', 'check-ignore', '--quiet', '--', str(p)], cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(check.returncode == 0, 'Output must already be Git-ignored')
    return p


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--profile-sha256', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args(argv)
    try:
        output = private_session(args.session)
        raw = qualified_bytes(args.profile, args.profile_sha256)
        planned, provenance = plan_sources(ROOT, args.source, json.loads(raw))
        receipt = dict(schema=1, source_files={k: dict(bytes=len(v), sha256=digest(v))
                                             for k, v in planned.items()},
                       profile_sha256=args.profile_sha256, provenance=provenance,
                       limits='Source production only. Private qualification inputs remain; no native build/run/adoption or ABI/fidelity proof.')
        if not args.check_only:
            output.mkdir(parents=True, exist_ok=False)
            for name, blob in planned.items():
                path = output / name
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(blob)
            with (output / 'source-receipt-private.json').open('x', encoding='utf-8', newline='\n') as stream:
                json.dump(receipt, stream, indent=2)
                stream.write('\n')
        print(json.dumps(dict(check_only=args.check_only, source_files=len(planned),
                              parameters=provenance['parameters'], native_run=False)))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('Prototype host source refused: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
