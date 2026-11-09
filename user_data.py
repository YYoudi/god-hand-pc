"""Original GPL-3.0-only preference isolation; no game data or native UI source."""
from pathlib import Path
import hashlib
import stat

LIMIT = 1024 * 1024


def controls_environment(user):
    # The launcher is not a self-test: an upstream INI must not activate a
    # destructive UI diagnostic now that a non-default controls file is set.
    return {'GODHAND_CONTROLS_FILE': str(Path(user) / 'controls.ini'),
            'GODHAND_CONTROLS_SELFTEST': '0'}


def _regular(path, destination=False):
    if path.is_symlink():
        raise ValueError("Controls symlinks are not supported")
    info = path.stat()
    if (not stat.S_ISREG(info.st_mode) or
            getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024)):
        raise ValueError("Controls must be an ordinary file")
    if destination and info.st_nlink != 1:
        raise ValueError("Hardlinked controls destinations are not supported")
    if info.st_size > LIMIT:
        raise ValueError("Controls file exceeds the metadata limit")


def contents(path, destination=False):
    path = Path(path)
    _regular(path, destination)
    with path.open('rb') as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("Controls file grew beyond the metadata limit")
    return data


def snapshot(path):
    path = Path(path)
    if not path.exists() and not path.is_symlink():
        return {'path': str(path), 'exists': False}
    data = contents(path, destination=True)
    return {'path': str(path), 'exists': True, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def prepare_controls(user, executable, fresh=False):
    user = Path(user).resolve(strict=True)
    path = user / 'controls.ini'
    # Check the un-resolved leaf first too: an inside-root alias is still unsafe.
    if path.is_symlink() or not path.resolve().is_relative_to(user):
        raise ValueError("Controls destination escapes or aliases user data")
    before = snapshot(path)
    if before['exists']:
        return {'operation': 'reuse', 'before': before}
    source = Path(executable).parent / 'controls.ini'
    if not fresh and source.exists():
        data = contents(source)
        with path.open('xb') as output:
            output.write(data)
        return {'operation': 'adopt-existing-byte-copy', 'source': {
                    'path': str(source), 'bytes': len(data),
                    'sha256': hashlib.sha256(data).hexdigest()}, 'before': snapshot(path)}
    return {'operation': 'native-defaults', 'before': before}
