"""Original invented module/section/word fixtures; no game data or maps."""
import copy
import hashlib
import struct
import unittest

import prototype_entries as e
from prototype_sdk import TextImage
from test_prototype_sdk import JR,ins,jump,pack,invented_elf


def module_bytes(word=None,addend=0,symbol_type=1):
    raw=bytearray(128);h=[0]*15
    h[0]=int.from_bytes(b'SNR2','little');h[1:5]=[64,1,80,1];h[10]=16;h[11]=len(raw)
    struct.pack_into('<15I',raw,0,*h)
    struct.pack_into('<IIi',raw,64,112,4,addend)
    struct.pack_into('<IIHBB',raw,80,96,0,7,symbol_type,0)
    raw[96:105]=b'Invented\0';struct.pack_into('<I',raw,112,jump(3,0x100038) if word is None else word)
    return bytes(raw)


def local_fixture(program=None,values=None,data_kind=1):
    # A section-byte view for the pure scanner, not a real game/ELF specimen.
    program=program if program is not None else [ins(15,0,8,0x30),ins(12,4,9,3),
        9<<16|9<<11|2<<6,8<<21|9<<16|8<<11|33,ins(35,8,25,0),25<<21|31<<11|9,0]
    code=bytearray(88);code[:4*len(program)]=pack(*program)
    for offset in (56,64,72,80):code[offset:offset+8]=pack(JR,0)
    data=pack(*(values if values is not None else [0x100040,0x100048,0x100050,0]))
    blob=bytes(code)+data;text=TextImage(0x100000,bytes(code),hashlib.sha256(blob).hexdigest())
    sections=(e.Section('.text',1,6,text.start,0,len(code)),e.Section('.data',data_kind,2,0x300000,len(code),len(data)))
    return blob,sections,text,((text.start,text.end,'invented.cpp'),)


def lookup(name,hsh):return e.ResolvedSymbol(name,0x100038,2) if (name,hsh)==('Invented',7) else None


def direct_fixture(**kwargs):
    _,_,text,units=local_fixture()
    source=e.ModuleSource('invented.rel','folder/invented.rel',0,module_bytes(**kwargs))
    return text,units,(source,)


class DirectEntryTests(unittest.TestCase):
    def test_original_jal_import_resolves_with_own_callback_and_keeps_bytes(self):
        text,units,modules=direct_fixture();before=modules[0].data;calls=[]
        def resolver(name,hsh):calls.append((name,hsh));return lookup(name,hsh)
        r=e.scan_direct_imports(text,units,modules,resolver)
        self.assertEqual(calls,[('Invented',7)]);self.assertEqual(modules[0].data,before)
        self.assertEqual(r['total_original_import_jal_uses'],1)
        self.assertEqual(r['candidates'][0]['target'],text.start+56)
        self.assertEqual(r['candidates'][0]['uses'][0]['offset'],112)

    def test_non_jal_relocation_is_rejected_not_enabled(self):
        text,units,modules=direct_fixture(word=jump(2,0x100038))
        r=e.scan_direct_imports(text,units,modules,lookup)
        self.assertEqual(r['candidates'],[]);self.assertEqual(len(r['rejected']),1)
        self.assertEqual(r['total_original_import_jal_uses'],0)

    def test_unresolved_import_remains_unresolved(self):
        text,units,modules=direct_fixture()
        r=e.scan_direct_imports(text,units,modules,lambda *_:None)
        self.assertEqual(r['unresolved_import_jal_uses'],1);self.assertEqual(r['candidates'],[])

    def test_existing_discovery_start_is_not_missing(self):
        text,units,modules=direct_fixture()
        r=e.scan_direct_imports(text,units,modules,lambda name,h:e.ResolvedSymbol(name,text.start,2))
        self.assertEqual(r['candidates'],[])

    def test_unmapped_or_unaligned_resolved_target_is_not_a_candidate(self):
        text,units,modules=direct_fixture()
        for address in (text.start-4,text.end,text.start+1):
            with self.subTest(address=address):
                r=e.scan_direct_imports(text,units,modules,lambda name,h:e.ResolvedSymbol(name,address,2))
                self.assertEqual(r['candidates'],[])

    def test_nonimport_symbol_is_not_an_import_use(self):
        text,units,modules=direct_fixture(symbol_type=2)
        r=e.scan_direct_imports(text,units,modules,lookup)
        self.assertEqual(r['total_original_import_jal_uses'],0)

    def test_malformed_symbol_name_and_relocation_bounds_refuse(self):
        text,units,modules=direct_fixture()
        for offset,value in [(80,999),(68,999<<8|4),(64,127)]:
            b=bytearray(modules[0].data);struct.pack_into('<I',b,offset,value)
            source=e.ModuleSource('invented.rel','invented.rel',0,bytes(b))
            with self.subTest(offset=offset),self.assertRaises(ValueError):e.scan_direct_imports(text,units,[source],lookup)

    def test_wrong_resolver_name_and_duplicate_modules_refuse(self):
        text,units,modules=direct_fixture()
        with self.assertRaises(ValueError):e.scan_direct_imports(text,units,modules,lambda *_:e.ResolvedSymbol('Wrong',text.start+56,2))
        with self.assertRaises(ValueError):e.scan_direct_imports(text,units,modules+modules,lookup)

    def test_nonzero_addend_needs_separate_qualification(self):
        text,units,modules=direct_fixture(addend=4)
        direct=e.scan_direct_imports(text,units,modules,lookup)
        with self.assertRaises(ValueError):e.derive_entries(text,units,direct,{'candidate_tables':[]},['invented.rel'])


