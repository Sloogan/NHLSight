"""Headless NHL scorebug reader — validates the pipeline without the Qt UI.

Usage:
    python src/nhl_cli.py --source 0                       # USB capture device 0
    python src/nhl_cli.py --source path/to/clip.mp4
    python src/nhl_cli.py --source frame.png               # single-shot detect on a still
    python src/nhl_cli.py --source frame.png --calibrate   # overlay ROI boxes on the still
    python src/nhl_cli.py --source 0 --obs-out ./obs       # also write OBS .txt files
"""
import argparse
import json
import sys
import time
from pathlib import Path

import cv2

from nhl_detector import NHLDetector, mask_white_text
from nhl_obs_output import write_obs_files
from nhl_scorebug import EA_NHL_INGAME_24


_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".webp")


def is_still_image(src: str) -> bool:
    return src.lower().endswith(_IMAGE_EXTS)


def open_source(src: str) -> cv2.VideoCapture:
    if src.isdigit():
        return cv2.VideoCapture(int(src))
    return cv2.VideoCapture(src)


def draw_calibration(frame, profile=EA_NHL_INGAME_24):
    h, w = frame.shape[:2]
    for field in (
        "away_team", "home_team", "away_score", "home_score",
        "away_sog", "home_sog", "time", "period",
        "away_pp", "home_pp", "pp_time",
    ):
        roi = getattr(profile, field)
        x, y, rw, rh = roi.to_pixels(w, h)
        cv2.rectangle(frame, (x, y), (x + rw, y + rh), (0, 255, 0), 1)
        cv2.putText(frame, field, (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX,
                    0.4, (0, 255, 0), 1, cv2.LINE_AA)
    return frame


def run_still(args) -> int:
    frame = cv2.imread(args.source)
    if frame is None:
        print(f"failed to read image: {args.source}", file=sys.stderr)
        return 1

    if args.calibrate:
        cv2.imwrite(args.calibrate_out, draw_calibration(frame.copy()))
        print(f"wrote {args.calibrate_out}", file=sys.stderr)

    detector = NHLDetector(Path(args.glyphs))
    state = detector.detect(frame)
    print(json.dumps(state.to_json()))
    if args.obs_out:
        write_obs_files(state, Path(args.obs_out))
    if args.show_mask:
        cv2.imwrite("mask.png", mask_white_text(frame))
        print("wrote mask.png", file=sys.stderr)
    return 0


def run_stream(args) -> int:
    cap = open_source(args.source)
    if not cap.isOpened():
        print(f"failed to open source: {args.source}", file=sys.stderr)
        return 1

    if args.calibrate:
        ok, frame = cap.read()
        cap.release()
        if not ok:
            print("no frame", file=sys.stderr)
            return 1
        cv2.imwrite(args.calibrate_out, draw_calibration(frame))
        print(f"wrote {args.calibrate_out}", file=sys.stderr)
        return 0

    detector = NHLDetector(Path(args.glyphs))
    obs_out = Path(args.obs_out) if args.obs_out else None

    last_emit = 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        state = detector.detect(frame)

        now = time.monotonic()
        if now - last_emit >= 0.1:
            print(json.dumps(state.to_json()), flush=True)
            if obs_out:
                write_obs_files(state, obs_out)
            last_emit = now

        if args.show_mask:
            cv2.imshow("mask", mask_white_text(frame))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--glyphs", default="glyphs", help="Directory with digits/, teams/, symbols/")
    ap.add_argument("--obs-out", default=None)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--calibrate-out", default="calibration.png")
    ap.add_argument("--show-mask", action="store_true")
    args = ap.parse_args()

    if is_still_image(args.source):
        return run_still(args)
    return run_stream(args)


if __name__ == "__main__":
    sys.exit(main())
