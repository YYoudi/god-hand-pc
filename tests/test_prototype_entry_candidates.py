"""Invented ranges/imports only, no game bytes, symbols, maps or decoder."""
import unittest
from prototype_entry_candidates import DirectImportUse as Use, missing_import_entries


class PrototypeEntryCandidateTests(unittest.TestCase):
    def test_explicit_scope_missing_only_and_all_exports_fence(self):
        ranges = [(0x800, 0x840), (0x100, 0x180)]
        exports = [0x800, 0x818, 0x838, 0x100, 0x130, 0x160]
        uses = [Use('first', 4, 0x100), Use('first', 8, 0x130),
                Use('first', 12, 0x818), Use('later', 4, 0x160)]
        before = (list(ranges), list(exports), list(uses))
        result = missing_import_entries(ranges, exports, uses, ['first'])
        self.assertEqual([(c.start,c.end,c.owner_start,c.owner_end) for c in result],
                         [(0x130,0x160,0x100,0x180),(0x818,0x838,0x800,0x840)])
        self.assertEqual(result[0].uses, (Use('first',8,0x130),))
        self.assertEqual((ranges,exports,uses), before)

    def test_final_entry_ends_at_owner_not_next_unrelated_export(self):
        r = missing_import_entries([(0x100,0x180),(0x200,0x240)],
                                   [0x140,0x200], [Use('a',4,0x140)], ['a'])
        self.assertEqual((r[0].start,r[0].end),(0x140,0x180))

    def test_permutation_preserves_results_and_collects_exact_scoped_uses(self):
        uses = [Use('b',8,0x140),Use('a',12,0x140),Use('a',4,0x140)]
        a = missing_import_entries([(0x100,0x180)], [0x140], uses, ['a','b'])
        b = missing_import_entries([(0x100,0x180)], [0x140], reversed(uses), ['b','a'])
        self.assertEqual(a,b)
        self.assertEqual(a[0].uses, (uses[2],uses[1],uses[0]))

    def test_existing_root_and_empty_exports_do_not_invent_entries(self):
        self.assertEqual(missing_import_entries([(0x100,0x180)], [0x100],
                                               [Use('a',0,0x100)], ['a']), ())
        with self.assertRaisesRegex(ValueError,'Unknown selected module'):
            missing_import_entries([(0x100,0x180)], [], [], ['a'])

    def test_malformed_and_overlapping_ranges_refuse(self):
        for ranges in ([],[(0x100,0x100)],[(0x100,0x183)],[(False,0x180)],
                       [(0x100,0x180),(0x100,0x180)],[(0x100,0x180),(0x140,0x200)],
                       [(0x100,0x100000004)],[(0x100,0x180,0x200)]):
            with self.subTest(ranges=ranges), self.assertRaises(ValueError):
                missing_import_entries(ranges, [], [], ['a'])

    def test_export_holes_duplicates_bool_and_unregistered_offsets_refuse(self):
        for exports in ([0x140,0x140],[0x180],[0x80],[0x142],[True],[0x100000000]):
            with self.subTest(exports=exports), self.assertRaises(ValueError):
                missing_import_entries([(0x100,0x180)],exports,[],['a'])
        with self.assertRaisesRegex(ValueError,'unregistered'):
            missing_import_entries([(0x100,0x180)],[0x100],[Use('a',4,0x104)],['a'])

    def test_bad_scope_uses_and_duplicate_sites_refuse(self):
        for scope,uses in (('a',[Use('a',4,0x140)]),([],[Use('a',4,0x140)]),(['a','a'],[Use('a',4,0x140)]),
                           (['absent'],[Use('a',4,0x140)]),(['a'],[Use('a',2,0x140)]),
                           (['a'],[Use('a',True,0x140)]),(['a'],[('a',4,0x140)]),
                           (['a'],[Use('a',4,0x140),Use('a',4,0x140)]),
                           (['a'],[Use('a',4,0x140),Use('bad\n',8,0x140)])):
            with self.subTest(scope=scope,uses=uses), self.assertRaises(ValueError):
                missing_import_entries([(0x100,0x180)],[0x140],uses,scope)

    def test_elf32_last_span_and_touching_ranges_are_valid(self):
        r = missing_import_entries([(0xfffffff0,0xfffffff8),(0xfffffff8,0x100000000)],
                                   [0xfffffffc], [Use('a',0,0xfffffffc)], ['a'])
        self.assertEqual((r[0].start,r[0].end),(0xfffffffc,0x100000000))


if __name__ == '__main__':
    unittest.main()
