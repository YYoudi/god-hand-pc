"""Original GPL-3.0-only bounded host-present CSV analysis. Never gameplay FPS."""
import argparse
import csv
import io
import json
import math
from pathlib import Path

HEADER = ('seconds', 'field', 'source_sequence', 'render_revision', 'new_source',
          'interval_ms', 'submit_ms', 'swap_ms', 'shared', 'hash_valid', 'image_hash', 'image_changed')
LIMIT = 64 * 1024 * 1024
ROWS = 1_000_000
U64 = 2**64 - 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unsigned(value):
    require(type(value) is str and value.isascii() and value.isdecimal() and len(value) <= 20,
            'Invalid unsigned field')
    result = int(value)
    require(result <= U64, 'Unsigned field overflow')
    return result


def nonnegative(value):
    try:
        require(type(value) is str and len(value) <= 32, 'Invalid timing length')
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError('Invalid timing value') from error
    require(math.isfinite(number) and 0 <= number <= 1e12, 'Invalid finite/nonnegative timing')
    return number


def parse(blob):
    require(type(blob) is bytes and len(blob) <= LIMIT, 'Present CSV budget')
    require(blob.endswith(b'\n'), 'Incomplete final CSV line; retain original, do not silently trim')
    try:
        lines = csv.reader(io.StringIO(blob.decode('utf-8')), strict=True)
        require(tuple(next(lines, ())) == HEADER, 'Unknown present CSV header')
        rows = []
        for columns in lines:
            require(len(rows) < ROWS and len(columns) == len(HEADER), 'CSV row shape/count budget')
            row = dict(zip(HEADER, columns))
            for key in ('seconds', 'interval_ms', 'submit_ms', 'swap_ms'):
                row[key] = nonnegative(row[key])
            for key in ('field', 'source_sequence', 'render_revision', 'image_hash'):
                row[key] = unsigned(row[key])
            for key in ('new_source', 'image_changed'):
                require(row[key] in ('-1', '0', '1'), 'Unknown observation flag')
                row[key] = int(row[key])
            for key in ('shared', 'hash_valid'):
                require(row[key] in ('0', '1'), 'Unknown boolean flag')
                row[key] = int(row[key])
            require(row['hash_valid'] or row['image_changed'] == -1, 'Unknown hash cannot prove image change')
            require(row['shared'] or (row['new_source'] == -1 and row['source_sequence'] == row['field']),
                    'Copy-path source/field observation inconsistent')
            if rows:
                require(row['seconds'] >= rows[-1]['seconds'] and row['field'] >= rows[-1]['field'],
                        'Non-monotonic present clock/field')
            rows.append(row)
    except (UnicodeError, csv.Error) as error:
        raise ValueError('Malformed present CSV') from error
    require(rows, 'No present records')
    return rows


def summarize(rows, lower, upper):
    require(type(lower) is int and type(upper) is int and 0 <= lower < upper <= U64,
            'Invalid requested field bounds')
    begin = next((i for i, r in enumerate(rows) if r['field'] >= lower), None)
    end = next((i for i, r in enumerate(rows) if r['field'] >= upper), None)
    require(begin is not None and end is not None and end > begin, 'Requested span not observed')
    first, last = rows[begin], rows[end]
    require(first['field'] < upper and last['seconds'] > first['seconds'], 'Collapsed observed span')
    # Intervals after the first selected row, through the first upper crossing.
    selected = rows[begin+1:end+1]
    return {
        'requested_fields': [lower, upper], 'observed_fields': [first['field'], last['field']],
        'boundary_overshoot': [first['field']-lower, last['field']-upper],
        'start_seconds': first['seconds'], 'end_seconds': last['seconds'],
        'field_span_wall_seconds': last['seconds']-first['seconds'],
        'host_present_intervals': len(selected),
        'distinct_observed_fields': len({r['field'] for r in rows[begin:end+1]}),
        'submit_wall_ms_sum': math.fsum(r['submit_ms'] for r in selected),
        'swap_wall_ms_sum': math.fsum(r['swap_ms'] for r in selected),
        'interval_wall_ms_sum': math.fsum(r['interval_ms'] for r in selected),
        'shared_rows': sum(r['shared'] for r in selected),
        'new_source_unknown_rows': sum(r['new_source'] == -1 for r in selected),
        'valid_hash_rows': sum(r['hash_valid'] for r in selected),
        'scope': 'Host-present observations over an actual field span, NOT game FPS/CPU busy time or isolated GPU classifier cost',
        'comparison_gate': 'Require identical actual field bounds, scenario/settings/input and verification images; no implicit work normalization',
        'precision': 'Native text timestamps are rounded; diagnostics can perturb the workload',
    }


def analyze(path, lower, upper):
    path = Path(path)
    require(path.stat().st_size <= LIMIT, 'Present CSV file budget')
    with path.open('rb') as stream:
        blob = stream.read(LIMIT+1)
    return summarize(parse(blob), lower, upper)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--from-field', type=int, required=True)
    parser.add_argument('--to-field', type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.csv, args.from_field, args.to_field), indent=2))


if __name__ == '__main__':
    main()
