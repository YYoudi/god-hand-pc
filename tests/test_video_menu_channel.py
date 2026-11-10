"""Invented metadata only, plus real C++ client/Python broker processes; no game."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

import pc
import video_menu_channel as channel
import video_settings as video


class BrokerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="godhand-channel-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        (self.root / ".local/retail-invented").mkdir(parents=True)
        self.initial = video.update(self.root, "retail-invented", 2)
        self.launch = self.root / ".local/retail-invented/packs/launches" / uuid.uuid4().hex
        self.launch.mkdir(parents=True)
        self.broker = channel.Broker(self.root, "retail-invented", self.launch, self.initial["sha256"], 3)

    def request(self, seq=1, op="set", logical=1, expected=None, scale="4"):
        fields = [channel.MAGIC, self.broker.session, str(seq), op, str(logical),
                  self.initial["sha256"] if expected is None else expected, scale]
        return ("\t".join(fields) + "\n").encode("ascii")

    def test_real_store_commit_then_read_and_retained_intents(self):
        channel._publish(self.broker.directory, "request-1", self.request())
        result = self.broker.poll()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(video.show(self.root, "retail-invented")["settings"]["native_scale"], 4)
        channel._publish(self.broker.directory, "request-2", self.request(2, "read", 0, "-", "-"))
        self.assertEqual(self.broker.poll()["snapshot"]["sha256"], result["snapshot"]["sha256"])
        self.assertTrue((self.broker.directory / "operation-1-started.json").exists())
        self.assertTrue((self.broker.directory / "operation-1-finished.json").exists())

    def test_partial_payload_without_marker_is_not_processed(self):
        path = self.broker.directory / "request-1.txt"
        path.write_bytes(self.request())
        self.assertIsNone(self.broker.poll())
        self.assertEqual(video.show(self.root, "retail-invented"), self.initial)
        (self.broker.directory / "request-1.ready").write_bytes(b"")
        self.assertEqual(self.broker.poll()["status"], "ok")

    def test_stale_external_edit_is_preserved_until_explicit_read(self):
        external = video.update(self.root, "retail-invented", 5)
        channel._publish(self.broker.directory, "request-1", self.request())
        self.assertEqual(self.broker.poll()["status"], "stale")
        self.assertEqual(video.show(self.root, "retail-invented"), external)

    def test_malformed_oversize_identity_or_path_tokens_stop_without_write(self):
        # Each malformed candidate gets a fresh owned channel, never resets one.
        for raw in [b"x"*513, self.request().replace(b"\n", b"\r\n"),
                    self.request().replace(self.broker.session.encode(), b"a"*32),
                    self.request().replace(b"\t4\n", b"\t../outside\n")]:
            with self.subTest(raw=raw[:50]):
                launch = self.launch.parent / uuid.uuid4().hex; launch.mkdir()
                b = channel.Broker(self.root, "retail-invented", launch, self.initial["sha256"], 3)
                (b.directory / "request-1.txt").write_bytes(raw)
                (b.directory / "request-1.ready").write_bytes(b"")
                with self.assertRaises((ValueError, OSError)): b.poll()
                self.assertTrue(b.stopped)
                self.assertEqual(video.show(self.root, "retail-invented"), self.initial)

    def test_hardlinked_marker_refused_without_changing_owner(self):
        owner = self.root / "invented-owner.txt"; owner.write_bytes(b"")
        try: os.link(owner, self.broker.directory / "request-1.ready")
        except OSError as error: self.skipTest(str(error))
        with self.assertRaises(ValueError): self.broker.poll()
        self.assertEqual(video.show(self.root, "retail-invented"), self.initial)
        self.assertEqual(owner.read_bytes(), b"")

    def test_reused_channel_constructor_refuses_without_replacing_config(self):
        before = (self.broker.directory / "config.txt").read_bytes()
        with self.assertRaises(OSError):
            channel.Broker(self.root, "retail-invented", self.launch, self.initial["sha256"], 3)
        self.assertEqual((self.broker.directory / "config.txt").read_bytes(), before)

    def test_scratch_store_and_service_never_change_persistent_preferences(self):
        launch = self.launch.parent / uuid.uuid4().hex; launch.mkdir()
        user = launch / "userdata"
        seed = video.update(self.root, "retail-invented", 2, expected_revision=None, user=user)
        broker = channel.Broker(self.root, "retail-invented", launch, seed["sha256"], 3, user=user)
        self.assertTrue((broker.directory / "config.txt").read_bytes().endswith(b"\tscratch\n"))
        service = channel.Service(broker).start()
        try:
            raw = self.request().replace(self.broker.session.encode(), broker.session.encode())
            channel._publish(broker.directory, "request-1", raw)
        finally:
            result = service.finish()  # no live client in this fixture; drains a published request
        self.assertEqual(result, {"stopped": True, "error": None, "operations": ["ok"]})
        self.assertEqual(video.show(self.root, "retail-invented"), self.initial)
        self.assertEqual(video.show(self.root, "retail-invented", user=user)["settings"]["native_scale"], 4)
        self.assertIsNone(seed["settings"]["previous"])
        with self.assertRaises(ValueError):
            video.update(self.root, "retail-invented", 8, user=self.root / "other")

    def test_service_preserves_error_and_does_not_restart_or_commit(self):
        channel._publish(self.broker.directory, "request-1", b"malformed\n")
        service = channel.Service(self.broker).start()
        result = service.finish()
        self.assertTrue(result["error"])
        self.assertEqual(result["operations"], [])
        self.assertTrue(self.broker.stopped)
        self.assertEqual(video.show(self.root, "retail-invented"), self.initial)


@unittest.skipUnless(shutil.which("g++") or shutil.which("clang++"), "C++20 needed")
class ProcessChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compilation = tempfile.TemporaryDirectory(prefix="godhand-client-program-")
        cls.addClassCleanup(cls.compilation.cleanup)
        cls.exe = Path(cls.compilation.name) / "invented-client.exe"
        command = [shutil.which("g++") or shutil.which("clang++"), "-std=c++20", "-O2", "-pthread",
                   "-Wall", "-Wextra", "-Werror", "-I", str(pc.ROOT / "adapter"),
                   str(pc.ROOT / "tests/video_menu_client_cases.cpp"), str(pc.ROOT / "adapter/video_menu_io.cpp"),
                   "-o", str(cls.exe)]
        if os.name == "nt": command.append("-municode")
        result = subprocess.run(command, capture_output=True, timeout=90)
        if result.returncode: raise RuntimeError(result.stderr.decode("utf8", errors="replace"))

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="godhand-channel-process-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        assert self.root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        (self.root / ".local/retail-invented").mkdir(parents=True)
        self.initial = video.update(self.root, "retail-invented", 2)
        self.launch = self.root / ".local/retail-invented/packs/launches" / uuid.uuid4().hex
        self.launch.mkdir(parents=True)
        self.directory = self.launch / "video-menu"
        self.server = None
        self.clients = []
        self.addCleanup(self.finish_fixture_processes)

    def finish_fixture_processes(self):
        # Stop only our tiny invented fixture worker, then wait its actual handle.
        # No killing/restarting a game, compiler or timed-out production observer.
        if self.server is not None and self.server.poll() is None:
            (self.root / "fixture-stop").write_bytes(b"")
            self.server.wait(timeout=8)
        for child in self.clients:
            if child.poll() is None: child.communicate(timeout=8)

    def wait_path(self, path, child=None):
        end = time.monotonic() + 8
        while time.monotonic() < end:
            if path.exists(): return
            if child is not None and child.poll() is not None: self.fail("Fixture child exited before expected path")
            time.sleep(0.005)
        self.fail("Fixture observation deadline, no restart")

    def start_server(self, *options):
        log = (self.root / "broker.log").open("wb"); self.addCleanup(log.close)
        self.server = subprocess.Popen([sys.executable, "-X", "utf8", str(pc.ROOT / "tests/video_menu_broker_driver.py"),
                                       str(self.root), str(self.launch), self.initial["sha256"], *options],
                                      stdout=log, stderr=log)
        self.wait_path(self.directory / "config.ready", self.server)

    def stop_server(self, expected=0):
        (self.root / "fixture-stop").write_bytes(b"")
        self.assertEqual(self.server.wait(timeout=8), expected)

    def test_cpp_and_python_roundtrip_reset_and_new_process_reload(self):
        self.start_server()
        result = subprocess.run([str(self.exe), "roundtrip", str(self.directory)], capture_output=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"ROUNDTRIP-RESET-READ", result.stdout)
        self.stop_server()
        selected = video.show(self.root, "retail-invented")
        self.assertIsNone(selected["settings"]["native_scale"])
        launch = self.launch.parent / uuid.uuid4().hex; launch.mkdir()
        fresh = channel.Broker(self.root, "retail-invented", launch, selected["sha256"], 3)
        reload = subprocess.run([str(self.exe), "initial", str(fresh.directory)], capture_output=True, timeout=5)
        self.assertEqual(reload.returncode, 0, reload.stderr)
        self.assertIn(b"INIT 3 ini", reload.stdout)

    def test_cpp_stale_then_explicit_read_then_success(self):
        self.start_server("--wait-first")
        child = subprocess.Popen([str(self.exe), "stale", str(self.directory)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.clients.append(child)
        self.wait_path(self.directory / "request-1.ready", child)
        video.update(self.root, "retail-invented", 5)
        (self.root / "fixture-go").write_bytes(b"")
        stdout, stderr = child.communicate(timeout=12)
        self.assertEqual(child.returncode, 0, stderr)
        self.assertIn(b"RECONCILED-SAVED", stdout)
        self.stop_server()
        self.assertEqual(video.show(self.root, "retail-invented")["settings"]["native_scale"], 6)

    def test_cpp_unknown_after_actual_commit_reconciles_without_blind_retry(self):
        self.start_server("--fault", "after-commit")
        result = subprocess.run([str(self.exe), "uncertain", str(self.directory)], capture_output=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"RECONCILED-SAVED", result.stdout)
        self.stop_server()
        self.assertEqual(video.show(self.root, "retail-invented")["settings"]["native_scale"], 6)
        first = json.loads((self.directory / "operation-1-finished.json").read_text())
        self.assertEqual(first["status"], "unknown")
        final = video.show(self.root, "retail-invented")
        previous = Path(final["path"]).parent / (final["settings"]["previous"] + ".json")
        middle = json.loads(previous.read_text())
        self.assertEqual(middle["native_scale"], 4)
        self.assertEqual(middle["previous"], self.initial["sha256"])  # no duplicate/blind commit

    def test_cpp_lost_reply_is_unknown_even_though_store_committed(self):
        self.start_server("--fault", "reply-publication")
        result = subprocess.run([str(self.exe), "lost-reply", str(self.directory)], capture_output=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"UNKNOWN-NO-RETRY", result.stdout)
        self.stop_server(expected=2)
        self.assertEqual(video.show(self.root, "retail-invented")["settings"]["native_scale"], 4)
        self.assertFalse((self.directory / "reply-1.ready").exists())

    def test_cpp_timeout_does_not_retry_or_claim_not_saved(self):
        channel.Broker(self.root, "retail-invented", self.launch, self.initial["sha256"], 3)
        result = subprocess.run([str(self.exe), "timeout", str(self.directory)], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"UNKNOWN-NO-RETRY", result.stdout)
        self.assertFalse((self.directory / "request-2.ready").exists())
        self.assertEqual(video.show(self.root, "retail-invented"), self.initial)

    def test_cpp_bad_identity_or_selection_ack_never_becomes_saved(self):
        for changed_index, value in [(1, "f"*32), (2, "2"), (4, "2"), (9, "5")]:
            with self.subTest(field=changed_index):
                launch = self.launch.parent / uuid.uuid4().hex; launch.mkdir()
                broker = channel.Broker(self.root, "retail-invented", launch, self.initial["sha256"], 3)
                child = subprocess.Popen([str(self.exe), "bad-reply", str(broker.directory)],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.clients.append(child)
                self.wait_path(broker.directory / "request-1.ready", child)
                fields = (broker.directory / "request-1.txt").read_text().rstrip("\n").split("\t")
                fields += ["ok", "b"*64, "4"]
                fields[changed_index] = value
                channel._publish(broker.directory, "reply-1", ("\t".join(fields) + "\n").encode())
                stdout, stderr = child.communicate(timeout=5)
                self.assertEqual(child.returncode, 0, stderr)
                self.assertIn(b"UNKNOWN-NO-RETRY", stdout)
                self.assertEqual(video.show(self.root, "retail-invented"), self.initial)

    def test_cpp_config_hardlinks_and_channel_reattachment_are_refused(self):
        broker = channel.Broker(self.root, "retail-invented", self.launch, self.initial["sha256"], 3)
        first = subprocess.run([str(self.exe), "initial", str(broker.directory)], capture_output=True, timeout=5)
        self.assertEqual(first.returncode, 0, first.stderr)
        config = (broker.directory / "config.txt").read_bytes()
        again = subprocess.run([str(self.exe), "initial", str(broker.directory)], capture_output=True, timeout=5)
        self.assertEqual(again.returncode, 3)
        self.assertEqual((broker.directory / "config.txt").read_bytes(), config)
        launch = self.launch.parent / uuid.uuid4().hex; directory = launch / "video-menu"
        directory.mkdir(parents=True)
        owner = self.root / "invented-config-owner.txt"; owner.write_bytes(config)
        try: os.link(owner, directory / "config.txt")
        except OSError as error: self.skipTest(str(error))
        (directory / "config.ready").write_bytes(b"")
        result = subprocess.run([str(self.exe), "raw-config", str(directory)], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(owner.read_bytes(), config)

    def test_cpp_wide_unicode_channel_path(self):
        # Owned invented Unicode directory; Windows fixture uses wmain/CreateFileW.
        unicode_root = self.root / "invented-é-漢"
        (unicode_root / ".local/retail-invented").mkdir(parents=True)
        initial = video.update(unicode_root, "retail-invented", 2)
        launch = unicode_root / ".local/retail-invented/packs/launches" / uuid.uuid4().hex
        launch.mkdir(parents=True)
        broker = channel.Broker(unicode_root, "retail-invented", launch, initial["sha256"], 3)
        result = subprocess.run([str(self.exe), "initial", str(broker.directory)], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"INIT 3 2", result.stdout)

    @unittest.skipUnless(os.name == "nt", "Windows file-sharing mode control")
    def test_ready_marker_live_writer_negative_and_readonly_creation_positive(self):
        config = (channel.MAGIC + "\t" + "a"*32 + "\t3\t2\t" + self.initial["sha256"] + "\tpersistent\n").encode()
        for writer in [True, False]:
            launch = self.launch.parent / uuid.uuid4().hex; directory = launch / "video-menu"
            directory.mkdir(parents=True)
            (directory / "config.txt").write_bytes(config)
            marker = directory / "config.ready"
            if writer:
                with marker.open("xb"):
                    result = subprocess.run([str(self.exe), "raw-config", str(directory)], capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 3)  # old visible-but-write-open marker conflicts
                self.assertIn(b"Cannot open message", result.stderr)
            else:
                fd = os.open(marker, os.O_RDONLY | os.O_CREAT | os.O_EXCL | os.O_BINARY)
                try:
                    result = subprocess.run([str(self.exe), "raw-config", str(directory)], capture_output=True, timeout=5)
                finally: os.close(fd)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(b"RAW-OK", result.stdout)
