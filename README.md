# Chat Requirement Daily Intake Skill

一個可公開分享的通用 Codex Skill，用於從群組聊天匯出資料中識別需求、產生日報、檢查重複項，並將確認屬於全新的需求寫入指定的問題或專案管理系統。

本倉庫不綁定特定企業、產品、群組名稱、聊天工具或專案平台。所有範圍均由使用者在 `config.yaml` 中自行填寫。

> [!WARNING]
> ## 使用限制：請在安裝前閱讀
>
> 本倉庫目前屬於 **Instruction-first Skill**。設定格式、需求分類、重複判斷規則與模擬資料乾跑已驗證，但在完成使用者真實資料來源與目標系統的端對端測試前，不應視為即裝即用的生產版本。
>
> 1. **資料來源解析器不是萬能的**
> 目前範例以已匯出的 `.txt`、`.json`、`.html`、`.csv` 等可讀檔案為主要輸入。若資料來源路徑內是聊天應用程式的加密資料庫、快取、媒體檔案或專有內部格式，本 Skill 不保證能夠直接解析。使用者應先確認實際匯出格式，並在必要時補充對應的欄位結構或解析器。
>
> 2. **目標專案系統仍需要可用的連線方式**
> 本 Skill 不內置適用於所有項目平台的通用寫入連接器。實際查詢、重複比對和新增事項，需要使用者俱備已授權的 Connector、官方 API、CLI 登錄狀態或可持續使用的瀏覽器工作階段，並完成項目與欄位對應。若連線或欄位不明確，Skill 必須停止寫入。
>
> 3. **Skill 本身不等於每日排程器**
> `time_range` 只定義每次執行應檢查的時間範圍與增量邏輯，不會自行在每天固定時間啟動。若要定時執行，仍需由 Codex 自動任務、本機 Agent、操作系統調度器或其他受控執行環境負責觸發，並確保該環境持續具備檔案存取、狀態保存及目標系統權限。
>
> 4. **相似度門檻需要搭配明確算法驗證**
> `exact_duplicate_threshold` 與 `highly_similar_threshold` 是策略參數，不代表倉庫已綁定特定 Embedding、字符串相似度或模型算法。使用者應明確指定實際比較方法，並使用真實歷史需求驗證門檻。在結果不確定時，只能列入日報或人工複核，不應自動寫入目標系統。
>
> **建議版本定位：** `v0.x`。只有在真實資料解析、歷史需求比對、目標系統查詢與寫入、授權重用及增量狀態保存均完成端對端驗證後，才建議標記為生產可用版本。

## 倉庫結構

```text
chat-requirement-daily-intake/
├─ SKILL.md
├─ README.md
├─ config.example.yaml
├─ agents/
│ └─ openai.yaml
├─ assets/
│ └─ SETUP_QUESTIONNAIRE.md
└─ references/
 ├─ CONFIGURATION_GUIDE.md
 └─ DAILY_REPORT_TEMPLATE.md
```


## 上傳到 GitHub 分享

最簡單的方式：

1. 在 GitHub 建立一個新的公開或私有倉庫。
2. 將本資料夾中的全部檔案上傳到倉庫根目錄。
3. 不要上傳自己的 `config.yaml`、聊天記錄、日報、索引或登入資料。
4. 在倉庫說明中提醒使用者先複製 `config.example.yaml` 為 `config.yaml`。

## 用戶安裝方式

### 方式一：讓 Codex 從 GitHub 安裝

在 Codex 中輸入：

```text
請使用 $skill-installer，從這個 GitHub 倉庫安裝 chat-requirement-daily-intake skill：
<貼上 GitHub 倉庫連結>
```

安裝後若未立即顯示，可重新啟動 Codex。

### 方式二：放入指定倉庫使用

把整個 Skill 資料夾複製到目標倉庫：

```text
<目標倉庫>/.agents/skills/chat-requirement-daily-intake/
```

確認最終路徑包含：

```text
<目標倉庫>/.agents/skills/chat-requirement-daily-intake/SKILL.md
```

### 方式三：作為個人通用 Skill

把整個資料夾複製到個人 Skill 目錄：

```text
$HOME/.agents/skills/chat-requirement-daily-intake/
```

Windows 的 `$HOME` 通常對應個人使用者目錄。用戶可直接要求 Codex 協助複製，不需要手動輸入指令。


