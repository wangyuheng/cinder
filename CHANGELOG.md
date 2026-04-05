# 变更日志

本文件记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [3.0.0] - 2025-01-XX

### 新增

#### 双层 Agent 架构
- **Decision Agent（决策代理）**: 智能决策代理，作为系统的大脑
  - 理解用户意图和上下文
  - 基于 Soul 配置文件做决策
  - 委派任务给 Worker Agent
  - 评估执行结果
  - 与用户交互以获取澄清
  - 决策流程状态机（UNDERSTAND → ANALYZE → DECIDE → DELEGATE → EVALUATE → COMPLETE）

- **Worker Agent（工作代理）**: 任务执行代理，专注于执行
  - 执行 Plan → Generate → Evaluation 流程
  - 返回客观数据，不做决策
  - 支持输出选项供决策
  - 报告执行状态和进度

- **Agent Orchestrator（代理编排器）**: Agent 间的通信枢纽
  - 管理 Agent 通信和消息传递
  - 控制 Agent 生命周期
  - 支持并发执行
  - 记录和追踪所有消息

- **Context Manager（上下文管理器）**: 状态管理系统
  - 短期上下文（内存）用于快速访问
  - 长期上下文（SQLite）用于持久化
  - 存储层间的自动同步
  - 上下文隔离（用户/会话/项目）
  - 大小管理和清理

#### 扩展的决策类型
- **代码接受**: 基于质量接受、改进或重新生成代码
- **技术选型**: 基于风险容忍度选择技术
- **架构决策**: 基于结构偏好选择架构模式
- **实现决策**: 基于细节导向选择实现方式

#### 增强的 Soul Profile 集成
- 扩展 SoulRuleEngine 添加结构偏好规则
- 扩展 SoulRuleEngine 添加细节导向规则
- 决策上下文传递机制
- 决策解释和推理

### 变更

#### 破坏性变更：API 变更
- `AutonomousExecutor.execute()` 返回结构变更
  - 旧：`{"status": "success", "results": [...]}`
  - 新：`{"status": "success", "decision": {...}, "worker_result": {...}}`
- Decision 阶段输出格式扩展以支持多种类型
- Worker 阶段输出格式标准化（移除决策字段）

#### 重构组件
- `AutonomousExecutor` 简化为 Agent 编排器
- 通过 `legacy_mode` 参数实现向后兼容层
- 新旧 API 格式转换工具

### 改进

#### 决策质量
- 在 Decision Agent 中集中决策逻辑
- Soul profile 集成实现个性化决策
- 上下文感知的决策制定
- 带推理链的决策解释

#### 用户体验
- 主动的用户交互
- 决策解释
- 跨会话的上下文感知
- 更好的错误处理和恢复

#### 架构
- 清晰的关注点分离（决策 vs 执行）
- 更好的扩展性支持新决策类型
- 模块化架构便于维护
- 改进的可测试性

### 性能

#### 监控
- LLM 调用追踪和指标
- 决策循环计数
- 上下文大小监控
- 执行时间追踪

#### 优化
- 上下文缓存减少 LLM 调用
- 决策缓存处理重复场景
- 优化的 prompt 工程

### 文档

#### 新增文档
- 架构设计文档
- 从旧架构到新架构的迁移指南
- 不同场景的使用示例
- API 文档更新

#### 示例
- 简单任务执行示例
- 技术选型决策示例
- 架构决策示例
- 集成示例

### 测试

#### 新增测试
- Decision Agent 单元测试
- Worker Agent 单元测试
- Agent Orchestrator 单元测试
- Context Manager 单元测试
- Agent 协作集成测试
- 不同决策类型的场景测试

### 迁移

#### 兼容层
- `legacy_mode` 参数实现向后兼容
- 结果格式转换工具
- 渐进式迁移路径

#### 迁移指南
- 分步迁移说明
- 破坏性变更文档
- 常见问题和解决方案
- 回滚计划

## [2.0.0] - 2024-XX-XX

### 新增
- 初始自主执行器实现
- Plan → Generate → Evaluation → Decision 流程
- Soul profile 集成
- 代理决策制定
- 决策日志记录

## [1.0.0] - 2024-XX-XX

### 新增
- 初始 CLI 实现
- Soul profile 生成
- 基本任务执行
- 配置管理
