<!-- Replace `ISSUE-ID` with the actual Linear issue key. Do not start work without an issue whose Description contains acceptance criteria. -->
Fixes ISSUE-ID

## What changed (plain language, 2–3 sentences)

## Why this approach (2–3 sentences, so Tera can learn from it)

## How it was verified

- [ ] Repo checks (see AGENTS.md → *This repo*) — paste the result summary:
- [ ] Test added or updated, or exact manual checks described below
- [ ] Checked at 375px (phone) and desktop, if UI changed
- [ ] `git diff --stat` contains only files this issue needs

**Not verified:** <!-- be honest: what you could not run or check -->

## Tests changed

- [ ] No existing test was deleted, skipped, or loosened
- If any test file changed, list each change and why:

## Safety check

- [ ] No secrets, `.env` values, tokens, or personal data in the diff or PR text
- [ ] New dependencies, external scripts, or network calls: none — or list exact name, version, source, and reason
- [ ] Protected files were changed only when named in the issue

## What could break (plain language)

<!-- Name affected pages, flows, or data so Tera can re-check them during UAT. -->

## Review

- [ ] `pr-reviewer` ran with Gemini and posted its full verdict in this PR's comments
- Verdict: `Ready for UAT` / `Needs changes` / `Too big`
- [ ] No unresolved P0/P1 findings
- If review could not run, explain why; stop before UAT until Tera runs it.

## UAT steps for Tera

1. Phone:
2. Desktop:

Expected result:

## Follow-ups (noticed but deliberately not done in this PR)

-
