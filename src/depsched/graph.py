from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Set, List, Iterable


@dataclass
class Graph:
    tasks: Set[str]
    preds: Dict[str, Set[str]]
    succs: Dict[str, Set[str]]


def build_graph(task_deps: Dict[str, Iterable[str]]) -> Graph:
    tasks: Set[str] = set(task_deps.keys())
    preds: Dict[str, Set[str]] = {t: set(task_deps[t]) for t in tasks}
    succs: Dict[str, Set[str]] = {t: set() for t in tasks}

    for t in tasks:
        for p in preds[t]:
            succs[p].add(t)

    return Graph(tasks=tasks, preds=preds, succs=succs)


def available_tasks(graph: Graph, completed: Set[str]) -> Set[str]:
    avail: Set[str] = set()
    for t in graph.tasks:
        if t in completed:
            continue
        if graph.preds[t].issubset(completed):
            avail.add(t)
    return avail


def downstream_closure(graph: Graph, start: Set[str]) -> Set[str]:
    out: Set[str] = set()
    stack: List[str] = list(start)
    while stack:
        cur = stack.pop()
        if cur in out:
            continue
        out.add(cur)
        stack.extend(graph.succs[cur])
    return out


def topo_check_acyclic(graph: Graph) -> None:
    preds = {t: set(graph.preds[t]) for t in graph.tasks}
    ready = [t for t in graph.tasks if not preds[t]]
    processed = 0

    while ready:
        n = ready.pop()
        processed += 1
        for s in graph.succs[n]:
            preds[s].discard(n)
            if not preds[s]:
                ready.append(s)

    if processed != len(graph.tasks):
        raise ValueError("Cycle detected in task dependency graph")