# Makefile 使用说明

## Python 解释器配置

Makefile 默认使用 `python3`，但你可以自定义：

### 方法 1: 环境变量

```bash
# 使用特定的 Python 版本
export PYTHON=python3.11
make install

# 或临时指定
PYTHON=python3.11 make install
```

### 方法 2: 命令行参数

```bash
make install PYTHON=python3.11
```

### 方法 3: 虚拟环境

如果你在虚拟环境中，Makefile 会自动使用：

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 现在会使用虚拟环境的 Python
make install
```

## 常见问题

### 1. `pip: command not found`

**原因**: 系统中没有 `pip` 命令

**解决**:
```bash
# 使用 python3 -m pip
make install

# 或指定 Python 版本
PYTHON=python3 make install
```

### 2. Python 版本不匹配

**原因**: 项目需要特定的 Python 版本

**解决**:
```bash
# 检查 Python 版本
python3 --version

# 使用特定版本
PYTHON=python3.11 make install
```

### 3. 权限问题

**原因**: 没有权限安装包

**解决**:
```bash
# 使用用户安装
PIP="python3 -m pip install --user" make install

# 或使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
make install
```

## 推荐工作流

### 开发环境设置

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
make install

# 3. 设置开发环境
make dev

# 4. 检查服务
make status
```

### 日常开发

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
make test

# 格式化代码
make format

# 检查代码质量
make lint
```

### 清理环境

```bash
# 清理服务
make clean

# 删除虚拟环境
rm -rf venv
```

## 使用 Invoke 作为替代

如果 Makefile 有问题，可以使用 Invoke：

```bash
# 安装 invoke
python3 -m pip install invoke

# 使用 invoke
inv install
inv dev
inv test
```

## Makefile 变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PYTHON` | `python3` | Python 解释器 |
| `PIP` | `$(PYTHON) -m pip` | pip 命令 |

## 示例

### 使用 Python 3.11

```bash
PYTHON=python3.11 make install
```

### 使用 conda 环境

```bash
# 激活 conda 环境
conda activate cinder

# 使用 conda 的 Python
make install
```

### 使用 pyenv

```bash
# 设置本地 Python 版本
pyenv local 3.11.0

# 安装
make install
```
