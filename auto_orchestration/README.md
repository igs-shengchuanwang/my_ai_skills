# agent-task-runner

> 研究與實作：讓 AI agents 自主處理多專案、多任務的工作流程
> Research & implementation: orchestrate AI agents to handle multi-project, multi-task workflows autonomously

---

## 問題背景 / The Problem

身為單一開發者同時處理多個專案時，瓶頸不是 AI 寫程式的能力，而是 **人工協調** 的時間：

> When a solo developer juggles multiple projects, the bottleneck is not AI's coding ability — it's the **manual coordination overhead**:

- 接收任務 → 拆分 → 派工 → 監控 → 驗收，每一步都要人介入
- 多個 AI agent 同時跑時，context 互相污染、進度難掌握
- 公司任務管理系統（如 Redmine）通常無法用個人帳號自動化串接
- E2E 遊戲測試大量仰賴人工，AI 難以完全取代

> - Receive → split → dispatch → monitor → verify; every step needs human input
> - Multiple parallel agents pollute each other's context, progress is opaque
> - Corporate task systems (Redmine) often can't be automated via personal accounts
> - E2E gameplay testing heavily depends on humans, AI can't fully replace

---

## 目標 / Goal

```
你（從操作者 → 變成審查者）
        ↕
Auto Orchestrator（任務分發 / 進度聚合 / 異常通知）
        ↕
多個 AI agents（Claude Code / Cursor / Codex …）
        ↕
多個專案（隔離的 git worktree）
```

**核心原則**：不要讓 AI 等你，要讓你等 AI。
> **Core principle**: Don't make AI wait for you — make yourself wait for AI.

---

## 研究範疇 / Research Scope

### 1. 編排模式 / Orchestration Patterns

| 模式 / Pattern | 說明 |
|---|---|
| Hub-and-Spoke | 中央 orchestrator 派發給各 worker agent |
| Pipeline | Agents 依序處理（A → B → C） |
| Parallel | 多 agent 並行處理獨立任務 |
| Evaluator-Optimizer | 一個 agent 產出、另一個審查迭代 |

### 2. 既有方案調研 / Existing Solutions Surveyed

- **[ComposioHQ/agent-orchestrator](https://github.com/ComposioHQ/agent-orchestrator)** — 以 GitHub PR 為核心的 agent 監督器；架構成熟但 v0.1.0 不穩定，且與 GitHub CI 緊耦合，不適合 Cocos / Redmine 工作流
- **APM (Agentic Project Management)** — Planner / Manager / Worker 三層架構；工具中立，可跨 Claude Code / Cursor / Codex
- **LangGraph / CrewAI / AutoGen** — 一般用途多 agent 框架，需自行設計工作流

### 3. 開放標準 / Open Standards

- **AGENTS.md** — 跨 AI 工具通用的專案指引格式
- **SKILL.md** — 跨平台工作技能格式
- **MCP (Model Context Protocol)** — AI 工具連接外部資料的協定

---

## 架構草案 / Architecture Draft

```
tasks.yaml  (人工輸入任務 / manual task intake)
    │
    ▼
┌─────────────────────────┐
│   Task Runner (核心)    │
│  - 讀取任務             │
│  - 為每任務開 worktree  │
│  - 啟動 agent           │
│  - 收集進度與產出       │
└─────────────────────────┘
    │
    ├──► Agent 1 (專案 A · 任務 T001)
    ├──► Agent 2 (專案 A · 任務 T002)
    └──► Agent 3 (專案 B · 任務 T003)
            │
            ▼
    progress.log + summary.md
            │
            ▼
        你的 Review
```

---

## 主要痛點：E2E 測試 / Core Pain: E2E Testing

遊戲開發中最難自動化的是「玩起來感覺對不對」。AI 不能完全取代，但可以縮小人工測試範圍：

> The hardest thing to automate in game dev is "does it feel right". AI can't fully replace it, but can shrink the human surface:

| 測試類型 | AI 能做 |
|---|---|
| 回歸測試（截圖比對） | ✅ |
| 腳本化場景回放 | ✅ |
| 測試案例生成 | ✅ |
| Bug 重現腳本 | ✅ |
| 「感覺對嗎？」 | ❌ 仍需人工 |

---

## 目前進度 / Current Status

- [x] 編排模式概念整理
- [x] agent-orchestrator 評估
- [x] APM 框架方法論記錄（見 `AI自主工作流程指引.md`）
- [x] AGENTS.md 範本（見 `AGENTS.md`）
- [ ] tasks.yaml schema 設計
- [ ] Task Runner MVP 實作
- [ ] 與 Cocos Creator headless build 整合
- [ ] 截圖回歸測試 pipeline

---

## 檔案 / Files

| 檔案 | 用途 |
|---|---|
| `README.md` | 本檔，研究總覽 |
| `AI自主工作流程指引.md` | 完整方法論（APM、跨裝置、跨 AI 工具） |
| `AGENTS.md` | 通用專案指引範本 |

---

## 參考資源 / References

- [Agent Orchestrator (ComposioHQ)](https://github.com/ComposioHQ/agent-orchestrator)
- [APM Framework](https://agentic-project-management.dev/)
- [AGENTS.md Spec](https://agents.md/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code Docs](https://code.claude.com/docs/en/overview)

---

## 授權 / License

MIT (Draft)
