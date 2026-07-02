# Copyright (c) 2026 Tencent Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def load_local_dotenv() -> None:
    """Load a nearby ``.env`` without overriding existing environment variables."""
    for path in (Path(__file__).with_name(".env"), Path.cwd() / ".env"):
        if path.is_file():
            load_dotenv(dotenv_path=path, override=False)
            return


def load_cube_env(*, need_llm: bool = True) -> None:
    """Validate CubeSandbox and optional LLM environment variables."""
    load_local_dotenv()

    required = ("E2B_API_KEY", "E2B_API_URL", "CUBE_TEMPLATE_ID")
    if need_llm:
        required = ("OPENAI_API_KEY", "OPENAI_BASE_URL", *required)

    for key in required:
        if not os.environ.get(key):
            raise SystemExit(f"Missing env var: {key}")

    cube_ssl = os.environ.get("CUBE_SSL_CERT_FILE")
    if cube_ssl and os.path.isfile(cube_ssl):
        os.environ["SSL_CERT_FILE"] = cube_ssl
        print(f"[ssl] SSL_CERT_FILE={cube_ssl} (for E2B data-plane HTTPS)")
