## Why

当前 Cinder 的 Worker Agent 使用基础的代码生成能力，缺乏对复杂代码库的深度理解和自动化测试验证能力。Codex 是 OpenAI 推出的专业 AI 软件工程 Agent，具备强大的代码生成、代码库理解、自动测试和 PR 创建能力。

通过集成 Codex，我们可以：
1. 提升代码生成质量和准确性
2. 增强对复杂代码库的理解能力
3. 实现自动化的测试验证和质量保证
4. 保持 Decision Agent 的决策优势和 Soul profile 的个性化特征

现在是集成的最佳时机，因为 Codex CLI 已经开源并提供了多种集成方式（exec、App Server、MCP），可以灵活选择最适合的集成方案。

## What Changes

- **新增 Codex 集成层**：创建独立的 Codex 集成模块，支持多种执行方式
- **扩展 Worker Agent**：在现有 Worker Agent 中集成 Codex 执行器，作为代码生成的增强选项
- **新增配置选项**：添加 Codex 相关的配置项，包括执行器选择、模型配置、超时设置等
- **保持向后兼容**：现有的 CodeGenerator 仍然可用，用户可以选择使用 Codex 或原有执行器
- **新增上下文传递机制**：将 Soul profile 和决策上下文传递给 Codex，确保输出符合用户偏好

## Capabilities

### New Capabilities

- `codex-executor`: Codex 执行器集成，支持通过 `codex exec` 方式执行任务
- `codex-app-server`: Codex App Server 客户端，支持会话管理和流式事件处理
- `codex-integration-manager`: Codex 集成管理器，负责执行器选择、上下文传递和结果统一

### Modified Capabilities

- `worker-agent`: 扩展 Worker Agent 以支持 Codex 执行器，保持现有的 Plan → Generate → Evaluation 流程

## Impact

### 代码影响
- 新增 `cinder_cli/executor/codex_executor.py`：Codex 执行器实现
- 新增 `cinder_cli/executor/codex_app_server_client.py`：App Server 客户端
- 新增 `cinder_cli/executor/codex_integration_manager.py`：集成管理器
- 修改 `cinder_cli/agents/worker_agent.py`：集成 Codex 执行器
- 修改 `cinder_cli/config.py`：添加 Codex 配置选项

### API 影响
- 新增配置项：`codex_integration.enabled`、`codex_integration.default_executor` 等
- Worker Agent 的执行器选择逻辑变更，但保持向后兼容

### 依赖影响
- 新增可选依赖：Codex CLI（用户需要单独安装）
- 无新增 Python 包依赖

### 系统影响
- 需要用户安装 Codex CLI 并配置认证
- 执行时间可能因 Codex 的能力而有所变化
- 成本可能因使用 Codex API 而增加
