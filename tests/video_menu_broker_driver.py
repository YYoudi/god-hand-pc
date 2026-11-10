"""Separate Python fixture process. Fault controls are invented tests, never public launch flags."""
from pathlib import Path
import argparse
import json
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import video_menu_channel as channel
import video_settings as video

parser = argparse.ArgumentParser()
parser.add_argument("root", type=Path)
parser.add_argument("launch", type=Path)
parser.add_argument("revision")
parser.add_argument("--fault", choices=("none", "after-commit", "reply-publication"), default="none")
parser.add_argument("--wait-first", action="store_true")
args = parser.parse_args()
broker = channel.Broker(args.root, "retail-invented", args.launch, args.revision, 3)
if args.fault == "after-commit":
    original = video.update
    first = [True]
    def uncertain(*a, **k):
        result = original(*a, **k)
        if first[0]:
            first[0] = False
            raise OSError("invented observer error AFTER canonical commit")
        return result
    video.update = uncertain
elif args.fault == "reply-publication":
    original_publish = channel._publish
    def fail_reply(directory, name, raw):
        if name == "reply-1": raise OSError("invented reply-publication failure AFTER commit")
        return original_publish(directory, name, raw)
    channel._publish = fail_reply
print("READY", flush=True)
end = time.monotonic() + 15
try:
    while time.monotonic() < end and not (args.root / "fixture-stop").exists():
        if not args.wait_first or (args.root / "fixture-go").exists():
            result = broker.poll()
            if result: print(json.dumps({"status": result["status"]}), flush=True)
        time.sleep(0.005)
    if time.monotonic() >= end: raise RuntimeError("Fixture observation deadline; no restart")
except BaseException as error:
    print("STOPPED", str(error), flush=True)
    raise SystemExit(2)
