## Context

### 当前状态

Cinder 采用双层 Agent 架构：
- **Decision Agent**: 作为大脑，负责理解用户意图、基于 Soul profile 做决策、评估结果
- **Worker Agent**: 作为执行者，执行 Plan → Generate → Evaluation 流程

Worker Agent 当前使用 `CodeGenerator` 类通过 Ollama API 调用模型生成代码，存在以下局限：
1. 缺乏对复杂代码库的深度理解
2. 无法自动运行测试验证
3. 代码生成质量受限于基础模型能力

### 约束

- 必须保持向后兼容，现有用户不受影响
- 不能增加强制的 Python 包依赖
- 必须复用现有的 Soul profile 和决策基础设施
- 执行时间增加控制在合理范围内
- 必须支持用户选择是否启用 Codex

### 利益相关者

- **开发者**: 需要清晰的架构和易于维护的代码
- **用户**: 需要更高质量的代码生成和更好的执行能力
- **系统**: 需要更好的扩展性和可测试性

## Goals / Non-Goals

**Goals:**

1. **集成 Codex 作为增强执行器**
   - 支持多种集成方式（exec、App Server、MCP）
   - 根据任务复杂度自动选择执行器
   - 保持现有架构的清晰性

2. **保持 Soul profile 的影响力**
   - 将 Soul profile 特征传递给 Codex
   - 确保输出符合用户偏好
   - 复用现有的决策和评估机制

3. **提供灵活的配置选项**
   - 用户可以选择启用或禁用 Codex
   - 可以选择不同的执行器
   - 可以配置模型、超时等参数

4. **实现渐进式集成**
   - 先实现简单的 exec 方式
   - 再逐步添加高级功能
   - 提供平滑的迁移路径

**Non-Goals:**

1. 不改变 Decision Agent 的核心逻辑
2. 不修改 Soul profile 的数据结构
3. 不优化 Codex CLI 本身的性能
4. 不实现并行任务执行
5. 不支持 Codex 的所有高级功能（仅实现核心集成）

## Decisions

### 决策 1: 采用分层集成架构

**选择**: 三层架构（Integration Manager → Executors → Codex CLI）

**理由**:
- 清晰的职责分离
- 易于扩展新的执行器
- 便于测试和维护
- 支持灵活的执行器选择

**架构图**:
```
Decision Agent
      ↓
CodexIntegrationManager
      ↓
┌─────┼─────┐
↓     ↓     ↓
Exec  App   MCP
```

**备选方案**:
- 直接在 Worker Agent 中集成
  - 拒绝原因：耦合度高，难以扩展
- 使用单一执行器
  - 拒绝原因：无法满足不同复杂度的任务需求

### 决策 2: 优先实现增强版 CodexExecExecutor

**选择**: 先实现基于 `codex exec` 的执行器，支持完整的 CLI 功能

**理由**:
- 实现相对简单，快速验证概念
- 无需管理额外进程
- 适合大多数任务场景
- 易于调试和测试
- Codex CLI 提供了丰富的功能支持

**实现方式**:
```python
class CodexExecExecutor:
    def execute(self, task: Task) -> Result:
        cmd = [
            "codex", "exec",
            "--json",                    # JSONL 输出
            "--skip-git-repo-check",     # 允许非 Git 仓库
            "--ephemeral",               # 不保存会话
        ]
        
        # 模型配置
        if task.model:
            cmd.extend(["--model", task.model])
        
        # 沙箱配置
        if task.sandbox_mode:
            cmd.extend(["--sandbox", task.sandbox_mode])
        
        # 便捷模式
        if task.full_auto:
            cmd.append("--full-auto")
        
        # 输出 schema 约束
        if task.output_schema:
            schema_file = self._write_schema_file(task.output_schema)
            cmd.extend(["--output-schema", schema_file])
        
        # 工作目录
        if task.cwd:
            cmd.extend(["--cd", task.cwd])
        
        # 任务描述
        cmd.append(task.description)
        
        # 执行并解析 JSONL 输出
        result = subprocess.run(cmd, capture_output=True, text=True)
        return self._parse_jsonl_output(result.stdout)
```

**关键功能**:
- ✅ JSONL 格式输出解析
- ✅ 支持沙箱模式配置
- ✅ 支持输出 schema 约束
- ✅ 支持便捷模式（full-auto）
- ✅ 支持非 Git 仓库执行
- ✅ 支持临时会话（ephemeral）

**备选方案**:
- 先实现 App Server 集成
  - 拒绝原因：复杂度高，风险大
- 同时实现所有执行器
  - 拒绝原因：工作量大，难以快速验证
- 实现简化版 exec 执行器
  - 拒绝原因：无法充分利用 Codex 的能力

### 决策 3: 使用任务描述传递上下文

**选择**: 在任务描述中嵌入 Soul profile 和决策上下文

**理由**:
- 简单直接，无需额外机制
- Codex 可以理解自然语言上下文
- 易于调试和验证
- 保持与现有系统的兼容性

