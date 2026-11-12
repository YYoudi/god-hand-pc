"""Invented source and original host statements only, never game fixtures."""
import hashlib
import unittest
from source_inserts import apply_inserts


def sha(data):return hashlib.sha256(data).hexdigest()


class InsertTests(unittest.TestCase):
    def run_plan(self, source, plan, expected, ending='lf'):
        return apply_inserts(source, plan, source_sha256=sha(source),
                             output_sha256=sha(expected), line_ending=ending)

    def test_out_of_order_profile_keeps_original_lines_in_order(self):
        source=b'first();\nsecond();\n'
        plan=[{'before_line':2,'text':'finish();\n'}, {'before_line':0,'text':'begin();\n'},
              {'before_line':1,'text':'observe();\n'}]
        result=b'begin();\nfirst();\nobserve();\nsecond();\nfinish();\n'
        self.assertEqual(self.run_plan(source,plan,result),result)
        self.assertEqual(source,b'first();\nsecond();\n')

    def test_explicit_crlf_and_lf_output(self):
        plan=[{'before_line':1,'text':'observe();\n'}]
        for source in (b'a();\nb();\n',b'a();\r\nb();\r\n'):
            lf=b'a();\nobserve();\nb();\n';crlf=lf.replace(b'\n',b'\r\n')
            self.assertEqual(self.run_plan(source,plan,lf),lf)
            self.assertEqual(self.run_plan(source,plan,crlf,'crlf'),crlf)

    def test_both_exact_identities_are_required(self):
        source=b'x();\n';plan=[{'before_line':0,'text':'observe();\n'}]
        for left,right in (('0'*64,sha(b'observe();\nx();\n')), (sha(source),'0'*64)):
            with self.assertRaises(ValueError):
                apply_inserts(source,plan,source_sha256=left,output_sha256=right,line_ending='lf')
        for bad in (None,'no hash','A'*64):
            with self.assertRaises(ValueError):
                apply_inserts(source,plan,source_sha256=bad,output_sha256=sha(source),line_ending='lf')

    def test_delete_replace_or_extra_fields_are_not_accepted(self):
        for row in ({'before_line':0,'text':'o();\n','delete':1}, {'replace_line':0,'text':'o();\n'},
                    {'before_line':0},None):
            with self.assertRaises(ValueError):self.run_plan(b'x();\n',[row],b'o();\nx();\n')

    def test_duplicate_invalid_and_unbounded_positions(self):
        for plan in ([],None,[{'before_line':0,'text':'o();\n'}]*2,
                     [{'before_line':n,'text':'o();\n'} for n in range(33)],
                     [{'before_line':-1,'text':'o();\n'}],[{'before_line':2,'text':'o();\n'}],
                     [{'before_line':True,'text':'o();\n'}]):
            with self.assertRaises(ValueError):self.run_plan(b'x();\n',plan,b'o();\nx();\n')

    def test_payload_and_source_encoding_guards(self):
        for payload in ('','missing ending','bad\r\n','bad\0\n',1,'a'*65536+'\n'):
            with self.assertRaises(ValueError):self.run_plan(b'x();\n',[{'before_line':0,'text':payload}],b'x();\n')
        for source in (b'',bytearray(b'x();\n'),b'\xff',b'x\0\n',b'x\ry\n'):
            with self.assertRaises(ValueError):self.run_plan(source,[{'before_line':0,'text':'o();\n'}],b'x();\n')

    def test_invalid_line_ending_refused(self):
        with self.assertRaises(ValueError):
            self.run_plan(b'x();\n',[{'before_line':0,'text':'o();\n'}],b'o();\nx();\n','guess')

    def test_original_line_without_terminal_newline_is_not_dropped(self):
        self.assertEqual(self.run_plan(b'x();',[{'before_line':0,'text':'o();\n'}],b'o();\nx();'),b'o();\nx();')
        source='first\u2028still first\nsecond\n'.encode()
        expected='first\u2028still first\nobserve();\nsecond\n'.encode()
        self.assertEqual(self.run_plan(source,[{'before_line':1,'text':'observe();\n'}],expected),expected)


if __name__=='__main__':unittest.main()
