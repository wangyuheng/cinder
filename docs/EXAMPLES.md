# 常见用例示例

本文档提供 Cinder 执行器的常见使用场景示例。

## 目录

1. [创建 Python 项目](#创建-python-项目)
2. [创建 Web 应用](#创建-web-应用)
3. [创建 REST API](#创建-rest-api)
4. [创建命令行工具](#创建命令行工具)
5. [创建数据处理脚本](#创建数据处理脚本)

---

## 创建 Python 项目

### 基础项目结构

```bash
cinder execute "创建一个Python项目，包含主程序和配置文件" --mode dry-run
```

预览输出：
```
任务分解:
  1. 创建项目目录结构
  2. 创建主程序文件
  3. 创建配置文件

复杂度估算:
  总复杂度: 4.5
  预计时间: 22.5 分钟
```

### 带测试的项目

```bash
cinder execute "创建一个带单元测试的Python计算器模块" --mode interactive
```

交互模式会：
1. 显示任务分解
2. 展示生成的代码
3. 询问是否接受每个文件

---

## 创建 Web 应用

### Flask 应用

```bash
cinder execute "创建一个Flask博客应用" \
  --constraint framework=flask \
  --constraint language=python
```

生成的文件结构：
```
project/
├── app.py
├── templates/
│   ├── base.html
│   └── index.html
├── static/
│   └── style.css
└── config.yaml
```

### FastAPI 应用

```bash
cinder execute "创建一个FastAPI用户管理API" \
  --constraint framework=fastapi
```

---

## 创建 REST API

### 基础 API

```bash
cinder execute "创建REST API，支持用户CRUD操作"
```

### 带认证的 API

```bash
cinder execute "创建带JWT认证的REST API" \
  --constraint auth=jwt \
  --constraint database=sqlite
```

---

## 创建命令行工具

### 基础 CLI

```bash
cinder execute "创建一个文件处理命令行工具"
```

### 带子命令的 CLI

```bash
cinder execute "创建一个Git风格的命令行工具，支持多个子命令"
```

---

## 创建数据处理脚本

### 数据转换

```bash
cinder execute "创建一个CSV转JSON的转换脚本"
```

### 数据分析

```bash
cinder execute "创建一个数据分析脚本，生成统计报告"
```

---

## 执行模式选择

### dry-run 模式（推荐先使用）

预览执行内容，不创建实际文件：

```bash
cinder execute "你的目标" --mode dry-run
```

### interactive 模式

每步确认，适合重要项目：

```bash
cinder execute "你的目标" --mode interactive
```

### auto 模式

自动执行，适合简单任务：

```bash
cinder execute "你的目标" --mode auto
```

---

## 查看执行历史

```bash
# 列出最近的执行
cinder execution list

# 查看特定执行详情
cinder execution show 1

# 生成执行报告
cinder execution report
```

---

## 最佳实践

1. **先用 dry-run 预览**：了解将要创建的文件和任务
2. **使用交互模式**：对关键项目进行精细控制
3. **查看执行日志**：跟踪项目历史和变更
4. **配置 soul 文件**：让生成的代码符合你的风格偏好

---

## 示例配置

在 `~/.cinder/config.yaml` 中设置默认偏好：

```yaml
# 默认语言
default_language: python

# 代码风格
code_style:
  indent_size: 4
  max_line_length: 100

# 安全设置
enable_backup: true
confirm_deletion: true
```
