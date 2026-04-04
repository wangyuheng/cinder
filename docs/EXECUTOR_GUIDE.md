# Cinder 执行器使用指南

## 概述

Cinder 执行器是一个强大的自主任务执行系统，能够将自然语言描述的目标转化为实际的代码文件。它结合了任务规划、代码生成、反思评估和文件操作，提供端到端的自动化体验。

## 核心概念

### 1. 执行模式

执行器支持三种执行模式：

- **auto（自动模式）**: 完全自动执行，无需用户干预
- **interactive（交互模式）**: 在关键步骤询问用户确认
- **dry-run（预览模式）**: 仅显示执行计划，不创建实际文件

### 2. 执行流程

```
用户目标
  ↓
任务分解 (Task Planner)
  ↓
代码生成 (Code Generator)
  ↓
反思评估 (Reflection Engine)
  ↓
文件创建 (File Operations)
  ↓
日志记录 (Execution Logger)
```

### 3. Soul 画像集成

执行器会根据你的 soul 画像进行决策：

- **风险容忍度**: 影响代码的风险级别
- **沟通风格**: 影响代码注释和文档风格
- **结构需求**: 影响代码组织方式

## 快速开始

### 基础用法

```bash
# 执行简单目标
cinder execute "创建一个Python Hello World程序"

# 预览执行计划
cinder execute "做个记账web应用" --mode dry-run

# 交互式执行
cinder execute "创建API" --mode interactive
```

### 指定约束

```bash
# 指定编程语言
cinder execute "创建一个脚本" --language python

# 指定框架
cinder execute "创建Web API" --framework fastapi

# 添加多个约束
cinder execute "创建用户管理系统" \
  --framework fastapi \
  --language python \
  --constraint "database=postgresql" \
  --constraint "auth=jwt"
```

## 使用场景

### 场景 1: 创建 Python 脚本

```bash
cinder execute "创建一个计算斐波那契数列的Python函数"
```

**执行过程：**
1. 识别为 Python 脚本任务
2. 生成斐波那契函数代码
3. 基于你的 soul 画像评估代码
4. 创建 `main.py` 文件

### 场景 2: 创建 Web 应用

```bash
cinder execute "做个记账web应用" --mode dry-run
```

**任务分解：**
1. 创建项目目录结构
2. 创建后端 API 框架
3. 创建前端页面
4. 创建配置文件

### 场景 3: 创建 API 项目

```bash
cinder execute "创建用户管理API" --framework fastapi --language python
```

**生成的文件：**
- `api.py` - FastAPI 主文件
- `models.py` - 数据模型
- `API.md` - API 文档

## 高级功能

### 1. 执行历史管理

```bash
# 查看执行历史
cinder execution list

# 查看特定执行的详细信息
cinder execution show 1

# 导出执行详情为 JSON
cinder execution show 1 --format json
```

### 2. 执行回滚

如果对执行结果不满意，可以回滚：

```bash
# 回滚特定执行创建的所有文件
cinder execution rollback 1
```

**注意：** 回滚会删除该执行创建的所有文件，但会保留备份。

### 3. 自定义配置

创建 `executor_config.yaml` 文件自定义执行器行为：

```yaml
# 执行策略
execution_timeout: 300
max_reflection_iterations: 3
quality_threshold: 0.7

# 安全设置
working_directory: "."
enable_backup: true
confirm_deletion: true

# 代码生成
default_language: "python"
code_style:
  indent_size: 4
  max_line_length: 100
```

## 最佳实践

### 1. 明确目标描述

**好的描述：**
```bash
cinder execute "创建一个使用FastAPI的用户认证API，支持注册、登录和JWT令牌"
```

**不好的描述：**
```bash
cinder execute "做个API"
```

### 2. 使用预览模式

在正式执行前，先用 dry-run 模式预览：

```bash
cinder execute "复杂的目标" --mode dry-run
```

### 3. 提供足够的约束

```bash
cinder execute "创建Web应用" \
  --framework fastapi \
  --language python \
  --constraint "database=postgresql" \
  --constraint "frontend=react"
```

### 4. 定期查看执行历史

```bash
cinder execution list --limit 20
```

### 5. 利用 Soul 画像

确保你的 soul 画像准确反映你的偏好：

```bash
# 生成或更新 soul 画像
cinder init

# 确认 soul 画像
cinder confirm
```

## 故障排除

### 问题 1: 代码生成失败

**症状：** 生成的代码有语法错误

**解决方案：**
```bash
# 使用交互模式，手动审查代码
cinder execute "目标" --mode interactive

# 或降低质量阈值
# 在配置文件中设置 quality_threshold: 0.6
```

### 问题 2: 文件创建失败

**症状：** 权限错误或路径错误

**解决方案：**
```bash
# 检查工作目录权限
ls -la .

# 使用绝对路径
cinder execute "目标" --constraint "output_dir=/tmp/project"
```

### 问题 3: 执行超时

**症状：** 执行时间过长

**解决方案：**
```bash
# 在配置文件中增加超时时间
execution_timeout: 600  # 10 分钟
```

### 问题 4: Soul 画像不匹配

**症状：** 生成的代码风格不符合预期

**解决方案：**
```bash
# 重新生成 soul 画像
cinder init

# 或手动调整 soul.meta.yaml
cinder confirm
```

## 安全考虑

### 1. 工作目录限制

执行器默认只能在当前工作目录及其子目录中创建文件。

### 2. 文件类型限制

只允许创建特定类型的文件：
- `.py`, `.js`, `.ts` - 代码文件
- `.html`, `.css` - 前端文件
- `.json`, `.yaml`, `.yml` - 配置文件
- `.md`, `.txt` - 文档文件

### 3. 备份机制

修改或删除文件前，执行器会自动创建备份：
```
.cinder_backups/
  ├── main.py.20250104_120000.bak
  └── config.yaml.20250104_120100.bak
```

### 4. 敏感信息保护

不要在目标描述中包含敏感信息：
```bash
# 不好的做法
cinder execute "创建连接到 postgresql://user:password@localhost/db 的API"

# 好的做法
cinder execute "创建数据库连接配置，使用环境变量"
```

## 性能优化

### 1. 启用缓存

在配置文件中启用缓存：
```yaml
enable_cache: true
cache_directory: ".cinder/cache"
cache_expiration: 3600
```

### 2. 并行执行

对于独立任务，启用并行执行：
```yaml
enable_parallel_execution: true
```

### 3. 减少反思迭代

对于简单任务，减少反思迭代次数：
```yaml
max_reflection_iterations: 1
```

## 示例项目

### 示例 1: 命令行工具

```bash
cinder execute "创建一个命令行工具，支持文件重命名功能" \
  --language python \
  --constraint "cli_framework=click"
```

### 示例 2: REST API

```bash
cinder execute "创建图书管理REST API" \
  --framework fastapi \
  --language python \
  --constraint "database=sqlite" \
  --constraint "auth=basic"
```

### 示例 3: Web 前端

```bash
cinder execute "创建待办事项Web应用前端" \
  --language javascript \
  --constraint "framework=react" \
  --constraint "styling=tailwind"
```

## 下一步

- 查看 [配置示例](executor_config.yaml) 了解更多配置选项
- 查看 [故障排除指南](TROUBLESHOOTING.md) 解决常见问题
- 查看 [API 文档](API.md) 了解内部实现

## 反馈与支持

如果遇到问题或有改进建议：
1. 查看 [故障排除指南](TROUBLESHOOTING.md)
2. 提交 Issue 到 GitHub
3. 查看执行日志获取详细信息
