"""Original invented host-hook text only; no game instructions/maps/pixels."""
import hashlib
import unittest
from prototype_module_attach import attach_qualified_module

SOURCE=b'''// invented original host layout
#include "runtime/ps2_cd_image.h"
void unhook(){existingRemove();originalUnregister(ram,ctx,rt);}
void registered(){
 const char* control=std::getenv("PROTOTYPE_MODULE_CONTROL");
 (void)prototype_event::install(rt,base,ram,std::strcmp(control,"negative")==0);
}
'''


class ModuleAttachTests(unittest.TestCase):
    def attach(self,source=SOURCE,**changes):
        args=dict(expected_sha256=hashlib.sha256(source).hexdigest(),namespace='invented_room',
                  begin=0x1800000,size=257)
        args.update(changes)
        return attach_qualified_module(source,**args)

    def test_exact_parent_has_four_additions_and_preserves_old_order(self):
        out=self.attach().decode('utf-8')
        self.assertIn('#include "invented_room_pack.h"\n#include "runtime/ps2_cd_image.h"',out)
        self.assertIn('existingRemove();invented_room::remove(GPR_U32(ctx,4)&0x0fffffff);originalUnregister',out)
        self.assertIn('if(base<0x1800101u && 0x1800000u<base+h[11])invented_room::remove(0x1800000u);',out)
        self.assertIn('prototype_event::install(rt,base,ram,std::strcmp(control,"negative")==0); (void)invented_room::install',out)
        self.assertEqual(SOURCE.count(b'originalUnregister'),1)

    def test_CRLF_parent_bytes_are_not_normalized(self):
        out=self.attach(SOURCE.replace(b'\n',b'\r\n'))
        self.assertNotIn(b'\n',out.replace(b'\r\n',b''))

    def test_wrong_hash_or_mutable_parent_refuses(self):
        with self.assertRaises(ValueError):self.attach(expected_sha256='0'*64)
        with self.assertRaises(ValueError):self.attach(bytearray(SOURCE))
        with self.assertRaises(ValueError):self.attach(expected_sha256='not a digest')

    def test_missing_or_repeated_markers_refuse(self):
        for text in (SOURCE.replace(b'originalUnregister',b'other'),
                     SOURCE+b'originalUnregister(ram,ctx,rt);',
                     SOURCE.replace(b'prototype_event::install',b'other::install')):
            with self.subTest(text=text),self.assertRaises(ValueError):self.attach(text)

    def test_invalid_profile_or_cpp_injection_refuses(self):
        for args in (dict(namespace='bad::name'),dict(namespace='quote"'),dict(begin=True),
                     dict(begin=-4),dict(begin=5),dict(size=63),dict(size=True),
                     dict(begin=32*1024*1024),dict(size=16*1024*1024+1)):
            with self.subTest(args=args),self.assertRaises(ValueError):self.attach(**args)

    def test_existing_namespace_is_not_reattached(self):
        with self.assertRaises(ValueError):self.attach(self.attach())


if __name__=='__main__':unittest.main()
