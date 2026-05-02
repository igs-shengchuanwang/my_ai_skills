# AI 自主工作流程指引
### 跨裝置、跨 AI 工具的工作流程系統

---

## 核心概念

> **不要讓 AI 等你，要讓你等 AI。**
> **任務 brief 是唯一的真相來源，執行者是可替換的。**

你的角色從「操作者」變成「審查者」。
任務設計得越清楚，不管是哪個 AI 工具或真人來執行，結果都會一致。

---

## 整體架構

```
你（每天 2–3 次 Review）
        ↕
   APM 框架（Planner → Manager → Workers）
        ↕
   任何執行者（Claude Code / Cursor / Codex / Gemini CLI / 真人）
        ↕
   Git + 雲端同步（跨裝置存取）
```

**與舊版的關鍵差異：**
- 不再綁定 Claude Code 為唯一執行工具
- 使用 APM 框架管理多 Agent 協作
- 使用 AGENTS.md（而非僅 CLAUDE.md）作為通用專案指引
- 透過 Git + 雲端同步實現跨裝置工作

---

## 工具中立原則 / Agent-Agnostic Principles

### 開放標準

本工作流程建立在三個開放標準之上：

- **AGENTS.md** — 專案指引的通用格式。Google、OpenAI、Cursor、Sourcegraph 共同推出。所有 AI 工具都能讀取。
- **SKILL.md** — 工作技能的跨平台格式。Claude Code、Cursor、Gemini CLI、Codex、Copilot 通用。
- **MCP (Model Context Protocol)** — 工具連接的通用協定。讓 AI 讀寫外部資料來源。

### 檔案分工

| 檔案 | 用途 | 誰讀 |
|------|------|------|
| `AGENTS.md` | 專案規則、build 指令、慣例 | 所有 AI 工具 + 人類 |
| `CLAUDE.md` | Claude Code 專屬設定（hooks 等） | Claude Code only |
| `.apm/` | APM 框架的計畫、記憶、狀態 | APM 管理的所有 Agent |

在 Claude Code 專案中，`CLAUDE.md` 只需一行引用：

```markdown
請先閱讀本專案的 AGENTS.md 作為基礎規則。以下是 Claude Code 專屬補充。
```

---

## APM 框架 / Agentic Project Management

### 安裝

```bash
npm install -g agentic-pm
```

### 在專案中初始化

```bash
cd ~/projects/你的專案
apm init
# → 選擇你的 AI 工具（Claude Code / Cursor / Copilot / Gemini CLI 等）
# → 自動建立 .apm/ 結構
```

### 兩個階段

**階段一：規劃（Planning）**

開一個新的 AI 對話 session，執行 setup command。
Planner 會：
1. 問你關於需求、限制、偏好的問題
2. 探索你的 codebase
3. 產出三份文件供你審查：
   - **Spec** — 要建什麼
   - **Plan** — 工作怎麼組織（階段、任務、依賴）
   - **Rules** — 工作怎麼執行（編碼標準等）

**你審查並批准後，才進入執行。**

**階段二：執行（Implementation）**

開新對話啟動 Manager。執行循環：

```
Manager（對話 2）
  ├── Worker A（對話 3）：前端任務
  ├── Worker B（對話 4）：shader 任務
  └── Worker C（對話 5）：測試任務
```

每個 Worker 是獨立的對話 session，context 不互相污染。

### 交接機制 / Handoff

當 Worker 的 context 快滿時：
1. Worker 寫一份 Handoff markdown
2. 你開一個新對話
3. 貼入 Handoff 檔案
4. 新 Worker 從斷點接續

### APM Auto（Claude Code 專用）

如果在 Claude Code 中想要更自動化：
- Manager 自動透過 subagent 派發任務
- 不需要手動搬運訊息
- 更快，但僅限 Claude Code，無法跨工具

---

## 每日工作節奏

### 🌅 早上 15 分鐘｜Review & 派發

1. 打開 Manager 對話，查看目前狀態
2. 審查昨天完成的工作（看 `.apm/Memory/` 下的 logs）
3. 批准下一批要派發的任務

### ☀️ 白天｜Workers 自主執行

Workers 在各自的 session 中執行任務。你去做其他事。

### 🔍 傍晚 10–20 分鐘｜Review & 調整

| 狀況 | 你要做的 |
|------|---------|
| ✅ 結果 OK | 直接用，或小改後採用 |
| ⚠️ 方向偏了 | 在 Manager 對話中修正指令 |
| ❌ 完全卡住 | 看 Memory logs，你決策方向後繼續 |
| 🔄 Context 快滿 | 執行 Handoff，開新 session 接續 |

