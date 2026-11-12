"""Invented pointer sets and ranges only; never original game data."""
import unittest
from prototype_table_candidates import missing_table_entries


class PrototypeTableCandidateTests(unittest.TestCase):
    def test_overlapping_subarrays_use_union_not_each_others_skipped_fences(self):
        groups=[[0x120,0x140,0x160],[0x140,0x160],[0x130,0x150]]
        r=missing_table_entries([(0x100,0x180)],groups)
        self.assertEqual([(x.start,x.end) for x in r],
                         [(0x120,0x130),(0x130,0x140),(0x140,0x150),(0x150,0x160),(0x160,0x180)])
        self.assertEqual(r[2].sets,(0,1))

    def test_existing_entries_aliases_and_repeated_groups_do_not_duplicate_roots(self):
        r=missing_table_entries([(0x100,0x180)],[[0x100,0x120,0x120],[0x100,0x120]])
        self.assertEqual(len(r),1);self.assertEqual((r[0].start,r[0].end,r[0].sets),(0x120,0x180,(0,1)))

    def test_no_candidate_crosses_owner_or_unmapped_gap(self):
        r=missing_table_entries([(0x200,0x240),(0x100,0x180)],[[0x140,0x220]])
        self.assertEqual([(x.start,x.end,x.owner_start,x.owner_end) for x in r],
                         [(0x140,0x180,0x100,0x180),(0x220,0x240,0x200,0x240)])

    def test_inputs_not_mutated_and_pointer_order_not_boundary_order(self):
        ranges=[[0x100,0x180]];groups=[[0x160,0x120,0x140]]
        r=missing_table_entries(ranges,groups)
        self.assertEqual([(x.start,x.end) for x in r],[(0x120,0x140),(0x140,0x160),(0x160,0x180)])
        self.assertEqual(ranges,[[0x100,0x180]]);self.assertEqual(groups,[[0x160,0x120,0x140]])

    def test_only_existing_entries_give_no_new_candidate(self):
        self.assertEqual(missing_table_entries([(0x100,0x140),(0x140,0x180)],[[0x100,0x140]]),())

    def test_malformed_owners_and_unmapped_unaligned_or_boolean_values_refuse(self):
        for ranges,groups in (([],[[0x120]]), ([(0x100,0x180),(0x140,0x200)],[[0x120]]),
                              ([(0x100,0x100)],[[0x100]]), ([(0x100,0x182)],[[0x120]]),
                              ([(0x100,0x180)],[[0x180]]), ([(0x100,0x180)],[[0x122]]),
                              ([(0x100,0x180)],[[False]]), ([(0x100,0x180)],[[0x100000000]])):
            with self.subTest(ranges=ranges,groups=groups),self.assertRaises(ValueError):
                missing_table_entries(ranges,groups)

    def test_empty_oversized_groups_and_duplicate_owners_refuse(self):
        for ranges,groups in (([(0x100,0x180)],[]), ([(0x100,0x180)],[[]]),
                              ([(0x100,0x180)],[[0x120]*4097]),
                              ([(0x100,0x180),(0x100,0x180)],[[0x120]])):
            with self.subTest(shape=(len(ranges),len(groups))),self.assertRaises(ValueError):
                missing_table_entries(ranges,groups)

    def test_last_elf32_half_open_range(self):
        r=missing_table_entries([(0xfffffff0,0x100000000)],[[0xfffffff0,0xfffffffc]])
        self.assertEqual((r[0].start,r[0].end),(0xfffffffc,0x100000000))


if __name__=='__main__':unittest.main()
