# Plan

This file is the single source of truth for scope and progress. Each unchecked item is one meaningful piece of work and one proposed commit. No commit, push, or paid API call happens without the required user authorization.

## Goal

Investigate ChatGPT/Codex subscription OAuth for embeddings and the GPT-6 Luna Decisions API, including user-authorized unofficial compatibility experiments. Record reproducible results and distinguish observed compatibility from documented support.

## Decisions

| Topic | Decision |
| --- | --- |
| Codex OAuth scope | OpenAI documents using ChatGPT OAuth with Codex app-server for the Responses API. The embeddings guide documents `/v1/embeddings`; it does not document ChatGPT OAuth for that endpoint. The user authorized low-volume unofficial experiments using the existing LangChain OAuth provider and an inherited client. Record endpoint-specific authentication results without exposing credentials |
| OpenAI embedding candidate | Use the current official embeddings guide to select the documented model at implementation time; the guide currently identifies `text-embedding-3-large` as the most capable and `text-embedding-3-small` as the smaller option |
| API billing | ChatGPT and API billing are separate. Keep API-backed runs disabled until an API credential and spending limit are explicitly provided |
| Local baseline | Include a local multilingual embedding model so the pilot can run without API credentials |
| Python and layout | Python 3.13; shared gateway in `pilot_kit/`, cases in `case01_*` and `case02_*`, tests in `tests/`, experiments in `notebooks/` |
| Documentation | English first, then Korean, Japanese, Simplified Chinese |

## Verification strategy

| Tier | What | Needs keys |
| --- | --- | --- |
| 1. Unit | Protocol, normalization, dimensions, batching, and retrieval metrics with fakes | no |
| 2. Script | Local embedding and retrieval smoke run; official OpenAI API smoke run only when separately authorized | API run only |
| 3. Notebook | Small Korean, English, and Japanese retrieval set; repeat queries, report top-k accuracy, latency, dimensions, and cost where applicable | API run only |

## Checklist

### Feasibility

- [x] Inspect repository and official docs: Codex OAuth is documented for app-server Responses inference; embeddings use `/v1/embeddings`; docs do not describe OAuth embeddings; billing is separate | `📄 docs(plan): record documented OAuth boundaries`
- [x] Run one low-volume OAuth compatibility probe using LangChain's refresh-aware token provider and an inherited OpenAI client; embeddings returned successfully without an API key | `✅ test(embeddings): record OAuth compatibility result`
- [x] Probe `POST /v1/decisions` once with `gpt-6-luna`; OAuth request returned HTTP 401 | `✅ test(decisions): record OAuth rejection result`
- [x] Upgrade OpenAI Python SDK to 3.26.0, confirm typed `client.decisions.create`, and retry once; OAuth still returned HTTP 401 | `⬆️ dep(openai): require SDK 3.26.0 for Decisions API`
- [x] Inspect SDK authentication and exception source, research firsthand reports, and repeat OAuth probes with normalized error handling and Codex headers | `📄 docs(auth): record Decisions authentication findings`

### Foundation and implementation

- [ ] Define a typed embedding gateway protocol and provider configuration, with experimental OAuth embeddings isolated behind explicit configuration and documented limitations | `✨ feat(embeddings): add provider gateway`
- [ ] Add offline unit tests for output shape, dimensions, batching, and failure handling | `✅ test(embeddings): cover provider gateway`
- [ ] Add a local multilingual embedding baseline with a small reproducible model and documented install/run steps | `✨ feat(local): add multilingual embedding baseline`
- [ ] Add an official OpenAI API provider for documented embedding models, disabled unless a separate API key is configured | `✨ feat(openai): add embeddings API provider`
- [ ] Add a retrieval case with a tiny fixed Korean, English, and Japanese dataset and hand-labeled expected matches | `✨ feat(retrieval): add multilingual retrieval case`
- [ ] Add a doctor check that reports provider readiness without printing secrets | `✨ feat(doctor): check embedding provider readiness`

### Verification and findings

- [ ] Run offline tests with fakes and the local model smoke check | `✅ test(embeddings): verify offline providers`
- [ ] If an API key and spend cap are explicitly approved, run the smallest live request against the current documented model; capture model ID, dimensions, latency, errors, and estimated charge without logging secrets | no commit
- [ ] Execute and repeat the retrieval notebook; report top-k accuracy and latency, separating local and API-backed results | `✅ test(notebooks): record retrieval results`
- [ ] Review conclusions against official docs and label unsupported or unverified claims | `📄 docs(plan): summarize embedding feasibility`

### Documentation and quality

- [x] Add native OpenAI Decisions API authentication guidance to all README locales | `📄 docs(readme): clarify Decisions API access`
- [ ] Update the English goal, README, and provider guide with the verified boundary and setup | `📄 docs(en): explain embedding providers`
- [ ] Translate changed sections into Korean, Japanese, and Simplified Chinese | `📄 docs(i18n): translate embedding provider guidance`
- [ ] Run ruff, format check, ty, pytest, notebook checks, Mermaid checks, and secret scan | `✅ test(quality): pass pilot quality gates`

