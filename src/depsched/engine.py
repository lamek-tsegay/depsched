from __future__ import annotations
from .timing import schedule_table, compute_critical_path

from pathlib import Path
from typing import Dict, List, Set, Optional
import fnmatch
import subprocess

from .config import load_pipeline
from .graph import build_graph, available_tasks, downstream_closure, topo_check_acyclic
from .state import load_state, save_state, reset_state as reset_state_file


import fnmatch

def _match_any_glob(path_str: str, globs: List[str]) -> bool:
    """
    Match path_str against glob patterns with globstar semantics:
    - '**' may match zero or more directories
    """
    p = path_str.replace("\\", "/")

    for g in globs:
        g = g.replace("\\", "/")

        patterns = {g}

        
        while "/**/" in g:
            g = g.replace("/**/", "/")
            patterns.add(g)

        if g.startswith("**/"):
            patterns.add(g[3:])

        if any(fnmatch.fnmatch(p, pat) for pat in patterns):
            return True

    return False


def pipeline_status(config_path: str, state_path: Optional[str] = None) -> Dict[str, List[str]]:
    spec = load_pipeline(config_path)
    graph = build_graph({t.name: t.deps for t in spec.tasks.values()})
    topo_check_acyclic(graph)

    spath = Path(state_path) if state_path else None
    state = load_state(spath) if spath else load_state()

    completed = sorted([t for t in state.completed if t in graph.tasks])
    avail = sorted(list(available_tasks(graph, state.completed)))
    pending = sorted(list(graph.tasks - state.completed))

    return {"completed": completed, "available": avail, "pending": pending}


def run_pipeline(config_path: str, *, state_path: Optional[str] = None, verbose: bool = True) -> List[str]:
    spec = load_pipeline(config_path)
    graph = build_graph({t.name: t.deps for t in spec.tasks.values()})
    topo_check_acyclic(graph)

    spath = Path(state_path) if state_path else None
    state = load_state(spath) if spath else load_state()

    ran: List[str] = []

    while True:
        avail = sorted(list(available_tasks(graph, state.completed)))
        if not avail:
            break

        tname = avail[0]  # deterministic order
        task = spec.tasks[tname]

        if verbose:
            print(f"[depsched] running: {tname}")
            print(f"  cmd: {task.cmd}")

        proc = subprocess.run(task.cmd, shell=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Task '{tname}' failed with exit code {proc.returncode}")

        state.completed.add(tname)
        ran.append(tname)

        if spath:
            save_state(state, spath)
        else:
            save_state(state)

    if state.completed != graph.tasks:
        uncompleted = sorted(list(graph.tasks - state.completed))
        raise RuntimeError(f"Stuck. Uncompleted tasks remain: {uncompleted}")

    return ran


def touch_path(config_path: str, changed_path: str, *, state_path: Optional[str] = None, verbose: bool = True) -> List[str]:
    spec = load_pipeline(config_path)
    graph = build_graph({t.name: t.deps for t in spec.tasks.values()})
    topo_check_acyclic(graph)

    spath = Path(state_path) if state_path else None
    state = load_state(spath) if spath else load_state()

    impacted_direct: Set[str] = set()
    for tname, task in spec.tasks.items():
        if task.inputs and _match_any_glob(changed_path, task.inputs):
            impacted_direct.add(tname)

    impacted_all = downstream_closure(graph, impacted_direct)

    before = set(state.completed)
    state.completed.difference_update(impacted_all)
    invalidated = sorted(list(before - state.completed))

    if verbose:
        if not impacted_direct:
            print("[depsched] no tasks matched inputs for:", changed_path)
        else:
            print("[depsched] direct impacted tasks:", sorted(list(impacted_direct)))
        print("[depsched] invalidated (including downstream):", invalidated)

    if spath:
        save_state(state, spath)
    else:
        save_state(state)

    return invalidated


def reset_state(config_path: str, *, state_path: Optional[str] = None) -> None:
    spath = Path(state_path) if state_path else None
    if spath:
        reset_state_file(spath)
    else:
        reset_state_file()

def plan_pipeline(config_path: str) -> str:
    """
    Return a printable timeline plan (start/end per task + makespan).
    """
    spec = load_pipeline(config_path)
    graph = build_graph({t.name: t.deps for t in spec.tasks.values()})
    topo_check_acyclic(graph)

    durations = {name: task.duration for name, task in spec.tasks.items()}
    tasks, makespan = schedule_table(graph, durations)

    lines = []
    lines.append("task,start,end,duration")

    for t in tasks:
        lines.append(f"{t.name},{t.start:.2f},{t.end:.2f},{t.duration:.2f}")

    cp, ms = compute_critical_path(graph, durations)

    lines.append("")
    lines.append("critical_path," + " -> ".join(cp))
    lines.append(f"makespan,{ms:.2f}")

    return "\n".join(lines)