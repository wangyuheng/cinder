# 安全最佳实践

本文档提供 Cinder 执行器的安全最佳实践指南。

## 目录

1. [安全架构概述](#安全架构概述)
2. [文件系统安全](#文件系统安全)
3. [代码执行安全](#代码执行安全)
4. [数据安全](#数据安全)
5. [安全配置建议](#安全配置建议)

---

## 安全架构概述

Cinder 执行器采用多层安全防护机制：

```
┌─────────────────────────────────────────────────────┐
│                   用户输入                          │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              路径验证层 (Path Validation)            │
│  - 检查路径是否在工作目录内                          │
│  - 检查文件扩展名是否允许                            │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              代码分析层 (Code Analysis)              │
│  - 检测危险代码模式                                  │
│  - 风险一致性评估                                    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              文件操作层 (File Operations)            │
│  - 自动备份                                          │
│  - 安全写入                                          │
└─────────────────────────────────────────────────────┘
```

---

## 文件系统安全

### 工作目录限制

所有文件操作都限制在指定的工作目录内：

```python
# 正确：使用相对路径
cinder execute "创建 main.py"

# 错误：尝试访问工作目录外的文件
cinder execute "创建 /etc/passwd"  # 会被拒绝
```

### 允许的文件类型

只有以下文件类型被允许创建：

| 类型 | 扩展名 | 说明 |
|------|--------|------|
| Python | `.py` | Python 源代码 |
| JavaScript | `.js` | JavaScript 源代码 |
| TypeScript | `.ts` | TypeScript 源代码 |
| Web | `.html`, `.css` | 网页文件 |
| 配置 | `.json`, `.yaml`, `.yml` | 配置文件 |
| 文档 | `.md`, `.txt` | 文档文件 |
| 脚本 | `.sh` | Shell 脚本 |

### 路径遍历防护

系统会检测并拒绝路径遍历攻击：

```bash
# 以下尝试都会被拒绝
../../../etc/passwd
~/../secret_file
./symlink_to_outside
```

---

## 代码执行安全

### 危险代码检测

反思引擎会检测以下危险模式：

| 模式 | 风险等级 | 说明 |
|------|----------|------|
| `eval()` | 高 | 动态执行代码，可能注入恶意代码 |
| `exec()` | 高 | 动态执行代码，可能注入恶意代码 |
| `__import__()` | 中 | 动态导入模块，可能加载恶意模块 |
| `subprocess.call()` | 中 | 执行系统命令，需要谨慎使用 |
| `os.system()` | 高 | 执行系统命令，高风险 |

### 风险一致性检查

代码风险会与用户的 soul 配置进行比对：

```yaml
# soul.meta.yaml
traits:
  risk_tolerance: 30  # 保守型用户

# 如果生成的代码包含 eval()，会触发警告
# 因为保守型用户应避免高风险代码
```

### 安全代码示例

**推荐的安全代码：**

```python
def safe_divide(a: float, b: float) -> float:
    """安全除法，包含错误处理。"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b
```

**应避免的危险代码：**

```python
def unsafe_execute(user_input: str):
    """危险：直接执行用户输入"""
    exec(user_input)  # 不安全！
```

---

## 数据安全

### 敏感信息处理

1. **不要在代码中硬编码敏感信息**

```python
# 错误
API_KEY = "sk-xxxxx"

# 正确：使用环境变量
import os
API_KEY = os.environ.get("API_KEY")
```

2. **配置文件安全**

```yaml
# ~/.cinder/config.yaml
# 不要存储敏感信息

# 正确：使用环境变量引用
database_url: ${DATABASE_URL}
```

### 日志安全

执行日志不记录敏感信息：

- 不记录 API 密钥
- 不记录密码
- 不记录个人身份信息

---

## 安全配置建议

### 保守型配置

适用于生产环境：

```yaml
# ~/.cinder/config.yaml

# 高质量阈值
quality_threshold: 0.9

# 启用备份
enable_backup: true

# 确认删除
confirm_deletion: true

# 启用反思
enable_reflection: true

# 限制文件大小
max_file_size: 524288  # 512KB
```

### 开发环境配置

适用于开发测试：

```yaml
# 开发环境可以更宽松
quality_threshold: 0.6
enable_backup: true
confirm_deletion: false
enable_reflection: true
```

### 禁用危险操作

```yaml
# 完全禁用某些操作
security:
  disable_eval: true
  disable_exec: true
  disable_subprocess: true
```

---

## 安全检查清单

使用 Cinder 前，请确认：

- [ ] 在正确的目录下执行命令
- [ ] 检查生成的代码是否包含危险模式
- [ ] 确认文件扩展名正确
- [ ] 检查 soul 配置是否符合你的风险偏好
- [ ] 启用备份功能
- [ ] 定期检查执行日志

---

## 安全事件响应

如果发现安全问题：

1. **立即停止使用**：停止执行任何新任务
2. **检查备份**：查看 `.cinder_backups/` 目录
3. **审查日志**：检查执行日志中的异常
4. **回滚更改**：使用 `cinder execution rollback` 回滚
5. **报告问题**：在 GitHub Issues 中报告

---

## 参考资料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python 安全最佳实践](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [代码注入防护](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html)
