"""Original invented preferences only; no upstream configuration/game fixtures."""
from pathlib import Path
import hashlib
import os
import tempfile
import unittest
import launch_packs
import user_data


class UserDataTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix='godhand-original-preferences-')
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.user = self.root/'userdata'; self.user.mkdir()
        self.binary = self.root/'runtime'; self.binary.mkdir()
        self.executable = self.binary/'invented-executable.txt'
        self.source = self.binary/'controls.ini'
        self.target = self.user/'controls.ini'
        self.data = b'# Invented preference file\r\n[Pad1]\r\nSquare = Keyboard/P\r\nUnknownFutureKey=keep\r\n'

    def test_byte_preserving_adoption_never_changes_source(self):
        self.source.write_bytes(self.data)
        record = user_data.prepare_controls(self.user,self.executable)
        self.assertEqual(record['operation'],'adopt-existing-byte-copy')
        self.assertEqual(self.target.read_bytes(),self.data)
        self.assertEqual(self.source.read_bytes(),self.data)
        self.assertEqual(record['source']['sha256'],hashlib.sha256(self.data).hexdigest())

    def test_existing_preferences_never_replaced_by_legacy(self):
        self.source.write_bytes(b'invented legacy preference')
        self.target.write_bytes(self.data)
        self.assertEqual(user_data.prepare_controls(self.user,self.executable)['operation'],'reuse')
        self.assertEqual(self.target.read_bytes(),self.data)

    def test_fresh_data_never_adopts_owner_preferences(self):
        self.source.write_bytes(self.data)
        result = user_data.prepare_controls(self.user,self.executable,fresh=True)
        self.assertEqual(result['operation'],'native-defaults')
        self.assertFalse(self.target.exists())
        self.assertEqual(self.source.read_bytes(),self.data)

    def test_missing_legacy_leaves_default_creation_to_native(self):
        result = user_data.prepare_controls(self.user,self.executable)
        self.assertFalse(result['before']['exists'])
        self.assertFalse(self.target.exists())

    def test_oversized_source_and_destination_refused(self):
        for path in [self.source,self.target]:
            with self.subTest(path=path):
                path.write_bytes(b'x'*(user_data.LIMIT+1))
                with self.assertRaises(ValueError):
                    user_data.prepare_controls(self.user,self.executable)
                path.unlink()

    def test_directory_destination_refused(self):
        self.target.mkdir()
        with self.assertRaises(ValueError): user_data.prepare_controls(self.user,self.executable)

    def test_hardlinked_destination_refused_without_changing_owner(self):
        self.source.write_bytes(self.data)
        try: os.link(self.source,self.target)
        except OSError as error: self.skipTest(str(error))
        with self.assertRaises(ValueError): user_data.prepare_controls(self.user,self.executable)
        self.assertEqual(self.source.read_bytes(),self.data)

    def test_symlink_destination_refused(self):
        self.source.write_bytes(self.data)
        try: self.target.symlink_to(self.source)
        except OSError as error: self.skipTest(str(error))
        with self.assertRaises(ValueError): user_data.prepare_controls(self.user,self.executable)
        self.assertEqual(self.source.read_bytes(),self.data)

    def test_unknown_binary_encoding_is_preserved_not_repaired(self):
        self.source.write_bytes(b'\xff\xfeInvented malformed preferences')
        user_data.prepare_controls(self.user,self.executable)
        self.assertEqual(self.source.read_bytes(),self.target.read_bytes())

    def test_snapshot_records_change_without_including_preferences(self):
        self.target.write_bytes(self.data)
        before=user_data.snapshot(self.target)
        self.target.write_bytes(self.data+b'# invented edit')
        self.assertNotEqual(before['sha256'],user_data.snapshot(self.target)['sha256'])
        self.assertNotIn('contents',before)

    def test_default_interactive_command_explicitly_disables_ini_timeout(self):
        command=launch_packs.runtime_command('invented.exe','invented.iso',False,None)
        self.assertEqual(command[-2:],['--time-limit','0'])
        self.assertIn('--window',command)

    def test_bounded_command_retains_hidden_deadline(self):
        command=launch_packs.runtime_command('invented.exe','invented.iso',True,37)
        self.assertEqual(command[-2:],['--time-limit','37'])
        self.assertIn('--headless',command)


if __name__=='__main__': unittest.main()
