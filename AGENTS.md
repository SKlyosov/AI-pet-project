# AGENTS.md

Greenfield product repo: private classifieds web service (RU-language). Planning artifacts live in `.planning/` (GSD: PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md, config.json, research/) — initialized 2026-11-18 on branch `chore/gsd-init`. No source, manifests, or CI yet; OpenCode agent config lives in `.opencode/`. `README.md` is a one-line placeholder — project context lives in `.planning/PROJECT.md`.

## Ground rules

- **Stack is deliberately undecided.** Do not assume a language, framework, or scaffold one without being asked. Roadmap Phase 1 is an explicit ADR user gate — the user picks from variants A/B/C in `.planning/research/STACK.md`.
- **No direct commits to `main`.** Work happens on `feat/<name>`, `fix/<name>`, or `chore/<name>` branches; commit messages follow Conventional Commits. Enforced by `.opencode/rules/git-main-protection.md`.
- There is nothing to build, test, or lint yet. Don't invent commands — when real tooling lands, record its exact usage here.

## Planning workflow (GSD)

- `.planning/ROADMAP.md` holds 10 phases; `.planning/STATE.md` tracks the current position.
- Phase lifecycle: `/gsd-discuss-phase <N>` (optional) → `/gsd-plan-phase <N>` → `/gsd-execute-phase <N>`; `/gsd-progress` shows status.
- Planning docs are committed to git (`commit_docs: true`); config in `.planning/config.json` (yolo, fine granularity, parallel execution, inherit models).

## Keeping this file useful

- Update this file the same commit that adds tooling, structure, or conventions. Verified facts only; omit anything you can't check.
