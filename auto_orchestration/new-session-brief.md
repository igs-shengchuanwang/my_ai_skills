# agent-task-runner — New Session Brief

Paste this into a new Claude Code session inside the `agent-task-runner` repo.

---

## Context

**Repo**: `agent-task-runner`

**Goal**: Build a lightweight local orchestrator that:
- Takes tasks from a manual `tasks.yaml`
- Spawns Claude Code agents per task in isolated git worktrees
- Tracks progress and reports back to the developer

## My Situation

- Projects include **Cocos Creator game dev**
- Task source is **manual** (no Redmine API access via personal account)
- Main pain: **e2e gameplay testing** still needs human judgment, but want to reduce the human surface
- Not using GitHub PR/CI flow as the primary workflow

## What We've Already Researched

- Surveyed **ComposioHQ/agent-orchestrator** — GitHub-PR-centric, v0.1.0 unstable, not a good fit for this stack
- Studied **APM (Agentic Project Management)** — Planner/Manager/Worker pattern, agent-agnostic
- Identified open standards: **AGENTS.md**, **SKILL.md**, **MCP**
- Reference files in `my_ai_skills/auto_orchestration/`:
  - `AI自主工作流程指引.md` — full methodology (APM, cross-device, cross-tool)
  - `AGENTS.md` — generic project guide template

## Architecture Direction

```
tasks.yaml  (manual input by developer)
    │
    ▼
Task Runner (core script)
  - reads tasks
  - creates git worktree per task
  - spawns Claude Code agent
  - collects progress + output
    │
    ├──► Agent 1 (Project A · Task T001)
    ├──► Agent 2 (Project A · Task T002)
    └──► Agent 3 (Project B · Task T003)
            │
            ▼
    progress.log + summary.md
            │
            ▼
        Developer Review
```

## First Task for This Session

1. Write fresh `README.md` for `agent-task-runner` (build-focused, not research notes)
2. Write `AGENTS.md` filled in for this specific project
3. Design `tasks.yaml` schema

## Language

Respond in **English with Traditional Chinese translation** (for English practice).
