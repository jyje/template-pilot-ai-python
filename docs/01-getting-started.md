# Getting started

## Use the template

```bash
gh repo create jyje/pilot-<topic> --template jyje/template-pilot-python --public --clone
cd pilot-<topic>
python3 scripts/init_pilot.py pilot-<topic> --description "what it studies"
```

`init_pilot.py` renames the template everywhere, sets the package description and the README tagline
in all languages, drops the "Use this template" blocks, and deletes itself. Then commit:
`🎉 init: set up pilot-<topic>`.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (it installs Python 3.13 for you)
- One chat model backend: (1) a ChatGPT subscription, or (2) an NVIDIA key from https://build.nvidia.com

## Set up

```bash
cp .env.sample .env      # add NVIDIA_API_KEY if you use NIM
cd src
uv sync

# Only for the ChatGPT provider, once:
uv run python -m pilot_kit.chatgpt_login
```

`.env` lives at the repo root and is gitignored. `.env.sample` shows the format with placeholders.

## Check it

```bash
uv run python doctor.py                    # environment and a live chat model call
uv run python -m case01_hello.main         # the example graph
uv run pytest                              # offline tests, no keys needed
uv run ruff check --fix . && uv run ruff format . && uv run ty check .
```

Switch the provider per command without editing `.env`:

```bash
LLM_PROVIDER=nim uv run python -m case01_hello.main
LLM_PROVIDER=openai LLM_MODEL=<a model your account can use> uv run python -m case01_hello.main
```

## Optional extras

```bash
uv sync --extra deepagents     # LangChain Deep Agents
uv sync --extra notebook       # Jupyter, to run and execute notebooks
uv sync --extra studio         # LangGraph Studio: uv run langgraph dev --no-browser
```

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `Not signed in to ChatGPT` | run `uv run python -m pilot_kit.chatgpt_login` once |
| `usage_limit_reached` (HTTP 429) from ChatGPT | the plan is used up. Set `LLM_PROVIDER=nim`, or try another model |
| `model is not supported when using Codex with a ChatGPT account` | pick a model from `python -m pilot_kit.chatgpt_models` |
| `410 Gone` from NIM | the model reached end of life. Pick another with `LLM_MODEL` |
| `403 Forbidden` from NIM | the key cannot run inference. Create a new key at build.nvidia.com |
| `ReadTimeout` or `SocketTimeoutError` | hosted latency. Raise `LLM_TIMEOUT` (for example 600) |
| Reply starts with `Here's a thinking process` | set `LLM_ENABLE_THINKING=false` |
