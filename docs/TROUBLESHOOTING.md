# 故障排除指南

## 常见问题

### 1. 安装问题

#### 问题：找不到 cinder 命令

**症状**：
```bash
command not found: cinder
```

**解决方案**：
```bash
# 确保已安装依赖
pip install -r requirements.txt

# 或以开发模式安装
pip install -e .

# 验证安装
which cinder
```

#### 问题：依赖冲突

**症状**：
```
ERROR: pip's dependency resolver does not currently take into account all the packages...
```

**解决方案**：
```bash
# 创建新的虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 重新安装
pip install -r requirements.txt
```

### 2. Soul 生成问题

#### 问题：问题显示乱码

**症状**：终端显示乱码或问号

**解决方案**：
```bash
# 确保终端支持 UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 或使用支持中文的终端设置
```

#### 问题：无法保存 soul 文件

**症状**：
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**：
```bash
# 检查目录权限
ls -la .

# 使用有权限的目录
cinder init --output ~/my-soul.md
```

#### 问题：会话恢复失败

**症状**：使用 --resume 后从头开始

**解决方案**：
```bash
# 检查会话文件是否存在
ls -la .cinder_session.json

# 如果文件损坏，删除并重新开始
rm .cinder_session.json
cinder init
```

### 3. 聊天问题

#### 问题：Ollama 连接失败

**症状**：
```
ConnectionError: Cannot connect to Ollama
```

**解决方案**：
```bash
# 确保 Ollama 服务正在运行
ollama serve

# 检查模型是否已下载
ollama list

# 如果没有，下载模型
ollama pull qwen3.5:9b
```

#### 问题：Claude CLI 未找到

**症状**：
```
FileNotFoundError: Claude CLI command not found
```

**解决方案**：
```bash
# 安装 Claude CLI
npm install -g @anthropic-ai/claude-cli

# 或指定 Claude CLI 路径
cinder chat --backend claude --claude-command /path/to/claude
```

#### 问题：代理模式不工作

**症状**：代理模式启用但没有自动决策

**解决方案**：
```bash
# 确保已生成并确认 soul
cinder confirm

# 检查 soul.meta.yaml 中的 confirmed 字段
cat soul.meta.yaml | grep confirmed

# 如果未确认，运行确认流程
cinder confirm
```

### 4. 决策日志问题

#### 问题：数据库锁定

**症状**：
```
sqlite3.OperationalError: database is locked
```

**解决方案**：
```bash
# 确保没有其他进程在使用数据库
lsof ~/.cinder/decisions.db

# 如果有，关闭其他进程或删除锁文件
rm ~/.cinder/decisions.db-wal
rm ~/.cinder/decisions.db-shm
```

#### 问题：决策日志过大

**症状**：数据库文件占用大量空间

**解决方案**：
```bash
# 清理旧决策
cinder decisions clean --older-than 30

# 导出并清理
cinder decisions export --format json --output backup.json
cinder decisions clean --older-than 0
```

### 5. 配置问题

#### 问题：配置文件损坏

**症状**：配置加载失败

**解决方案**：
```bash
# 重置配置
cinder config --reset

# 或手动删除配置文件
rm ~/.cinder/config.yaml
```

#### 问题：配置不生效

**症状**：修改配置后行为未改变

**解决方案**：
```bash
# 检查当前配置
cinder config --list

# 确保使用正确的配置文件路径
cat ~/.cinder/config.yaml
```

### 6. 向后兼容问题

#### 问题：旧脚本显示弃用警告

**症状**：
```
DeprecationWarning: cli.py is deprecated
```

**解决方案**：
```bash
# 这是正常的，提示使用新命令
# 迁移到新命令
cinder init  # 替代 python cli.py
cinder chat  # 替代 python chat.py
```

### 7. 性能问题

#### 问题：响应缓慢

**症状**：命令执行很慢

**解决方案**：
```bash
# 使用更快的模型
cinder chat --model qwen3.5:3b

# 降低温度参数
cinder chat --temperature 0.1

# 禁用日志（如果不需要）
cinder chat --no-logging
```

#### 问题：内存占用高

**症状**：Python 进程占用大量内存

**解决方案**：
```bash
# 定期清理决策日志
cinder decisions clean --older-than 30

# 使用较小的模型
cinder chat --model qwen3.5:3b
```

## 调试技巧

### 启用详细日志

```bash
# 设置日志级别
export CINDER_LOG_LEVEL=DEBUG

# 运行命令
cinder init
```

### 检查系统状态

```bash
# 查看配置
cinder config --list

# 查看决策统计
cinder decisions stats

# 查看当前模式
cinder chat
# 然后输入 /mode
```

### 数据恢复

```bash
# 备份 soul 文件
cp soul.md soul.md.backup
cp soul.meta.yaml soul.meta.yaml.backup

# 备份决策日志
cinder decisions export --format json --output decisions-backup.json
```

## 获取帮助

如果以上方法都无法解决问题：

1. 查看文档：`cinder --help`
2. 查看命令帮助：`cinder <command> --help`
3. 提交 Issue：https://github.com/your-repo/cinder/issues
4. 提供以下信息：
   - 操作系统版本
   - Python 版本
   - 完整的错误信息
   - 复现步骤