## Initial finding: 2026-10-08

The repository's current Codex OAuth integration uses an experimental private LangChain chat class and a ChatGPT Codex backend. OpenAI documents a supported ChatGPT OAuth integration through Codex app-server for the Responses API. The embeddings guide documents `/v1/embeddings` examples using API-key authentication and does not document ChatGPT OAuth for that endpoint. OpenAI states API billing is separate from ChatGPT subscriptions. Documentation links and current model and SDK guidance were rechecked on 2026-10-10. A one-shot experiment used LangChain's `_FileChatGPTOAuthTokenProvider` through a subclassed OpenAI client, without supplying an API key or printing the token. `text-embedding-3-large` returned successfully with 3072 dimensions and 7 prompt tokens. This proves that the tested request worked at that time; it does not establish that the path is officially supported, that future calls will work, or which usage and billing bucket was charged. A second one-shot probe to `POST /v1/decisions` with `gpt-6-luna` returned HTTP 401 using the same OAuth provider. The first Decisions probe used OpenAI SDK 3.16.2, which lacked the typed `decisions` resource. The project dependency and lockfile are now upgraded to 3.26.0, where `client.decisions.create` is available; a retry through that typed method also returned HTTP 401. No retries were made within either request. The original probe did not retain the error message correctly. The diagnostic follow-up below records the server rejection and rules out missing bearer and Codex account headers for the tested requests. Do not infer that the successful embeddings request implies other endpoints accept the same OAuth token. Do not use either path for production until support, usage accounting, and terms are verified. See [Codex app-server](https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server), [embeddings](https://developers.openai.com/api/docs/guides/embeddings), [Decisions](https://developers.openai.com/api/docs/guides/decisions), and [billing](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform).


## Authentication diagnosis: 2026-10-08

Three additional low-volume requests used OpenAI Python 3.26.0, the existing LangChain token provider, inherited OpenAI clients, a 20-second timeout, and zero SDK retries. Token values and account identifiers were not printed.

| Probe | Observed result |
| --- | --- |
| `/v1/embeddings`, `text-embedding-3-large` | Success, 3072 dimensions, 5 input tokens |
| `/v1/decisions`, `gpt-6-luna`, OAuth bearer | HTTP 401, `invalid_request_error`, `A valid API key is required.` |
| `/v1/decisions`, same payload, OAuth bearer plus headers obtained from the authenticated LangChain Codex chat client | Same HTTP 401 and message; Authorization, ChatGPT-Account-Id, and originator headers were present |

SDK source findings:

- Both typed resource methods declare `security={"bearer_auth": True}`. The OpenAI client resolves the callable API credential before building the bearer header. Decisions has no additional beta authentication header in the installed resource implementation.
- The SDK unwraps a top-level `error` object before assigning exception `body`, `code`, and `type`. The earlier probe unwrapped `body` again with an empty default, losing diagnostic fields. The follow-up reads the normalized fields directly.
- LangChain refreshes expired access tokens and adds account and originator headers for Codex chat. Reusing those headers did not change the Decisions result.

The strongest inference is that the public Decisions route rejects this OAuth credential type. The same provider succeeded on embeddings during the same diagnostic run. The evidence does not establish a universal restriction for every OAuth flow or account, nor reveal the server implementation. No working direct Decisions OAuth method was found in the researched sources.

Relevant firsthand reports and documentation:

- [OpenClaw embeddings report](https://github.com/openclaw/openclaw/issues/111985): OAuth reached the embeddings endpoint and returned 429 insufficient_quota; historical successful embeddings were reported. This supports account-specific compatibility and accounting uncertainty.
- [OAuth bridge matrix](https://github.com/sueun-dev/chatgpt-oauth-bridge): reports direct OAuth embeddings success and direct TTS 401, demonstrating endpoint-specific results. Its June 2026 matrix does not establish Decisions support.
- [OpenClaw Responses routing report](https://github.com/openclaw/openclaw/issues/38706): the reporter resolved a Responses 401 by selecting the Codex backend and reported that adding a Platform API scope broke login. This is evidence for a Responses routing issue, not a Decisions fix.
- [Codex custom-provider report](https://github.com/openai/codex/issues/19743): a 401 missing-scope error stopped after removing a custom public API provider configuration.
- [Decisions guide](https://developers.openai.com/api/docs/guides/decisions): identifies the dedicated public endpoint and minimum Python SDK 3.26.0.

Future experiments should preserve normalized error fields and distinguish the native Decisions API from a decision implemented through structured Responses output. A successful structured-output call would not validate the native Decisions endpoint or its probability outputs.
