# Codex review — alternative GenAI provider fallback

`openai/codex-action@v1` (wired in PR 10.7) requires `OPENAI_API_KEY`.
This document records the investigation into alternative providers
(Zhipu BigModel GLM, Ollama Cloud) that could serve as a fallback when
that secret isn't set or the OpenAI billing is paused.

## TL;DR

| Provider | Responses API endpoint exists? | Auth tested | Verdict |
|---|---|---|---|
| OpenAI | yes (`https://api.openai.com/v1/responses`) | n/a (primary) | use as primary |
| Zhipu BigModel GLM | **yes** — `https://open.bigmodel.cn/api/paas/v4/responses` returns 401 on unauthenticated probe (endpoint reachable, not 404) | failed with the operator-supplied key | needs working credentials before we can wire |
| Ollama Cloud | unverified | not tested (key shape would differ) | future investigation |

## Endpoint shape

### Zhipu BigModel

- Chat completions: `POST https://open.bigmodel.cn/api/paas/v4/chat/completions`
- Responses API: `POST https://open.bigmodel.cn/api/paas/v4/responses`
- Auth header: `Authorization: Bearer <api-key>` (per Zhipu v4 docs; older versions used JWT signing of the key — confirm before automating)
- Default model name: `glm-4.6`
- Endpoint `/v4/responses` **was reachable** in May 2026 testing — it returned a structured 401 to an unauthenticated POST, which means it routes the request (not a 404 missing-route). This is a strong signal that the Responses API spec is honored at Zhipu's side.

### Ollama Cloud

Per `docs.ollama.com/api/openai-compatibility`:
- Chat completions: `POST https://ollama.com/v1/chat/completions`
- Responses API: claimed by docs but **not yet tested in this codebase**.
- Auth header: `Authorization: Bearer <api-key>` (standard).
- Model name: provider-prefixed (e.g. `gpt-oss:120b`).

## Why this slice didn't wire up the workflow yet

The operator-supplied Zhipu key returned 401 against both `/v4/chat/completions` and `/v4/responses`. The Zhipu API's default 401 message is the same as for an *unauthenticated* request, so we can't distinguish "wrong key" from "expired key" from the response alone.

To unblock:

1. Operator confirms the Zhipu key is currently active (check Zhipu BigModel dashboard for the key's status / quota / expiry).
2. If it's a different auth shape (JWT-signed), operator regenerates a v4-compatible API key.
3. Operator stores it as the `ZHIPU_API_KEY` secret in repo Settings → Secrets and variables → Actions. (Or `GENAI_API_KEY` if we go provider-generic.)
4. Re-run this investigation against the working key; if `/v4/responses` accepts the same payload shape Codex CLI emits, we wire the codex-action endpoint override.

## Proposed wiring (when credentials are validated)

### Path A — codex-action `responses-api-endpoint` override

If Codex CLI emits Responses-API-spec payloads that Zhipu accepts:

```yaml
- name: Run Codex (Zhipu fallback)
  uses: openai/codex-action@v1
  with:
    openai-api-key: ${{ secrets.ZHIPU_API_KEY }}
    responses-api-endpoint: https://open.bigmodel.cn/api/paas/v4/responses
    model: glm-4.6
    sandbox: read-only
    prompt: ...  # same prompt as the OpenAI path
```

Same verdict-enforcement step from `.github/workflows/codex-review.yml` reused.

### Path B — separate fallback workflow using chat completions

If Zhipu's `/v4/responses` doesn't honor the Codex CLI's payload shape:

```yaml
- name: Zhipu chat-completions review
  run: |
    DIFF=$(git diff origin/${{ github.event.pull_request.base.ref }}...HEAD)
    PROMPT=$(printf 'Review this diff per the team conventions (verdict line first, P0/P1 block, etc.):\n\n%s' "$DIFF")
    curl -fsS -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
      -H "Authorization: Bearer ${{ secrets.ZHIPU_API_KEY }}" \
      -H "Content-Type: application/json" \
      -d "$(jq -n --arg p "$PROMPT" '{model:"glm-4.6",messages:[{role:"user",content:$p}],max_tokens:4096}')" \
      | jq -r '.choices[0].message.content' > /tmp/codex-output.txt
    echo "CODEX_FINAL_MESSAGE<<EOF" >> "$GITHUB_OUTPUT"
    cat /tmp/codex-output.txt >> "$GITHUB_OUTPUT"
    echo "EOF" >> "$GITHUB_OUTPUT"
```

Then reuse the verdict-enforcement bash from 10.7 + the post_feedback job.

## Operator action required

1. Verify the Zhipu key's status at the BigModel console.
2. Either rotate the key or share an Ollama Cloud key as an alternative.
3. Set the secret in the GitHub repo (`ZHIPU_API_KEY` or `OLLAMA_API_KEY` or `GENAI_API_KEY`).
4. Re-run the investigation against the working credentials so we know which path (A or B) the implementation goes down.

Until then, `codex-action` falls back to its no-op precondition skip when `OPENAI_API_KEY` is unset, and PR review continues to run locally via the `openai/codex-plugin-cc` plugin per `CLAUDE.md`.
