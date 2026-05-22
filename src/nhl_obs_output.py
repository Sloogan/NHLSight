from pathlib import Path
from nhl_scorebug import NHLGameState


_FIELDS = (
    "home_team", "away_team", "home_score", "away_score",
    "home_sog", "away_sog", "time", "period", "pp_time",
)


def write_obs_files(state: NHLGameState, out_dir: Path) -> None:
    """One file per scoreboard field — OBS Text (GDI+) sources point at these."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for field in _FIELDS:
        value = getattr(state, field)
        text = "" if value is None else str(value)
        (out_dir / f"{field}.txt").write_text(text, encoding="utf-8")
    (out_dir / "home_pp.txt").write_text("1" if state.home_pp else "0", encoding="utf-8")
    (out_dir / "away_pp.txt").write_text("1" if state.away_pp else "0", encoding="utf-8")
