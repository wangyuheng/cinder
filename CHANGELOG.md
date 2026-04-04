# 变更日志

本项目所有值得注意的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.2.0] - 2026-04-04

### 新增
- 严格 PGE (Plan-Generation-Evaluation) 执行流程
  - 增强的任务规划，使用 LLM 进行目标理解
  - 迭代式代码生成，包含自我评估
  - 全面评估，包含 Soul 一致性检查
  - 严格的阶段分离 (Plan → Generation → Evaluation → Decision)
- 质量阈值配置
  - plan_quality_threshold (默认: 0.7)
  - code_quality_threshold (默认: 0.8)
  - evaluation_quality_threshold (默认: 0.7)
- 迭代生成配置
  - enable_iterative_generation (默认: true)
  - enable_comprehensive_evaluation (默认: true)
- 多维度代码评估
  - 语法质量检查
  - 逻辑质量评估
  - 风格质量评价
  - 文档质量评分
- Soul 一致性检查
  - 风险容忍度对齐
  - 结构偏好对齐
  - 细节导向对齐
- 风险评估功能
  - 安全风险检测
  - 性能风险识别
  - 可维护性风险分析

### 变更
- 重构 AutonomousExecutor 使用严格的阶段分离
- 增强 TaskPlanner，使用 LLM 进行目标理解
- 改进 CodeGenerator，添加迭代生成循环
- 增强 ReflectionEngine，实现全面评估

### 技术细节
- Plan 阶段: decompose_goal_with_validation() 包含质量评分
- Generation 阶段: generate_with_iterations() 包含自我评估
- Evaluation 阶段: evaluate_comprehensive() 包含 Soul 对齐
- Decision 阶段: Evaluation 后基于 Soul 的决策

## [2.1.0] - 2026-04-04

### 新增
- Web Dashboard 管理界面
  - 仪表盘首页显示执行统计和最近活动
  - 执行历史页面支持查看、筛选和详情展示
  - Soul 配置页面支持可视化编辑
  - 决策记录页面展示决策历史和统计
  - 任务触发页面支持手动触发新执行
  - 主题切换功能（默认浅色主题）
- FastAPI 后端 REST API
  - 执行历史 API 端点
  - Soul 配置 API 端点
  - 决策记录 API 端点
  - 任务触发 API 端点
- 一键启动脚本 `scripts/start-web.sh`
  - 自动启动前后端服务
  - 实时彩色日志追踪（青色后端 + 绿色前端）
  - 支持自定义端口配置
  - 优雅停止服务
- Web 相关文档
  - Web 界面使用指南
  - 部署指南更新

### 变更
- 默认主题从深色改为浅色
- 优化启动脚本的日志输出颜色（适合白色背景）
- 更新 README 和相关文档

### 技术栈
- 后端：FastAPI + Uvicorn
- 前端：Next.js 14 + Tailwind CSS + React Query
- 图标：Lucide Icons

## [2.0.0] - 2026-04-04

### 新增
- 使用 Click 框架完全重写 CLI
- 通过 6 个核心问题的交互式 soul 画像生成
- 包含维度解释的 soul 确认工作流
- Soul 调整能力（重新回答问题、手动调整特质、自定义规则）
- 基于 soul 规则的代理决策
- 使用 SQLite 数据库的决策日志
- 决策审查工作流
- 聊天会话中的交互式模式切换
- 多后端支持（Ollama 和 Claude）
- 配置管理系统
- 完整的文档
- 使用 pytest 的测试套件

### 变更
- 命令名从 `cinder-cli` 简化为 `cinder`
- 旧的 `cli.py` 和 `chat.py` 标记为已弃用
- 通过交互式提示改进用户体验

### 功能

#### CLI 命令
- `cinder init`: 通过交互式问题生成 soul 画像
- `cinder confirm`: 查看并确认 soul 画像
- `cinder chat`: 启动与 soul 引导 agent 的对话
- `cinder decisions`: 管理决策日志
- `cinder config`: 管理配置设置

#### Soul 画像
- 6 维度人格评估
- 特质向量计算（13 个特质）
- 决策画像生成
- Agent 行为准则
- 自定义决策规则支持

#### 代理决策
- 风险容忍度规则应用
- 沟通偏好规则
- 决策边界规则
- 置信度评分
- 高风险决策检测
- 不确定决策的人工升级

#### 决策日志
- SQLite 数据库存储决策
- 查询和过滤能力
- 统计和洞察
- 导出为 CSV/JSON
- 旧决策自动归档

## [1.0.0] - 2026-04-04

### 新增
- 初始版本
- 基础 soul 画像生成
- 简单的聊天界面
- Ollama 后端支持
