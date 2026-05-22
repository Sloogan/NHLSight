from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass(slots=True)
class NHLGameState:
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_score: int = 0
    away_score: int = 0
    time: Optional[str] = None
    period: Optional[str] = None
    home_pp: bool = False
    away_pp: bool = False
    pp_time: Optional[str] = None

    def to_json(self) -> dict:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class ROI:
    """Normalized rect in [0,1]. Resolved against actual frame size at runtime."""
    x: float
    y: float
    w: float
    h: float

    def to_pixels(self, frame_w: int, frame_h: int) -> tuple[int, int, int, int]:
        x = int(self.x * frame_w)
        y = int(self.y * frame_h)
        w = int(self.w * frame_w)
        h = int(self.h * frame_h)
        return x, y, w, h


@dataclass(slots=True, frozen=True)
class ScorebugProfile:
    """Layout of the EA NHL 24/25 in-game scorebug, centered at top of frame.

    Starting estimates — must be calibrated against a real 1920x1080 capture
    by overlaying boxes (see scripts/nhl_calibrate.py).
    """
    name: str
    away_team: ROI
    away_score: ROI
    period: ROI
    time: ROI
    home_score: ROI
    home_team: ROI
    home_pp: ROI
    away_pp: ROI
    pp_time: ROI


EA_NHL_INGAME_24 = ScorebugProfile(
    name="ea_nhl_ingame_24",
    away_team=ROI(x=0.355, y=0.020, w=0.055, h=0.035),
    away_score=ROI(x=0.410, y=0.018, w=0.040, h=0.045),
    period=ROI(x=0.475, y=0.015, w=0.050, h=0.025),
    time=ROI(x=0.460, y=0.040, w=0.080, h=0.035),
    home_score=ROI(x=0.550, y=0.018, w=0.040, h=0.045),
    home_team=ROI(x=0.590, y=0.020, w=0.055, h=0.035),
    away_pp=ROI(x=0.405, y=0.065, w=0.045, h=0.020),
    home_pp=ROI(x=0.550, y=0.065, w=0.045, h=0.020),
    pp_time=ROI(x=0.470, y=0.075, w=0.060, h=0.025),
)
