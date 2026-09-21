# はじめに

## テンプレートを使う

```bash
gh repo create jyje/pilot-<topic> --template jyje/template-pilot-ai-python --public --clone
cd pilot-<topic>
python3 scripts/init_pilot.py pilot-<topic> --description "what it studies"
```

`init_pilot.py` はテンプレート名をすべて置き換え、パッケージの説明と README のタグラインを全言語で設定し、
「Use this template」のブロックを削除して、自分自身も削除します。その後コミットします:
`🎉 init: set up pilot-<topic>`。

## 前提条件

- [uv](https://docs.astral.sh/uv/)（Python 3.13 も自動でインストールされます）
- チャットモデルのバックエンドを 1 つ: (1) ChatGPT サブスクリプション、または (2) https://build.nvidia.com の NVIDIA キー

## セットアップ

```bash
cp .env.sample .env      # NIM を使う場合は NVIDIA_API_KEY を追加
cd src
uv sync

# ChatGPT プロバイダを使う場合のみ、一度だけ:
uv run python -m pilot_kit.chatgpt_login
```

`.env` はリポジトリのルートに置き、gitignore 対象です。`.env.sample` にはプレースホルダ付きの形式が載っています。

## 確認する

```bash
uv run python doctor.py                    # 環境と、実際のチャットモデル呼び出し
uv run python -m case01_hello.main         # サンプルのグラフ
uv run pytest                              # オフラインテスト、キー不要
uv run ruff check --fix . && uv run ruff format . && uv run ty check .
```

`.env` を編集せず、コマンドごとにプロバイダを切り替えられます:

```bash
LLM_PROVIDER=nim uv run python -m case01_hello.main
LLM_PROVIDER=openai LLM_MODEL=<a model your account can use> uv run python -m case01_hello.main
```

## オプションの extra

```bash
uv sync --extra deepagents     # LangChain Deep Agents
uv sync --extra notebook       # Jupyter、ノートブックの実行用
uv sync --extra studio         # LangGraph Studio: uv run langgraph dev --no-browser
```

## トラブルシューティング

| 症状 | 原因と対処 |
| --- | --- |
| `Not signed in to ChatGPT: ...` | `uv run python -m pilot_kit.chatgpt_login` を一度実行します。メッセージがトークンファイルの欠落、空、破損、不完全のどれかを示し、自動選択はそのとき NIM に切り替わります |
| ChatGPT から `usage_limit_reached`（HTTP 429） | プランの上限に達しています。`LLM_PROVIDER=nim` にするか、別のモデルを試します |
| `model is not supported when using Codex with a ChatGPT account` | `python -m pilot_kit.chatgpt_models` に出るモデルを選びます |
| NIM から `410 Gone` | モデルがサポート終了です。`LLM_MODEL` で別のモデルを選びます |
| NIM から `403 Forbidden` | そのキーでは推論を実行できません。build.nvidia.com で新しいキーを作ります |
| `ReadTimeout` または `SocketTimeoutError` | ホスト側のレイテンシです。`LLM_TIMEOUT` を上げます（例: 600） |
| 返信が `Here's a thinking process` で始まる | `LLM_ENABLE_THINKING=false` を設定します |
