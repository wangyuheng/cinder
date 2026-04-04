# 故障排除指南

本文档提供 Cinder 执行器常见问题的解决方案。

## 目录

1. [安装问题](#安装问题)
2. [执行问题](#执行问题)
3. [Ollama 连接问题](#ollama-连接问题)
4. [文件操作问题](#文件操作问题)
5. [性能问题](#性能问题)

---

## 安装问题

### 问题：Python 版本不兼容

**症状**：
```
ERROR: Package 'cinder-cli' requires Python >=3.10
```

**解决方案**：
```bash
# 检查 Python 版本
python --version

# 如果版本低于 3.10，安装新版本
# macOS
brew install python@3.11

# 创建新的虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate
```

### 问题：依赖安装失败

**症状**：
```
ERROR: Could not find a version that satisfies the requirement...
```

**解决方案**：
```bash
# 更新 pip
pip install --upgrade pip

# 清理缓存重新安装
pip cache purge
pip install -e .
```

---

## 执行问题

### 问题：执行卡住不动

**症状**：命令执行后没有响应

**解决方案**：
1. 检查 Ollama 是否运行：
```bash
ollama list
```

2. 检查模型是否可用：
```bash
ollama pull qwen3.5:9b
```

3. 使用 dry-run 模式测试：
```bash
cinder execute "测试" --mode dry-run
```

### 问题：生成的代码质量差

**症状**：生成的代码不完整或有错误

**解决方案**：
1. 使用交互模式手动审核：
```bash
cinder execute "你的目标" --mode interactive
```

2. 调整配置中的质量阈值：
```yaml
# ~/.cinder/config.yaml
quality_threshold: 0.8
max_iterations: 5
```

3. 指定更具体的约束：
```bash
cinder execute "创建API" --constraint style=google --constraint framework=fastapi
```

---

## Ollama 连接问题

### 问题：无法连接到 Ollama

**症状**：
```
ConnectionError: Cannot connect to Ollama
```

**解决方案**：
1. 启动 Ollama 服务：
```bash
ollama serve
```

2. 检查 Ollama 地址：
```bash
# 默认地址
curl http://localhost:11434/api/tags

# 如果使用自定义地址
export OLLAMA_HOST=http://your-host:11434
```

### 问题：模型不存在

**症状**：
```
Error: model 'qwen3.5:9b' not found
```

**解决方案**：
```bash
# 拉取模型
ollama pull qwen3.5:9b

# 或使用其他模型
cinder execute "目标" --model llama2
```

---

## 文件操作问题

### 问题：路径不在工作目录内

**症状**：
```
ValueError: 路径不在工作目录内
```

**解决方案**：
1. 使用相对路径而非绝对路径
2. 确保在正确的目录下执行命令：
```bash
cd /your/project
cinder execute "目标"
```

### 问题：文件类型不允许

**症状**：
```
ValueError: 不允许的文件类型: .exe
```

**解决方案**：
只允许以下文件类型：
- `.py` - Python
- `.js` - JavaScript
- `.ts` - TypeScript
- `.html` - HTML
- `.css` - CSS
- `.json` - JSON
- `.yaml` / `.yml` - YAML
- `.md` - Markdown
- `.txt` - 纯文本
- `.sh` - Shell 脚本

### 问题：备份恢复失败

**症状**：无法恢复之前的文件版本

**解决方案**：
1. 检查备份目录：
```bash
ls -la .cinder_backups/
```

2. 手动恢复：
```bash
cp .cinder_backups/filename.bak original_location
```

---

## 性能问题

### 问题：执行速度慢

**解决方案**：
1. 使用更快的模型：
```bash
cinder execute "目标" --model qwen2.5:7b
```

2. 减少迭代次数：
```yaml
# ~/.cinder/config.yaml
max_reflection_iterations: 1
```

3. 禁用不必要的检查：
```yaml
enable_reflection: false
auto_format: false
```

### 问题：内存占用高

**解决方案**：
1. 使用较小的模型
2. 清理执行日志：
```bash
cinder execution cleanup --days 7
```

---

## 日志和调试

### 启用详细日志

```bash
# 设置日志级别
export CINDER_LOG_LEVEL=DEBUG

# 执行命令
cinder execute "目标" --mode dry-run
```

### 查看执行日志

```bash
# 查看最近的执行
cinder execution list

# 查看特定执行的详细信息
cinder execution show 1

# 导出执行报告
cinder execution report --output report.md
```

---

## 常见错误代码

| 错误代码 | 描述 | 解决方案 |
|---------|------|---------|
| E001 | 配置文件损坏 | 删除 `~/.cinder/config.yaml` 重新初始化 |
| E002 | 数据库锁定 | 关闭其他 Cinder 进程 |
| E003 | Ollama 超时 | 检查 Ollama 服务状态 |
| E004 | 文件权限错误 | 检查文件权限 |
| E005 | 磁盘空间不足 | 清理磁盘空间 |

---

## 获取帮助

如果以上方案无法解决问题：

1. 查看 GitHub Issues: https://github.com/wangyuheng/cinder/issues
2. 提交新 Issue 并附上：
   - 错误信息
   - 执行命令
   - 配置文件内容
   - Python 和 Ollama 版本
