# AGENTS.md

Greenfield repo: one bootstrap commit, tracking `origin/main`. No source, manifests, or CI yet; OpenCode agent config lives in `.opencode/` (verified 2026-11-16). `README.md` is a one-line placeholder — there is no project documentation to rely on.

## Ground rules

- **Stack is deliberately undecided.** Do not assume a language, framework, or scaffold one without being asked.
- **No direct commits to `main`.** Work happens on `feat/<name>`, `fix/<name>`, or `chore/<name>` branches; commit messages follow Conventional Commits. Enforced by `.opencode/rules/git-main-protection.md`.
- There is nothing to build, test, or lint. Don't invent commands — when real tooling lands, record its exact usage here.

## Keeping this file useful

- Update this file the same commit that adds tooling, structure, or conventions. Verified facts only; omit anything you can't check.
