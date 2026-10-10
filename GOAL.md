# GOAL

## Initial prompt

"Please experiment in the jyje pilot template project. I want to use the latest embedding model with an authentication token from my OpenAI Codex subscription. Make a plan."

## Requirements

| # | Requirement | Answer |
| --- | --- | --- |
| 1 | Subject | Whether Codex subscription OAuth works with embeddings and the Decisions API, and which supported alternatives are available |
| 2 | Purpose | Record reproducible, endpoint-specific compatibility evidence and compare supported API and local alternatives for multilingual retrieval |
| 3 | Official docs | [Embeddings](https://developers.openai.com/api/docs/guides/embeddings); [Decisions](https://developers.openai.com/api/docs/guides/decisions); [Codex app-server](https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server); [billing](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform) |
| 4 | Vendor skill | None required for the initial feasibility study |
| 5 | Cases | Case 01: auth and provider feasibility. Case 02: multilingual retrieval comparison |
| 6 | Providers | Keep Codex OAuth scoped to the existing chat integration. Compare an official OpenAI API embedding provider if separately authorized and a local embedding model |
| 7 | Python | 3.13 |
| 8 | References | Existing `pilot_kit` Codex chat integration and official OpenAI API documentation |
| 9 | Logo | Existing template logo |
| 10 | Languages | English, Korean, Japanese, Simplified Chinese |
| 11 | Verification | Offline fakes first; live calls only through documented APIs and with approved credentials; repeated small retrieval experiments |
| 12 | Secrets | Never inspect or copy `~/.codex/auth.json`; do not read token values; keep any explicitly supplied API key in ignored `.env` |

## What it is not

This is a feasibility pilot, not a production embedding service or a way to bypass API billing, Codex usage limits, or undocumented endpoint restrictions. Any unofficial compatibility experiment is bounded and reported as endpoint-specific; it does not make that authentication path supported or suitable for production. The pilot will not reverse engineer private Codex endpoints.
