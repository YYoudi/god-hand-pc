"""Invented numeric records only; no game pixels/hashes/native files in CI."""
import csv
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import frame_spans as f


def record(seconds, field, **extra):
    result = dict(seconds=seconds, field=field, source_sequence=field, render_revision=0,
                  new_source=-1, interval_ms=20, submit_ms=3, swap_ms=5,
                  shared=0, hash_valid=0, image_hash=0, image_changed=-1)
    result.update(extra)
    return result


def encode(rows, header=f.HEADER):
    text = io.StringIO(); writer = csv.DictWriter(text, fieldnames=header)
    writer.writeheader(); writer.writerows(rows)
    return text.getvalue().encode()


class FrameSpanTests(unittest.TestCase):
    def test_repeats_gaps_and_actual_boundaries_are_not_game_fps(self):
        rows = f.parse(encode([record(0, 1), record(.02, 3), record(.04, 3),
                               record(.06, 5), record(.08, 9), record(.10, 11)]))
        s = f.summarize(rows, 2, 8)
        self.assertEqual(s['observed_fields'], [3,9]); self.assertEqual(s['boundary_overshoot'], [1,1])
        self.assertEqual(s['host_present_intervals'], 3); self.assertEqual(s['distinct_observed_fields'], 3)
        self.assertAlmostEqual(s['field_span_wall_seconds'], .06)
        self.assertEqual(s['submit_wall_ms_sum'], 9); self.assertEqual(s['swap_wall_ms_sum'], 15)
        self.assertIn('NOT game FPS', s['scope']); self.assertNotIn('fps', s)

    def test_shape_flags_nonfinite_bounds_and_monotonicity_refuse(self):
        base = [record(0,1),record(.02,3),record(.04,5)]
        for key,value in [('seconds','nan'),('submit_ms','inf'),('interval_ms',-1),('field',-1),
                          ('image_hash',str(2**64)),('shared',2),('image_changed',1),('new_source',1)]:
            bad = [dict(r) for r in base];bad[1][key]=value
            with self.subTest(key=key,value=value), self.assertRaises(ValueError): f.parse(encode(bad))
        for seconds,field in [(-1,3),(.01,0)]:
            bad = [dict(r) for r in base];bad[1].update(seconds=seconds,field=field)
            with self.assertRaises(ValueError): f.parse(encode(bad))
        with self.assertRaises(ValueError):
            f.parse(encode([record(.03,1),record(.02,3)]))
        for bounds in [(3,3),(-1,3),(True,5),(1,2**64),(1,90),(2,3)]:
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                f.summarize(f.parse(encode(base)),*bounds)

    def test_schema_truncation_budget_and_encoding_refuse(self):
        blob = encode([record(0,1)])
        for bad in [b'', blob[:-1], b'wrong\n', blob+b'1,2\n', b'\xff\n']:
            with self.assertRaises(ValueError): f.parse(bad)
        with patch.object(f,'LIMIT',4), self.assertRaises(ValueError): f.parse(blob)
        with patch.object(f,'ROWS',0), self.assertRaises(ValueError): f.parse(blob)

    def test_shared_source_is_separate_from_observed_field(self):
        a=record(0,1);a.update(shared=1,source_sequence=7,new_source=1,hash_valid=1,image_hash=23,image_changed=1)
        b=record(.02,3);b.update(shared=1,source_sequence=7,new_source=0,hash_valid=1,image_hash=23,image_changed=0)
        s=f.summarize(f.parse(encode([a,b])),1,3)
        self.assertEqual(s['shared_rows'],1);self.assertEqual(s['valid_hash_rows'],1)
        self.assertEqual(s['new_source_unknown_rows'],0)

    def test_bounded_read_only_file_analysis(self):
        with tempfile.TemporaryDirectory(prefix='godhand-present-synthetic-') as name:
            path=Path(name)/'invented.csv';blob=encode([record(0,1),record(.02,3)])
            path.write_bytes(blob);self.assertEqual(f.analyze(path,1,3)['observed_fields'],[1,3])
            self.assertEqual(path.read_bytes(),blob)
            with patch.object(f,'LIMIT',4), self.assertRaises(ValueError): f.analyze(path,1,3)
