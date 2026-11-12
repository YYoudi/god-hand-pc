"""Original invented sources/profiles only, no upstream or game fixtures."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import prototype_host_sources as host


def sha(blob):
    return host.digest(blob)


def render(blob, values, kinds, expected, ending='lf'):
    return host.render_template(blob, values, kinds, output_sha256=sha(expected), line_ending=ending)


@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix='host-original-') as tmp:
        root = Path(tmp)
        subprocess.run(['git', 'init', '--quiet', str(root)], check=True, capture_output=True)
        (root / '.gitignore').write_text('.local/\n', encoding='utf-8')
        dep = root / 'dependency'
        spec = dict(schema=1, version='prototype-host-source-v1', upstream_revision=host.REVISION,
                    parameters={'NUMBER': 'u32', 'HEADER': 'include'}, templates=[], overrides=[])
        profile = dict(schema=1, qualification='Invented source identity only; never a game qualification',
                       parameters=dict(NUMBER='0x12u', HEADER='G:/Invented Only/header.hpp'), outputs={})
        blobs = {}
        for path, out in host.TEMPLATES.items():
            blob = b'// invented original host only\nunsigned value = @@NUMBER@@;\n#include "@@HEADER@@"\n'
            p = root / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(blob)
            spec['templates'].append(dict(path=path, output=out, sha256=sha(blob)))
            expected = blob.replace(b'@@NUMBER@@', b'0x12u').replace(b'@@HEADER@@', profile['parameters']['HEADER'].encode())
            profile['outputs'][out] = dict(sha256=sha(expected), line_ending='lf')
        for path, out in host.OVERRIDES.items():
            blob = b'// invented dependency, not vendor source\n'
            p = dep / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(blob)
            blobs[path] = blob
            after = b'// invented addition\n' + blob
            spec['overrides'].append(dict(path=path, output=out, before_sha256=sha(blob),
                after_sha256=sha(after), edits=[dict(start=0, end=0, insert='// invented addition\n')]))
            profile['outputs'][out] = dict(sha256=sha(after.replace(b'\n', b'\r\n')), line_ending='crlf')
        recipe = root / 'adapter/prototype_host_integration.json'
        recipe.write_text(json.dumps(spec), encoding='utf-8')
        p = root / 'profile-private.json'
        p.write_text(json.dumps(profile), encoding='utf-8')
        args = ['--source', str(dep), '--profile', str(p), '--profile-sha256', sha(p.read_bytes()),
                '--session', 'invented-new']
        original = subprocess.check_output

        def git(command, **kwargs):
            if command[:2] == ['git', 'rev-parse']:
                return host.REVISION + '\n'
            if command[:2] == ['git', 'show']:
                return blobs[command[-1].split(':', 1)[1]]
            return original(command, **kwargs)

        with mock.patch.object(host, 'ROOT', root), mock.patch.object(host.subprocess, 'check_output', side_effect=git):
            yield root, dep, recipe, spec, profile, args


def call(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = host.main(args)
    return code, out.getvalue(), err.getvalue()


class TypedRendererTests(unittest.TestCase):
    def test_repeated_literal_and_path_without_expression_evaluation(self):
        blob = b'@@WORD@@ + @@WORD@@\n#include "@@PATH@@"\n'
        result = b'0x12u + 0x12u\n#include "G:/Invented/header.hpp"\n'
        self.assertEqual(render(blob, {'WORD': '0x12u', 'PATH': 'G:/Invented/header.hpp'},
                                {'WORD': 'u32', 'PATH': 'include'}, result), result)

    def test_empty_parameters_are_supported_for_unchanged_plain_sources(self):
        self.assertEqual(render(b'invented();\n', {}, {}, b'invented();\n'), b'invented();\n')

    def test_numeric_boundaries_and_lexical_spelling_preserved(self):
        for value in ('0x0', '0x00000000u', '0xffffffffU', '0xABCDEF12'):
            self.assertEqual(render(b'@@N@@', {'N': value}, {'N': 'u32'}, value.encode()), value.encode())

    def test_numeric_expression_sign_suffix_and_overflow_refuse(self):
        for value in ('-1', '42', '0x100000000', '0x1ull', '0x1 + 0x2', '0x1; execute();', '0x1\n', True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render(b'@@N@@', {'N': value}, {'N': 'u32'}, b'unused')

    def test_include_directive_injection_and_parent_components_refuse(self):
        for value in ('', '../secret', 'G:/a/../b', 'header"\n#error', 'a\\b', '<header>',
                      'a;statement', '@@WORD@@', 'a\0b', 'é.hpp', 'a' * 513):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render(b'@@P@@', {'P': value}, {'P': 'include'}, b'unused')

    def test_missing_extra_and_wrong_typed_parameter_sets_refuse(self):
        for values, kinds in (({}, {}), ({'N': '0x1', 'EXTRA': '0x2'}, {'N': 'u32'}),
                              ({'N': '0x1'}, {'N': 'arbitrary-cpp'}), ([], {})):
            with self.subTest(values=values), self.assertRaises(ValueError):
                render(b'@@N@@', values, kinds, b'unused')

    def test_canonical_template_and_well_formed_tokens_required(self):
        for blob in (b'', b'\xff', b'a\0', b'a\r\n', b'@@', b'@@lower@@', b'@@A-B@@', bytearray(b'plain')):
            with self.subTest(blob=blob), self.assertRaises(ValueError):
                render(blob, {}, {}, b'unused')

    def test_output_eol_is_explicit_and_hash_covers_complete_source(self):
        for ending, expected in (('lf', b'0x1\n'), ('crlf', b'0x1\r\n')):
            self.assertEqual(render(b'@@N@@\n', {'N': '0x1'}, {'N': 'u32'}, expected, ending), expected)
        for ending, expected in (('guess', b'0x1\n'), ('lf', b'different'), ('crlf', b'0x1\n')):
            with self.subTest(ending=ending), self.assertRaises(ValueError):
                render(b'@@N@@\n', {'N': '0x1'}, {'N': 'u32'}, expected, ending)


class HostPlanTests(unittest.TestCase):
    def test_public_templates_pin_lf_on_windows_checkouts(self):
        root = Path(__file__).resolve().parents[1]
        spec = host.recipe(root)
        for row in spec['templates']:
            blob = (root / row['path']).read_bytes()
            self.assertEqual(sha(blob), row['sha256'])
            host.token_names(blob)
            result = subprocess.check_output(['git', 'check-attr', 'eol', '--', row['path']],
                                             cwd=root, text=True).strip()
            self.assertEqual(result, row['path'] + ': eol: lf')

    def test_all_five_planned_sources_leave_inputs_unchanged(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            outputs, provenance = host.plan_sources(root, dep, profile)
            self.assertEqual(set(outputs), host.OUTPUTS)
            self.assertEqual(provenance['parameters'], 2)
            for name, blob in outputs.items():
                self.assertEqual(sha(blob), profile['outputs'][name]['sha256'])
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            self.assertFalse((root / '.local').exists())

    def test_pinned_revision_and_changed_checked_out_dependency_refuse(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            with mock.patch.object(host.subprocess, 'check_output', return_value='0' * 40 + '\n'):
                with self.assertRaises(ValueError):
                    host.plan_sources(root, dep, profile)
            (dep / next(iter(host.OVERRIDES))).write_bytes(b'changed dependency\n')
            with self.assertRaises(ValueError):
                host.plan_sources(root, dep, profile)

    def test_only_explicit_git_lf_to_checkout_crlf_is_allowed(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            for path in host.OVERRIDES:
                p = dep / path
                p.write_bytes(p.read_bytes().replace(b'\n', b'\r\n'))
            outputs, provenance = host.plan_sources(root, dep, profile)
            self.assertEqual(len(outputs), 5)
            for path in host.OVERRIDES:
                self.assertEqual(provenance['inputs'][path]['checkout_policy'], 'git-lf-to-checkout-crlf')

    def test_edited_template_or_transformation_postimage_refuses(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            path = root / next(iter(host.TEMPLATES))
            path.write_bytes(path.read_bytes() + b'changed\n')
            with self.assertRaises(ValueError):
                host.plan_sources(root, dep, profile)
        with fixture() as (root, dep, recipe, spec, profile, args):
            spec['overrides'][0]['edits'][0]['insert'] = 'wrong original addition\n'
            recipe.write_text(json.dumps(spec), encoding='utf-8')
            with self.assertRaises(ValueError):
                host.plan_sources(root, dep, profile)

    def test_recipe_paths_version_and_schema_do_not_expand_allowlist(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            for mutator in (lambda s: s.update(schema=2), lambda s: s.update(version='retail'),
                            lambda s: s['templates'][0].update(path='../outside'),
                            lambda s: s['overrides'][0].update(output='../outside'),
                            lambda s: s['parameters'].update(NUMBER='cpp')):
                changed = copy.deepcopy(spec)
                mutator(changed)
                recipe.write_text(json.dumps(changed), encoding='utf-8')
                with self.assertRaises(ValueError):
                    host.plan_sources(root, dep, profile)

    def test_profile_missing_extra_or_untyped_fields_refuse(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            for mutator in (lambda p: p.update(schema=2), lambda p: p.update(qualification=''),
                            lambda p: p['parameters'].pop('NUMBER'), lambda p: p['outputs'].pop('main.cpp'),
                            lambda p: p['parameters'].update(ARBITRARY='0x1'),
                            lambda p: p['outputs']['main.cpp'].update(line_ending='guess'),
                            lambda p: p['outputs']['main.cpp'].update(sha256='unqualified')):
                changed = copy.deepcopy(profile)
                mutator(changed)
                with self.assertRaises(ValueError):
                    host.plan_sources(root, dep, changed)

    def test_wrong_parameter_and_wrong_complete_output_hash_refuse(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            profile['parameters']['NUMBER'] = '0x13u'
            with self.assertRaises(ValueError):
                host.plan_sources(root, dep, profile)
            profile['parameters']['NUMBER'] = '0x12u'
            profile['outputs']['main.cpp']['sha256'] = '0' * 64
            with self.assertRaises(ValueError):
                host.plan_sources(root, dep, profile)

    def test_declared_but_unused_parameter_refuses(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            spec['parameters']['UNUSED'] = 'u32'
            profile['parameters']['UNUSED'] = '0x1'
            recipe.write_text(json.dumps(spec), encoding='utf-8')
            with self.assertRaises(ValueError):
                host.plan_sources(root, dep, profile)


class HostCLITests(unittest.TestCase):
    def test_real_invented_cli_writes_only_five_fresh_private_sources_and_receipt(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            code, out, err = call(args)
            self.assertEqual(code, 0, err)
            self.assertEqual(json.loads(out)['source_files'], 5)
            dest = root / '.local/prototype-host/sessions/invented-new'
            names = {p.relative_to(dest).as_posix() for p in dest.rglob('*') if p.is_file()}
            self.assertEqual(names, host.OUTPUTS | {'source-receipt-private.json'})
            for name in host.OUTPUTS:
                self.assertEqual(sha((dest / name).read_bytes()), profile['outputs'][name]['sha256'])

    def test_check_only_and_identity_refusal_write_nothing(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            self.assertEqual(call(args + ['--check-only'])[0], 0)
            wrong = args[:]
            wrong[wrong.index('--profile-sha256') + 1] = '0' * 64
            self.assertEqual(call(wrong)[0], 2)
            self.assertFalse((root / '.local').exists())

    def test_stale_output_preserved_and_traversal_session_refused(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            self.assertEqual(call(args)[0], 0)
            before = {p: p.read_bytes() for p in (root / '.local').rglob('*') if p.is_file()}
            self.assertEqual(call(args)[0], 2)
            for name in ('../outside', 'Upper', 'a/b', '.', 'a' * 65):
                wrong = args[:]
                wrong[-1] = name
                self.assertEqual(call(wrong)[0], 2)
            self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_nonignored_output_and_nondirectory_ancestor_refused(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            (root / '.gitignore').write_text('', encoding='utf-8')
            self.assertEqual(call(args)[0], 2)
            self.assertFalse((root / '.local').exists())
            (root / '.gitignore').write_text('.local/\n', encoding='utf-8')
            (root / '.local').write_text('preserved nondirectory', encoding='utf-8')
            self.assertEqual(call(args)[0], 2)
            self.assertEqual((root / '.local').read_text(), 'preserved nondirectory')

    def test_invalid_final_source_refuses_before_partial_output(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            (dep / list(host.OVERRIDES)[-1]).write_bytes(b'changed final source\n')
            self.assertEqual(call(args)[0], 2)
            self.assertFalse((root / '.local').exists())

    def test_symlink_ancestor_refused_when_available(self):
        with fixture() as (root, dep, recipe, spec, profile, args):
            target = root / 'separate-preserved'
            target.mkdir()
            try:
                (root / '.local').symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest('Symlinks unavailable on this host')
            self.assertEqual(call(args)[0], 2)
            self.assertEqual(list(target.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
