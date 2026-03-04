from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from .graph import Graph, topo_check_acyclic


@dataclass(frozen=True)
class TimedTask:
    name: str
    start: float
    end: float
    duration: float


def topo_order(graph: Graph) -> List[str]:
    """Return a topological order of the DAG (raises if cycle)."""
    topo_check_acyclic(graph)

    preds = {t: set(graph.preds[t]) for t in graph.tasks}
    ready = sorted([t for t in graph.tasks if not preds[t]])

    order: List[str] = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for s in graph.succs[n]:
            preds[s].discard(n)
            if not preds[s]:
                ready.append(s)
                ready.sort()

    return order


def compute_earliest_schedule(graph: Graph, durations: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float], float]:
    """
    Earliest-start schedule:
    start[t] = max(end[p] for p in preds[t]) else 0
    end[t] = start[t] + duration[t]
    returns (start_times, end_times, makespan)
    """
    order = topo_order(graph)

    start: Dict[str, float] = {}
    end: Dict[str, float] = {}

    for t in order:
        preds = graph.preds[t]
        if preds:
            st = max(end[p] for p in preds)
        else:
            st = 0.0
        start[t] = st
        end[t] = st + float(durations.get(t, 0.0))

    makespan = max(end.values()) if end else 0.0
    return start, end, makespan


def schedule_table(graph: Graph, durations: Dict[str, float]) -> Tuple[List[TimedTask], float]:
    start, end, makespan = compute_earliest_schedule(graph, durations)
    tasks = [
        TimedTask(name=t, start=start[t], end=end[t], duration=durations.get(t, 0.0))
        for t in graph.tasks
    ]
    tasks.sort(key=lambda x: (x.start, x.end, x.name))
    return tasks, makespan