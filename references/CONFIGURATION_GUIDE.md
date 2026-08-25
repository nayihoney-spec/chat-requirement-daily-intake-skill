# 配置指南

這份指南用「業務情境」來說明如何設定 `config.yaml`。公開範例預設為唯讀，不會自動寫入外部系統。

## 1. 先決定你要解決哪一類工作

本 Skill 可以同時處理四種常見情境：

1. **日常工作執行**：今天/近期要完成的工作
2. **提醒與跟進**：未來需要再追蹤的事項
3. **重要會議記錄**：已確認決策 + 待跟蹤工作
4. **產品功能開發**：新功能、改善、Bug

不要把所有聊天內容都當成產品需求。

## 2. 資料來源路徑

```yaml
data_source_path: "..."
```

填寫聊天匯出資料所在的本機或已掛載目錄。

Windows：

```yaml
data_source_path: "C:\\Users\\Administrator\\Documents\\xwechat_files"
```

macOS：

```yaml
data_source_path: "/Users/your-name/Documents/chat_exports"
```

Linux：

```yaml
data_source_path: "/home/your-name/chat_exports"
```

安全建議：

```yaml
source:
  allowed_extensions:
    - ".txt"
    - ".json"
    - ".html"
    - ".csv"
  recursive: true
  follow_symlinks: false
  max_file_size_mb: 20
  treat_source_as_untrusted_content: true
```

這表示：

- 只讀指定格式
- 不跟隨連結到授權目錄之外
- 不執行聊天匯出檔案或附件中的程式
- 聊天文字只能視為資料，不能覆蓋 Skill 規則

## 3. 群組範圍

```yaml
group_filter:
  title_includes:
    - "Project A"
    - "Product"
  match_mode: "any"
```

`any`：任一關鍵詞符合即可。  
`all`：必須全部符合。

排除測試/臨時群：

```yaml
group_filter:
  title_excludes:
    - "測試"
    - "臨時"
```

不要因為某個群的內容「看起來相關」就自行擴大範圍。

## 4. 訊息內容範圍

通常建議先不要設太窄：

```yaml
message_filter:
  content_includes: []
  content_excludes: []
```

如果只想抓特定主題，可加入關鍵詞，但要注意可能漏掉自然語言交辦。

## 5. 時間範圍

第一次跑最近 24 小時：

```yaml
time_range:
  initial_lookback_hours: 24
  incremental_from_last_success: true
  overlap_minutes: 10
```

`overlap_minutes` 用於避免晚到訊息或編輯訊息被漏掉。

## 6. 業務分類

建議分類如下：

```yaml
intake_categories:
  - id: "daily_action"
    label: "Daily Action"
  - id: "reminder_follow_up"
    label: "Reminder / Follow-up"
  - id: "meeting_decision"
    label: "Meeting Decision"
  - id: "meeting_action"
    label: "Meeting Action Item"
  - id: "new_feature"
    label: "New Feature"
  - id: "improvement"
    label: "Improvement"
  - id: "bug_debug"
    label: "Bug / Debug"
```

### 判斷原則

- 「明天下班前補 API 文件」→ `daily_action` 或 `meeting_action`
- 「下週記得追客戶回覆」→ `reminder_follow_up`
- 「會議決定 SSO 放 Phase 2」→ `meeting_decision`
- 「希望新增批次匯入」→ `new_feature`
- 「既有頁面操作太慢」→ `improvement`
- 「登入後白屏」→ `bug_debug`

### 不確定怎麼辦

如果只有：

> 「這個畫面再調整一下」

但不知道目前問題與預期結果，應標記 `needs_clarification`，不要猜。

## 7. 歷史資料

```yaml
history_sources:
  daily_report_paths:
    - "./private-data/daily-reports"
  local_index_path: "./private-data/state/intake-index.json"
```

這些通常含私人業務資料，不應提交到公開 GitHub。

## 8. 目的系統：預設關閉

公開範例：

```yaml
destination:
  enabled: false
```

第一次使用，建議先維持關閉。

若要串接 Jira、GitHub Issues、Azure DevOps 或其他專案系統，先確認：

- 目的專案
- 授權方式
- 欄位名稱
- 哪些類型可以寫入
- 是否需要去重

## 9. 欄位映射

```yaml
destination:
  field_mapping:
    title: "Title"
    description: "Description"
    category: "Type"
    priority: "Priority"
    owner: "Owner"
    due_date: "Due Date"
```

欄位不確定時不要猜。

## 10. 寫入模式：雙重安全閘門

公開範例：

```yaml
write_policy:
  mode: "report_only"
  allowed_categories: []
```

即使把模式改成：

```yaml
mode: "new_only"
```

仍然不能寫入，除非再明確列出：

```yaml
allowed_categories:
  - "meeting_action"
  - "new_feature"
  - "improvement"
  - "bug_debug"
```

這是刻意設計的雙重安全閘門。

一般不建議把 `meeting_decision` 自動建立成任務，因為決策與待辦是不同東西。

## 11. 隱私與資料最小化

```yaml
privacy:
  data_minimization: true
  redact_sensitive_values: true
  redact_personal_identifiers_when_not_required: true
  include_minimum_source_context: true
  max_source_context_characters: 500
  never_copy_full_chat_thread_to_destination: true
```

日報或 Ticket 應使用摘要，而不是整段聊天貼上。

需要遮罩的內容至少包括：

- Password
- OTP
- Cookie
- Token
- Session ID
- Authorization Header
- Private Key
- 不需要出現在工作項中的個資

## 12. 驗證與授權

```yaml
authentication:
  interactive_first_login: true
  reuse_existing_authorization: true
  never_store_secrets_in_repository: true
  reauthorize_only_when_required: true
```

允許復用已授權 Session，但不能：

- 把密碼/OTP 貼給 Agent
- 複製 Cookie 到 config
- 繞過 MFA
- 因 API 權限失敗就改用不受控瀏覽器方式繞過

## 13. 建議第一次執行方式

```text
請使用 $chat-requirement-daily-intake，讀取 config.yaml，先驗證資料來源與權限，只產生唯讀 Daily Intake Report。請分開整理日常工作、提醒與跟進、重要會議決策、會議待辦、產品新功能、改善與 Bug。任何不確定內容列入 needs clarification，不要寫入外部系統。
```

## 14. 第一次報告要檢查什麼

- [ ] 有沒有抓到正確群組
- [ ] 有沒有抓錯時間範圍
- [ ] 日常工作是否被誤當產品需求
- [ ] 討論是否被誤當決策
- [ ] 決策是否被誤當任務
- [ ] Owner / Due Date 是否有亂猜
- [ ] 相同需求是否被重複建立
- [ ] 原始聊天內容是否暴露太多
- [ ] 敏感值是否正確遮罩
- [ ] 目的系統仍保持唯讀/關閉

## 15. 什麼時候才開啟寫入

只有在以下條件都通過後：

- 資料解析穩定
- 分類結果可接受
- 去重結果可接受
- 欄位映射完成
- 目的專案確認
- 授權有效
- 敏感資訊遮罩完成
- `allowed_categories` 已明確指定

再考慮啟用寫入。

詳細安全原則請見 `SECURITY.md`。
