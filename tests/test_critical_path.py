from depsched.config import load_pipeline
from depsched.graph import build_graph
from depsched.timing import compute_critical_path


def test_critical_path(tmp_path):
    cfg = tmp_path / "timed.yaml"
    cfg.write_text(
        """
tasks:
  a:
    deps: []
    cmd: "python -c \\"print('a')\\""
    duration: 3

  b:
    deps: ["a"]
    cmd: "python -c \\"print('b')\\""
    duration: 5

  c:
    deps: ["a"]
    cmd: "python -c \\"print('c')\\""
    duration: 2

  d:
    deps: ["b", "c"]
    cmd: "python -c \\"print('d')\\""
    duration: 1
""",
        encoding="utf-8",
    )

    spec = load_pipeline(str(cfg))
    graph = build_graph({t.name: t.deps for t in spec.tasks.values()})
    durations = {name: task.duration for name, task in spec.tasks.items()}

    path, makespan = compute_critical_path(graph, durations)

    assert makespan == 9
    assert path == ["a", "b", "d"]