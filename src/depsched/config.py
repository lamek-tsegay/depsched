from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Iterable
import yaml


@dataclass(frozen=True)
class TaskSpec:
    name: str
    cmd: str
    deps: List[str]
    inputs: List[str]


@dataclass(frozen=True)
class PipelineSpec:
    tasks: Dict[str, TaskSpec]


def load_pipeline(path: str) -> PipelineSpec:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict) or "tasks" not in raw:
        raise ValueError("Config must be a mapping with a top-level 'tasks:' key")

    tasks_raw = raw["tasks"]
    if not isinstance(tasks_raw, dict):
        raise ValueError("'tasks' must be a mapping of task_name -> spec")

    tasks: Dict[str, TaskSpec] = {}

    for name, spec in tasks_raw.items():
        if not isinstance(name, str):
            raise ValueError("Task names must be strings")
        if not isinstance(spec, dict):
            raise ValueError(f"Task '{name}' spec must be a mapping")

        cmd = spec.get("cmd")
        deps = spec.get("deps", [])
        inputs = spec.get("inputs", [])

        if not isinstance(cmd, str) or not cmd.strip():
            raise ValueError(f"Task '{name}' must have non-empty string 'cmd'")
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
            raise ValueError(f"Task '{name}' 'deps' must be a list[str]")
        if not isinstance(inputs, list) or any(not isinstance(p, str) for p in inputs):
            raise ValueError(f"Task '{name}' 'inputs' must be a list[str]")

        tasks[name] = TaskSpec(name=name, cmd=cmd, deps=deps, inputs=inputs)

    for t in tasks.values():
        for d in t.deps:
            if d not in tasks:
                raise ValueError(f"Task '{t.name}' depends on unknown task '{d}'")

    return PipelineSpec(tasks=tasks)