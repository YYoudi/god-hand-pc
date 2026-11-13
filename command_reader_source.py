"""Original GPL-3.0-only, exact-input host edit; never edits generated game code."""
import argparse
import hashlib
import json
from pathlib import Path

def apply(blob, recipe):
    digest=lambda b:hashlib.sha256(b).hexdigest()
    if digest(blob)!=recipe['input_sha256']:
        raise ValueError('Host preimage differs')
    result=blob
    for edit in recipe['edits']:
        old=edit['old'].encode('utf-8');new=edit['new'].encode('utf-8')
        if not old or result.count(old)!=1:
            raise ValueError('Host edit is absent or ambiguous')
        result=result.replace(old,new,1)
    if digest(result)!=recipe['output_sha256']:
        raise ValueError('Host postimage differs')
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    a=p.parse_args(argv)
    try:
        src=Path(a.input);dest=Path(a.output)
        if src.is_symlink() or not src.is_file() or src.stat().st_size>100000:
            raise ValueError('Ordinary bounded private host input required')
        if dest.exists() or dest.is_symlink():
            raise ValueError('Output must be new')
        recipe=json.loads((Path(__file__).parent/'adapter/command_line_reader_integration.json').read_text(encoding='utf-8'))
        result=apply(src.read_bytes(),recipe)
        with dest.open('xb') as stream:stream.write(result)
        print('Exact private host postimage emitted; no compilation or game execution.')
        return 0
    except (OSError,ValueError) as e:
        print(str(e));return 2

if __name__=='__main__':raise SystemExit(main())
