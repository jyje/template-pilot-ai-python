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
- [ ] Run one low-volume OAuth compatibility probe using LangChain's refresh-aware token provider and an inherited OpenAI client; embeddings returned successfully without an API key | `✅ test(embeddings): record OAuth compatibility result`
- [ ] Probe `POST /v1/decisions` once with `gpt-6-luna`; OAuth request returned HTTP 401 | `✅ test(decisions): record OAuth rejection result`
- [ ] Upgrade OpenAI Python SDK to 3.26.0, confirm typed `client.decisions.create`, and retry once; OAuth still returned HTTP 401 | `⬆️ dep(openai): require SDK 3.26.0 for Decisions API`
- [ ] Inspect SDK authentication and exception source, research firsthand reports, and repeat OAuth probes with normalized error handling and Codex headers | `📄 docs(auth): record Decisions authentication findings`

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

- [ ] Update the English goal, README, and provider guide with the verified boundary and setup | `📄 docs(en): explain embedding providers`
- [ ] Translate changed sections into Korean, Japanese, and Simplified Chinese | `📄 docs(i18n): translate embedding provider guidance`
- [ ] Run ruff, format check, ty, pytest, notebook checks, Mermaid checks, and secret scan | `✅ test(quality): pass pilot quality gates`

## Initial finding: 2026-10-08

The repository uses an experimental private LangChain chat class with a ChatGPT Codex backend. OpenAI documents ChatGPT OAuth through Codex app-server for Responses inference. The embeddings guide documents `/v1/embeddings` but does not document ChatGPT OAuth for that endpoint. OpenAI states API billing is separate from ChatGPT subscriptions. Documentation links and model and SDK guidance were rechecked on 2026-10-10. Do not treat undocumented OAuth compatibility as supported or production-ready. See [Codex app-server](https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server), [embeddings](https://developers.openai.com/api/docs/guides/embeddings), [Decisions](https://developers.openai.com/api/docs/guides/decisions), and [billing](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform).
