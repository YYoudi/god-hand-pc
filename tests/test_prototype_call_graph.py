"""Invented symbols/candidate IDs only; not MIPS/SDK/runtime fixtures."""
import unittest
from prototype_call_graph import refine_domains


class PrototypeCallGraphTests(unittest.TestCase):
    def test_singleton_caller_reduces_known_target_without_changing_input(self):
        domains={'caller':{1},'callee':{10,11},'unrelated':{20,21}}
        out=refine_domains(domains,{('caller',1):[('callee',11)]})
        self.assertEqual(out,{'caller':frozenset({1}),'callee':frozenset({11}),'unrelated':frozenset({20,21})})
        self.assertEqual(domains['callee'],{10,11})

    def test_known_target_rejects_wrong_ambiguous_callers(self):
        out=refine_domains({'caller':{1,2,3},'callee':{10}},
            {('caller',1):[('callee',10)],('caller',2):[('callee',11)],('caller',3):[('callee',12)]})
        self.assertEqual(out['caller'],{1})

    def test_two_survivors_do_not_become_a_guessed_match(self):
        out=refine_domains({'caller':{1,2},'callee':{10,11}},
            {('caller',1):[('callee',10)],('caller',2):[('callee',11)]})
        self.assertEqual(out['caller'],{1,2}); self.assertEqual(out['callee'],{10,11})

    def test_cycle_propagates_and_conflicting_callers_refuse(self):
        out=refine_domains({'a':{1},'b':{2,3}},
            {('a',1):[('b',2)],('b',2):[('a',1)],('b',3):[('a',9)]})
        self.assertEqual(out,{'a':frozenset({1}),'b':frozenset({2})})
        with self.assertRaises(ValueError):
            refine_domains({'a':{1},'b':{2},'c':{3,4}},
                {('a',1):[('c',3)],('b',2):[('c',4)]})

    def test_empty_domains_bad_callers_and_unknown_targets_refuse(self):
        for domains,calls in [({},{}),({'a':set()},{}),
                             ({'a':{1}},{('missing',1):[]}),
                             ({'a':{1}},{('a',2):[]}),
                             ({'a':{1}},{('a',1):[('unknown',2)]})]:
            with self.assertRaises(ValueError):refine_domains(domains,calls)


if __name__=='__main__':unittest.main()
