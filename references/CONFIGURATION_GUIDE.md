# 配置指南

## 1. 数据来源路径

字段：

```yaml
data_source_path: "..."
```

填写聊天记录实际所在的本机或已挂载目录。

Windows 示例：

```yaml
data_source_path: "C:\\Users\\Administrator\\Documents\\xwechat_files"
```

macOS 示例：

```yaml
data_source_path: "/Users/your-name/Documents/chat_exports"
```

Linux 示例：

```yaml
data_source_path: "/home/your-name/chat_exports"
```

注意：

- Windows YAML 中建议使用双反斜线。
- 路径必须由实际运行 Codex 的环境访问。
- 云端环境通常不能直接读取个人电脑的 `C:\` 目录。

## 2. 群组标题范围

字段：

```yaml
group_filter:
  title_includes:
    - "XXXXXX"
```

`XXXXXX` 是示例占位符。请替换成自己的项目、产品、客户或业务关键词。

### 任一关键词符合即可

```yaml
group_filter:
  title_includes:
    - "Project A"
    - "Product Feedback"
  match_mode: "any"
```

### 必须同时符合所有关键词

```yaml
group_filter:
  title_includes:
    - "Project A"
    - "External"
  match_mode: "all"
```

### 排除群组

```yaml
group_filter:
  title_excludes:
    - "测试"
    - "临时"
```

## 3. 消息内容范围

不限制内容：

```yaml
message_filter:
  content_includes: []
  content_excludes: []
```

只处理包含指定词语的消息：

```yaml
message_filter:
  content_includes:
    - "需求"
    - "异常"
    - "建议"
```

建议不要设置过窄，否则真实需求可能被漏掉。

## 4. 时间范围

首次运行检查过去 24 小时：

```yaml
time_range:
  initial_lookback_hours: 24
```

首次检查过去 7 天：

```yaml
time_range:
  initial_lookback_hours: 168
```

后续按上次成功执行时间增量处理：

```yaml
time_range:
  incremental_from_last_success: true
```

## 5. 自定义需求类别

默认类别可直接使用，也可以修改。

示例：

```yaml
requirement_categories:
  - id: "new_feature"
    label: "New Feature"
    description: "新增能力"
  - id: "improvement"
    label: "Improvement"
    description: "改善既有能力"
  - id: "bug_debug"
    label: "Bug / Debug"
    description: "异常、错误或诊断需求"
```

增加自定义类别：

```yaml
  - id: "question"
    label: "Question"
    description: "需要确认的使用或配置问题"
```

若该类别不应自动写入目标系统，应在 `write_policy` 或执行说明中明确排除。

## 6. 历史资料

配置历史日报和本地索引：

```yaml
history_sources:
  daily_report_paths:
    - "./private-data/daily-reports"
  local_index_path: "./private-data/state/requirement-index.json"
```

这些路径通常包含私人数据，不应提交到公开 GitHub。

## 7. 目标项目系统

填写自己的项目入口：

```yaml
destination:
  project_url: "REPLACE_WITH_YOUR_PROJECT_URL"
  project_name: "REPLACE_WITH_YOUR_PROJECT_NAME"
```

目标系统可以通过：

- 已授权连接器
- 官方 API
- 已登录命令行工具
- 固定浏览器用户资料

进行访问。

Skill 不应尝试绕过登录或组织安全规则。

## 8. 字段映射

把左侧标准字段映射到目标系统的真实字段：

```yaml
destination:
  field_mapping:
    title: "Title"
    description: "Description"
    category: "Type"
    priority: "Priority"
```

若目标系统使用中文字段，可以填写：

```yaml
destination:
  field_mapping:
    title: "需求标题"
    description: "需求描述"
    category: "需求类型"
    priority: "优先级"
```

字段名称不确定时，首次运行应停止写入并要求使用者确认。

## 9. 写入模式

只生成日报：

```yaml
write_policy:
  mode: "report_only"
```

仅新增确认全新的事项：

```yaml
write_policy:
  mode: "new_only"
  create_verified_new_only: true
```

首次运行建议关闭自动写入：

```yaml
write_policy:
  first_run_write_enabled: false
```

待使用者确认分类、重复判断与字段映射后再打开。

## 10. 授权复用

```yaml
authentication:
  interactive_first_login: true
  reuse_existing_authorization: true
  reauthorize_only_when_required: true
```

这表示：

- 首次由使用者自行完成登录或授权。
- 后续在同一执行环境中优先复用有效会话。
- 会话失效、权限撤销或触发安全验证时，再要求重新授权。

它不代表永久免登录，也不能绕过目标系统的会话期限或安全策略。

## 11. 使用者填写检查表

完成配置前确认：

- [ ] 数据来源路径可访问
- [ ] 群组标题关键词已替换
- [ ] 时间范围正确
- [ ] 需求类别符合实际
- [ ] 历史日报路径存在
- [ ] 目标项目正确
- [ ] 字段映射完整
- [ ] 写入模式已确认
- [ ] 首次运行是否允许写入已确认
- [ ] 私密配置和数据不会提交 GitHub
