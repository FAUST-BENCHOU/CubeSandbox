# Copyright (c) 2026 Tencent Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import ssl

import certifi
import httpx
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI


def make_chat_model(model_name: str) -> BaseChatModel:
    """Build an OpenAI-compatible chat model (DeepSeek, TokenHub, etc.)."""
    bare = model_name.split("/", 1)[-1] if "/" in model_name else model_name
    bare = bare.split(":", 1)[-1] if ":" in bare else bare

    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.Client(verify=ssl_ctx, trust_env=False)
    print("[ssl] LLM client: certifi CA bundle, trust_env=False")

    return ChatOpenAI(
        model=bare,
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        timeout=120,
        http_client=http_client,
    )
