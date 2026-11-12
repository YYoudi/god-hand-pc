"""Invented source envelopes/catalogs, no original game bytes or instructions."""
import hashlib
import io
import struct
import unittest
from unittest.mock import patch
import module_inputs as m
from resources import Window
from test_resources import record


def invented_module():
    b=bytearray(256)
    struct.pack_into('<15I',b,0,int.from_bytes(b'SNR2','little'),96,1,80,1,140,
                     64,72,112,0,128,len(b),0,160,160)
    b[64:80]=b'Invented data!!\0'
    struct.pack_into('<IIHBB',b,80,180,64,7,0,0)
    struct.pack_into('<IIi',b,96,64,2,0)
    b[140:152]=b'example.elf\0';b[180:185]=b'name\0'
    return bytes(b)


def invented_disc():
    module=invented_module();other=b'NOT A MODULE!!!\0'
    archive=b'AFS\0'+struct.pack('<I',2)+struct.pack('<IIII',64,len(module),320,len(other))+bytes(40)+module+other
    pool=b'demo\0unit.ReL\0other.dat\0'
    rows=[(1,0,24),(3,0,0),(2,5,0),(2,14,1),(3,0,0)]
    fst=b'FST\0\0\0\x80\x3f'+struct.pack('<II',16,16+len(pool))+pool+b''.join(struct.pack('<III',*r) for r in rows)
    d=bytearray(24*2048);pvd=bytearray(2048);pvd[:7]=b'\x01CD001\x01'
    struct.pack_into('<H',pvd,128,2048);struct.pack_into('>H',pvd,130,2048)
    rr=record(b'\0',20,2048,2);pvd[156:156+len(rr)]=rr;d[16*2048:17*2048]=pvd
    directory=record(b'\0',20,2048,2)+record(b'\1',20,2048,2)
    directory+=record(b'GODHAND.FST;1',21,len(fst))+record(b'_DATA.AFS;1',22,len(archive))
    d[20*2048:20*2048+len(directory)]=directory;d[21*2048:21*2048+len(fst)]=fst;d[22*2048:22*2048+len(archive)]=archive
    return bytes(d)


class ModuleInputTests(unittest.TestCase):
    def test_immutable_envelope_metadata_and_source_hash_only(self):
        raw=invented_module();r=m.inspect_module_bytes(raw)
        self.assertEqual(r,m.ModuleMetadata(256,hashlib.sha256(raw).hexdigest(),1,1,0,128))
        self.assertEqual(raw,invented_module())

    def test_signature_declared_size_and_unsupported_input_refuse(self):
        bad=[]
        for offset,value in ((0,0),(0,int.from_bytes(b'SNR1','little')),(44,255)):
            b=bytearray(invented_module());struct.pack_into('<I',b,offset,value);bad.append(bytes(b))
        bad += [b'',b'\0'*59,bytearray(invented_module())]
        for b in bad:
            with self.subTest(size=len(b)),self.assertRaises(ValueError):m.inspect_module_bytes(b)

    def test_alignment_is_not_a_guessed_load_address(self):
        for a in (0,3,8192,0xffffffff):
            b=bytearray(invented_module());struct.pack_into('<I',b,40,a)
            with self.subTest(alignment=a),self.assertRaises(ValueError):m.inspect_module_bytes(bytes(b))
        b=bytearray(invented_module());struct.pack_into('<I',b,40,1)
        self.assertEqual(m.inspect_module_bytes(bytes(b)).load_alignment,1)

    def test_table_ranges_counts_and_alignment_refuse(self):
        for offset,value in ((4,20),(4,255),(4,98),(8,65537),(12,256),(16,65537),(32,260),(36,37)):
            b=bytearray(invented_module());struct.pack_into('<I',b,offset,value)
            with self.subTest(offset=offset,value=value),self.assertRaises(ValueError):m.inspect_module_bytes(bytes(b))

    def test_full_invented_catalog_filters_non_REL_without_reading_payload(self):
        class Count(io.BytesIO):
            def __init__(self,b):super().__init__(b);self.reads=[]
            def read(self,n=-1):self.reads.append((self.tell(),n));return super().read(n)
        raw=invented_disc();stream=Count(raw);result=m.module_inputs(Window(stream))
        self.assertEqual(len(result),1);r=result[0]
        self.assertEqual((r.path,r.afs_ordinal,r.offset,r.metadata.bytes),('demo/unit.ReL',0,22*2048+64,256))
        self.assertEqual(r.metadata.sha256,hashlib.sha256(invented_module()).hexdigest())
        other=22*2048+320
        self.assertTrue(all(at+n<=other or at>=other+16 for at,n in stream.reads))
        self.assertEqual(raw,invented_disc())

    def test_missing_catalog_or_aliasing_FST_AFS_refuses(self):
        with patch.object(m,'iso_root',return_value={}):
            with self.assertRaises(ValueError):m.module_inputs(None)
        for files in ({'one.rel':0,'other.dat':0},{'one.rel':1},{'one.rel':2,'other.dat':0}):
            with patch.object(m,'fst_files',return_value=files),self.subTest(files=files):
                with self.assertRaises(ValueError):m.module_inputs(Window(io.BytesIO(invented_disc())))

    def test_truncated_or_non_SNR_REL_refuses_without_repair(self):
        raw=bytearray(invented_disc());raw[22*2048+64:22*2048+68]=b'NOPE'
        with self.assertRaises(ValueError):m.module_inputs(Window(io.BytesIO(raw)))
        with patch.object(m,'afs_entries',return_value=[Window(io.BytesIO(b'SNR2')),Window(io.BytesIO(b'other'))]):
            with self.assertRaises(ValueError):m.module_inputs(Window(io.BytesIO(invented_disc())))

    def test_zero_length_tables_may_have_zero_or_end_offset(self):
        b=bytearray(invented_module());struct.pack_into('<IIII',b,4,0,0,256,0)
        r=m.inspect_module_bytes(bytes(b));self.assertEqual((r.symbol_records,r.relocation_records),(0,0))
        b=bytearray(invented_module());struct.pack_into('<I',b,36,1)
        self.assertEqual(m.inspect_module_bytes(bytes(b)).export_records,1)


if __name__=='__main__':unittest.main()
