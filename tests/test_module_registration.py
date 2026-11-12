"""Invented sparse metadata and original host rendering, no game fixtures."""
import unittest
from dataclasses import replace
from module_registration import parse_generated_table, render_registration, RegistrationTable


TABLE = '''extern const uint32_t g_ps2RecompiledFunctionTableBase = 0x1040u;
extern const uint32_t g_ps2RecompiledFunctionTableEnd = 0x1050u;
extern const uint32_t g_ps2RecompiledFunctionTableSlotCount = 4u;
PS2Runtime::RecompiledFunction g_ps2RecompiledFunctionTable[4u] = {};
        g_ps2RecompiledFunctionTable[0] = invented_first; // 0x1040
        g_ps2RecompiledFunctionTable[3] = invented_second; // 0x104c
'''
NAMES = {'invented_first', 'invented_second'}


class RegistrationTests(unittest.TestCase):
    def render(self, table=None, **changes):
        args=dict(table=table or parse_generated_table(TABLE,NAMES),linked=b'A'*256,
                  base=0x1000,code_begin=0x1040,code_end=0x1050,
                  namespace='invented',log_name='Example',registration_api='module')
        args.update(changes)
        return dict(render_registration(**args))

    def test_sparse_order_and_holes_are_preserved(self):
        t=parse_generated_table(TABLE,NAMES)
        self.assertEqual(t,RegistrationTable(0x1040,0x1050,4,((0x1040,'invented_first'),(0x104c,'invented_second'))))
        self.assertEqual(len(t.entries),2)

    def test_duplicate_or_missing_header_and_slot_extent_refuse(self):
        for text in (TABLE.replace('0x1050u','0x1054u'),TABLE.replace('4u;','0u;'),
                     TABLE+TABLE.splitlines()[0]+'\n',TABLE.replace('Base =','Wrong ='),
                     TABLE.replace('[4u]','[5u]'),TABLE.replace('0x1040u','0x1041u'),
                     TABLE.replace('0x1050u','0x2000004u')):
            with self.subTest(text=text),self.assertRaises(ValueError):parse_generated_table(text,NAMES)

    def test_wrong_slot_pc_unknown_name_or_duplicate_assignment_refuses(self):
        for text in (TABLE.replace('// 0x104c','// 0x1048'),TABLE.replace('[3]','[4]'),
                     TABLE.replace('invented_second;', 'unknown;'),TABLE+TABLE.splitlines()[-1]+'\n'):
            with self.subTest(text=text),self.assertRaises(ValueError):parse_generated_table(text,NAMES)

    def test_unsupported_expression_is_not_silently_dropped(self):
        for expression in ('&invented_second','nullptr','[]{}','invented_second + 1'):
            with self.subTest(expression=expression),self.assertRaises(ValueError):
                parse_generated_table(TABLE.replace('= invented_second;','= '+expression+';'),NAMES)
        for line in ('  g_ps2RecompiledFunctionTable [2] = invented_first;',
                     'other(); g_ps2RecompiledFunctionTable[2] = invented_first;'):
            with self.subTest(line=line),self.assertRaises(ValueError):
                parse_generated_table(TABLE+line+'\n',NAMES)

    def test_empty_aliases_invalid_names_and_mutable_input_refuse(self):
        for text,names in ((TABLE,set()),(TABLE,{'bad::name'}),(TABLE,'invented_first'),(TABLE.encode(),NAMES),
                           ('\n'.join(TABLE.splitlines()[:4]),NAMES),(TABLE+'\0',NAMES)):
            with self.subTest(names=names),self.assertRaises(ValueError):parse_generated_table(text,names)

    def test_render_has_guard_hash_exact_range_and_no_hole_filling(self):
        r=self.render();s=r['invented_pack.cpp']
        self.assertIn('if(base!=0x1000u)return false;',s)
        self.assertIn('ram+0x1040u,0x10u',s)
        self.assertIn('clearModuleFunctions(0x1000u,0x1100u)',s)
        self.assertEqual(s.count('u,&invented_'),2)
        self.assertNotIn('{0x1044u,',s)
        self.assertIn('if(!ps2x::setModuleFunction(e.address,e.fn))return false;',s)
        self.assertIn('namespace invented',r['invented_pack.h'])

    def test_registration_api_choice_is_explicit_and_not_collapsed(self):
        a=self.render(registration_api='runtime')['invented_pack.cpp']
        b=self.render()['invented_pack.cpp']
        self.assertEqual(a.replace('runtime->registerFunction','ps2x::setModuleFunction'),b)
        with self.assertRaises(ValueError):self.render(registration_api='guess')

    def test_bad_module_extent_pointer_names_or_source_injection_refuse(self):
        for changes in (dict(base=True),dict(base=0x1001),dict(base=32*1024*1024),
                        dict(code_end=0x1040),dict(code_begin=0x1044),dict(code_end=0x1200),
                        dict(namespace='bad::name'),dict(namespace='name\"'),dict(log_name='bad\\ntext'),
                        dict(linked=bytearray(256))):
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.render(**changes)

    def test_direct_table_construction_is_not_a_trust_token(self):
        t=parse_generated_table(TABLE,NAMES)
        for changes in (dict(slots=3),dict(entries=()),dict(end='wrong'),dict(entries=[(0x1040,'name')]),dict(entries=((0x1041,'name'),)),
                        dict(entries=((0x1040,'name'),(0x1040,'other'))),
                        dict(entries=((0x1050,'outside'),)),dict(entries=((0x1040,'bad::name'),))):
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.render(replace(t,**changes))


if __name__=='__main__':unittest.main()
