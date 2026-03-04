from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Set, Dict, Any


DEFAULT_STATE_DIR = Path(".depsched")
DEFAULT_STATE_PATH = DEFAULT_STATE_DIR / "state.json"


@dataclass
class State:
    completed: Set[str]

    def to_json(self) -> Dict[str, Any]:
        return {"completed": sorted(self.completed)}

    @staticmethod
    def from_json(obj: Dict[str, Any]) -> "State":
        completed = obj.get("completed", [])
        if not isinstance(completed, list) or any(not isinstance(x, str) for x in completed):
            raise ValueError("Invalid state.json: 'completed' must be list[str]")
        return State(completed=set(completed))


def load_state(path: Path = DEFAULT_STATE_PATH) -> State:
    if not path.exists():
        return State(completed=set())
    with open(path, "r", encoding="utf-8") as f:
        return State.from_json(json.load(f))


def save_state(state: State, path: Path = DEFAULT_STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.to_json(), f, indent=2)
        f.write("\n")


def reset_state(path: Path = DEFAULT_STATE_PATH) -> None:
    if path.exists():
        path.unlink()