"""Original GPL-3.0-only bounded local preference broker; no game/GUI dependency."""
from pathlib import Path
import hashlib
import json
import os
import re
import uuid
import threading

import runtime_packs
import video_settings as video

MAGIC = "GHPCV1"
LIMIT = 512
MAX_SEQUENCE = 128


def scale_token(value):
    video.require(value is None or (type(value) is int and 1 <= value <= 8), "Invalid menu scale")
    return "ini" if value is None else str(value)


def parse_scale(value):
    video.require(value == "ini" or value in tuple(map(str, range(1, 9))), "Invalid wire scale")
    return None if value == "ini" else int(value)


def tokens(raw, count):
    video.require(0 < len(raw) <= LIMIT and raw.endswith(b"\n") and b"\r" not in raw,
                  "Invalid menu wire length/newline")
    try:
        line = raw[:-1].decode("ascii")
    except UnicodeError as error:
        raise ValueError("Menu wire must be ASCII") from error
    fields = line.split("\t")
    video.require(len(fields) == count and fields[0] == MAGIC and
                  all(re.fullmatch(r"[a-zA-Z0-9-]+", x) for x in fields), "Invalid menu wire fields")
    return fields


def parse_request(raw, session, sequence):
    fields = tokens(raw, 7)
    _, nonce, seq, operation, logical_id, expected, scale = fields
    video.require(nonce == session and seq == str(sequence) and 1 <= sequence <= MAX_SEQUENCE,
                  "Menu request identity differs")
    if operation == "set":
        video.require(logical_id in tuple(map(str, range(1, 65))) and video.HASH.fullmatch(expected),
                      "Invalid set identity/revision")
        value = parse_scale(scale)
    else:
        video.require(operation == "read" and (logical_id, expected, scale) == ("0", "-", "-"),
                      "Invalid read request")
        value = None
    return {"fields": fields, "op": operation, "id": int(logical_id), "expected": expected, "scale": value}


def _read(path):
    video._ordinary(path)
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    video.require(len(raw) <= LIMIT, "Menu wire grew beyond its limit")
    return raw


