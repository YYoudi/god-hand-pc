"""Original invented-data tests; no game or upstream source fixture."""
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import scheduler_retirement_candidate as candidate


class SchedulerCandidateTests(unittest.TestCase):
    def test_unique_edits(self):
        self.assertEqual(candidate.apply_unique_edits('alpha beta', [('alpha', 'delta')]), 'delta beta')

    def test_ambiguous_refused(self):
        with self.assertRaises(ValueError):
            candidate.apply_unique_edits('alpha alpha', [('alpha', 'delta')])

    def test_missing_refused(self):
        with self.assertRaises(ValueError):
            candidate.apply_unique_edits('beta', [('alpha', 'delta')])

    def test_no_change_refused(self):
        with self.assertRaises(ValueError):
            candidate.apply_unique_edits('alpha', [('alpha', 'alpha')])

    def test_empty_context_refused(self):
        with self.assertRaises(ValueError):
            candidate.apply_unique_edits('alpha', [('', 'delta')])

    def test_unknown_source_refused(self):
        with self.assertRaises(ValueError):
            candidate.render_candidate(b'invented source, not an upstream fixture')

    def test_candidate_fingerprint_checked(self):
        import hashlib
        data = b'alpha\r\n'
        with mock.patch.object(candidate, 'SOURCE_SHA256', hashlib.sha256(data).hexdigest()), \
             mock.patch.object(candidate, 'EDITS', [('alpha', 'beta')]):
            with self.assertRaisesRegex(ValueError, 'fingerprint'):
                candidate.render_candidate(data)

    def test_candidate_bytes_platform_independent(self):
        import hashlib
        data = b'alpha\r\n'
        expected = b'beta\r\n'
        with mock.patch.object(candidate, 'SOURCE_SHA256', hashlib.sha256(data).hexdigest()), \
             mock.patch.object(candidate, 'CANDIDATE_SHA256', hashlib.sha256(expected).hexdigest()), \
             mock.patch.object(candidate, 'EDITS', [('alpha', 'beta')]):
            self.assertEqual(candidate.render_candidate(data), expected)

    def test_private_output_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                candidate.write_new_candidate(root/'public.cpp', b'invented', root)
            self.assertFalse((root/'public.cpp').exists())

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); private = root/'.local'; private.mkdir()
            target = private/'candidate.cpp'; target.write_bytes(b'original')
            with self.assertRaises(FileExistsError):
                candidate.write_new_candidate(target, b'new', root)
            self.assertEqual(target.read_bytes(), b'original')

    def test_private_new_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); private = root/'.local'; private.mkdir()
            target = private/'candidate.cpp'
            candidate.write_new_candidate(target, b'invented', root)
            self.assertEqual(target.read_bytes(), b'invented')

    def test_explicit_directory_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                candidate.write_new_candidate(root/'.local/new/candidate.cpp', b'invented', root)
            self.assertFalse((root/'.local').exists())

    def test_wrong_suffix_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'.local').mkdir()
            with self.assertRaises(ValueError):
                candidate.write_new_candidate(root/'.local/candidate.txt', b'invented', root)


if __name__ == '__main__':
    unittest.main()
