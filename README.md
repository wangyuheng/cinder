# Cinder CLI

基于 soul 画像的个人代理命令行交互工具。

## 功能特性

- **交互式 Soul 画像生成**：通过 6 个核心问题引导用户生成个性化 soul 画像
- **Soul 确认工作流**：查看、理解和调整你的 soul 画像
- **代理决策**：基于你的 soul 偏好，agent 可代为决策
- **决策日志**：追踪和分析所有代理决策
- **多后端支持**：支持 Ollama 和 Claude
- **自主任务执行**：从自然语言目标到实际代码文件的端到端自动化

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或以开发模式安装
pip install -e .
```

## 快速开始

### 1. 生成 Soul 画像

```bash
# 交互模式（推荐首次使用）
cinder init

# 快速模式（使用默认值）
cinder init --quick

# 恢复未完成的会话
cinder init --resume

# 自定义输出路径
cinder init --output my-soul.md
```

### 2. 确认 Soul 画像

```bash
# 查看并确认 soul 画像
cinder confirm

# 跳过确认提示
cinder confirm --skip-confirmation
```

### 3. 与 Soul 引导的 Agent 对话

```bash
# 使用 Ollama 交互式对话（默认）
cinder chat

# 使用 Claude 后端
cinder chat --backend claude

# 启用代理决策模式
cinder chat --proxy

# 单条消息模式
cinder chat --message "我今天应该专注于什么？"
```

### 4. 管理决策日志

```bash
# 列出最近的决策
cinder decisions list

# 查看决策详情
cinder decisions show 1

# 查看统计信息
cinder decisions stats

# 导出决策
cinder decisions export --format json --output decisions.json

# 清理旧决策
cinder decisions clean --older-than 90
```

### 5. 配置管理

```bash
# 查看所有配置
cinder config --list

# 设置配置值
cinder config backend ollama

# 重置为默认值
cinder config --reset
```

### 6. 自主任务执行

```bash
# 执行自然语言目标
cinder execute "创建一个Python Hello World程序"

# 预览执行计划（不创建文件）
cinder execute "做个记账web应用" --mode dry-run

# 交互式执行
cinder execute "创建API" --mode interactive

# 指定框架和语言
cinder execute "创建REST API" --framework fastapi --language python

# 添加约束条件
cinder execute "创建Web应用" --constraint "database=postgresql" --constraint "auth=jwt"

# 查看执行历史
cinder execution list

# 查看执行详情
cinder execution show 1

# 回滚执行
cinder execution rollback 1
```

### 7. Web 管理界面

```bash
# 一键启动（推荐）
./scripts/start-web.sh

# 或使用 CLI 命令
cinder server

# 自定义端口
./scripts/start-web.sh --backend-port 9000 --frontend-port 3001

