Fixes ISSUE-ID

<!-- For a Linear issue, replace ISSUE-ID with its actual key. For Tera-requested governance-document-only maintenance allowed by AGENTS.md §1, replace this whole line with `TASK — short summary`. Do not invent an issue key. -->

## What changed (plain language, 2–3 sentences)

## Why this approach (2–3 sentences, so Tera can learn from it)

## How it was verified

- [ ] Repo checks (see AGENTS.md → *This repo*) — paste the result summary:
- [ ] Test added or updated, or exact manual checks described below
- [ ] If UI changed, checked at 375px (phone) and desktop; otherwise mark N/A for a docs/non-UI change
- [ ] `git diff --stat` contains only files this issue or governance task needs

**Not verified:** <!-- be honest: what you could not run or check -->

## Tests changed

- [ ] No existing test was deleted, skipped, or loosened
- If any test file changed, list each change and why:

## Safety check

- [ ] No secrets, `.env` values, tokens, or personal data in the diff or PR text
- [ ] New dependencies, external scripts, or network calls: none — or list exact name, version, source, and reason
- [ ] Protected files were named in the issue or in Tera's explicit governance-only request

## What could break (plain language)

<!-- Name affected pages, flows, or data so Tera can re-check them during UAT. -->

## Review

- [ ] `pr-reviewer` ran with Gemini and posted its full verdict in this PR's comments
- Verdict: `Ready for UAT` / `Needs changes` / `Too big — split it`
- [ ] No unresolved P0/P1 findings
- If review could not run, explain why; stop before UAT until Tera runs it.

## UAT steps for Tera

1. Describe the focused checks Tera should perform.
2. For UI changes, include phone (375px) and desktop checks; for docs-only/non-UI changes, state why those checks are N/A.

Expected result:

## Follow-ups (noticed but deliberately not done in this PR)

-
