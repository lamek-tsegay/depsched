# depsched

A dependency-aware task runner inspired by build systems like make, Bazel, and CI pipelines.

depsched models tasks as a Directed Acyclic Graph (DAG), runs tasks when their prerequisites are satisfied, stores completion state, and supports incremental rebuilds via invalidation (“touch”).



## Why This Project Exists

Modern engineering workflows rely on dependency graphs:

- Build systems (make, Bazel)
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Data pipelines
- Workflow engines

All of these systems:

1. Represent work as a dependency graph.
2. Execute tasks only when prerequisites are satisfied.
3. Re-run only what is affected when an input changes.

## Features

- DAG-based task scheduling
- Deterministic execution order
- Persistent state tracking in `.depsched/state.json`
- Incremental rebuild support via `touch`
- Cycle detection
- Configurable via YAML



## Installation (Local Development)

From the project root:

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

Run tests:

pytest -q



## Example Usage

Check task status:

depsched status -c examples/pipeline.yaml

Run the full pipeline:

depsched run -c examples/pipeline.yaml

Invalidate tasks impacted by a file change:

depsched touch -c examples/pipeline.yaml src/app.py

Reset scheduler state:

depsched reset -c examples/pipeline.yaml



## Example Config (YAML)

File: examples/pipeline.yaml

```
tasks:
  format:
    deps: []
    cmd: "python -c \"print('format ok')\""
    inputs: ["src/**/*.py"]

  lint:
    deps: ["format"]
    cmd: "python -m compileall -q src"
    inputs: ["src/**/*.py"]

  test:
    deps: ["lint"]
    cmd: "python -c \"print('tests ok')\""
    inputs: ["src/**/*.py"]

  build:
    deps: ["test"]
    cmd: "python -c \"print('build ok')\""
    inputs: ["src/**/*.py"]

```

### Field Explanation

deps:
List of prerequisite task names.

cmd:
Shell command executed when the task runs.

inputs:
File glob patterns used to determine which tasks are invalidated when a file changes.



## How Invalidation Works

When you run:

depsched touch -c pipeline.yaml src/app.py

depsched:

1. Finds tasks whose `inputs` match the file path.
2. Marks those tasks as incomplete.
3. Recursively marks all downstream dependent tasks as incomplete.
4. Saves the updated state.


## Project Structure

```
depsched/
│
├── src/depsched/
│   ├── cli.py
│   ├── config.py
│   ├── engine.py
│   ├── graph.py
│   └── state.py
│
├── tests/
├── examples/
├── pyproject.toml
└── README.md
```



## Technical Highlights

- Graph construction with adjacency sets
- Topological validation for cycle detection
- Deterministic scheduling
- Transitive downstream invalidation
- Clean separation of CLI, engine, graph, and state layers


## License

MIT 