## 適用場景

- 從本機或已掛載目錄讀取聊天記錄
- 僅處理標題包含指定字樣的群組
- 識別新功能、改善與缺陷類需求
- 與歷史日報和專案系統現有事項比對
- 僅新增確認屬於全新且非重複的事項
- 首次人工授權後，盡量重複使用既有登入工作階段
- 遇到權限、解析、映射或重複判斷不明確時停止寫入

## 無程式碼使用方式

### 第一步：下載或複製倉庫

把本倉庫下載到自己的電腦，或在 GitHub 中使用此倉庫作為模板。

### 第二步：建立個人配置

複製：

```text
config.example.yaml
```

並改名為：

```text
config.yaml
```

使用一般文字編輯器開啟即可，不需要寫入程式。

### 第三步：填寫自己的條件

至少修改以下內容：

```yaml
data_source_path: "C:\\Users\\Administrator\\Documents\\xwechat_files"

group_filter:
 title_includes:
 - "XXXXXX"
```

上面的目錄與 `XXXXXX` 只是範例。

使用者應自行填寫：

- 聊天資料所在目錄
- 群組標題必須包含的字樣
- 是否排除部分群組
- 首次檢查多少小時
- 後續是否依上次成功時間增量檢查
- 需求類別
- 歷史日報位置
- 目標專案系統
- 項目連結或項目識別訊息
- 字段映射
- 日報輸出位置
- 是否允許首次運行直接寫入

完整說明請見 `references/CONFIGURATION_GUIDE.md`。

### 第四步：在 Codex 中調用

在本倉庫目錄中開啟 Codex，然後輸入：

```text
請使用 $chat-requirement-daily-intake，讀取 config.yaml，先驗證設定與權限，再執行首次初始化。若需要登入或授權，請停下來讓我完成。未經確認不要猜測字段，也不要寫入不確定的需求。
```

### 第五步：首次授權

根據實際環境，使用者可能需要：

- 允許 Codex 存取本機資料目錄
- 在固定瀏覽器使用者檔案中登入目標項目系統
- 授權連接器或命令列工具
- 確認項目與字段映射

不要把密碼、驗證碼、Cookie 或令牌貼到聊天、設定或 GitHub。

### 第六步：驗證首次結果

首次運行應輸出：

- 掃描群組數量
- 掃描訊息數量
- 識別需求數量
- 各類別數量
- 重複與相似需求數量
- 確認全新需求數量
- 實際寫入數量
- 未寫入項目
- 阻塞點
- 登入工作階段是否可以在同一執行環境中重複使用

## 自訂範圍範例

### 只處理標題包含一個字樣的群組

```yaml
group_filter:
 title_includes:
 - "XXXXXX"
 match_mode: "any"
```

### 標題包含任一字樣即可

```yaml
group_filter:
 title_includes:
 - "Project A"
 - "Support"
 - "Product Feedback"
 match_mode: "any"
```

### 必須同時包含所有字樣

```yaml
group_filter:
 title_includes:
 - "Project A"
 - "External"
 match_mode: "all"
```

### 排除測試群組

```yaml
group_filter:
 title_excludes:
 - "測試"
 - "暫時"
```

### 首次檢查過去 72 小時

```yaml
time_range:
 initial_lookback_hours: 72
 incremental_from_last_success: true
```

### 只產生日報，不寫入專案系統

```yaml
write_policy:
 mode: "report_only"
 first_run_write_enabled: false
```

## 重要限制

Skill 是可重複使用的工作說明，不會自動產生本機檔案權限、瀏覽器登入狀態或項目系統權限。

要實現定時自動執行，運行環境必須能夠：

1. 持續存取配置的資料目錄。
2. 保存執行狀態。
3. 查詢目標項目中的既有事項。
4. 在組織安全性政策允許下重複使用登入工作階段或連接器授權。
5. 在登入失效時通知使用者重新授權。

## 隱私與安全

公開 GitHub 倉庫中只能放：

- `SKILL.md`
- 範例配置
- 使用說明
- 不含真實業務資料的模板

不要提交：

- `config.yaml`
- 聊天記錄
- 日報正文
- 本地索引
- 瀏覽器使用者資料
- 密碼、驗證碼、Cookie、令牌
- 私人項目連結與客戶訊息

本倉儲的 `.gitignore` 已預設排除常見私人設定與運作資料。
