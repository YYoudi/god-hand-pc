"""Invented configuration/empty library fixtures, no game/runtime source."""
from pathlib import Path
import copy
import shutil
import subprocess
import tempfile
import unittest
import prototype_generic as g


class GenericConfigurationTests(unittest.TestCase):
    def deps(self):
        return {name: '/invented/' + name for name in g.DEPENDENCIES}

    def test_explicit_disconnected_generic_profile(self):
        source = g.cmake_project('/invented/runtime', self.deps()).decode()
        self.assertIn('add_subdirectory("/invented/runtime" runtime EXCLUDE_FROM_ALL)', source)
        self.assertIn('set(FETCHCONTENT_FULLY_DISCONNECTED ON', source)
        for name in ('FFMPEG', 'SDL_INPUT', 'AGRESSIVE_LOGS', 'SCCACHE'):
            self.assertIn(f'set(PS2X_ENABLE_{name} OFF', source)
        self.assertNotIn('generated', source)
        self.assertNotIn('.lib', source)
        self.assertNotIn('/fp:fast', source)
        self.assertNotIn('CMAKE_BUILD_TYPE', source)

    def test_five_explicit_msvc_outputs(self):
        paths = g.msvc_library_outputs(r'G:\invented\build')
        self.assertEqual(set(paths), set(g.TARGETS))
        self.assertEqual(len(set(paths.values())), 5)
        self.assertEqual(paths['raylib'], 'G:/invented/build/_deps/raylib-build/raylib/raylib.lib')
        self.assertEqual(paths['ps2_iop'], 'G:/invented/build/runtime/ps2xIOP/ps2_iop.lib')

    def test_windows_and_posix_paths_are_explicit_literals(self):
        a = g.cmake_project(r'G:\invented\runtime', self.deps())
        b = g.cmake_project('G:/invented/runtime', self.deps())
        self.assertEqual(a, b)
        self.assertNotIn(b'\r', a)
        self.assertTrue(a.endswith(b'\n'))

    def test_paths_cannot_inject_commands_or_escape_to_parents(self):
        for bad in (None, '', 1, 'relative', 'G:relative', '/a/../b', '/a"b',
                    '/a;b', '/a${inject}', '/a\nb', '/a\rb', '/a\0b'):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):g.cmake_project(bad, self.deps())
                with self.assertRaises(ValueError):g.msvc_library_outputs(bad)

    def test_exact_dependency_profile_required(self):
        for bad in (None, [], {}, {'raylib': '/a'}, {**self.deps(), 'guessed': '/b'}):
            with self.assertRaises(ValueError):g.cmake_project('/runtime', bad)
        for name in g.DEPENDENCIES:
            deps = self.deps(); deps[name] = '${other}'
            with self.assertRaises(ValueError):g.cmake_project('/runtime', deps)

    def test_literal_paths_with_spaces_do_not_change_the_profile(self):
        deps = {n: f'G:/source trees/{n}' for n in g.DEPENDENCIES}
        text = g.cmake_project('G:/source trees/runtime', deps).decode()
        self.assertIn('"G:/source trees/runtime"', text)
        self.assertIn('FETCHCONTENT_SOURCE_DIR_RLIMGUI "G:/source trees/rlimgui"', text)

    def test_input_mapping_is_not_mutated_or_order_sensitive(self):
        deps = self.deps(); before = copy.deepcopy(deps)
        result = g.cmake_project('/runtime', deps)
        self.assertEqual(deps, before)
        self.assertEqual(result, g.cmake_project('/runtime', dict(reversed(list(deps.items())))))

    def test_actual_cmake_on_invented_target_tree(self):
        cmake, ninja = shutil.which('cmake'), shutil.which('ninja')
        cc, cxx = shutil.which('gcc'), shutil.which('g++')
        if not all((cmake, ninja, cc, cxx)):
            self.skipTest('CMake/Ninja and GNU C/C++ required for invented fixture')
        with tempfile.TemporaryDirectory(prefix='gh-gen-') as directory:
            root = Path(directory); runtime = root/'invented-runtime'; runtime.mkdir()
            deps = {n: str(root/n) for n in g.DEPENDENCIES}
            for p in deps.values():Path(p).mkdir()
            (root/'CMakeLists.txt').write_bytes(g.cmake_project(str(runtime), deps))
            (runtime/'invented.cpp').write_text('int invented(){return 7;}\n', encoding='utf-8')
            body = '''
if(NOT FETCHCONTENT_FULLY_DISCONNECTED OR PS2X_ENABLE_FFMPEG OR PS2X_ENABLE_SDL_INPUT OR URBAN_BUILD_RECOMP OR URBAN_BUILD_TOOLS)
 message(FATAL_ERROR "Unexpected synthetic profile")
endif()
if(NOT CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
 message(FATAL_ERROR "Unexpected synthetic build mode")
endif()
'''
            for name in g.TARGETS:body += f'add_library({name} STATIC invented.cpp)\n'
            (runtime/'CMakeLists.txt').write_text(body, encoding='utf-8')
            commands = [[cmake, '-S', str(root), '-B', str(root/'build'), '-G', 'Ninja',
                         '-DCMAKE_C_COMPILER='+cc, '-DCMAKE_CXX_COMPILER='+cxx,
                         '-DCMAKE_MAKE_PROGRAM='+ninja, '-DCMAKE_BUILD_TYPE=RelWithDebInfo'],
                        [cmake, '--build', str(root/'build'), '--target', *g.TARGETS, '--parallel', '2']]
            for command in commands:
                result = subprocess.run(command, capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            archives = list((root/'build').rglob('*.a'))
            self.assertEqual(len(archives), 5)


if __name__ == '__main__':unittest.main()