class LocalTableTests(unittest.TestCase):
    def test_local_load_jalr_prefix_is_code_backed_but_not_complete_index_domain(self):
        b,s,t,u=local_fixture();before=b;r=e.scan_indirect_uses(b,s,t,u)
        self.assertEqual(b,before);self.assertEqual(r['qualified_local_uses'],1)
        table=r['candidate_tables'][0];prefix=table['tables'][0]
        self.assertEqual(table['uses'][0]['kind'],'local-jalr')
        self.assertEqual(prefix['values'],[t.start+64,t.start+72,t.start+80])
        self.assertEqual(prefix['stop'],{'index':3,'value':0})
        self.assertFalse(prefix['full_mask_domain_verified']);self.assertEqual(prefix['prefix_limit'],4)

    def test_stored_pointer_is_only_a_stored_pointer_candidate(self):
        b,s,t,u=local_fixture(program=[ins(15,0,8,0x30),ins(12,4,9,3),9<<16|9<<11|2<<6,
            8<<21|9<<16|8<<11|33,ins(35,8,25,0),ins(43,29,25,8),0])
        r=e.scan_indirect_uses(b,s,t,u)
        self.assertEqual(r['qualified_local_uses'],1)
        self.assertEqual(r['candidate_tables'][0]['uses'][0]['kind'],'local-stored-pointer')

    def test_unknown_and_ee_mult_u_destinations_kill_pointer_origins(self):
        prefix=[ins(15,0,8,0x30),ins(12,4,9,3),9<<16|9<<11|2<<6,
                8<<21|9<<16|8<<11|33,ins(35,8,25,0)]
        for barrier in (28<<26,4<<21|5<<16|25<<11|24,4<<21|5<<16|25<<11|25):
            b,s,t,u=local_fixture(program=prefix+[barrier,25<<21|31<<11|9,0])
            with self.subTest(barrier=barrier):self.assertEqual(e.scan_indirect_uses(b,s,t,u)['qualified_local_uses'],0)
        # DIV has no modeled GPR destination; it must not be conflated with MULT.
        b,s,t,u=local_fixture(program=prefix+[4<<21|5<<16|25<<11|26,25<<21|31<<11|9,0])
        self.assertEqual(e.scan_indirect_uses(b,s,t,u)['qualified_local_uses'],1)

    def test_control_delay_load_is_not_used_as_local_evidence(self):
        b,s,t,u=local_fixture(program=[ins(15,0,8,0x30),ins(12,4,9,3),9<<16|9<<11|2<<6,
            8<<21|9<<16|8<<11|33,jump(2,0x100030),ins(35,8,25,0),25<<21|31<<11|9,0])
        self.assertEqual(e.scan_indirect_uses(b,s,t,u)['qualified_local_uses'],0)

    def test_fresh_entry_and_branch_target_join_are_flow_barriers(self):
        b,s,t,u=local_fixture();split=t.start+20
        self.assertEqual(e.scan_indirect_uses(b,s,t,[(t.start,split,'a'),(split,t.end,'b')])['qualified_local_uses'],0)
        # A later branch targets the earlier JALR: global target discovery fences it.
        bb=bytearray(b);struct.pack_into('<I',bb,32,ins(4,4,5,-4));bb=bytes(bb)
        tt=TextImage(t.start,bb[:len(t.text)],hashlib.sha256(bb).hexdigest())
        self.assertEqual(e.scan_indirect_uses(bb,s,tt,u)['qualified_local_uses'],0)

    def test_short_invalid_prefix_is_not_enabled(self):
        for values in ([0x100040,0x100048,0,0],[0x100040,0x100041,0,0]):
            b,s,t,u=local_fixture(values=values)
            with self.subTest(values=values):self.assertEqual(e.scan_indirect_uses(b,s,t,u)['candidate_tables'],[])

    def test_overlapping_and_nobits_sections_are_not_first_match_guesses(self):
        b,s,t,u=local_fixture()
        duplicate=e.Section('.other',1,2,s[1].address,s[1].offset,s[1].size)
        self.assertEqual(e.scan_indirect_uses(b,s+(duplicate,),t,u)['candidate_tables'],[])
        b,s,t,u=local_fixture(data_kind=8)
        self.assertEqual(e.scan_indirect_uses(b,s,t,u)['candidate_tables'],[])

    def test_constant_pointer_data_without_local_use_does_not_qualify(self):
        b,s,t,u=local_fixture(program=[0]*7)
        self.assertEqual(e.scan_indirect_uses(b,s,t,u)['candidate_tables'],[])

    def test_text_section_and_blob_identity_mismatch_refuse(self):
        b,s,t,u=local_fixture()
        with self.assertRaises(ValueError):e.scan_indirect_uses(b[:-1]+b'x',s,t,u)
        bad=(e.Section('.text',1,6,t.start+4,0,len(t.text)),s[1])
        with self.assertRaises(ValueError):e.scan_indirect_uses(b,bad,t,u)


