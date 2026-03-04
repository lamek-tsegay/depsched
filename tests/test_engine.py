from pathlib import Path
from depsched.engine import pipeline_status, run_pipeline, touch_path


def write_config(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "pipeline.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_run_and_touch(tmp_path):
    cfg = write_config(
        tmp_path,
        """
tasks:
  a:
    deps: []
    cmd: "python -c \\"print('a')\\""
    inputs: ["src/**/*.py"]

  b:
    deps: ["a"]
    cmd: "python -c \\"print('b')\\""
    inputs: ["src/**/*.py"]

  c:
    deps: ["b"]
    cmd: "python -c \\"print('c')\\""
    inputs: ["src/**/*.py"]
""",
    )

    state_path = tmp_path / "state.json"

    s = pipeline_status(str(cfg), state_path=str(state_path))
    assert s["available"] == ["a"]

    ran = run_pipeline(str(cfg), state_path=str(state_path), verbose=False)
    assert ran == ["a", "b", "c"]

    invalidated = touch_path(str(cfg), "src/app.py", state_path=str(state_path), verbose=False)
    assert set(invalidated) == {"a", "b", "c"}

    s2 = pipeline_status(str(cfg), state_path=str(state_path))
    assert s2["available"] == ["a"]