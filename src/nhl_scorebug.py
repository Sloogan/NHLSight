from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(slots=True)
class NHLGameState:
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_score: int = 0
    away_score: int = 0
    home_sog: int = 0
    away_sog: int = 0
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

    Column order left-to-right: NHL logo | team abbr | goals | shots on goal
    | time/period. Two stacked rows: away team (top) and home team (bottom).
    Coordinates are normalized against frame size so the same profile works
    for 1080p and 4K captures.
    """
    name: str
    away_team: ROI
    home_team: ROI
    away_score: ROI
    home_score: ROI
    away_sog: ROI
    home_sog: ROI
    time: ROI
    period: ROI
    home_pp: ROI
    away_pp: ROI
    pp_time: ROI


# Calibrated against a 1920x1080 EA NHL 25 capture (Scotiabank Arena, MTL@TOR).
# PP fields are not visible in idle play — kept at zero-area until we get a
# reference frame with an active penalty.
EA_NHL_INGAME_24 = ScorebugProfile(
    name="ea_nhl_25_top_left",
    away_team=ROI(x=0.0599, y=0.0093, w=0.0573, h=0.0463),
    home_team=ROI(x=0.0599, y=0.0556, w=0.0573, h=0.0463),
    away_score=ROI(x=0.1198, y=0.0139, w=0.0391, h=0.0417),
    home_score=ROI(x=0.1198, y=0.0602, w=0.0391, h=0.0417),
    away_sog=ROI(x=0.1589, y=0.0139, w=0.0339, h=0.0324),
    home_sog=ROI(x=0.1589, y=0.0648, w=0.0339, h=0.0324),
    time=ROI(x=0.1953, y=0.0139, w=0.0469, h=0.0417),
    period=ROI(x=0.1953, y=0.0648, w=0.0469, h=0.0324),
    away_pp=ROI(x=0.0, y=0.0, w=0.0, h=0.0),
    home_pp=ROI(x=0.0, y=0.0, w=0.0, h=0.0),
    pp_time=ROI(x=0.0, y=0.0, w=0.0, h=0.0),
)
