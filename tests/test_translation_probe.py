"""Original source generation/policy tests; no external tool or game inputs."""
from pathlib import Path
import tempfile
import unittest
import translation_probe as p
import translation_fixtures as f


class NativeProbeTests(unittest.TestCase):
    def test_one_translation_unit_per_compile_and_private_objects(self):
        directory=Path('/invented-owned-scratch')
        units=[directory/'one.cpp',directory/'two.cpp']
        plan=p.compile_plan('invented-cl',directory,[],units,directory/'synthetic.exe')
        self.assertEqual(len(plan),3)
        for _,command,timeout in plan[:-1]:
            self.assertIn('/c',command)
            self.assertNotIn('/MP',command)
            self.assertEqual(len([a for a in command if str(a).endswith('.cpp')]),1)
            self.assertTrue(next(str(a)[3:] for a in command if str(a).startswith('/Fo')).startswith(str(directory)))
            self.assertEqual(timeout,600)
        self.assertFalse(any(str(a).endswith('.cpp') for a in plan[-1][1]))

    def test_inherited_compiler_and_game_switches_cannot_change_controls(self):
        env=p.merge_native_environment({'PATH':'kept','CL':'/unsafe','_CL_':'/unsafe',
                                        'GODHAND_ISO':'private','ps2x_test':'unsafe'},
                                       'INCLUDE=invented\nCL=/unsafe\nPS2X_OLD=1\n=drive=internal\n')
        self.assertEqual(env,{'PATH':'kept','INCLUDE':'invented'})

    def test_harness_uses_four_invented_input_outcomes(self):
        with tempfile.TemporaryDirectory(prefix='godhand-invented-harness-') as folder:
            assert Path(folder).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
            suite=f.write_suite(Path(folder)/'suite')
            symbols={c['name']:'Invented_'+c['name'].replace('-','_') for c in suite['cases']}
            text=p.native_harness(suite['cases'],symbols)
            self.assertEqual(text.count('{"'),4)
            self.assertIn('std::runtime_error',text)
            self.assertIn('nullptr',text)
            self.assertNotIn('God Hand',text)

    def test_unexpected_function_identifier_refused(self):
        case={'name':'invented','entry':1,'fault':2,'expected':[]}
        with self.assertRaises(ValueError): p.native_harness([case],{'invented':'bad(); injected'})

    def test_environment_batch_requires_existing_toolchain(self):
        with tempfile.TemporaryDirectory(prefix='godhand-invented-env-') as folder:
            root=Path(folder);path=root/'VC/Auxiliary/Build/vcvars64.bat'
            with self.assertRaises(ValueError):p.environment_batch(root)
            path.parent.mkdir(parents=True);path.write_text('rem invented fixture\n')
            text=p.environment_batch(root)
            self.assertIn('call "',text)
            self.assertIn('if errorlevel 1',text)

    def test_environment_path_command_characters_refused(self):
        for suffix in ['bad"path','bad%path','bad!path','bad\npath','bad&path']:
            with self.subTest(suffix=suffix),self.assertRaises(ValueError):p.environment_batch(Path.cwd()/suffix)


if __name__=='__main__':unittest.main()
