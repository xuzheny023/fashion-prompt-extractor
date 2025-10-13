# -*- coding: utf-8 -*-
"""
日志系统测试

用法:
    python tools/test_logger.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger, info, warning, error, debug

print("=" * 60)
print("日志系统测试")
print("=" * 60)

# 测试1: 基本日志级别
print("\n[1/4] 测试基本日志级别:")
log = get_logger("test")
log.debug("这是 DEBUG 日志")
log.info("这是 INFO 日志")
log.success("这是 SUCCESS 日志")
log.warning("这是 WARNING 日志")
log.error("这是 ERROR 日志")

# 测试2: 不同模块
print("\n[2/4] 测试不同模块:")
ui_log = get_logger("ui")
api_log = get_logger("api")
db_log = get_logger("database")

ui_log.info("UI 初始化完成")
api_log.info("API 服务启动")
db_log.warning("数据库连接池接近上限")

# 测试3: 便捷函数
print("\n[3/4] 测试便捷函数:")
info("使用便捷函数记录 INFO", module="app")
warning("使用便捷函数记录 WARNING", module="app")
error("使用便捷函数记录 ERROR", module="app")

# 测试4: 异常记录
print("\n[4/4] 测试异常记录:")
try:
    result = 1 / 0
except ZeroDivisionError:
    log.exception("捕获到异常:")

# 检查日志文件
print("\n[日志文件检查]:")
log_file = Path("logs/app.log")
if log_file.exists():
    size = log_file.stat().st_size
    print(f"  ✓ 日志文件存在: {log_file}")
    print(f"  ✓ 文件大小: {size} 字节")
    print(f"\n  最后 5 行日志:")
    lines = log_file.read_text(encoding='utf-8').strip().split('\n')
    for line in lines[-5:]:
        print(f"    {line}")
else:
    print(f"  ✗ 日志文件不存在: {log_file}")

print("\n" + "=" * 60)
print("✅ 日志系统测试完成")
print("=" * 60)
print("\n💡 提示:")
print("  - 日志文件: logs/app.log")
print("  - 日志级别: INFO (可在 src/config.py 修改)")
print("  - 文件轮转: 单个文件最大 5MB")
print("  - 日志保留: 最近 10 天")


