# 变更日志

本项目所有值得注意的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.0.0] - 2025-01-04

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

## [1.0.0] - 2024-12-01

### 新增
- 初始版本
- 基础 soul 画像生成
- 简单的聊天界面
- Ollama 后端支持
