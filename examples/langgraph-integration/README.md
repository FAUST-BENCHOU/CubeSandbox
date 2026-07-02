# LangGraph + CubeSandbox Example

[中文](README_zh.md)

This directory shows how to connect a [LangGraph](https://github.com/langchain-ai/langgraph) agent to [CubeSandbox](https://github.com/TencentCloud/CubeSandbox).

It uses [Deep Agents](https://github.com/langchain-ai/deepagents) `create_deep_agent()` with the E2B-compatible API so tool calls run inside CubeSandbox MicroVMs.

```text
LangGraph Agent (Deep Agents)
        │
        └── langchain-e2b.E2BSandbox
                └── e2b.Sandbox ──► CubeAPI (:3000)
                        │
                        ▼
                  CubeSandbox MicroVM (envd)
```

## Prerequisites

- Python 3.11+
- Running CubeSandbox with CubeAPI reachable
- A sandbox template
- An OpenAI-compatible LLM API key

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # API keys, CubeAPI URL, template ID, mkcert CA path

# Sandbox connectivity only (no LLM)
python e2b_demo.py --sandbox-only

# Full agent
python e2b_demo.py
python e2b_demo.py --model deepseek-chat --question "What Linux distro is this?"
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | LLM API key |
| `OPENAI_BASE_URL` | LLM endpoint (e.g. DeepSeek) |
| `E2B_API_URL` | CubeAPI URL |
| `E2B_API_KEY` | CubeAPI auth key |
| `CUBE_TEMPLATE_ID` | Sandbox template ID |
| `CUBE_SSL_CERT_FILE` | mkcert root CA for E2B data-plane HTTPS |

## Files

| File | Description |
|------|-------------|
| `e2b_demo.py` | Entry script |
| `demo_common.py` | Agent and sandbox connectivity helpers |
| `cube_patches.py` | envd patches (root user, stdin) |
| `env_utils.py` | Load `.env`, validate variables |
| `llm_utils.py` | OpenAI-compatible LLM client |

## CubeSandbox adaptations

`cube_patches.py` runs before the E2B SDK is used:

| Patch | Reason |
|-------|--------|
| `default_username = "root"` | Cube envd only supports root |
| Drop `stdin` kwarg | Older envd rejects it |
| `workdir = "/root"` | Cube images use root |
| `CUBE_SSL_CERT_FILE` → `SSL_CERT_FILE` | Trust mkcert CA for E2B HTTPS (same as openai-agents-example) |

The LLM client uses certifi + `trust_env=False` so `SSL_CERT_FILE` does not affect DeepSeek and other public HTTPS APIs.

Point `CUBE_SSL_CERT_FILE` at the **mkcert root CA**, not `cube-root-ca.crt`.

## Core code

```python
from cube_patches import apply_cube_envd_patches
apply_cube_envd_patches()

from deepagents import create_deep_agent
from e2b import Sandbox
from langchain_e2b import E2BSandbox

sandbox = Sandbox.create(template=template_id, timeout=300)
backend = E2BSandbox(sandbox=sandbox, workdir="/root", timeout=300)

agent = create_deep_agent(model=chat_model, backend=backend, system_prompt="...")
result = agent.invoke({"messages": [{"role": "user", "content": question}]})
```

## Related docs

- [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents sandboxes](https://docs.langchain.com/oss/python/deepagents/sandboxes)
- [OpenAI Agents example](../openai-agents-example/README.md)