**实现方式**:
```python
def build_task_prompt(self, task: Task, context: dict) -> str:
    soul = self.soul_meta
    return f"""
# 上下文信息

## 用户性格特征
- 风险偏好：{soul['traits']['risk_tolerance']}
- 沟通风格：{soul['traits']['communication_style']}

## 任务理解
- 目标类型：{context.get('goal_type')}
- 关键功能：{context.get('key_features')}

# 任务描述
{task.description}
"""
```

**备选方案**:
- 使用 AGENTS.md 文件
  - 拒绝原因：需要额外的文件管理，复杂度高
- 通过环境变量传递
  - 拒绝原因：信息量有限，不够灵活

### 决策 4: 保持现有的评估机制

**选择**: 复用 ReflectionEngine 评估 Codex 输出

**理由**:
- 保持评估标准的一致性
- 无需重新实现评估逻辑
- Decision Agent 可以继续使用现有的决策流程
- 降低集成风险

**流程**:
```
Codex 执行 → ReflectionEngine 评估 → Decision Agent 决策 → 迭代改进
```

**备选方案**:
- 使用 Codex 的自我评估
  - 拒绝原因：缺乏与 Soul profile 的一致性
- 实现新的评估机制
  - 拒绝原因：工作量大，风险高

### 决策 5: 提供配置开关和降级机制

**选择**: 在配置中提供开关，失败时降级到 CodeGenerator

**理由**:
- 用户可以选择是否启用
- 失败时有备选方案
- 降低生产风险
- 便于 A/B 测试

**配置示例**:
```yaml
codex_integration:
  enabled: true
  fallback_on_error: true
  default_executor: "exec"
  
  exec:
    model: "gpt-5.4"
    sandbox_mode: "workspace-write"
    approval_policy: "never"
    skip_git_repo_check: true
    ephemeral: true
```

**备选方案**:
- 强制启用 Codex
  - 拒绝原因：影响现有用户
- 不提供降级机制
  - 拒绝原因：风险高

### 决策 6: 简化执行器选择逻辑

**选择**: 优先使用 exec 执行器，仅在需要会话持久化时使用 app-server

**理由**:
- exec 执行器功能已足够强大
- 无需管理额外进程
- 降低集成复杂度
- 适合大多数使用场景

**实现方式**:
```python
class CodexIntegrationManager:
    def select_executor(self, task: Task) -> str:
        # 简单任务：使用 exec
        if not task.needs_context_persistence:
            return "exec"
        
        # 需要会话持久化：使用 app-server
        return "app_server"
```

**备选方案**:
- 根据任务复杂度选择
  - 拒绝原因：复杂度评估困难，容易误判
- 让用户手动选择
  - 拒绝原因：增加用户负担

### 决策 7: 降低 MCP 集成优先级

**选择**: MCP 集成作为可选的扩展功能，不在初期实现

**理由**:
- MCP 主要用于将 Codex 暴露给其他客户端
- 对于 Cinder 的用例，exec 和 app-server 更合适
- 降低初期开发工作量
- 可以作为未来的扩展功能

**实现时机**: 阶段 3（可选）

**备选方案**:
- 同时实现 MCP 集成
  - 拒绝原因：工作量大，优先级低
- 不实现 MCP 集成
  - 拒绝原因：可能限制未来的扩展性

## Risks / Trade-offs

### 风险 1: Codex CLI 未安装或配置错误

**影响**: 用户无法使用 Codex 功能

**缓解**:
- 提供清晰的安装和配置文档
- 在启动时检查 Codex CLI 是否可用
- 提供降级到 CodeGenerator 的机制

**监控**: 记录 Codex 执行失败的原因和频率

### 风险 2: Codex 输出不符合 Soul profile

**影响**: 生成的代码可能不符合用户偏好

**缓解**:
- 在任务描述中明确传递 Soul profile 特征
- 使用 ReflectionEngine 评估输出质量
- Decision Agent 可以拒绝不符合的输出

**监控**: 记录用户对 Codex 输出的反馈和修改

### 风险 3: 执行时间或成本增加

**影响**: 用户体验下降或成本上升

**缓解**:
- 提供配置选项控制 Codex 的使用
- 对简单任务使用 CodeGenerator
- 提供超时设置

**监控**: 追踪执行时间和 API 调用次数

### 风险 4: 集成复杂度增加维护成本

**影响**: 代码维护难度增加

**缓解**:
- 采用分层架构，职责清晰
- 编写完善的测试
- 提供详细的文档

**监控**: 定期代码审查和重构

### 权衡: 灵活性 vs 简单性

**选择**: 优先保证简单性，预留扩展点

**理由**:
- 当前阶段不需要过度灵活
- 简单的架构更易于理解和维护
- 预留扩展点，未来可以按需扩展

**优势**: 降低学习成本，减少维护负担

**劣势**: 可能需要重构才能支持某些高级场景

### 权衡: 性能 vs 质量

**选择**: 牺牲一定性能换取质量

**理由**:
- Codex 的代码生成质量更高
- 可以减少返工次数
- 长期来看节省时间

**优势**: 提升代码质量，减少错误

**劣势**: 执行时间可能增加