class DerivedEntryTests(unittest.TestCase):
    def pipeline(self):
        b,s,t,u=local_fixture();_,_,modules=direct_fixture()
        direct=e.scan_direct_imports(t,u,modules,lookup);indirect=e.scan_indirect_uses(b,s,t,u)
        return b,s,t,u,direct,indirect

    def test_full_invented_pipeline_emits_generator_labels_and_exact_lf(self):
        b,s,t,u,direct,indirect=self.pipeline();old=copy.deepcopy((direct,indirect))
        result,csv=e.derive_entries(t,u,direct,indirect,['invented.rel'])
        self.assertEqual((direct,indirect),old)
        self.assertEqual(len(result['indirect']),3);self.assertEqual(len(result['direct']),1)
        self.assertTrue(csv.startswith('Name,Start,End,Size\nPrototypeDispatchEntry_00100040,'))
        self.assertIn('PrototypeExportEntry_00100038,0x100038,0x100058,32\n',csv)
        self.assertNotIn('\r',csv)

    def test_stored_table_generator_labels_are_not_recovered_symbols(self):
        _,_,t,u,direct,indirect=self.pipeline()
        indirect['candidate_tables'][0]['uses'][0]['kind']='local-stored-pointer'
        result,_=e.derive_entries(t,u,direct,indirect,['invented.rel'])
        self.assertTrue(result['indirect'][0]['Name'].startswith('PrototypeMpegTableEntry_'))

    def test_explicit_unknown_module_refuses_instead_of_using_a_fallback(self):
        _,_,t,u,direct,indirect=self.pipeline()
        with self.assertRaises(ValueError):e.derive_entries(t,u,direct,indirect,['unknown.rel'])

    def test_known_zero_candidate_module_is_not_unknown_or_a_fallback_scope(self):
        b,s,t,u,direct,indirect=self.pipeline()
        direct['modules'].append(dict(name='zero.rel'))
        together,_=e.derive_entries(t,u,direct,indirect,['invented.rel','zero.rel'])
        zero,_=e.derive_entries(t,u,direct,indirect,['zero.rel'])
        self.assertEqual(len(together['direct']),1);self.assertEqual(zero['direct'],[])
        self.assertEqual(len(zero['indirect']),3)

    def test_duplicate_direct_indirect_starts_refuse(self):
        b,s,t,u,direct,indirect=self.pipeline()
        direct['candidates'][0]['target']=t.start+64
        with self.assertRaises(ValueError):e.derive_entries(t,u,direct,indirect,['invented.rel'])

    def test_known_outgoing_branch_is_not_hidden_by_a_terminal_pair(self):
        b,s,t,u,direct,indirect=self.pipeline();raw=bytearray(t.text)
        struct.pack_into('<I',raw,64,ins(4,4,5,0x100))
        bad=TextImage(t.start,bytes(raw),hashlib.sha256(bytes(raw)).hexdigest())
        self.assertTrue(e.known_noncall_exits(bad,t.start+64,t.start+72))
        with self.assertRaises(ValueError):e.derive_entries(bad,u,direct,indirect,['invented.rel'])

    def test_terminal_pair_is_only_a_terminal_pair_not_entry_execution_proof(self):
        self.assertTrue(e.terminal_pair(pack(JR,0)))
        self.assertTrue(e.terminal_pair(pack(JR,ins(9,0,2,7),0)))
        self.assertFalse(e.terminal_pair(pack(0,0)))
        with self.assertRaises(ValueError):e.terminal_pair(b'bad')

    def test_runtime_relocation_table_order_and_type_subset_are_explicit(self):
        records=[(0x100010,6,-1),(0x100004,4,0),(0x100008,5,1),(0x100000,1,0)]
        self.assertEqual(e.relocation_text(records),'Address,kind\n0x100010,lo16\n0x100004,j26\n0x100008,hi16\n')
        with self.assertRaises(ValueError):e.relocation_text([(0x100001,4,0)])

    def test_elf_section_envelope_and_discovery_overlap_are_refused(self):
        raw=invented_elf();t,sections=e.elf_sections(raw,hashlib.sha256(raw).hexdigest())
        self.assertEqual([s.name for s in sections],['','.shstrtab','.text'])
        with self.assertRaises(ValueError):e.discovery_units(t,[(t.start,t.end,'a'),(t.start,t.end,'b')])


if __name__=='__main__':unittest.main()
