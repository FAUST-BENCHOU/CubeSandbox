# LangGraph + CubeSandbox 示例

[English](README.md)

本目录演示如何将 [LangGraph](https://github.com/langchain-ai/langgraph) Agent 接入 [CubeSandbox](https://github.com/TencentCloud/CubeSandbox) 沙箱。

使用 [Deep Agents](https://github.com/langchain-ai/deepagents) 的 `create_deep_agent()` 构建 LangGraph Agent，通过 E2B 兼容 API 在 CubeSandbox MicroVM 内执行工具。

```text
LangGraph Agent (Deep Agents)
        │
        └── langchain-e2b.E2BSandbox
                └── e2b.Sandbox ──► CubeAPI (:3000)
                        │
                        ▼
                  CubeSandbox MicroVM (envd)
```

## 前置条件

- Python 3.11+
- CubeSandbox 已部署，CubeAPI 可访问
- 已创建沙箱模板
- OpenAI 兼容 LLM API Key

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入 API Key、CubeAPI 地址、模板 ID、mkcert 证书路径

# 仅测沙箱（无需 LLM）
python e2b_demo.py --sandbox-only

# 完整 Agent
python e2b_demo.py
python e2b_demo.py --model deepseek-chat --question "What Linux distro is this?"
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | LLM API Key |
| `OPENAI_BASE_URL` | LLM 地址（如 DeepSeek） |
| `E2B_API_URL` | CubeAPI 地址 |
| `E2B_API_KEY` | CubeAPI 鉴权 Key |
| `CUBE_TEMPLATE_ID` | 沙箱模板 ID |
| `CUBE_SSL_CERT_FILE` | E2B 数据面 HTTPS 所需 mkcert 根证书 |

## 文件说明

| 文件 | 说明 |
|------|------|
| `e2b_demo.py` | 入口脚本 |
| `demo_common.py` | Agent / 沙箱连通性测试 |
| `cube_patches.py` | envd 兼容补丁（root 用户、stdin） |
| `env_utils.py` | 加载 `.env`、校验环境变量 |
| `llm_utils.py` | 构建 OpenAI 兼容 LLM 客户端 |

## CubeSandbox 适配

`cube_patches.py` 在导入 E2B SDK 前应用：

| 补丁 | 原因 |
|------|------|
| `default_username = "root"` | Cube envd 只支持 root |
| 移除 `stdin` 参数 | 旧版 envd 不支持 |
| `workdir = "/root"` | Cube 镜像以 root 为主 |
| `CUBE_SSL_CERT_FILE` → `SSL_CERT_FILE` | E2B 数据面 HTTPS 信任 mkcert CA（同 openai-agents-example） |

LLM 客户端使用 certifi 公网 CA + `trust_env=False`，避免 `SSL_CERT_FILE` 污染 DeepSeek 等 HTTPS 请求。

`CUBE_SSL_CERT_FILE` 须指向 **mkcert 根证书**，不要用 `cube-root-ca.crt`。

## 核心代码

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

## 相关文档

- [LangGraph 文档](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents 沙箱文档](https://docs.langchain.com/oss/python/deepagents/sandboxes)
- [OpenAI Agents 集成示例](../openai-agents-example/README_zh.md)
