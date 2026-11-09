"""Original invented Windows command-output bytes, no process/game fixtures."""
import subprocess
import unittest

import setup_pc as build


class ProcessInventoryTests(unittest.TestCase):
    def test_localized_bytes_are_not_decoded_and_csv_request_is_explicit(self):
        calls = []
        def query(*args, **kwargs):
            calls.append((args, kwargs))
            return b"Invented localized idle information: \xff\x82\xa0\r\n"
        build.require_no_game(query)
        self.assertEqual(calls[0][0][0],
                         ["tasklist", "/FI", "IMAGENAME eq godhand.exe", "/FO", "CSV", "/NH"])
        self.assertEqual(calls[0][1], {})

    def test_ascii_image_guard_survives_undecodable_memory_columns(self):
        for raw in (b'"godhand.exe","42","Invented","0","123\xff456 K"\r\n',
                    b'"GODHAND.EXE","99","Invented","0","10 K"\r\n'):
            with self.assertRaisesRegex(ValueError, "running game"):
                build.require_no_game(lambda command: raw)

    def test_unknown_output_and_inventory_command_failure_refuse_safely(self):
        for raw in ("Wrong text interface", b'\xff\xfe"\0g\0o\0d\0', None):
            with self.assertRaisesRegex(ValueError, "encoding"):
                build.require_no_game(lambda command: raw)
        def failed(command): raise subprocess.CalledProcessError(1, command)
        with self.assertRaises(subprocess.CalledProcessError): build.require_no_game(failed)


if __name__ == "__main__": unittest.main()
