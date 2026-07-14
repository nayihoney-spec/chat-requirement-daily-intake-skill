
# Chat Requirement Daily Intake Skill

一个可公开分享的通用 Codex Skill，用于从群聊导出数据中识别需求、生成日报、检查重复项，并将确认属于全新的需求写入指定的问题或项目管理系统。

本仓库不绑定特定企业、产品、群组名称、聊天工具或项目平台。所有范围均由使用者在 `config.yaml` 中自行填写。

## 仓库结构

```text
chat-requirement-daily-intake/
├─ SKILL.md
├─ README.md
├─ config.example.yaml
├─ agents/
│  └─ openai.yaml
├─ assets/
│  └─ SETUP_QUESTIONNAIRE.md
└─ references/
   ├─ CONFIGURATION_GUIDE.md
   └─ DAILY_REPORT_TEMPLATE.md
```


## 上传到 GitHub 分享

最简单的方式：

1. 在 GitHub 建立一个新的公开或私有仓库。
2. 将本资料夹中的全部文件上传到仓库根目录。
3. 不要上传自己的 `config.yaml`、聊天记录、日报、索引或登录资料。
4. 在仓库说明中提醒使用者先复制 `config.example.yaml` 为 `config.yaml`。

## 使用者安装方式

### 方式一：让 Codex 从 GitHub 安装

在 Codex 中输入：

```text
请使用 $skill-installer，从这个 GitHub 仓库安装 chat-requirement-daily-intake skill：
<贴上 GitHub 仓库链接>
```

安装后若未立即显示，可重新启动 Codex。

### 方式二：放入指定仓库使用

把整个 Skill 资料夹复制到目标仓库：

```text
<目标仓库>/.agents/skills/chat-requirement-daily-intake/
```

确认最终路径包含：

```text
<目标仓库>/.agents/skills/chat-requirement-daily-intake/SKILL.md
```

### 方式三：作为个人通用 Skill

把整个资料夹复制到个人 Skill 目录：

```text
$HOME/.agents/skills/chat-requirement-daily-intake/
```

Windows 的 `$HOME` 通常对应个人用户目录。使用者可直接要求 Codex 协助复制，不需要手动输入命令。


## 适用场景

- 从本机或已挂载目录读取聊天记录
- 仅处理标题包含指定字样的群组
- 识别新功能、改善与缺陷类需求
- 与历史日报和项目系统现有事项比对
- 仅新增确认属于全新且非重复的事项
- 首次人工授权后，尽量复用既有登录会话
- 遇到权限、解析、映射或重复判断不明确时停止写入

## 无代码使用方式

### 第一步：下载或复制仓库

把本仓库下载到自己的电脑，或在 GitHub 中使用此仓库作为模板。

### 第二步：建立个人配置

复制：

```text
config.example.yaml
```

并改名为：

```text
config.yaml
```

使用一般文字编辑器打开即可，不需要写程序。

### 第三步：填写自己的条件

至少修改以下内容：

```yaml
data_source_path: "C:\\Users\\Administrator\\Documents\\xwechat_files"

group_filter:
  title_includes:
    - "XXXXXX"
```

上面的目录与 `XXXXXX` 只是示例。

使用者应自行填写：

- 聊天数据所在目录
- 群组标题必须包含的字样
- 是否排除部分群组
- 首次检查多少小时
- 后续是否按上次成功时间增量检查
- 需求类别
- 历史日报位置
- 目标项目系统
- 项目链接或项目识别信息
- 字段映射
- 日报输出位置
- 是否允许首次运行直接写入

完整说明请见 `references/CONFIGURATION_GUIDE.md`。

### 第四步：在 Codex 中调用

在本仓库目录中打开 Codex，然后输入：

```text
请使用 $chat-requirement-daily-intake，读取 config.yaml，先验证配置与权限，再执行首次初始化。若需要登录或授权，请停下来让我完成。未经确认不要猜测字段，也不要写入不确定的需求。
```

### 第五步：首次授权

根据实际环境，使用者可能需要：

- 允许 Codex 访问本机数据目录
- 在固定浏览器用户资料中登录目标项目系统
- 授权连接器或命令行工具
- 确认项目与字段映射

不要把密码、验证码、Cookie 或令牌粘贴到聊天、配置或 GitHub。

### 第六步：验证首次结果

首次运行应输出：

- 扫描群组数量
- 扫描消息数量
- 识别需求数量
- 各类别数量
- 重复与相似需求数量
- 确认全新需求数量
- 实际写入数量
- 未写入项目
- 阻塞点
- 登录会话是否可以在同一执行环境中复用

## 自定义范围示例

### 只处理标题包含一个字样的群组

```yaml
group_filter:
  title_includes:
    - "XXXXXX"
  match_mode: "any"
```

### 标题包含任一字样即可

```yaml
group_filter:
  title_includes:
    - "Project A"
    - "Support"
    - "Product Feedback"
  match_mode: "any"
```

### 必须同时包含所有字样

```yaml
group_filter:
  title_includes:
    - "Project A"
    - "External"
  match_mode: "all"
```

### 排除测试群组

```yaml
group_filter:
  title_excludes:
    - "测试"
    - "临时"
```

### 首次检查过去 72 小时

```yaml
time_range:
  initial_lookback_hours: 72
  incremental_from_last_success: true
```

### 只生成日报，不写入项目系统

```yaml
write_policy:
  mode: "report_only"
  first_run_write_enabled: false
```

## 重要限制

Skill 是可重复使用的工作说明，不会自动产生本机文件权限、浏览器登录状态或项目系统权限。

要实现定时自动执行，运行环境必须能够：

1. 持续访问配置的数据目录。
2. 保存执行状态。
3. 查询目标项目中的既有事项。
4. 在组织安全政策允许下复用登录会话或连接器授权。
5. 在登录失效时通知使用者重新授权。

## 隐私与安全

公开 GitHub 仓库中只能放：

- `SKILL.md`
- 示例配置
- 使用说明
- 不含真实业务数据的模板

不要提交：

- `config.yaml`
- 聊天记录
- 日报正文
- 本地索引
- 浏览器用户资料
- 密码、验证码、Cookie、令牌
- 私有项目链接与客户信息

本仓库的 `.gitignore` 已默认排除常见私人配置与运行数据。
