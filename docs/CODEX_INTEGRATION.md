# Codex 集成用户指南

## 概述

Codex 是 OpenAI 推出的专业 AI 软件工程 Agent，能够理解代码库、生成代码、运行测试并创建 Pull Request。Cinder 现已集成 Codex，提供更强大的代码生成能力。

## 功能特性

### 核心能力

- **代码生成**: 使用 Codex 生成高质量代码
- **代码库理解**: Codex 能够理解整个代码库的结构
- **自动测试**: 自动运行测试验证代码质量
- **上下文传递**: 自动传递 Soul profile 和决策上下文
- **降级机制**: Codex 不可用时自动降级到 CodeGenerator
- **灵活配置**: 支持多种执行模式和参数配置

### 集成方式

Cinder 支持三种 Codex 集成方式：

1. **CodexExecExecutor** (推荐) - 使用 `codex exec` 非交互模式
2. **CodexAppServerClient** - 使用 App Server 进行会话管理
3. **CodexMCPBridge** - 通过 MCP 协议集成（可选）

## 安装

### 1. 安装 Codex CLI

**方式 1: 使用 npm**
```bash
npm install -g @openai/codex
```

**方式 2: 使用 Ollama**
```bash
ollama launch codex --model kimi-k2.5:cloud
```

### 2. 验证安装

```bash
codex --version
```

### 3. 认证 Codex

```bash
codex auth login
```

## 配置

### 启用 Codex

编辑 `cinder.yaml` 文件：

```yaml
codex_integration:
  enabled: true  # 启用 Codex
  fallback_on_error: true  # 启用降级机制
  default_executor: "exec"  # 默认执行器
  
  exec:
    model: "gpt-5.4"  # 使用的模型
    sandbox_mode: "workspace-write"  # 沙箱模式
    approval_policy: "never"  # 审批策略
    skip_git_repo_check: true  # 跳过 Git 仓库检查
    ephemeral: true  # 临时会话
    timeout: 300  # 超时时间（秒）
    full_auto: true  # 全自动模式
```

### 配置选项说明

#### 全局配置

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | false | 是否启用 Codex |
| `fallback_on_error` | bool | true | 是否在错误时降级 |
| `default_executor` | string | "exec" | 默认执行器 |

#### Exec 配置

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | string | "gpt-5.4" | 使用的模型 |
| `sandbox_mode` | string | "workspace-write" | 沙箱模式 |
| `approval_policy` | string | "never" | 审批策略 |
| `skip_git_repo_check` | bool | true | 跳过 Git 检查 |
| `ephemeral` | bool | true | 临时会话 |
| `timeout` | int | 300 | 超时时间 |
| `full_auto` | bool | false | 全自动模式 |

### 沙箱模式

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| `read-only` | 只读模式 | 代码审查、探索 |
| `workspace-write` | 工作区可写 | 开发任务（推荐） |
| `danger-full-access` | 完全访问 | CI/CD、高级自动化 |

### 审批策略

| 策略 | 说明 | 使用场景 |
|------|------|----------|
| `never` | 从不审批 | 自动化执行（推荐） |
| `on-request` | 每次都审批 | 最大控制 |
| `on-failure` | 失败时审批 | 平衡自动化 |
| `untrusted` | 不信任模式 | 高风险场景 |

## 使用方式

### 1. 通过 Cinder CLI

```bash
# 执行任务（自动使用 Codex）
.venv/bin/python cinder execute "创建一个简单的 Python 函数"

# 指定语言
.venv/bin/python cinder execute "创建一个 Hello World 程序" --language python

# 添加约束
.venv/bin/python cinder execute "创建一个计算器类" --constraint "style=simple"
```

### 2. 直接使用 Codex

```bash
# 简单任务
codex exec "Create a simple Python function"

# 指定模型
codex exec --model gpt-5.4 "Create a REST API"

# 使用沙箱模式
codex exec --sandbox workspace-write "Refactor the code"

# 全自动模式
codex exec --full-auto "Fix all type errors"
```

### 3. 编程方式

```python
from cinder_cli.config import Config
from cinder_cli.executor.codex_integration_manager import (
    CodexIntegrationManager,
    TaskContext,
)

# 加载配置
config = Config()

# 创建管理器
manager = CodexIntegrationManager(config)

# 创建任务上下文
context = TaskContext(
    soul_profile={
        "traits": {
            "risk_tolerance": "moderate",
            "communication_style": "concise"
        }
    },
    decision_context={
        "goal_type": "code_generation",
        "key_features": ["simple", "readable"]
    }
)

# 执行任务
result = manager.execute_task(
    "Create a Python function that adds two numbers",
    context
)

if result.success:
    print(f"Generated code:\n{result.output}")
else:
    print(f"Error: {result.error}")
```