def _write(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _publish(directory, name, raw):
    video.require(len(raw) <= LIMIT, "Menu output exceeds wire bound")
    _write(directory / (name + ".txt"), raw)
    # Exclusive empty marker is the commit point. Payload/attempts remain intact;
    # no replacing files or deleting evidence, no half-payload consumed.
    # A zero-length marker needs creation, not an open write handle/fsync. On
    # Windows a consumer's immutable read can otherwise race that live writer
    # and fail sharing checks after the marker already became visible.
    flags = os.O_RDONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(directory / (name + ".ready"), flags, 0o600)
    os.close(descriptor)


class Broker:
    """One owner/one new channel. Restart never reattaches/replays old requests."""
    def __init__(self, root, name, launch_directory, expected_revision, run_scale, *, user=None):
        initial = video.show(root, name, user=user)
        video.require(initial is not None and initial["sha256"] == expected_revision,
                      "Menu launch snapshot differs from current preferences")
        scale_token(run_scale)
        workspace = runtime_packs.workspace_path(root, name)
        launch = Path(launch_directory)
        video.require(launch.is_absolute() and re.fullmatch(r"[a-f0-9]{32}", launch.name) and
                      launch.parent == workspace / "packs/launches", "Menu channel requires an owned launch")
        for path in [workspace / "packs", workspace / "packs/launches", launch]:
            video._ordinary(path, directory=True)
        self.directory = launch / "video-menu"
        self.directory.mkdir()  # exclusive, never resume a previous channel
        self.root, self.name = root, name
        self.user = user
        self.session = uuid.uuid4().hex
        self.authorized_revision = expected_revision
        self.sequence, self.last_set_id = 1, 0
        self.unknown, self.stopped = False, False
        config = [MAGIC, self.session, scale_token(run_scale),
                  scale_token(initial["settings"]["native_scale"]), initial["sha256"],
                  "scratch" if user is not None else "persistent"]
        _publish(self.directory, "config", ("\t".join(config) + "\n").encode("ascii"))

    def _journal(self, suffix, data):
        raw = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("ascii")
        _write(self.directory / ("operation-" + str(self.sequence) + "-" + suffix + ".json"), raw)

    def poll(self):
        video.require(not self.stopped, "Menu channel stopped; inspect its retained evidence")
        if self.sequence > MAX_SEQUENCE:
            return None
        video._ordinary(self.directory, directory=True)
        marker = self.directory / ("request-" + str(self.sequence) + ".ready")
        if not marker.exists() and not marker.is_symlink():
            return None
        try:
            video.require(_read(marker) == b"", "Menu ready marker must be empty")
            raw = _read(self.directory / ("request-" + str(self.sequence) + ".txt"))
            request = parse_request(raw, self.session, self.sequence)
            if request["op"] == "set":
                video.require(request["id"] > self.last_set_id, "Menu set ID reused/out of order")
                self.last_set_id = request["id"]
            self._journal("started", {"request_sha256": hashlib.sha256(raw).hexdigest(),
                                      "operation": request["op"], "id": request["id"],
                                      "expected": request["expected"], "scale": request["scale"]})
            status, result = "unknown", None
            if request["op"] == "read":
                try:
                    result = video.show(self.root, self.name, user=self.user)
                    status = "ok" if result is not None else "rejected"
                except (OSError, ValueError):
                    status = "unknown"
            elif self.unknown:
                status = "unknown"  # read first; no blind retry after an uncertain commit
            elif request["expected"] != self.authorized_revision:
                status = "stale"
            else:
                try:
                    result = video.update(self.root, self.name, request["scale"],
                                          expected_revision=request["expected"], user=self.user)
                    status = "ok"
                except video.StaleRevision:
                    status = "stale"  # known no-commit conflict, not a catch-all I/O claim
                except (OSError, ValueError):
                    self.unknown = True
                    status = "unknown"
            reply = request["fields"] + [status, result["sha256"] if status == "ok" else "-",
                      scale_token(result["settings"]["native_scale"]) if status == "ok" else "-"]
            self._journal("finished", {"status": status, "confirmed_revision":
                                       result["sha256"] if status == "ok" else None})
            _publish(self.directory, "reply-" + str(self.sequence), ("\t".join(reply) + "\n").encode("ascii"))
            if status == "ok":
                self.authorized_revision = result["sha256"]
                self.unknown = False
            self.sequence += 1
            return {"status": status, "snapshot": result, "request": request}
        except BaseException:
            # Even a reply-write error can occur AFTER the store committed.
            # Preserve attempts and stop, never replay or call this NotSaved.
            self.stopped = True
            raise


class Service:
    """One owned broker thread; stop only after its native client process ended."""
    def __init__(self, broker):
        self.broker = broker
        self.stop_event = threading.Event()
        self.error = None
        self.operations = []
        self.thread = threading.Thread(target=self._run, name="godhand-video-preferences", daemon=False)

    def _run(self):
        try:
            while not self.stop_event.is_set():
                value = self.broker.poll()
                if value: self.operations.append(value["status"])
                self.stop_event.wait(0.005)
            # Caller confirmed client exit. Drain already-published immutable
            # requests once, not a retry/replay of an uncertain operation.
            for _ in range(MAX_SEQUENCE):
                value = self.broker.poll()
                if value is None: break
                self.operations.append(value["status"])
        except BaseException as error:
            self.error = str(error)

    def start(self):
        self.thread.start()
        return self

    def finish(self):
        self.stop_event.set()
        self.thread.join(timeout=10)
        video.require(not self.thread.is_alive(), "Video broker still alive; retain the launch and inspect, do not restart")
        return {"stopped": True, "error": self.error, "operations": list(self.operations)}
