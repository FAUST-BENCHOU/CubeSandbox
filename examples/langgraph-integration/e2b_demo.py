# Copyright (c) 2026 Tencent Inc.
# SPDX-License-Identifier: Apache-2.0

"""
LangGraph + CubeSandbox demo (E2B-compatible SDK).

Usage:
    cp .env.example .env
    pip install -r requirements.txt
    python e2b_demo.py
    python e2b_demo.py --sandbox-only
"""

from __future__ import annotations

import argparse
import os

from cube_patches import apply_cube_envd_patches

apply_cube_envd_patches()

from e2b import Sandbox  # noqa: E402
from langchain_e2b import E2BSandbox  # noqa: E402

from demo_common import CUBE_WORKDIR, run_agent_demo, run_sandbox_check  # noqa: E402
from env_utils import load_cube_env  # noqa: E402


def create_backend(*, template: str, timeout: int) -> tuple[Sandbox, E2BSandbox]:
    sandbox = Sandbox.create(template=template, timeout=timeout)
    backend = E2BSandbox(sandbox=sandbox, workdir=CUBE_WORKDIR, timeout=timeout)
    return sandbox, backend


def main() -> None:
    parser = argparse.ArgumentParser(description="LangGraph + CubeSandbox (E2B SDK)")
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument(
        "--question",
        default="What OS is running? Show uname and the first 3 lines of /etc/os-release.",
    )
    parser.add_argument("--template", default=None)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--sandbox-only", action="store_true")
    args = parser.parse_args()

    load_cube_env(need_llm=not args.sandbox_only)

    template = args.template or os.environ.get("CUBE_TEMPLATE_ID")
    if not template:
        raise SystemExit("Missing template: set CUBE_TEMPLATE_ID or pass --template")

    sandbox = None
    try:
        sandbox, backend = create_backend(template=template, timeout=args.timeout)
        if args.sandbox_only:
            run_sandbox_check(backend=backend, sandbox=sandbox, label="E2B SDK -> CubeAPI")
        else:
            run_agent_demo(
                backend=backend,
                sandbox=sandbox,
                label="E2B SDK -> CubeAPI",
                model=args.model,
                question=args.question,
            )
    finally:
        if sandbox is not None:
            print("\n[cleanup] destroying sandbox ...")
            sandbox.kill()


if __name__ == "__main__":
    main()
