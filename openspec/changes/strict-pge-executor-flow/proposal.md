## Why

当前 executor 的执行流程存在质量问题：Plan 阶段过于简单（仅基于关键词匹配)、Generation 缺乏迭代优化、Evaluation 与 Decision 混淆。这导致生成的代码质量不稳定，低质量代码也会被接受和执行。现在需要严格遵循 Plan → Generation → Evaluation → Decision 流程
确保每个阶段都有明确的质量控制和验证机制
从而提升整体代码生成质量。

## What Changes

重构 executor 执行流程
严格分离四个阶段并引入质量验证机制：

- **Plan 阶段增强**: 使用 LLM 理解目标语义、生成结构化任务依赖图、验证计划完整性和可行性
- **Generation 迭代化**: 实现迭代生成循环、自我评估机制、反馈驱动的改进
- **Evaluation 全面化**: 多维度评估、Soul 一致性检查、详细质量报告
- **Decision 明确化**: 在 Evaluation 通过后基于 Soul 进行决策、优化决策逻辑

## Capabilities

### New Capabilities

- `enhanced-task-planning`: 增强的任务规划能力
包含目标理解、计划生成和计划验证三个子阶段
确保生成的任务计划具有高质量

- `iterative-code-generation`: 迭代式代码生成能力
包含代码生成、自我评估和迭代改进循环
确保生成的代码达到质量阈值

### Modified Capabilities

- `autonomous-executor`: 自主执行器
修改执行流程以严格遵循 Plan → Generation → Evaluation → Decision 顺序
在 Evaluation 通过后才进行 Decision

## Impact

**受影响的代码**:
- `cinder_cli/executor/autonomous_executor.py` - 重构执行流程
- `cinder_cli/executor/task_planner.py` - 增强计划生成和验证
- `cinder_cli/executor/code_generator.py` - 添加迭代生成机制
- `cinder_cli/executor/reflection_engine.py` - 增强评估维度

**API 变更**:
- `TaskPlanner.decompose_goal_with_validation()` - 新增方法
- `CodeGenerator.generate_with_iterations()` - 新增方法
- `ReflectionEngine.evaluate_comprehensive()` - 新增方法

**依赖**:
- 无新增外部依赖
- 使用现有的 LLM 后端 (Ollama/Claude)

**系统影响**:
- 执行时间可能增加（因为迭代优化）
- 代码质量显著提升
- 决策链路更加清晰可追溯