# 自动打开浏览器
./scripts/start-web.sh --open
```

Web 界面功能：
- 📊 **仪表盘** - 执行统计和最近活动
- 📜 **执行历史** - 查看和管理执行记录
- ⚙️ **Soul 配置** - 可视化编辑 Soul 设置
- 📋 **决策记录** - 查看决策历史和统计
- 🎯 **任务触发** - 手动触发新执行
- 🎨 **主题切换** - 浅色/深色主题（默认浅色）
- 📝 **实时日志** - 彩色日志追踪（青色后端 + 绿色前端）

详见 [Web 界面使用指南](docs/WEB_GUIDE.md)。

## 命令参考

### `cinder init`

通过交互式问题引导初始化 soul 画像。

**选项：**
- `--output PATH`: soul.md 的输出路径（默认：soul.md）
- `--name TEXT`: 被分析者的姓名
- `--quick`: 快速模式，使用默认值
- `--resume`: 恢复未完成的会话
- `--skip-confirmation`: 跳过 soul 确认

### `cinder confirm`

确认并调整现有的 soul 画像。

**选项：**
- `--skip-confirmation`: 跳过确认提示

### `cinder chat`

启动与 soul 引导 agent 的对话会话。

**选项：**
- `--message TEXT`: 发送单条消息（非交互模式）
- `--temperature FLOAT`: 模型温度
- `--reflection-loop`: 启用反思循环（仅 Claude）
- `--proxy`: 启用代理决策模式
- `--no-logging`: 禁用决策日志

### `cinder decisions`

管理决策日志和统计。

**子命令：**
- `list`: 列出决策历史
- `show`: 显示决策详情
- `stats`: 显示决策统计
- `export`: 导出决策日志
- `clean`: 清理旧决策
- `review`: 审查代理决策

### `cinder config`

管理配置设置。

**选项：**
- `--list`: 列出所有配置
- `--reset`: 重置为默认配置

### `cinder execute`

自主执行自然语言目标。

**参数：**
- `GOAL`: 自然语言描述的目标

**选项：**
- `--mode`: 执行模式 (auto, interactive, dry-run)
- `--constraint`: 约束条件 (key=value 格式，可多次使用)
- `--language`: 编程语言 (默认: python)
- `--framework`: 使用的框架

**示例：**
```bash
cinder execute "创建一个Python脚本"
cinder execute "做个记账web应用" --mode dry-run
cinder execute "创建API" --framework fastapi --language python
```

### `cinder execution`

管理执行历史和日志。

**子命令：**
- `list`: 列出执行历史
- `show`: 显示执行详情
- `rollback`: 回滚执行

## 全局选项

- `--backend [ollama|claude]`: 使用的后端
- `--model TEXT`: Ollama 后端的模型名称
- `--soul PATH`: soul.md 文件路径
- `--meta PATH`: soul.meta.yaml 文件路径

## 配置

配置存储在 `~/.cinder/config.yaml`。

**默认配置：**
```yaml
backend: ollama
model: qwen3.5:9b
claude_command: claude
soul_path: soul.md
meta_path: ""
temperature: 0.2
reflection_loop: false
max_iterations: 3
sleep_seconds: 1.0
proxy_mode: false
decision_logging: true
log_retention_days: 90
encryption: false
```

## Soul 画像

Soul 画像由两个文件组成：

1. **soul.md**：人类可读的画像，包含：
   - 核心特质
   - 决策画像
   - Agent 行为准则
   - 沟通偏好
   - 决策边界

2. **soul.meta.yaml**：机器可读的元数据，包含：
   - 原始答案
   - 特质分数
   - 确认状态

## 代理决策

启用代理模式后，agent 可以基于你的 soul 画像代为决策：

- **风险容忍度**：保守、平衡或激进的决策
- **沟通风格**：结构化或对话式的响应
- **决策边界**：高风险决策自动升级为人工确认

所有代理决策都会记录：
- 决策上下文
- 应用的 soul 规则
- 置信度分数
- 是否需要人工确认

## 使用示例

### 示例 1：完整工作流

```bash
# 1. 生成 soul 画像
cinder init --name "Alice"

# 2. 确认画像
cinder confirm

# 3. 启用代理模式开始对话
cinder chat --proxy

# 4. 查看决策
cinder decisions list
cinder decisions stats
```

### 示例 2：快速设置

```bash
# 为有经验用户提供快速模式
cinder init --quick --skip-confirmation

# 立即开始对话
cinder chat --message "我今天应该做什么？"
```

### 示例 3：决策分析

```bash
# 导出决策用于分析
cinder decisions export --format csv --output my-decisions.csv

# 查看低置信度决策
cinder decisions list --min-confidence 0.5

# 标记决策为正确/错误
cinder decisions review 1 --correct
cinder decisions review 2 --incorrect --reason "风险太高"
```

### 示例 4：自主任务执行

```bash
# 创建简单的 Python 脚本
cinder execute "创建一个计算斐波那契数列的Python函数"

# 创建 Web 应用（预览模式）
cinder execute "做个记账web应用" --mode dry-run

# 创建 FastAPI 项目
cinder execute "创建用户管理API" --framework fastapi --language python

# 查看执行历史
cinder execution list

# 查看执行详情
cinder execution show 1 --format json

# 如果不满意，可以回滚
cinder execution rollback 1
```

## 从旧 CLI 迁移

如果你之前使用旧的 `cli.py` 和 `chat.py` 脚本：

```bash
# 旧方式（已弃用）
python cli.py --output soul.md
python chat.py --backend ollama

# 新方式
cinder init --output soul.md
cinder chat --backend ollama
```

旧脚本仍然可用，但会显示弃用警告。

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black cinder_cli/
ruff check cinder_cli/
```

## 许可证

MIT License

## 贡献

欢迎贡献！请先阅读贡献指南。
