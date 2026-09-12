# Ollama PR Review

The PR reviewer uses Ollama Cloud directly. The scheduling solver remains a
local greedy heuristic; this change does not add an LLM to application routes.

## Configuration

| GitHub Actions setting | Kind | Default |
| --- | --- | --- |
| `OLLAMA_API_KEY` | Secret | Required; no fallback to an OpenAI key |
| `OLLAMA_ENDPOINT` | Repository variable | `https://ollama.com/api/chat` |
| `OLLAMA_MODEL` | Repository variable | `glm-5.3-flash` |

Set the secret using GitHub's secret UI or `gh secret set OLLAMA_API_KEY`, which
prompts for the value. Never put the key in source, a PR, chat, or a command-line
argument. Repository `.env` files do not configure GitHub-hosted runners.

Use the full native chat URL, not an OpenAI-compatible `/v1` URL. Endpoints must
use HTTPS with no embedded credentials, query, or fragment. Redirects are
rejected. Only point the endpoint at an approved provider: it receives PR
metadata and patches, and the bearer key. Model names are configurable, but
there is no automatic fallback to a different model or provider.

Ollama's [cloud API documentation](https://docs.ollama.com/cloud) describes
direct bearer-key access. Its public `/api/tags` catalog lists `glm-5.3-flash`;
the [model library](https://ollama.com/library/glm-5.3-flash) uses the separate
`:cloud` tag for requests proxied through a local Ollama installation.

## Review Behavior

- Run `.github/workflows/codex-review.yml` on PR open, push, reopen, and ready-for-review.
- Keep the stable check name `codex-pr-review-gate` for future GitHub enforcement.
- Fetch metadata and patches through GitHub's API. Never check out or execute PR code in the credential-bearing job.
- Bind results to the event's head and base SHAs; recheck before and after publishing feedback.
- Send only bounded diff context to the model. This is a diff-only reviewer, not a repository-exploring agent.
- Ask for JSON and validate it locally. Ollama Cloud currently does not support [structured output enforcement](https://docs.ollama.com/capabilities/structured-outputs), so no `format` parameter is sent.
- Post validated feedback as inert JSON text, not a GitHub approval. P0/P1 findings fail even if the model claims a safe verdict.
- Fail on missing credentials, provider errors, timeouts, incomplete output, malformed reports, stale commits, or unsuccessful feedback publication. Never silently skip review or convert an error to success.

Limit requests to 400,000 UTF-8 bytes of PR metadata/patches and 480 seconds.
Read Ollama's newline-delimited JSON stream within a 10-minute job limit.
Bound the response stream to 2,000,000 bytes and final-answer content to 30,000
characters. Discard reasoning text without logging it; require a complete stream
ending in `done: true` with `done_reason: stop` before validating the report.
Streaming allows long reasoning-model responses without waiting for a single
buffered response under the former two-minute deadline. Keep the requested
model and its default reasoning behavior; do not substitute a model to pass review.
Fail on missing patches (including binary-only changes), patch line-count
mismatches, and incomplete GitHub file listings. Split oversized PRs or obtain
independent review through the repository's approved process; do not bypass a
required check. External-fork and Dependabot PRs cannot normally access this
secret and will fail closed. Do not use a privileged fork trigger to execute
their code. A dedicated trusted-review service remains a future option.

An LLM verdict is fallible and does not prove production readiness. Keep CI,
human review where required, and GitHub mergeability as separate requirements.
Reviewer agents must never merge. Builder agents must not bypass protection.

## Request Diagnostics

Failed HTTP requests report the numeric status with fixed troubleshooting guidance.
Check the API key for 401, account/model access for 403, endpoint/model configuration
for 404, and quota/rate limits for 429. Server errors suggest checking the provider
service. These are troubleshooting hints, not a diagnosis of the provider's cause.
Network/timeout failures before a response do not report an HTTP status.
Log the HTTP status when response headers arrive. Report expiration of the
480-second request deadline separately from HTTP authentication failures.
Never log provider response bodies, status text, headers, or transport exception
messages. Correct the configuration or provider issue and rerun the failed job;
do not bypass the review gate.

## Rollout And Validation

1. Add the workflow conversion in a PR and configure the Ollama secret separately.
2. Review and merge the workflow normally, retaining existing required CI checks.
3. Confirm the check appears and exercises pass/fail paths on a PR.
4. Only then require `codex-pr-review-gate` in branch protection or rulesets.

This conversion does not change GitHub settings, auto-merge, or branch protection.
Workflow-file changes themselves require trusted review: a PR able to edit its
own workflow can alter a check's logic, so a status name alone is not a tamper-proof gate.

Run `poetry run pytest tests/unit/test_ollama_review_workflow.py` with Node.js
20+ installed. Tests execute the actual inline workflow JavaScript with mocked
GitHub/Ollama calls, including failure cases; no live AI key or inference is used.
Run `make test-unit-fast` while iterating and `make test-all` before pushing.
Verify live provider access and GitHub checks separately before claiming setup complete.
## Local Test Policy (2026-09-12)

The repository owner explicitly requested: "Yes remove CI tests from action,
local can run all the tests." This is an intentional change in assurance, not
an attempt to represent static checks as test evidence. Run `make test-all`
locally for each PR, and `make test-mobile` for mobile changes; attach results
for the pushed source revision. GitHub does not independently attest those runs.

The owner subsequently authorized updating the reviewer policy to permit this
local-only model. The workflow supplies that policy in the reviewer system
prompt, outside untrusted PR content. Absence of hosted tests alone is not a
blocking finding. Missing or weakened coverage, broken local commands, code
defects, security issues, and deceptive evidence remain reviewable. The existing
P0/P1 failure enforcement, stale-head checks, and fail-closed error handling are
unchanged. No returned verdict is overridden or converted into approval.
Record the exact pushed head SHA alongside local results before merging.

Current hosted checks are `Lint and type-check`, `Flutter analyze` (mobile paths),
and `codex-pr-review-gate`. The backend job includes a blocking
`poetry run mypy api/utils api/core api/schemas` step with no error suppression,
and a separate advisory `poetry run mypy api` step for legacy debt. It also
validates PostgreSQL migrations. None of these steps executes test suites.

Retired check names are `Lint, type-check, and test`, `End-to-end (Playwright)`,
and `Flutter analyze + test`. The pre-change main protection API returned 404
and the rulesets API returned an empty array; no protection settings were changed.
Use current names for any later administrative gate setup. Historical run reports
retain the old names as evidence, not current configuration instructions.
