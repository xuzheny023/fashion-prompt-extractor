# -*- coding: utf-8 -*-
"""
快速验证类型定义

用法:
    python tools/verify_types.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🔍 验证标准化数据类型...")

# 测试导入
try:
    from src.types import ScoreItem, RankedResult, QueryMeta
    print("✓ 导入成功")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试基本功能
try:
    item = ScoreItem("test", 0.5)
    result = RankedResult(items=[item])
    meta = QueryMeta(ms=100)
    print("✓ 基本功能正常")
except Exception as e:
    print(f"✗ 基本功能异常: {e}")
    sys.exit(1)

# 测试 __all__ 导出
try:
    from src.types import __all__
    expected = {'ScoreItem', 'RankedResult', 'QueryMeta'}
    actual = set(__all__)
    if expected == actual:
        print(f"✓ __all__ 导出正确: {__all__}")
    else:
        print(f"✗ __all__ 不匹配")
        print(f"  期望: {expected}")
        print(f"  实际: {actual}")
        sys.exit(1)
except Exception as e:
    print(f"✗ __all__ 检查失败: {e}")
    sys.exit(1)

print("\n✅ 所有验证通过！")
print("\n💡 下一步:")
print("  1. 查看使用指南: docs/TYPES_GUIDE.md")
print("  2. 运行完整测试: python tools/test_types.py")
print("  3. 开始迁移现有代码")

