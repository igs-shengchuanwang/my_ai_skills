# Global Claude Code Rules

回答最高原則：盡可能簡潔，簡短說重點

## Cocos Creator 相關規範
- **永遠從官方文件網站開始查詢**：https://docs.cocos.com/creator/3.8/manual/zh/
- **如要考慮底層實現需參考請看 engine repo**：https://github.com/cocos/cocos-engine
- 不可自行假設簡化用法，需確認文件或 source 依據
- 查不到確切依據時**必須明確告知使用者「無法查證」**，不可直接給出未經驗證的程式碼

### Cocos Creator 編譯除錯
- **編譯器差異**：Cocos 3.8 packer-driver 使用 **Babel parser**，比 IDE 的 TypeScript Language Server (tsc) 嚴格。常見差異：
  - enum 成員間逗號 Babel 視為必要，tsc 容忍省略
  - IDE 顯示語法 OK 不代表 Cocos 能編譯
- **錯誤訊息位置**：Cocos 編譯失敗時，Console 面板只顯示下游的 `Script missing` 假象，**真正的 SyntaxError 在** `temp/programming/packer-driver/logs/debug.log`
- **除錯流程**：遇到 `Script missing` 不要直接相信表面錯誤訊息，先去看 packer-driver `debug.log` 找根因

## Claude Code 相關規範
- **永遠從官方文件網站開始查詢**：https://code.claude.com/docs/en/overview
- 不可自行假設簡化用法，需確認文件或 source 依據

## TypeScript / Cocos Creator 程式碼風格規範（依據 ESLint 規則）

### 縮排與格式
- 縮排使用 **4 空格**（`.mjs` 檔案使用 2 空格）
- 語句結尾必須加**分號**
- 大括號使用 **1tbs** 風格（`{` 在同一行）
- 檔案結尾必須有**空行**

### 命名規範
- 變數 / 函式 / 參數：**camelCase**（允許前導 `_`）
- exported const：**UPPER_CASE**
- 型別 / 類別 / 列舉 / 介面：**PascalCase**
- 列舉成員：**PascalCase**
- `.ts` / `.tsx` 檔案名稱：**PascalCase**

### 安全性
- 禁止使用 `eval` 及隱含的 eval（`no-eval`, `no-implied-eval`）
- 禁止使用未定義的全域變數（`no-undef`）
- 禁止覆寫全域物件（`no-global-assign`）
- 禁止模組循環引用（`import/no-cycle`）

### TypeScript 特有
- 禁止 `#` private 語法，必須使用 TypeScript `private` 修飾子
- class 成員必須標明存取修飾子（`public` / `protected` / `private`）
- 避免使用 `any` 型別（warn 層級）

### 控制流與區塊
- 所有控制流語句（`if` / `else` / `for` / `while` 等）都必須加大括號（`curly: error`）
- 禁止不必要的獨立區塊（`no-lone-blocks`）

### Cocos Creator 專屬
- `@ccclass("Name")` 的字串參數必須與 class 名稱一致

## Global Skills
- **cocos-mcp**：操作 Cocos Creator 編輯器的 MCP skill，位於 ~/.claude/skills/cocos-mcp/SKILL.md。使用時機：需要透過 MCP 控制 Cocos Creator 場景、節點、元件等操作時。
- **redmine**：Redmine 專案管理 skill，位於 ~/.claude/skills/redmine/SKILL.md。使用時機：需要查詢或操作 Redmine 議題、專案時。