## 验证集成

### 运行验证脚本

```bash
.venv/bin/python verify_codex.py
```

### 预期输出

```
✓ Codex CLI: Pass
✓ Configuration: Pass
✓ Integration Manager: Pass
✓ Worker Agent: Pass
✓ Codex Exec: Pass

✅ All tests passed!
```

## 故障排除

### 问题 1: Codex CLI 未安装

**错误信息**: `Codex CLI is not installed`

**解决方案**:
```bash
# 安装 Codex CLI
npm install -g @openai/codex

# 或使用 Ollama
ollama launch codex --model kimi-k2.5:cloud
```

### 问题 2: Codex 未认证

**错误信息**: `Codex CLI is not authenticated`

**解决方案**:
```bash
# 认证 Codex
codex auth login
```

### 问题 3: 沙箱权限错误

**错误信息**: `Operation blocked by sandbox policy`

**解决方案**:
```yaml
# 修改 cinder.yaml
codex_integration:
  exec:
    sandbox_mode: "danger-full-access"  # 使用完全访问模式
```

### 问题 4: 执行超时

**错误信息**: `Execution timed out after 300 seconds`

**解决方案**:
```yaml
# 增加超时时间
codex_integration:
  exec:
    timeout: 600  # 增加到 10 分钟
```

### 问题 5: Decision Agent 拒绝代码

**现象**: 生成的代码质量评分很高，但 Decision Agent 拒绝所有代码

**原因**: Decision Agent 的决策逻辑问题，不是 Codex 集成的问题

**解决方案**:
1. 调整 Soul profile 的决策阈值
2. 修改 Decision Agent 的接受标准
3. 或直接使用 Codex CLI（绕过 Decision Agent）

## 最佳实践

### 1. 选择合适的沙箱模式

- **开发环境**: 使用 `workspace-write`
- **CI/CD**: 使用 `danger-full-access`
- **代码审查**: 使用 `read-only`

### 2. 配置合理的超时时间

- **简单任务**: 60-120 秒
- **中等任务**: 300 秒（默认）
- **复杂任务**: 600-900 秒

### 3. 使用降级机制

```yaml
codex_integration:
  enabled: true
  fallback_on_error: true  # 启用降级
```

### 4. 传递上下文

确保传递 Soul profile 和决策上下文，以获得符合预期的输出：

```python
context = TaskContext(
    soul_profile=soul_meta,  # 用户偏好
    decision_context=decision,  # 决策上下文
    quality_requirements={  # 质量要求
        "quality_threshold": 0.8
    }
)
```

## 高级用法

### 使用 Output Schema

```python
result = manager.execute_task(
    "Analyze the code and return issues",
    context,
    output_schema={
        "type": "object",
        "properties": {
            "issues": {"type": "array"},
            "score": {"type": "number"}
        }
    }
)
```

### 指定工作目录

```python
result = manager.execute_task(
    "Refactor the code in this directory",
    context,
    cwd=Path("/path/to/project")
)
```

### 使用不同的模型

```python
result = manager.execute_task(
    "Complex task requiring deep reasoning",
    context,
    model="o3"  # 使用深度推理模型
)
```

## 参考资源

- [Codex CLI 官方文档](https://github.com/openai/codex)
- [Codex MCP Server](https://www.npmjs.com/package/@etheaven/codex-mcp-server)
- [Cinder 文档](../README.md)
- [Soul Profile 指南](../soul.md)

## 更新日志

### v1.0.0 (2026-04-05)

- ✅ 实现 CodexExecExecutor
- ✅ 实现 CodexIntegrationManager
- ✅ 集成到 Worker Agent
- ✅ 支持所有 Codex CLI 参数
- ✅ 实现 Soul profile 上下文传递
- ✅ 实现降级机制
- ✅ 完整的单元测试
- ✅ 验证脚本

## 反馈和支持

如有问题或建议，请：
1. 查看故障排除部分
2. 运行验证脚本检查集成状态
3. 查看日志文件获取详细错误信息
4. 提交 Issue 到项目仓库