---

## 強指令的四個要素

不管派給誰（AI 或人類），任務指令都要包含：

1. **輸入在哪** — 指定檔案路徑或資料來源
2. **輸出長什麼樣** — 格式、規格、存放位置
3. **完成的定義** — 什麼條件叫「做完了」
4. **邊界條件** — 遇到問題怎麼辦

### 範例

```
讀取 assets/heat/shader/heat-vfx-sprite.effect，
分析目前的煙霧效果實作方式，
對照 Cocos 官方手冊中的 shader 章節（https://docs.cocos.com/creator/3.8/manual/zh/shader/），
提出三個效能優化建議，
完成後存到 .apm/Memory/ 對應的任務 log 中。
如果需要查看引擎原始碼，從 https://github.com/cocos/cocos-engine 取得。
不確定的地方先做最合理的假設，在 log 中說明。
```

---

## 跨裝置工作 / Cross-Device Workflow

### 同步策略

| 內容 | 同步方式 | 原因 |
|------|---------|------|
| 程式碼、AGENTS.md、.apm/ | **Git** | 版本控制、可追溯 |
| 任務草稿、inbox 素材、知識庫 | **雲端同步**（iCloud / OneDrive / Google Drive） | 不需要每件事都 commit |
| API keys、tokens | **密碼管理器**（1Password 等） | 安全，永遠不進 Git 或雲端同步 |

### 跨裝置接續工作的流程

1. 在電腦 A 完成工作 → commit & push
2. 在電腦 B 拉取 → `git pull`
3. APM 的 `.apm/Memory/` 和 `Implementation_Plan.md` 已包含所有狀態
4. 開新的 AI session → 它讀取 AGENTS.md + .apm/ 就能接續

---

## 跨 AI 工具工作 / Cross-AI Workflow

### 同一個專案，不同工具

| 情境 | 建議工具 |
|------|---------|
| 深度 coding、多檔案重構 | Claude Code（最強 codebase 理解） |
| 快速小修、UI 調整 | Cursor（IDE 整合好） |
| 需要第二意見 | Gemini CLI 或 Codex |
| Cocos 編輯器驗證 | 你自己手動做 |
| 文案、策略、分析 | Claude.ai 對話介面 |

### 切換工具時的注意事項

- 所有工具都讀 `AGENTS.md`，所以專案規則不需要重複說明
- APM 的狀態存在 `.apm/` 檔案中，不存在任何工具的記憶裡
- 切換工具 = 開一個新 session + 讓它讀 .apm/ 狀態
- 如果是 Claude Code 專用設定（hooks、auto-memory），那些只寫在 CLAUDE.md

---

## 專案結構 / Project Structure

```
~/projects/你的專案/
├── AGENTS.md              ← 通用專案指引（所有工具讀）
├── CLAUDE.md              ← Claude Code 專屬補充
├── .apm/                  ← APM 框架
│   ├── guides/            ← Planner/Manager/Worker 工作流程規則
│   ├── Memory/            ← 任務記憶日誌
│   ├── Implementation_Plan.md  ← 專案計畫（source of truth）
│   └── metadata.json
├── assets/                ← 專案程式碼
└── ...
```

舊版的 `/inbox /tasks /output /review` 結構由 APM 的 `.apm/` 取代。
如果你仍然需要放原始素材，可以保留 `/inbox`。

---

## 安裝清單 / Setup Checklist

- [ ] 安裝 Node.js 18+
- [ ] 安裝 Claude Code: `npm install -g @anthropic-ai/claude-code`
- [ ] 安裝 APM: `npm install -g agentic-pm`
- [ ] 在專案中初始化 APM: `cd ~/projects/你的專案 && apm init`
- [ ] 建立 AGENTS.md（本指引附有範本）
- [ ] 建立 CLAUDE.md（一行引用 AGENTS.md + Claude 專屬設定）
- [ ] 確認 Git remote 設定好，可以跨裝置 push/pull
- [ ] 選擇雲端同步方案（iCloud / OneDrive / Google Drive）

---

## 參考資源 / References

- APM 框架: https://agentic-project-management.dev/
- APM Getting Started: https://agentic-project-management.dev/docs/getting-started/
- AGENTS.md 規範: https://agents.md/
- Synthesis Engineering（方法論）: https://synthesisengineering.org/
- Rajiv Pant 的跨工具實踐: https://rajiv.com/blog/2026/04/27/synthesis-project-management-claude-code-codex/
- cc-context-awareness（Context 監控附件）: https://github.com/sdi2200262/cc-context-awareness

---

*整理自 AI 工作流程規劃對話 · 2026-05*
