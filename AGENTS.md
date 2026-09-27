# AGENTS.md

Rules for every coding agent in this repo: **Codex** (implementer), **Droid + Gemini** (reviewer), **Claude Code** (reads this via `CLAUDE.md`), and any other tool or human developer.
Read the whole file before starting. The *This repo* section comes first because it holds the facts you need most: base branch, checks, and what must never be touched.

## This repo: sunagawa-heiwa-archive.github.io

A static archive preserving 208 public articles about the Sunagawa peace movement (砂川平和ひろば公開記事アーカイブ), served by GitHub Pages at sunagawa-heiwa-archive.github.io.

- **Base branch:** `main` on `origin` = `sunagawa-heiwa-archive/sunagawa-heiwa-archive.github.io` (the organization repo that GitHub Pages serves).
- **Tera's fork:** remote `fork` = `terazadl/sunagawa-heiwa-archive.github.io`. Branch from `origin/main`, push the branch to `fork`, open the PR into `origin` `main`. Merging to `origin/main` publishes the site.
- **Stack:** hand-written static HTML/CSS/JS. No build step, no package manager.

### Checks (run before every PR)

```bash
python3 scripts/check_links.py        # internal links and images must resolve
python3 -m http.server 8000           # then open the pages you changed, at 375px and desktop
```

### Archive rules — this is a preservation record, not a rewrite

- **Never change archived article content**: body text, titles, dates, author attribution, or images. Changes to `articles/` are limited to site chrome (navigation, metadata, accessibility, layout) and must leave the archived text byte-identical.
- **`raw/` is the original capture. Never modify it.**
- Editorial restraint is deliberate: do not add commentary, summaries, or "corrections" to archived material.
- Site UI and editorial text are bilingual Japanese / English; keep both in sync.
- **Zero external scripts, fonts, trackers, or analytics.** Everything is self-hosted.

### Bulk edits across `articles/`

Bulk changes are done by a script in `scripts/`, never by hand-editing 208 files.

- The script must be **idempotent**: running it a second time changes nothing. Prove it: run it twice and show that the second run leaves `git diff --stat` unchanged.
- Commit the script in the same PR as its output.
- Show in the PR that no article body text changed (e.g. diff one article before/after and explain the change is chrome-only).

---

# General rules (all of Tera's repos)

## Who does what

| Role | Who | Does | Never does |
|---|---|---|---|
| Product owner | Tera | Writes Linear issues with acceptance criteria, sets priority, does UAT, merges PRs, deploys | — |
| Implementer | Codex (or a human developer) | One Linear issue → one branch → one PR | Merge, deploy, push to protected branches |
| Reviewer | Droid running Gemini (`pr-reviewer` droid) | Reviews PRs and posts findings | Push commits, approve its own work, merge |

Stay in your role. An agent that implemented a change must not also be its reviewer.
Tera is not an engineer: explain things to her in plain language first, code second.

## 1. Before writing code

1. **There must be a written task with acceptance criteria.** Normally that is a Linear issue (ID like `SITES-12`). Until Linear is set up, a task in the prompt with acceptance criteria also counts; use `TASK` in place of the issue ID. If the criteria are missing or vague, stop and propose them in plain language. Do not guess.
2. **Restate the task** in at most 5 bullets: what will change, what will not, which files you expect to touch, then wait for Tera's OK.
   *Fast lane:* a small fix (one file, about 20 lines or fewer, no logic change — e.g. a typo, a copy tweak, one CSS value) may skip the wait. It still needs the checks and a PR.
3. **Start from the latest base branch** (see *This repo*): `git fetch origin && git switch -c <type>/<ISSUE-ID>-<short-slug> origin/<base>`.

## 2. Scope rules — most bugs come from breaking these

- **One issue per PR.** No drive-by refactors, renames, reformatting, or "while I'm here" fixes. List them under *Follow-ups* in the PR instead.
- **Small diffs.** Aim for under ~300 changed lines and ~10 files. If it will be bigger, say so and propose a split first.
- **No new dependencies**, frameworks, build tools, CDNs, fonts, trackers, or external scripts without explicit approval in the issue.
- **Do not rewrite content** (articles, copy, data, numbers) unless the issue asks for it.
- **Never touch generated output or deploy branches by hand** (see *This repo*).
- **Never commit secrets**: `.env*` (except `.env.example`), tokens, API keys, `.wrangler/`, personal data.
- **Do not delete files** unless the issue says so; list any deletion explicitly in the PR.

## 3. Bugs: reproduce → failing test → fix

1. Reproduce the bug and write down the steps.
2. Add a test or check script that **fails because of this bug**.
3. Fix it and show the same test passing.

If the bug cannot be tested automatically, say why in the PR and give exact manual repro steps for UAT. A fixed bug with no test is expected to come back.

## 4. Definition of done (all required before requesting review)

- [ ] The repo checks in *This repo* pass. Paste a short summary of the output into the PR.
- [ ] New or changed behavior has a test, or a written manual check.
- [ ] UI changes checked at 375px (phone) and desktop widths.
- [ ] `git diff --stat origin/<base>` shows only files this issue needs.
- [ ] PR description follows the template, in plain language.

## 5. Commits and PRs

- Commit format: `type(scope): summary [ISSUE-ID]`. Types: `feat` `fix` `content` `style` `refactor` `test` `chore` `docs`.
- PR title: `[ISSUE-ID] short summary`. PR body starts with `Fixes ISSUE-ID` so Linear links and closes it.
- Never push directly to the base branch. Never force-push a branch someone else is using. Never merge your own PR — Tera merges after UAT.

## 6. Reporting

- Say exactly what you ran, what passed, and **what you did not verify**. Do not write "fixed" or "works" without evidence.
- When unsure, ask one specific question instead of guessing.
- Keep a short *Why this approach* (2–3 sentences, plain language) in every PR. Tera reads these to learn.
