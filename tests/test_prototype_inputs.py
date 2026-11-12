"""Invented ELF metadata and invented payload only; no game fixtures."""
import struct
import unittest
from prototype_inputs import text_discovery_copy, LIMIT


def invented():
    data=bytearray(512)
    ident=b'\x7fELF\x01\x01\x01'+b'\0'*9
    struct.pack_into('<16sHHIIIIIHHHHHH',data,0,ident,2,8,1,0x4000,52,320,0,52,32,1,40,4,3)
    struct.pack_into('<8I',data,52,1,128,0x4000,0x4000,64,80,5,16)
    data[128:192]=b'Invented mapped bytes only; no real opcodes or game data.'.ljust(64,b'!')
    names=b'\0.text\0.synthetic\0.shstrtab\0';data[240:240+len(names)]=names
    struct.pack_into('<10I',data,360,1,1,6,0x4000,128,32,0,0,4,0)
    struct.pack_into('<10I',data,400,7,1,7,0x4020,160,32,0,0,4,0)
    struct.pack_into('<10I',data,440,18,3,0,0,240,len(names),0,0,1,0)
    return bytes(data)


class PrototypeInputsTests(unittest.TestCase):
    def test_only_non_text_flags_change_and_source_load_bytes_equal(self):
        original=invented();r=text_discovery_copy(original)
        self.assertEqual(r.load_segments,1)
        self.assertEqual(r.changes,((2,408,7,3),))
        self.assertEqual(r.data[128:192],original[128:192])
        self.assertEqual(len(r.data),len(original))
        self.assertEqual([i for i,(a,b) in enumerate(zip(original,r.data)) if a!=b],[408])
        self.assertEqual(struct.unpack_from('<I',original,408)[0],7)
        self.assertEqual(text_discovery_copy(r.data).changes,())

    def test_edit_inside_load_segment_refuses(self):
        data=bytearray(invented());struct.pack_into('<H',data,44,2)
        # Keep the legitimate .text mapping and add a SECOND invented load
        # covering the section flag. An earlier malformed fixture lost .text
        # mapping and was correctly refused before reaching this invariant.
        struct.pack_into('<8I',data,84,1,400,0x8000,0x8000,64,64,4,4)
        with self.assertRaisesRegex(ValueError,'overlaps PT_LOAD'):text_discovery_copy(bytes(data))

    def test_bad_header_tables_names_and_ranges_refuse(self):
        cases=[]
        for offset,fmt,value in [(18,'H',3),(5,'B',2),(20,'I',2),(40,'H',51),
                                 (42,'H',1),(44,'H',0),(46,'H',0),(48,'H',257),
                                 (50,'H',0),(32,'I',500),(28,'I',40),
                                 (68,'I',1000),(72,'I',1),(60,'I',0xfffffff0),(360,'I',1000),
                                 (364,'I',8),(368,'I',0),(376,'I',510),
                                 (380,'I',1000),(372,'I',0x9000),(444,'I',1),(456,'I',510)]:
            d=bytearray(invented());struct.pack_into('<'+fmt,d,offset,value);cases.append(bytes(d))
        cases.extend([b'',b'\0'*52,bytearray(invented()),b'\0'*(LIMIT+1)])
        for d in cases:
            with self.subTest(shape=(type(d).__name__,len(d))):
                with self.assertRaises(ValueError):text_discovery_copy(d)


if __name__=='__main__':unittest.main()
