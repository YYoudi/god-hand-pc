"""Original GPL-3.0-only private host-profile production CLI.

Reads the original prototype disc/ELF plus exact previously qualified native
registration observations. It does not discover fresh bases or execute the game.
No populated address/parameter map is a producer input. Role selection knowledge
is disclosed in the public hash-only policy; no clean-room/ABI claim is made.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys

from module_inputs import module_inputs
from prototype_entries import elf_sections
from prototype_host_profile import View, derive_parameters
from prototype_host_sources import (TOKEN, canonical, input_templates, parameter,
                                    plan_sources, recipe, token_names)
from prototype_sdk import require
from prototype_sdk_inputs import digest, ordinary_bytes, qualified_bytes
from resources import Window, afs_entries, iso_root

ROOT = Path(__file__).resolve().parent
MODULES = {'mcport', 'r020', 'r100', 'event', 'r101'}


def public_policy(root):
    blob = ordinary_bytes(Path(root)/'adapter/prototype_host_profile.json', 128*1024)
    spec = json.loads(blob)
    require(set(spec) == {'schema', 'version', 'original_elf_sha256', 'original_disc_sha256',
                         'scope', 'observations', 'selectors'} and spec['schema'] == 1 and
            spec['version'] == 'prototype-host-profile-v1' and
            set(spec['observations']) == MODULES and
            set(spec['selectors']) == set(recipe(root)['parameters']), 'Unsupported profile policy/scope')
    return spec, digest(blob)


def observed_modules(spec, paths, raw_modules):
    """Replay pinned ORIGINAL capture metadata, not a fresh runtime observation.

    Identity, complete captured header and original disc size are checked. Prior
    code/static-link comparison supplies the retained qualification; this stage
    does not redo relocations or certify arbitrary mutable data/loader lifetimes.
    """
    require(type(paths) is dict and set(paths) == set(spec) == set(raw_modules),
            'Exact qualified observation/module set required')
    result, provenance = {}, {}
    for name in sorted(spec):
        row, path = spec[name], paths[name]
        require(type(row) is dict and set(row) == {'disc_source_sha256', 'metadata_sha256', 'capture_sha256'} and
                type(path) is dict and set(path) == {'metadata', 'capture'}, 'Unsupported observation descriptor')
        raw = raw_modules[name]
        require(digest(raw) == row['disc_source_sha256'], 'Original module identity differs')
        metadata = qualified_bytes(path['metadata'], row['metadata_sha256'])
        capture = qualified_bytes(path['capture'], row['capture_sha256'])
        data = json.loads(metadata)
        require(type(data) is dict and set(data) == {'base', 'size', 'ra', 'name_pointer', 'header'},
                'Original registration metadata schema differs')
        base, size = data['base'], data['size']
        require(type(base) is int and type(size) is int and base % 4 == 0 and
                0 <= base < base+size <= 32*1024*1024 and size == len(raw) == len(capture) and
                len(capture) >= 60, 'Observed module bounds/size differ')
        header = list(struct.unpack_from('<15I', capture))
        require(data['header'] == header and header[0] == int.from_bytes(b'SNR2', 'little') and
                header[11] == size, 'Complete captured registration header differs')
        result[name] = (base, size)
        provenance[name] = dict(metadata_sha256=digest(metadata), capture_sha256=digest(capture),
                                original_module_sha256=digest(raw), historical_observation=True)
    return result, provenance


def describe_outputs(root, source, parameters):
    """Compute complete expected postimages from the qualified producer values.

    This is not an independent output oracle. A separate new-output manifest and
    actual tested-host comparison are needed to establish the stated replay.
    Portable include-root changes need their own build/native acceptance.
    """
    spec = recipe(root)
    templates, provenance = input_templates(root, source, spec)
    outputs = {}
    require(set(parameters) == set(spec['parameters']), 'Profile/template parameter sets differ')
    for key, kind in spec['parameters'].items():
        parameter(parameters[key], kind)
    for name, blob in templates.items():
        names = token_names(blob)
        rendered = TOKEN.sub(lambda m: parameters[m[1]], canonical(blob))
        ending = 'lf' if name == 'main.cpp' else 'crlf'
        if ending == 'crlf':
            rendered = rendered.replace('\n', '\r\n')
        outputs[name] = dict(sha256=digest(rendered.encode('utf-8')), line_ending=ending)
    return outputs, provenance


def produce(root, source, spec, elf, disc, observations, adapter_root, module_root):
    text, _ = elf_sections(elf, spec['original_elf_sha256'])
    catalog = iso_root(disc)
    require('SLPM_665.50' in catalog and
            catalog['SLPM_665.50'].read(0, catalog['SLPM_665.50'].size) == elf, 'Original disc BOOT/ELF differ')
    archive = afs_entries(catalog['_DATA.AFS'])
    descriptors = {Path(m.path).stem: m for m in module_inputs(disc)}
    require(MODULES <= set(descriptors), 'Original module scope missing')
    raw = {name: archive[descriptors[name].afs_ordinal].read(0, descriptors[name].metadata.bytes)
           for name in MODULES}
    modules, observed = observed_modules(spec['observations'], observations, raw)
    views = {'boot': View(text.start, text.text)}
    views.update({name: View(modules[name][0], blob) for name, blob in raw.items()})
    parameters, fields = derive_parameters(spec['selectors'], views, modules,
                                           dict(adapter=adapter_root, modules=module_root))
    for key, row in spec['selectors'].items():
        if row['kind'] == 'include':
            ordinary_bytes(parameters[key])
    outputs, source_provenance = describe_outputs(root, source, parameters)
    profile = dict(schema=1, qualification=(
        'Public hash-only selectors replay previously qualified prototype roles from original inputs; '
        'five pinned historical native registrations supply bases, not fresh-base/ABI/lifetime discovery.'),
        parameters=parameters, outputs=outputs)
    planned, _ = plan_sources(root, source, profile)
    require(set(planned) == set(outputs), 'Host source coverage differs')
    return profile, dict(observations=observed, field_sources=fields, host_sources=source_provenance)


def private_session(name):
    require(type(name) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,63}', name), 'Fresh private session name required')
    p = ROOT
    for part in ('.local', 'prototype-host-profile', 'sessions', name):
        p = p/part
        if p.exists() or p.is_symlink():
            info = p.lstat()
            require(stat.S_ISDIR(info.st_mode) and not p.is_symlink() and
                    not getattr(info, 'st_file_attributes', 0)&1024, 'Aliased output ancestor refused')
    require(not p.exists(), 'Session exists; preserve it')
    require(subprocess.run(['git', 'check-ignore', '--quiet', '--', str(p)], cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0,
            'Output must already be Git-ignored')
    return p


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'elf', 'disc', 'observations', 'adapter-root', 'module-root', 'session'):
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args(argv)
    try:
        output = private_session(args.session)
        spec, policy_hash = public_policy(ROOT)
        elf = qualified_bytes(args.elf, spec['original_elf_sha256'])
        observations = json.loads(ordinary_bytes(args.observations, 64*1024))
        disc = Path(args.disc); info = disc.lstat()
        require(stat.S_ISREG(info.st_mode) and not disc.is_symlink() and
                not getattr(info, 'st_file_attributes', 0)&1024 and
                2048 <= info.st_size <= 8*1024**3, 'Ordinary bounded original disc required')
        with disc.open('rb') as stream:
            require(hashlib.file_digest(stream, 'sha256').hexdigest() == spec['original_disc_sha256'],
                    'Original prototype disc identity differs')
            profile, provenance = produce(ROOT, args.source, spec, elf, Window(stream), observations,
                                          args.adapter_root, args.module_root)
            stream.seek(0)
            require(hashlib.file_digest(stream, 'sha256').hexdigest() == spec['original_disc_sha256'],
                    'Original disc changed during production')
        profile_blob = (json.dumps(profile, indent=2)+'\n').encode('utf-8')
        receipt = dict(schema=1, policy_sha256=policy_hash, profile_sha256=digest(profile_blob),
                       parameters=len(profile['parameters']), provenance=provenance, native_run=False,
                       limits='Previously qualified roles and historical bases replayed; not fresh native/ABI/installer acceptance.')
        if not args.check_only:
            output.mkdir(parents=True, exist_ok=False)
            with (output/'host-profile-private.json').open('xb') as f:
                f.write(profile_blob)
            with (output/'derivation-private.json').open('x', encoding='utf-8', newline='\n') as f:
                json.dump(receipt, f, indent=2); f.write('\n')
        print(json.dumps(dict(check_only=args.check_only, parameters=receipt['parameters'],
                              historical_observations=len(provenance['observations']), native_run=False)))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('Prototype host profile refused: '+str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
