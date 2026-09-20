# 시작하기

## 템플릿 사용

```bash
gh repo create jyje/pilot-<topic> --template jyje/template-pilot-python --public --clone
cd pilot-<topic>
python3 scripts/init_pilot.py pilot-<topic> --description "무엇을 다루는지"
```

`init_pilot.py`는 템플릿 이름을 전부 바꾸고, 패키지 설명과 모든 언어 README의 태그라인을 설정하고,
"Use this template" 블록을 지운 뒤 스스로 삭제합니다. 그다음 커밋합니다: `🎉 init: set up pilot-<topic>`.

## 준비물

- [uv](https://docs.astral.sh/uv/) (Python 3.13은 uv가 설치해 줍니다)
- 채팅 모델 백엔드 하나: (1) ChatGPT 구독, 또는 (2) https://build.nvidia.com 에서 받은 NVIDIA 키

## 설정

```bash
cp .env.sample .env      # NIM을 쓰면 NVIDIA_API_KEY 입력
cd src
uv sync

# ChatGPT 공급자만, 한 번:
uv run python -m pilot_kit.chatgpt_login
```

`.env`는 저장소 루트에 있고 gitignore 대상입니다. `.env.sample`은 플레이스홀더로 형식만 보여 줍니다.

## 점검

```bash
uv run python doctor.py                    # 환경과 채팅 모델 실호출
uv run python -m case01_hello.main         # 예시 그래프
uv run pytest                              # 오프라인 테스트, 키 불필요
uv run ruff check --fix . && uv run ruff format . && uv run ty check .
```

`.env`를 고치지 않고 명령마다 공급자를 바꿀 수 있습니다.

```bash
LLM_PROVIDER=nim uv run python -m case01_hello.main
LLM_PROVIDER=openai LLM_MODEL=<계정에서 쓸 수 있는 모델> uv run python -m case01_hello.main
```

## 선택 extra

```bash
uv sync --extra deepagents     # LangChain Deep Agents
uv sync --extra notebook       # Jupyter, 노트북 실행용
uv sync --extra studio         # LangGraph Studio: uv run langgraph dev --no-browser
```

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `Not signed in to ChatGPT` | `uv run python -m pilot_kit.chatgpt_login`을 한 번 실행 |
| ChatGPT의 `usage_limit_reached` (HTTP 429) | 요금제 사용량 소진. `LLM_PROVIDER=nim`으로 바꾸거나 다른 모델 시도 |
| `model is not supported when using Codex with a ChatGPT account` | `python -m pilot_kit.chatgpt_models`에 나온 모델을 선택 |
| NIM의 `410 Gone` | 모델이 수명 종료. `LLM_MODEL`로 다른 모델 선택 |
| NIM의 `403 Forbidden` | 키로 추론을 실행할 수 없음. build.nvidia.com에서 새 키 발급 |
| `ReadTimeout` 또는 `SocketTimeoutError` | 호스티드 지연. `LLM_TIMEOUT`을 올리기(예: 600) |
| 응답이 `Here's a thinking process`로 시작 | `LLM_ENABLE_THINKING=false` 설정 |
