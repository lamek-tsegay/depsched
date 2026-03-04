from __future__ import annotations

import argparse
from .engine import run_pipeline, pipeline_status, touch_path, reset_state


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="depsched",
        description="Dependency-aware task runner (make/CI-lite).",
    )
    parser.add_argument("-c", "--config", required=True, help="Path to pipeline YAML (e.g., pipeline.yaml)")
    parser.add_argument("--state", default=None, help="Path to state.json (default: .depsched/state.json)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Reduce output")

    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="Show completed/available/pending tasks")
    sub.add_parser("run", help="Run tasks until completion")

    p_touch = sub.add_parser("touch", help="Invalidate tasks affected by a changed file (cascades downstream)")
    p_touch.add_argument("path", help="Changed file path (used to match task inputs globs)")

    sub.add_parser("reset", help="Delete scheduler state (mark all tasks incomplete)")

    args = parser.parse_args()
    verbose = not args.quiet

    if args.cmd == "status":
        s = pipeline_status(args.config, state_path=args.state)
        print("completed:", s["completed"])
        print("available:", s["available"])
        print("pending:  ", s["pending"])
        return

    if args.cmd == "run":
        ran = run_pipeline(args.config, state_path=args.state, verbose=verbose)
        if verbose:
            print("[depsched] ran tasks:", ran)
        return

    if args.cmd == "touch":
        touch_path(args.config, args.path, state_path=args.state, verbose=verbose)
        return

    if args.cmd == "reset":
        reset_state(args.config, state_path=args.state)
        if verbose:
            print("[depsched] state reset")
        return


if __name__ == "__main__":
    main()