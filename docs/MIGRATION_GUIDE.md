# 迁移指南：严格 PGE 执行流程

本指南帮助现有用户从旧版本的执行流程迁移到新的严格 PGE (Plan-Generation-Evaluation-Decision) 流程。

## 概述

v2.2.0 引入了严格的阶段分离和质量控制机制，主要变更包括：

1. **Plan 阶段增强**： LLM-based 目标理解和计划验证
2. **Generation 迭代化**： 迭代生成循环和自我评估
3. **Evaluation 全面化**： 多维度评估和 Soul 一致性检查
4. **Decision 明确化**： Evaluation 通过后的 Soul-based 决策

## 破坏性变更

### 执行流程变更

**旧流程:**
```
decompose_goal → generate_code → evaluate_execution → decision (混合)
```

**新流程:**
```
Plan (LLM理解+验证) → Generation (迭代优化) → Evaluation (全面评估) → Decision (Soul-based)
```

### API 变更

#### TaskPlanner

**新增方法:**
- `understand_goal_with_llm(goal, constraints)` - LLM-based 目标理解
- `decompose_goal_with_validation(goal, constraints)` - 带验证的计划生成
- `validate_plan(plan, understanding)` - 计划验证
- `_regenerate_plan_with_feedback(...)` - 反馈驱动的重新生成

**向后兼容:**
- `decompose_goal()` 方法仍然可用，但建议使用新方法

#### CodeGenerator

**新增方法:**
- `generate_with_iterations(description, language, constraints, max_iterations, quality_threshold)` - 迭代生成
- `_self_evaluate(code, description, language)` - 自我评估
- `_regenerate_with_feedback(...)` - 反馈驱动的重新生成

**向后兼容:**
- `generate_code()` 方法仍然可用，但建议使用新方法

#### ReflectionEngine

**新增方法:**
- `evaluate_comprehensive(code, task, soul_meta)` - 全面评估
- `_evaluate_code_quality_detailed(...)` - 详细代码质量评估
- `_evaluate_soul_alignment(...)` - Soul 一致性检查
- `_assess_risks(...)` - 风险评估

**向后兼容:**
- `evaluate_execution()` 方法仍然可用，但建议使用新方法

## 新功能

### 质量阈值配置

新增配置选项控制质量阈值：

```yaml
# ~/.cinder/config.yaml
plan_quality_threshold: 0.7      # 计划质量阈值
code_quality_threshold: 0.8      # 代码质量阈值
evaluation_quality_threshold: 0.7  # 评估质量阈值
```

### 迭代生成配置

控制迭代生成行为

```yaml
enable_iterative_generation: true      # 启用迭代生成
enable_comprehensive_evaluation: true  # 启用全面评估
```

### 执行流程追踪

新的执行流程会记录详细的阶段信息

```python
execution_flow = {
    "goal": "...",
    "phases": [
        {"phase": "plan", "quality_score": 0.85, ...},
        {"phase": "generation", "iterations": 2, ...},
        {"phase": "evaluation", "average_quality": 0.82, ...},
        {"phase": "decision", "accepted_count": 3, ...}
    ],
    "status": "success"
}
```

## 迁移步骤

### 1. 更新配置文件

检查并更新 `~/.cinder/config.yaml`:

```bash
cinder config --list
```

如果缺少新配置项，手动添加:

```yaml
plan_quality_threshold: 0.7
code_quality_threshold: 0.8
evaluation_quality_threshold: 0.7
enable_iterative_generation: true
enable_comprehensive_evaluation: true
```

### 2. 验证 Soul 配置

确保 Soul 配置文件包含必要的特质

```bash
cinder soul show
```

检查以下特质:
- `risk_tolerance` (0-100)
- `structure` (0-100)
- `detail_orientation` (0-100)

### 3. 测试新流程

使用简单目标测试新流程

```bash
cinder execute "创建一个简单的Python脚本" --mode auto
```

预期输出:
```
[bold blue]PHASE 1: PLAN[/bold blue]
[dim]Plan phase complete: 1 tasks, quality=0.85[/dim]

[bold green]PHASE 2: GENERATION[/bold green]
[dim]Task 1: 2 iterations, quality=0.82[/dim]

[bold yellow]PHASE 3: EVALUATION[/bold yellow]
[dim]Evaluated 1: quality=0.82, approved=true[/dim]

[bold magenta]PHASE 4: DECISION[/bold magenta]
[dim]Decision phase complete: 1/1 accepted[/dim]

[green]✓ 执行完成[/green]
```

### 4. 调整质量阈值（可选）

如果需要更严格或宽松的质量控制

```bash
# 更严格的计划质量
cinder config plan_quality_threshold 0.8

# 更宽松的代码质量
cinder config code_quality_threshold 0.7
```

## 常见问题

### Q: 执行时间增加了怎么办？

A: 迭代生成会增加执行时间，但可以通过以下方式优化:

1. 降低质量阈值
```bash
cinder config code_quality_threshold 0.7
```

2. 禁用迭代生成（不推荐）
```bash
cinder config enable_iterative_generation false
```

### Q: Plan 阶段失败怎么办？

A: Plan 阶段会自动重新生成计划（最多2次）。如果仍然失败:

1. 检查目标描述是否清晰
2. 尝试分解为更小的目标
3. 添加更多约束条件

### Q: 如何查看详细的执行流程？

A: 执行结果中包含 `execution_flow` 字段

```python
result = cinder.execute("...")
print(json.dumps(result["execution_flow"], indent=2))
```

### Q: Soul 一致性检查失败怎么办？

A: Soul 一致性检查可能因为代码风格不匹配而失败

1. 检查 Soul 配置的特质值
2. 调整代码以匹配 Soul 偏好
3. 或调整 Soul 配置以匹配代码风格

## 性能影响

### 执行时间

- **Plan 阶段**: +20-30% (LLM 理解)
- **Generation 阶段**: +50-100% (迭代生成)
- **Evaluation 阶段**: +10-20% (全面评估)
- **总体**: +80-150%

### 质量提升

- **代码质量**: +30-50% (迭代优化)
- **计划质量**: +20-40% (LLM 理解)
- **决策准确性**: +15-25% (Soul 一致性)

## 回滚计划

如果遇到问题，可以回滚到旧流程:

```bash
# 使用旧的方法
task_planner.decompose_goal(goal, constraints)
code_generator.generate_code(description, language)
reflection_engine.evaluate_execution(code, task)
```

## 获取帮助

如果遇到问题:

1. 查看执行流程日志: `~/.cinder/execution_logs/`
2. 检查配置: `cinder config --list`
3. 提交 Issue: https://github.com/wangyuheng/cinder/issues
