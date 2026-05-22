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
    """Layout of the EA NHL 25 in-game scorebug pinned to the top-left.

    Two stacked rows: away team (top) and home team (bottom). Coordinates
    are normalized against frame size so the same profile works for 1080p
    and 4K captures.
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


# Calibrated against a 1920x1080 EA NHL 25 capture (Scotiabank Arena, MTL@TOR).
# PP fields are not visible in idle play — kept at zero-area until we get a
# reference frame with an active penalty.
EA_NHL_INGAME_24 = ScorebugProfile(
    name="ea_nhl_25_top_left",
    away_team=ROI(x=0.0443, y=0.0185, w=0.0521, h=0.0324),
    home_team=ROI(x=0.0443, y=0.0556, w=0.0521, h=0.0370),
    away_score=ROI(x=0.0990, y=0.0167, w=0.0313, h=0.0370),
    home_score=ROI(x=0.0990, y=0.0556, w=0.0313, h=0.0370),
    time=ROI(x=0.1719, y=0.0167, w=0.0703, h=0.0370),
    period=ROI(x=0.1849, y=0.0602, w=0.0417, h=0.0324),
    away_pp=ROI(x=0.0, y=0.0, w=0.0, h=0.0),
    home_pp=ROI(x=0.0, y=0.0, w=0.0, h=0.0),
    pp_time=ROI(x=0.0, y=0.0, w=0.0, h=0.0),
)
