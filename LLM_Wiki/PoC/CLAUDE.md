# LLM Wiki — Schema

本檔案是整個 wiki 系統的行為規範。LLM 在操作 wiki 時必須遵守此文件的所有規則。
此文件由使用者與 LLM 共同演化，隨著使用經驗逐步調整。

---

## 架構

```
PoC/
├── CLAUDE.md          # 本檔案 — Schema（LLM 行為規範）
├── raw/               # 原始資料（不可變，LLM 只讀不寫）
└── wiki/              # LLM 維護的知識庫（LLM 擁有完整讀寫權）
    ├── index.md       # 內容目錄（每次 ingest 必須更新）
    └── log.md         # 操作紀錄（append-only）
```

---

## 三層分離原則

1. **raw/** — 原始資料。不可變。LLM 讀取但永不修改。這是事實來源。
2. **wiki/** — LLM 生成與維護的知識庫。摘要、實體頁、概念頁、比較、綜合分析。LLM 擁有此層的完整控制權。
3. **CLAUDE.md** — 本檔案。定義 wiki 的結構慣例與操作流程。

---

## 操作流程

### Ingest（收錄新資料）

當使用者將新 source 加入 raw/ 並要求處理時：

1. 閱讀 source 全文
2. 與使用者討論關鍵要點
3. 在 wiki/ 建立該 source 的摘要頁
4. 更新 wiki/index.md
5. 更新所有相關的實體頁、概念頁（若不存在則新建）
6. 在 wiki/log.md 追加紀錄

一次處理一份 source，保持使用者參與。

### Query（查詢）

當使用者提出問題時：

1. 先讀 wiki/index.md 找到相關頁面
2. 讀取相關頁面內容
3. 綜合回答，附上引用來源
4. 若回答具有長期價值，建議使用者是否要回填為 wiki 頁面

### Lint（健康檢查）

定期或使用者要求時：

1. 檢查頁面間的矛盾
2. 找出孤立頁面（無 inbound links）
3. 找出被提及但尚未建立的概念
4. 找出缺失的交叉引用
5. 建議可進一步調查的問題或新 source

---

## Wiki 頁面慣例

### 檔案命名
- 使用 kebab-case：`concept-name.md`
- 摘要頁前綴 source：`source-article-title.md`

### 頁面結構
每個 wiki 頁面必須包含 YAML frontmatter：

```yaml
---
type: source | concept | entity | comparison | synthesis
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: []        # 引用的 raw/ 檔案
tags: []
---
```

### 交叉引用
- 使用 markdown link 格式：`[顯示文字](relative-path.md)`
- 每個頁面底部維護 "Related" 區塊列出相關頁面

---

## index.md 規範

按類別組織，每個條目包含：
- 連結
- 一行摘要
- 類型標記

```markdown
## Sources
- [標題](source-xxx.md) — 一行摘要 `source`

## Concepts
- [概念名](concept-xxx.md) — 一行摘要 `concept`

## Entities
- [實體名](entity-xxx.md) — 一行摘要 `entity`
```

---

## log.md 規範

Append-only。每筆紀錄格式：

```markdown
## [YYYY-MM-DD] operation | 標題
簡短描述做了什麼，影響了哪些頁面。
```

operation 為以下之一：`ingest` | `query` | `lint` | `update`

---

## 演化紀錄

- **2026-04-07** — 初始版本建立
