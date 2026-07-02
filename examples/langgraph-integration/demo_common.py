# Copyright (c) 2026 Tencent Inc.
# SPDX-License-Identifier: Apache-2.0

"""Shared helpers for LangGraph / Deep Agents CubeSandbox demos."""

from __future__ import annotations

import os
import time
from typing import Protocol

from deepagents import create_deep_agent
from deepagents.backends.sandbox import BaseSandbox

from llm_utils import make_chat_model

CUBE_WORKDIR = "/root"
MARKER_PATH = "/tmp/langgraph-cube-marker.txt"
MARKER_CONTENT = "langgraph + cubesandbox\n"

SYSTEM_PROMPT = (
    "You are a helpful assistant running inside a CubeSandbox MicroVM. "
    "Use the execute tool and filesystem tools to inspect the environment. "
    "Be concise and show command output when relevant."
)


class SandboxHandle(Protocol):
    def kill(self) -> None: ...


def run_sandbox_check(*, backend: BaseSandbox, sandbox: SandboxHandle, label: str) -> None:
    print(f"Backend:  {label}")
    print(f"CubeAPI:  {os.environ['E2B_API_URL']}\n")

    t0 = time.monotonic()
    print(f"[create] sandbox_id={backend.id}")

    result = backend.execute("uname -a && cat /etc/os-release | head -3")
    print(f"[execute] exit={result.exit_code}  {(time.monotonic() - t0) * 1000:.0f} ms")
    print(result.output.strip())

    backend.upload_files([(MARKER_PATH, MARKER_CONTENT.encode("utf-8"))])
    read_back = backend.download_files([MARKER_PATH])[0]
    if read_back.content is None:
        raise RuntimeError(f"failed to read marker file: {read_back.error}")

    text = read_back.content.decode("utf-8")
    if text.strip() != MARKER_CONTENT.strip():
        raise RuntimeError(f"marker mismatch: {text!r}")

    print(f"\n{'=' * 60}")
    print("PASS: CubeSandbox backend is reachable.")


def run_agent_demo(
    *,
    backend: BaseSandbox,
    sandbox: SandboxHandle,
    label: str,
    model: str,
    question: str,
) -> None:
    print(f"Backend:  {label}")
    print(f"Model:    {model}")
    print(f"CubeAPI:  {os.environ['E2B_API_URL']}")
    print(f"Question: {question}\n")
    print(f"[sandbox] sandbox_id={backend.id}")

    agent = create_deep_agent(
        model=make_chat_model(model),
        backend=backend,
        system_prompt=SYSTEM_PROMPT,
    )

    print("[agent] running LangGraph agent (Deep Agents harness) ...\n")
    t1 = time.monotonic()
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    elapsed_ms = (time.monotonic() - t1) * 1000

    messages = result.get("messages", [])
    answer = messages[-1].content if messages else result
    print(f"{'=' * 60}")
    print(answer)
    print(f"\n[done] {elapsed_ms:.0f} ms")
