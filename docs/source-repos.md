# Source repositories

Tracking external sources studied to extract reusable AI-coding-agent practices for SignUpFlow.

## How to use this file

- Add a row when a new source is introduced.
- Set `Status = extracted` only after observations are recorded in `research-log.md`.
- Set `Status = promoted` once at least one practice was promoted into `AGENTS.md`, `CLAUDE.md`, or a Copilot instruction file.
- Do not delete rows. If a source is rejected, mark `Status = rejected` and keep the row.

## Sources

| Source | Type | Status | Used for | URL |
|---|---|---|---|---|
| tomqwu/GenAI_Common | Repo | promoted | Cross-agent file layout (`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md`), house style, validation checklist, anti-hallucination rules, PR/commit format, instruction hierarchy, research-log workflow | https://github.com/tomqwu/GenAI_Common |

## Adding a new source

1. Append a row above with `Status = pending`.
2. Open `docs/research-log.md` and add a section under **Observations** with date, source name, and 3-6 bullet observations.
3. Decide which observations are stable enough to promote.
4. Promote into `AGENTS.md`, `CLAUDE.md`, or a Copilot instruction file as appropriate.
5. Update `Status` here to `extracted` then `promoted`.
6. If the rule applies to other repos, open it upstream in `tomqwu/GenAI_Common`.
