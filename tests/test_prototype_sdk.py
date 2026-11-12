"""Original invented ELF/word fixtures only; no real SDK maps/game code/assets."""
import copy
import hashlib
import struct
import unittest
from unittest import mock

import prototype_sdk as sdk


def pack(*values):return struct.pack('<'+'I'*len(values),*values)
def ins(op,rs=0,rt=0,imm=0):return op<<26|rs<<21|rt<<16|(imm&65535)
def jump(op,address):return op<<26|(address>>2)&0x3ffffff
def move(rd,rs):return rs<<21|rd<<11|0x25
JR=31<<21|8


def invented_elf(code=pack(0,JR,0,0),base=0x100000):
    names=b'\0.shstrtab\0.text\0'; strings=52+3*40
    text=(strings+len(names)+3)&~3
    ident=b'\x7fELF\x01\x01\x01'+b'\0'*9
    header=struct.pack('<16sHHIIIIIHHHHHH',ident,2,8,1,base,0,52,0,52,0,0,40,3,1)
    null=struct.pack('<10I',*([0]*10))
    shstr=struct.pack('<10I',1,3,0,0,strings,len(names),0,0,1,0)
    body=struct.pack('<10I',names.index(b'.text'),1,6,base,text,len(code),0,0,4,0)
    return (header+null+shstr+body+names).ljust(text,b'\0')+code


def image(start,blob):return sdk.TextImage(start,blob,hashlib.sha256(blob).hexdigest())


def pipeline_fixture(duplicate_leaf=True):
    ra,pa=0x100000,0x200000
    leaf=pack(ins(9,0,2,0x1234),JR,0,0)
    other=leaf if duplicate_leaf else pack(ins(9,0,2,0x4321),JR,0,0)
    filler=pack(ins(9,0,3,99),ins(9,0,3,98),ins(9,0,3,97),ins(9,0,3,96))
    retail=image(ra,pack(jump(3,ra+32),0,JR,0)+filler+leaf)
    prototype=image(pa,pack(jump(3,pa+64),0,JR,0)+filler+other+filler+leaf)
    symbols=[sdk.SdkSymbol(ra,'InventedCaller','invented-only',0.8),
             sdk.SdkSymbol(ra+32,'InventedLeaf','invented-only',0.8)]
    spans=[(ra,ra+16),(ra+32,ra+48)]
    initial=sdk.initial_candidates(prototype,retail,spans,symbols,{pa})
    cfg=sdk.cfg_candidates(prototype,retail,initial,{pa,pa+32,pa+64})
    return prototype,retail,initial,cfg


class SdkEnvelopeTests(unittest.TestCase):
    def test_invented_elf_text_read_only(self):
        blob=invented_elf();old=blob
        text=sdk.load_text_elf(blob,hashlib.sha256(blob).hexdigest())
        self.assertEqual((text.start,text.end,text.text),(0x100000,0x100010,pack(0,JR,0,0)))
        self.assertEqual(old,blob)

    def test_elf_identity_and_mutability_refused(self):
        blob=invented_elf();digest=hashlib.sha256(blob).hexdigest()
        for b,h in [(blob,'0'*64),(bytearray(blob),digest),(blob,'UPPER'),(b'bad',digest)]:
            with self.subTest(type=type(b),hash=h),self.assertRaises(ValueError):sdk.load_text_elf(b,h)

    def test_elf_envelope_bounds_and_format_refused(self):
        original=invented_elf()
        # Header byte fields: machine, section offset, section stride/count/name index.
        changes=[(18,'H',3),(32,'I',0xfffffffc),(46,'H',39),(48,'H',0),(50,'H',3)]
        for offset,kind,value in changes:
            b=bytearray(original);struct.pack_into('<'+kind,b,offset,value);b=bytes(b)
            with self.subTest(offset=offset),self.assertRaises(ValueError):
                sdk.load_text_elf(b,hashlib.sha256(b).hexdigest())

    def test_duplicate_or_missing_text_refused(self):
        original=invented_elf()
        for kind in ('duplicate','missing'):
            b=bytearray(original)
            if kind=='duplicate':b[52:92]=b[132:172]
            else:struct.pack_into('<I',b,132,0)
            b=bytes(b)
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                sdk.load_text_elf(b,hashlib.sha256(b).hexdigest())

    def test_invalid_text_span_and_zero_register_style_values_refused(self):
        for base,data,digest in [(1,pack(0),'0'*64),(0xfffffffc,pack(0,0),'0'*64),
                                 (0,b'', '0'*64),(0,pack(0),'bad')]:
            with self.subTest(base=base),self.assertRaises(ValueError):sdk.TextImage(base,data,digest)
        t=image(0x100000,pack(0,JR,0,0))
        for a,n in [(0x100001,4),(0x100000,3),(0x0ffffc,4),(0x100010,4),(True,4)]:
            with self.subTest(address=a,size=n),self.assertRaises(ValueError):t.span(a,n)

    def test_symbol_metadata_rejects_injection_and_nonfinite_score(self):
        for a,name,method,score in [(1,'Name','test',0),(0,'x"},','test',0),
                                    (0,'Name','line\nbreak',0),(0,'Name','test',float('nan')),
                                    (0,'Name','test',2),(True,'Name','test',0)]:
            with self.subTest(name=name,score=score),self.assertRaises(ValueError):
                sdk.SdkSymbol(a,name,method,score)


