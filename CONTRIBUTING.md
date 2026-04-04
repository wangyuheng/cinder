# 贡献指南

感谢你对 Cinder 的贡献兴趣！本文档提供贡献的指南和说明。

## 开发环境设置

### 前置要求

- Python 3.10 或更高版本
- pip 或你喜欢的包管理器

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/wangyuheng/cinder.git
cd cinder
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows 上: venv\Scripts\activate
```

3. 安装开发依赖：
```bash
pip install -e ".[dev]"
```

## 开发工作流

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=cinder_cli --cov-report=html

# 运行特定测试文件
pytest tests/test_config.py
```

### 代码格式化

我们使用 Black 和 Ruff 进行代码格式化：

```bash
# 格式化代码
black cinder_cli tests

# 检查代码规范
ruff check cinder_cli tests

# 自动修复代码规范问题
ruff check --fix cinder_cli tests
```

### 类型检查

```bash
mypy cinder_cli
```

## 项目结构

```
cinder/
├── cinder_cli/          # 主包
│   ├── cli.py          # CLI 入口点
│   ├── config.py       # 配置管理
│   ├── database.py     # 数据库操作
│   └── ...             # 其他模块
├── tests/              # 测试套件
├── docs/               # 文档
├── examples/           # 示例文件
└── pyproject.toml      # 项目配置
```

## 编码规范

### 代码风格

- 遵循 PEP 8 指南
- 使用 Black 进行格式化（行长：100）
- 为函数签名使用类型提示
- 为公共函数和类编写文档字符串

### 示例代码风格

```python
def calculate_score(answers: dict[str, str]) -> int:
    """
    根据用户答案计算分数。
    
    Args:
        answers: 问题键到答案值的字典。
        
    Returns:
        计算的分数（整数）。
    """
    score = 0
    for key, value in answers.items():
        score += len(value)
    return score
```

### 提交信息

遵循约定式提交格式：

- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档变更
- `test:` 测试添加/修改
- `refactor:` 代码重构
- `chore:` 维护任务

示例：
```
feat: 添加代理决策模式切换

添加在聊天会话中使用 /proxy 命令切换代理模式的功能。
```

## Pull Request 流程

1. Fork 仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 进行更改
4. 运行测试和代码检查
5. 提交更改
6. 推送到你的 fork
7. 打开 Pull Request

### PR 检查清单

- [ ] 代码遵循项目的风格指南
- [ ] 测试在本地通过
- [ ] 为新功能添加了新测试
- [ ] 文档已更新（如需要）
- [ ] 提交信息遵循约定式格式

## 报告问题

报告问题时，请包含：

1. Python 版本
2. 操作系统
3. 复现步骤
4. 预期行为
5. 实际行为
6. 错误信息/堆栈跟踪

## 许可证

通过贡献，你同意你的贡献将根据 MIT 许可证授权。
