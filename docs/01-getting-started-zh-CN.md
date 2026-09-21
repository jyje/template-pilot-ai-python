# 快速开始

## 使用模板

```bash
gh repo create jyje/pilot-<topic> --template jyje/template-pilot-ai-python --public --clone
cd pilot-<topic>
python3 scripts/init_pilot.py pilot-<topic> --description "what it studies"
```

`init_pilot.py` 会在各处替换模板名称，为所有语言设置包描述和 README 标语，删除“Use this template”
区块，并删除自身。然后提交：`🎉 init: set up pilot-<topic>`。

## 前置条件

- [uv](https://docs.astral.sh/uv/)（它会为你安装 Python 3.13）
- 一个聊天模型后端：(1) ChatGPT 订阅，或 (2) 来自 https://build.nvidia.com 的 NVIDIA 密钥

## 设置

```bash
cp .env.sample .env      # 使用 NIM 时添加 NVIDIA_API_KEY
cd src
uv sync

# 仅 ChatGPT 提供方需要，只需一次：
uv run python -m pilot_kit.chatgpt_login
```

`.env` 位于仓库根目录，已被 gitignore。`.env.sample` 用占位符展示了格式。

## 检查

```bash
uv run python doctor.py                    # 环境，以及一次真实的聊天模型调用
uv run python -m case01_hello.main         # 示例图
uv run pytest                              # 离线测试，无需密钥
uv run ruff check --fix . && uv run ruff format . && uv run ty check .
```

无需编辑 `.env`，可以按命令切换提供方：

```bash
LLM_PROVIDER=nim uv run python -m case01_hello.main
LLM_PROVIDER=openai LLM_MODEL=<a model your account can use> uv run python -m case01_hello.main
```

## 可选的 extra

```bash
uv sync --extra deepagents     # LangChain Deep Agents
uv sync --extra notebook       # Jupyter，用于运行和执行 notebook
uv sync --extra studio         # LangGraph Studio: uv run langgraph dev --no-browser
```

## 故障排查

| 现象 | 原因与解决 |
| --- | --- |
| `Not signed in to ChatGPT: ...` | 运行一次 `uv run python -m pilot_kit.chatgpt_login`。消息会说明令牌文件是缺失、为空、已损坏还是不完整，此时自动选择会回退到 NIM |
| ChatGPT 返回 `usage_limit_reached`（HTTP 429） | 套餐额度已用完。设置 `LLM_PROVIDER=nim`，或换一个模型 |
| `model is not supported when using Codex with a ChatGPT account` | 从 `python -m pilot_kit.chatgpt_models` 中选择模型 |
| NIM 返回 `410 Gone` | 该模型已停止服务。用 `LLM_MODEL` 选择另一个 |
| NIM 返回 `403 Forbidden` | 该密钥无法运行推理。在 build.nvidia.com 创建新密钥 |
| `ReadTimeout` 或 `SocketTimeoutError` | 托管服务延迟较高。调大 `LLM_TIMEOUT`（例如 600） |
| 回复以 `Here's a thinking process` 开头 | 设置 `LLM_ENABLE_THINKING=false` |
