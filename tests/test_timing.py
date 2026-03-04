from depsched.config import load_pipeline
from depsched.graph import build_graph
from depsched.timing import compute_earliest_schedule


def test_compute_earliest_schedule_simple(tmp_path):
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

    start, end, makespan = compute_earliest_schedule(graph, durations)

    # a starts at 0, ends at 3
    assert start["a"] == 0
    assert end["a"] == 3

    # b depends on a => starts at 3
    assert start["b"] == 3
    assert end["b"] == 8

    # c depends on a => starts at 3
    assert start["c"] == 3
    assert end["c"] == 5

    # d depends on b and c => starts at max(8,5)=8
    assert start["d"] == 8
    assert end["d"] == 9

    assert makespan == 9