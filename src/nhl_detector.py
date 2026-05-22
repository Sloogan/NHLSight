from pathlib import Path
from typing import Optional
import cv2
import numpy as np

from nhl_scorebug import NHLGameState, ROI, ScorebugProfile, EA_NHL_INGAME_24


# EA NHL scorebug uses near-white text on a dark/translucent panel.
# Mask once per frame so digit/letter matching runs on a clean binary patch.
_WHITE_LOWER_HSV = np.array([0, 0, 200], dtype=np.uint8)
_WHITE_UPPER_HSV = np.array([180, 60, 255], dtype=np.uint8)


def mask_white_text(frame_bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, _WHITE_LOWER_HSV, _WHITE_UPPER_HSV)


def crop_roi(mask: np.ndarray, roi: ROI) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, rw, rh = roi.to_pixels(w, h)
    return mask[y0 : y0 + rh, x0 : x0 + rw]


class GlyphBank:
    """Pre-loaded binary glyph templates. Keys are the labels (e.g. "0", "TOR")."""

    def __init__(self, templates: dict[str, np.ndarray]):
        self.templates = templates

    @classmethod
    def from_dir(cls, dir_path: Path) -> "GlyphBank":
        templates: dict[str, np.ndarray] = {}
        if not dir_path.exists():
            return cls(templates)
        for png in dir_path.glob("*.png"):
            img = cv2.imread(str(png), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
            templates[png.stem] = binary
        return cls(templates)

    def best_match(self, patch: np.ndarray, threshold: float = 0.7) -> Optional[tuple[str, float, int]]:
        """Return (label, score, x_offset) of the single best matching template, or None."""
        best: Optional[tuple[str, float, int]] = None
        for label, tmpl in self.templates.items():
            if tmpl.shape[0] > patch.shape[0] or tmpl.shape[1] > patch.shape[1]:
                continue
            res = cv2.matchTemplate(patch, tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold and (best is None or max_val > best[1]):
                best = (label, float(max_val), int(max_loc[0]))
        return best


def read_digit_field(patch: np.ndarray, digits: GlyphBank, max_chars: int = 2) -> str:
    """Greedy left-to-right matching: find each digit, then mask it out and repeat."""
    chars: list[tuple[int, str]] = []
    work = patch.copy()
    for _ in range(max_chars):
        hit = digits.best_match(work)
        if hit is None:
            break
        label, _, x_off = hit
        tmpl_w = digits.templates[label].shape[1]
        chars.append((x_off, label))
        work[:, max(0, x_off - 1) : x_off + tmpl_w + 1] = 0
    chars.sort(key=lambda c: c[0])
    return "".join(c[1] for c in chars)


def read_team_field(patch: np.ndarray, teams: GlyphBank) -> Optional[str]:
    hit = teams.best_match(patch, threshold=0.6)
    return hit[0] if hit else None


def detect_pp_active(patch: np.ndarray, fill_ratio: float = 0.15) -> bool:
    """Powerplay indicator: small panel that fills with white text when active."""
    if patch.size == 0:
        return False
    return float(np.count_nonzero(patch)) / patch.size > fill_ratio


class NHLDetector:
    def __init__(self, glyph_dir: Path, profile: ScorebugProfile = EA_NHL_INGAME_24):
        self.profile = profile
        self.digits = GlyphBank.from_dir(glyph_dir / "digits")
        self.teams = GlyphBank.from_dir(glyph_dir / "teams")
        self.symbols = GlyphBank.from_dir(glyph_dir / "symbols")

    def detect(self, frame_bgr: np.ndarray) -> NHLGameState:
        mask = mask_white_text(frame_bgr)
        p = self.profile

        home_score_s = read_digit_field(crop_roi(mask, p.home_score), self.digits, 2)
        away_score_s = read_digit_field(crop_roi(mask, p.away_score), self.digits, 2)

        return NHLGameState(
            home_team=read_team_field(crop_roi(mask, p.home_team), self.teams),
            away_team=read_team_field(crop_roi(mask, p.away_team), self.teams),
            home_score=int(home_score_s) if home_score_s.isdigit() else 0,
            away_score=int(away_score_s) if away_score_s.isdigit() else 0,
            time=read_clock(crop_roi(mask, p.time), self.digits, self.symbols),
            period=read_period(crop_roi(mask, p.period), self.digits, self.symbols),
            home_pp=detect_pp_active(crop_roi(mask, p.home_pp)),
            away_pp=detect_pp_active(crop_roi(mask, p.away_pp)),
            pp_time=read_clock(crop_roi(mask, p.pp_time), self.digits, self.symbols),
        )


def read_clock(patch: np.ndarray, digits: GlyphBank, symbols: GlyphBank) -> Optional[str]:
    """MM:SS during regular play, SS.S in the final minute."""
    combined = GlyphBank({**digits.templates, **symbols.templates})
    text = read_digit_field(patch, combined, max_chars=5)
    return text if text else None


def read_period(patch: np.ndarray, digits: GlyphBank, symbols: GlyphBank) -> Optional[str]:
    combined = GlyphBank({**digits.templates, **symbols.templates})
    text = read_digit_field(patch, combined, max_chars=2)
    return text if text else None
