"""Invented text/hashes only; no native host or game fixture."""
import hashlib
import unittest
from command_reader_source import apply

def sha(b):return hashlib.sha256(b).hexdigest()
class CommandReaderSourceTests(unittest.TestCase):
    def recipe(self):return {'input_sha256':sha(b'own old text'),'output_sha256':sha(b'own new text'),'edits':[{'old':'old','new':'new'}]}
    def test_original_edit(self):self.assertEqual(apply(b'own old text',self.recipe()),b'own new text')
    def test_drift_refused(self):
        with self.assertRaises(ValueError):apply(b'different',self.recipe())
    def test_ambiguous_refused(self):
        r=self.recipe();r['input_sha256']=sha(b'old old')
        with self.assertRaises(ValueError):apply(b'old old',r)
    def test_bad_postimage_refused(self):
        r=self.recipe();r['output_sha256']='0'*64
        with self.assertRaises(ValueError):apply(b'own old text',r)
    def test_empty_edit_refused(self):
        r=self.recipe();r['edits'][0]['old']=''
        with self.assertRaises(ValueError):apply(b'own old text',r)
