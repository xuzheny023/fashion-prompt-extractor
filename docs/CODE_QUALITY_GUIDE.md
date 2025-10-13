# 代码质量指南

## 📦 工具配置

本项目使用以下工具保证代码质量：

- **Black** - 代码格式化
- **Ruff** - 快速 Lint 检查
- **EditorConfig** - 编辑器统一配置

---

## 🔧 配置文件

### pyproject.toml

**Black 配置：**
- 行宽：100
- 目标版本：Python 3.10+
- 排除：venv, build, dist 等

**Ruff 配置：**
- 行宽：100
- 启用规则：E, W, F, I, N, UP, B, C4
- 忽略：E501（行太长，由 Black 处理）

### .editorconfig

**统一配置：**
- 编码：UTF-8
- 缩进：4 空格（Python）
- 换行：LF
- 尾部空格：自动删除

---

## 🚀 使用方法

### 方法1: PowerShell 脚本（推荐）

```powershell
# 运行格式化脚本
.\scripts\format.ps1
```

**功能：**
- ✅ 自动检查依赖
- ✅ 运行 Black 格式化
- ✅ 运行 Ruff 检查并修复
- ✅ 显示统计信息

---

### 方法2: 手动运行

#### 安装工具

```bash
# 安装 Black 和 Ruff
.\venv\Scripts\pip.exe install black ruff
```

#### 运行 Black

```bash
# 格式化所有 Python 文件
.\venv\Scripts\python.exe -m black .

# 只检查不修改
.\venv\Scripts\python.exe -m black . --check

# 查看差异
.\venv\Scripts\python.exe -m black . --diff
```

#### 运行 Ruff

```bash
# 检查并自动修复
.\venv\Scripts\python.exe -m ruff check . --fix

# 只检查不修复
.\venv\Scripts\python.exe -m ruff check .

# 查看所有问题
.\venv\Scripts\python.exe -m ruff check . --output-format=full
```

---

## 📋 代码规范

### 格式化规范（Black）

#### 行宽

```python
# ✅ 好 - 行宽 <= 100
def my_function(arg1, arg2, arg3):
    return arg1 + arg2 + arg3

# ❌ 差 - 行宽 > 100
def my_function_with_very_long_name_that_exceeds_one_hundred_characters(argument1, argument2, argument3):
    pass
```

#### 字符串引号

```python
# ✅ 好 - 使用双引号
message = "Hello, World!"

# ✅ 也可以 - 单引号（Black 会保留）
message = 'Hello, World!'
```

#### 导入排序

```python
# ✅ 好 - 标准库 → 第三方 → 本地
import os
import sys

import numpy as np
import torch

from src.config import cfg
from src.types import ScoreItem
```

---

### Lint 规范（Ruff）

#### 未使用的导入

```python
# ❌ 差
import os  # 未使用
import sys

def main():
    print("Hello")

# ✅ 好
import sys

def main():
    print("Hello")
```

#### 未使用的变量

```python
# ❌ 差
def calculate(x, y):
    result = x + y  # 未使用
    return x * y

# ✅ 好
def calculate(x, y):
    return x * y
```

#### 命名规范

```python
# ❌ 差
def MyFunction():  # 函数名应该小写
    pass

MyVariable = 10  # 变量名应该小写

# ✅ 好
def my_function():
    pass

my_variable = 10
```

---

## 🔍 常见问题

### 问题1: E501 - 行太长

**说明：** 由 Black 自动处理，Ruff 已配置忽略

**解决：** 运行 Black 格式化

```bash
.\venv\Scripts\python.exe -m black .
```

### 问题2: F401 - 未使用的导入

**说明：** 导入了但未使用的模块

**解决：**
```python
# 删除未使用的导入
# import unused_module  # 删除这行

# 或在 __init__.py 中保留（已配置忽略）
from .module import something  # __init__.py 中允许
```

### 问题3: I001 - 导入顺序错误

**说明：** 导入顺序不符合规范

**解决：** Ruff 会自动修复
```bash
.\venv\Scripts\python.exe -m ruff check . --fix
```

---

## 📝 Git 工作流

### 提交前检查

```bash
# 1. 格式化代码
.\venv\Scripts\python.exe -m black .

# 2. Lint 检查
.\venv\Scripts\python.exe -m ruff check . --fix

# 3. 提交
git add .
git commit -m "chore: format & lint (black/ruff) + config"
```

### Pre-commit Hook（可选）

创建 `.git/hooks/pre-commit`：

```bash
#!/bin/sh
# 提交前自动格式化

echo "Running Black..."
.\venv\Scripts\python.exe -m black .

echo "Running Ruff..."
.\venv\Scripts\python.exe -m ruff check . --fix

git add -u
```

---

## 🎯 最佳实践

### 1. 定期格式化

```bash
# 每天工作结束前
.\scripts\format.ps1
```

### 2. 提交前检查

```bash
# 提交前运行
.\venv\Scripts\python.exe -m black . --check
.\venv\Scripts\python.exe -m ruff check .
```

### 3. CI/CD 集成

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install black ruff
      - name: Run Black
        run: black . --check
      - name: Run Ruff
        run: ruff check .
```

---

## 📊 配置详情

### Black 配置

```toml
[tool.black]
line-length = 100
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.venv
  | venv
  | build
  | dist
)/
'''
```

### Ruff 配置

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]

ignore = [
    "E501",  # line too long
    "B008",  # function calls in defaults
]
```

### EditorConfig

```ini
[*.py]
indent_style = space
indent_size = 4
max_line_length = 100
charset = utf-8
```

---

## 🔗 相关资源

- [Black 文档](https://black.readthedocs.io/)
- [Ruff 文档](https://docs.astral.sh/ruff/)
- [EditorConfig](https://editorconfig.org/)
- [PEP 8](https://peps.python.org/pep-0008/)

---

## ✅ 检查清单

提交代码前：

- [ ] 运行 Black 格式化
- [ ] 运行 Ruff 检查
- [ ] 无 Lint 错误
- [ ] 代码行宽 <= 100
- [ ] 导入顺序正确
- [ ] 无未使用的导入/变量

---

✅ **代码质量工具已配置！** 保持代码整洁和一致性。 🎉

