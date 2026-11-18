---
schema_version: 1
open_count: 2
waived_count: 0
fixed_count: 0
total_count: 2
last_updated: 2026-11-18T10:07:56.750Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 1 | unmet-truth | apps/core/views.py | 33 | healthz-503-branch-implemented-but-not-covered-by-automated-test-dependency-down-scenario | open |  | 2026-11-18T09:15:03.961Z |  |
| 2 | 1 | unrun-verify | .github/workflows/ci.yml |  | first-CI-run-on-GitHub-Actions-pending-first-branch-push-green-pipeline-to-be-confirmed-at-gsd-verify-work | open |  | 2026-11-18T10:07:56.750Z |  |

````json
[
  {
    "id": 1,
    "kind": "unmet-truth",
    "phase": "1",
    "file": "apps/core/views.py",
    "line": 33,
    "description": "healthz-503-branch-implemented-but-not-covered-by-automated-test-dependency-down-scenario",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-11-18T09:15:03.961Z",
    "resolved_at": null,
    "milestone": null
  },
  {
    "id": 2,
    "kind": "unrun-verify",
    "phase": "1",
    "file": ".github/workflows/ci.yml",
    "line": null,
    "description": "first-CI-run-on-GitHub-Actions-pending-first-branch-push-green-pipeline-to-be-confirmed-at-gsd-verify-work",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-11-18T10:07:56.750Z",
    "resolved_at": null,
    "milestone": null
  }
]
````
