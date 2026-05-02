# <Project Name> — 專案指引 / Project Guide

> 本檔案是所有 AI 工具與人類協作者的共用指引。
> This file is the shared guide for all AI tools and human collaborators.

## 語言 / Language

所有回應、commit message、文件、註解一律使用**繁體中文**。
不可使用簡體中文。程式碼中的變數與函式名稱使用英文。

## 專案概述 / Project Overview

[在此填寫專案目的與目前工作重點]

## 技術棧 / Tech Stack

- Framework/Engine: [框架或引擎名稱]
- Language: [程式語言]
- Version Control: Git (使用 worktree 隔離分支)

## 必讀參考 / Required References

任何相關開發工作，**必須先查閱**以下資源再動手：

- 官方手冊/文件: [填寫網址]
- 相關程式碼庫: [填寫網址]
- 不可過度依賴訓練資料中的舊知識，因為版本差異可能導致錯誤

## 重要限制 / Critical Constraints

- [請列出專案的特殊限制、測試環境要求或架構規範]
- [例如：修改 UI 需在設備上實機驗證]

## 工作原則 / Working Principles

1. **先產出任務指令，再執行** — 直接重寫程式碼或產出成品前，先產出可審查的計畫
2. **遇到不確定的地方** — 做最合理的假設，完成後在 summary 中說明原因
3. **遇到錯誤** — 先嘗試自行修復，無法修復才在 summary 中說明
4. **每個任務完成後** — 輸出 summary.md 說明做了什麼、做了哪些假設

## 目錄結構 / Directory Structure

```
src/
├── [重點目錄1]/         ← 說明
├── [重點目錄2]/         ← 說明
└── ...
```

## Git 工作流 / Git Workflow

- 使用 Git worktree 隔離功能分支：`git worktree add ../my-worktree feature-branch`
- 新分支用 `-b`：`git worktree add -b new-feature ../new-worktree`
- Commit message 使用繁體中文

## 開發注意事項 / Development Notes

- [填寫開發時需特別注意的事項]
- [例如特定的編譯流程、預覽方式等]

## 給人類協作者的補充 / For Human Collaborators

- 開發環境: macOS 或 Windows
- 專案管理: 使用 APM (Agentic Project Management) 框架
- 有任何問題，查看 `.apm/` 目錄下的 Memory logs 和 Implementation Plan