class SdkNormalizationTests(unittest.TestCase):
    def test_direct_targets_normalized_but_branches_preserved(self):
        a=pack(jump(3,0x101000),0,ins(4,8,9,2),0)
        b=pack(jump(3,0x203000),0,ins(4,8,9,2),0)
        self.assertEqual(sdk.normalize_linear(a)[0],sdk.normalize_linear(b)[0])
        c=pack(jump(3,0x203000),0,ins(4,8,9,3),0)
        self.assertNotEqual(sdk.normalize_linear(a)[0],sdk.normalize_linear(c)[0])

    def test_linear_signed_absolute_operand_and_small_constant(self):
        blob=pack(ins(15,0,8,0x11),ins(9,8,9,0xffff),JR,0)
        result,masks=sdk.normalize_linear(blob)
        self.assertEqual(set(masks),{0,1})
        self.assertEqual(struct.unpack('<4I',result)[:2],(ins(15,0,8,0),ins(9,8,9,0)))
        self.assertEqual(sdk.normalize_linear(pack(ins(15,0,8,0),ins(9,8,9,12),JR,0))[1],{})

    def test_linear_stops_at_call_and_branch(self):
        for barrier in (jump(3,0x101000),ins(4,4,5,1)):
            self.assertNotIn(0,sdk.normalize_linear(pack(ins(15,0,8,0x10),barrier,
                                                         ins(35,8,9,4),0))[1])

    def test_cfg_absolute_address_and_registers_preserved(self):
        a=pack(ins(15,0,8,0x10),ins(13,8,8,0x80),ins(35,8,9,0),JR,0)
        b=pack(ins(15,0,8,0x20),ins(13,8,8,0x90),ins(35,8,9,0),JR,0)
        an,mask=sdk.normalize_cfg(a,0x100000);bn,_=sdk.normalize_cfg(b,0x200000)
        self.assertEqual(an,bn);self.assertEqual(set(mask),{0,1,2})
        self.assertNotEqual(an,sdk.normalize_cfg(pack(ins(15,0,8,0x20),ins(13,8,8,0x90),
                                                        ins(35,8,10,0),JR,0),0x200000)[0])

    def test_cfg_constant_not_address_remains_unmasked(self):
        b=pack(ins(15,0,8,0),ins(9,8,9,5),JR,0)
        self.assertEqual(sdk.normalize_cfg(b,0x100000),(b,{}))

    def test_cfg_unknown_write_kills_address_origin(self):
        xor=8<<21|9<<16|8<<11|0x26
        b=pack(ins(15,0,8,0x10),xor,ins(35,8,10,4),JR,0)
        self.assertEqual(sdk.normalize_cfg(b,0x100000)[1],{})

    def test_cfg_ld_into_its_base_does_not_reuse_the_preload_address(self):
        b=pack(ins(15,0,8,0x10),ins(55,8,8,0),ins(35,8,9,4),JR,0)
        with mock.patch.object(sdk,'CFG_NO_RT_WRITE',sdk.NO_RT_WRITE):
            self.assertEqual(set(sdk.normalize_cfg(b,0x100000)[1]),{0,1,2})
        self.assertEqual(set(sdk.normalize_cfg(b,0x100000)[1]),{0,1})

    def test_cfg_move_propagates_origin(self):
        b=pack(ins(15,0,8,0x10),move(9,8),ins(35,9,10,4),JR,0)
        self.assertEqual(set(sdk.normalize_cfg(b,0x100000)[1]),{0,2})

    def test_cfg_call_clobber_and_preserved_register_model(self):
        for reg,expected in [(8,set()),(16,{0,3})]:
            b=pack(ins(15,0,reg,0x10),jump(3,0x101000),0,ins(35,reg,9,4),JR,0)
            with self.subTest(register=reg):self.assertEqual(set(sdk.normalize_cfg(b,0x100000)[1]),expected)

    def test_cfg_return_does_not_normalize_unreachable_address_tail(self):
        b=pack(JR,0,ins(15,0,8,0x10),ins(35,8,9,4))
        self.assertEqual(sdk.normalize_cfg(b,0x100000),(b,{}))

    def test_cfg_return_delay_slot_is_visited(self):
        b=pack(ins(15,0,8,0x10),JR,ins(35,8,9,4),0)
        self.assertEqual(set(sdk.normalize_cfg(b,0x100000)[1]),{0,2})

    def test_cfg_unconditional_branch_skips_conflicting_unreachable_write(self):
        b=pack(ins(4,4,4,2),ins(15,0,8,0x10),ins(15,0,8,0),ins(35,8,9,4),JR,0)
        self.assertEqual(set(sdk.normalize_cfg(b,0x100000)[1]),{1,3})

    def test_cfg_same_valued_join_unions_origins_but_conflicting_join_is_unknown(self):
        for high,expected in [(0x10,{2,5,7}),(0x20,set())]:
            b=pack(ins(4,4,5,4),0,ins(15,0,8,0x10),jump(2,0x10001c),0,
                   ins(15,0,8,high),0,ins(35,8,9,4),JR,0)
            with self.subTest(high=high):self.assertEqual(set(sdk.normalize_cfg(b,0x100000)[1]),expected)

    def test_cfg_loop_converges_and_zero_register_is_not_an_origin(self):
        b=pack(ins(15,0,0,0x10),ins(35,0,9,4),ins(5,4,5,0xfffd),0,JR,0)
        self.assertEqual(sdk.normalize_cfg(b,0x100000)[1],{})

    def test_cfg_input_budget_alignment_and_overflow_refused(self):
        for blob,base in [(b'',0),(bytearray(pack(0)),0),(b'123',0),
                          (pack(0)*(sdk.MAX_SPAN//4+1),0),(pack(0),1),
                          (pack(0,0),0xfffffffc)]:
            with self.subTest(base=base,length=len(blob)),self.assertRaises(ValueError):sdk.normalize_cfg(blob,base)


class SdkProducerTests(unittest.TestCase):
    def test_aligned_search_does_not_skip_match_after_unaligned_occurrence(self):
        # Historical find(next+4) sees offset1 then skips the aligned offset4.
        haystack=b'baaaaaaa';needle=b'aaaa';old=[];at=-4
        while True:
            at=haystack.find(needle,at+4)
            if at<0:break
            if at%4==0:old.append(at)
        self.assertEqual(old,[]);self.assertEqual(sdk.aligned_matches(haystack,needle),[4])

    def test_aligned_search_bounds_and_budget_are_refusals_not_truncation(self):
        for hay,needle in [(b'aaaa',b''),(b'aaa',b'a'),(b'a',b'aaaa'),(bytearray(b'aaaa'),b'aaaa')]:
            with self.subTest(hay=hay),self.assertRaises(ValueError):sdk.aligned_matches(hay,needle)
        with self.assertRaises(ValueError):sdk.aligned_matches(b'\0'*(4*(sdk.MAX_MATCHES+1)+4),b'\0'*4)

    def test_invented_full_pipeline_does_not_enable_context_only_ambiguous_leaf(self):
        p,r,initial,cfg=pipeline_fixture()
        old=copy.deepcopy(cfg);qualified=sdk.qualify_candidates(p,r,cfg)
        self.assertEqual(cfg,old)
        self.assertEqual(len(initial),2);self.assertEqual(len(cfg[1]['full_cfg_matches']),2)
        self.assertEqual(qualified['domains_after'][str(r.start+32)],[p.start+64])
        self.assertEqual([x['name'] for x in qualified['selected']],['InventedCaller'])
        self.assertEqual(len(qualified['unresolved']),2)
        self.assertEqual(len(qualified['selected'][0]['known_call_edges_checked']),1)
        self.assertEqual(sdk.binding_text(qualified),'{0x00200000u,"InventedCaller"},\n')

    def test_invented_unique_spans_and_direct_calls_select_two(self):
        p,r,_,cfg=pipeline_fixture(False);q=sdk.qualify_candidates(p,r,cfg)
        self.assertEqual(len(q['selected']),2);self.assertEqual(q['rejected'],[])
        self.assertEqual(q['unresolved'],[])

    def test_nonentry_coarse_occurrence_is_not_admitted(self):
        p,r,initial,_=pipeline_fixture()
        cfg=sdk.cfg_candidates(p,r,initial,{p.start})
        self.assertEqual(len(cfg[1]['coarse_candidates']),0)

    def test_registration_comments_are_bounded_text_slots_not_a_function_ceiling(self):
        # Invented large sparse code/table envelope, not an actual SDK/game.
        body=pack(ins(9,0,2,7),JR,0,0)
        p=image(0x200000,body+pack(0)*100001);r=image(0x100000,body)
        slots=set(range(p.start,p.start+100001*4,4))
        symbols=[sdk.SdkSymbol(r.start,'Invented','invented-only',0)]
        result=sdk.initial_candidates(p,r,[(r.start,r.end)],symbols,slots)
        self.assertEqual(result[0]['prototype_registered'],[p.start])
        for bad in ({p.end},{p.start+1}):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                sdk.initial_candidates(p,r,[(r.start,r.end)],symbols,bad)

    def test_signature_constant_difference_not_fuzzy_matched(self):
        p,r,_,_=pipeline_fixture(False)
        symbol=sdk.SdkSymbol(r.start+32,'InventedLeaf','invented-only',0.8)
        initial=sdk.initial_candidates(p,r,[(r.start+32,r.end)],[symbol],set())
        cfg=sdk.cfg_candidates(p,r,initial,{p.start+32,p.start+64})
        self.assertEqual([m['address'] for m in cfg[0]['full_cfg_matches']],[p.start+64])

    def test_overlapping_owner_and_duplicate_metadata_refused(self):
        p,r,_,_=pipeline_fixture()
        symbol=sdk.SdkSymbol(r.start,'InventedCaller','invented-only',0)
        for ranges,symbols in [([(r.start,r.end),(r.start,r.start+16)],[symbol]),
                               ([(r.start,r.end)],[symbol,symbol])]:
            with self.subTest(ranges=ranges),self.assertRaises(ValueError):
                sdk.initial_candidates(p,r,ranges,symbols,set())

    def test_mutated_actual_candidate_bytes_refused(self):
        p,r,_,cfg=pipeline_fixture(False)
        cfg[0]['full_cfg_matches'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):sdk.qualify_candidates(p,r,cfg)

    def test_forged_hash_of_wrong_but_real_span_refused(self):
        p,r,_,cfg=pipeline_fixture(False)
        fake=copy.deepcopy(cfg);m=fake[1]['full_cfg_matches'][0]
        m['address']=p.start+32;m['sha256']=hashlib.sha256(p.span(m['address'],16)).hexdigest()
        with self.assertRaises(ValueError):sdk.qualify_candidates(p,r,fake)

    def test_binding_text_rejects_duplicate_or_injected_identifier(self):
        row=dict(name='Invented',prototype_address=0x200000)
        with self.assertRaises(ValueError):sdk.binding_text(dict(selected=[row,row]))
        with self.assertRaises(ValueError):sdk.binding_text(dict(selected=[dict(name='x"},',prototype_address=0x200000)]))

    def test_binding_line_endings_are_explicit_and_platform_independent(self):
        q=dict(selected=[dict(name='Invented',prototype_address=0x200000)])
        lf='{0x00200000u,"Invented"},\n'
        self.assertEqual(sdk.binding_text(q),lf)
        self.assertEqual(sdk.binding_text(q,line_ending='crlf'),lf[:-1]+'\r\n')
        for policy in ('native','auto','\r',None):
            with self.subTest(policy=policy),self.assertRaises(ValueError):sdk.binding_text(q,line_ending=policy)


if __name__=='__main__':unittest.main()
