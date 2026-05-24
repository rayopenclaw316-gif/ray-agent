import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"


def load(filename: str) -> dict:
    p = _DATA_DIR / filename
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save(filename: str, data: dict) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    (_DATA_DIR / filename).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
