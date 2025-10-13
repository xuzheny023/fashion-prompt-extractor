# -*- coding: utf-8 -*-
"""
配置模块测试

用法:
    python tools/test_config.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import cfg, check_vector_bank, get_cache_dir, is_ai_enabled

print("=" * 60)
print("配置模块测试")
print("=" * 60)

# 基础路径
print("\n[1/5] 基础路径:")
print(f"  ROOT: {cfg.ROOT}")
print(f"  DATA_DIR: {cfg.DATA_DIR}")
print(f"  CACHE_DIR: {cfg.CACHE_DIR}")
print(f"  ✓ 目录{'存在' if cfg.DATA_DIR.exists() else '不存在'}")

# 向量库
print("\n[2/5] 向量库:")
print(f"  FABRIC_BANK: {cfg.FABRIC_BANK}")
print(f"  存在: {cfg.FABRIC_BANK.exists()}")
print(f"  FABRIC_CENTROIDS: {cfg.FABRIC_CENTROIDS}")
print(f"  存在: {cfg.FABRIC_CENTROIDS.exists()}")
print(f"  ✓ 向量库状态: {'✓ 正常' if check_vector_bank() else '✗ 未构建'}")

# 检索参数
print("\n[3/5] 检索参数:")
print(f"  MIN_SAMPLES: {cfg.MIN_SAMPLES}")
print(f"  TOPC (粗排候选数): {cfg.TOPC}")
print(f"  TOPK (返回结果数): {cfg.TOPK}")
print(f"  LOW_CONF (低置信度): {cfg.LOW_CONF}")
print(f"  CLOSE_GAP (精排阈值): {cfg.CLOSE_GAP}")

# AI 复核
print("\n[4/5] AI 复核:")
print(f"  AI_BACKEND: {cfg.AI_BACKEND}")
print(f"  启用状态: {'✓ 启用' if is_ai_enabled() else '✗ 未启用'}")
if cfg.AI_BACKEND == "openai":
    print(f"  OPENAI_MODEL: {cfg.OPENAI_MODEL}")
    print(f"  API_KEY: {'已设置' if cfg.OPENAI_API_KEY else '未设置'}")
elif cfg.AI_BACKEND == "ollama":
    print(f"  OLLAMA_MODEL: {cfg.OLLAMA_MODEL}")
    print(f"  BASE_URL: {cfg.OLLAMA_BASE_URL}")

# 功能开关
print("\n[5/5] 功能开关:")
print(f"  ENABLE_CLIP: {cfg.ENABLE_CLIP}")
print(f"  ENABLE_FAISS: {cfg.ENABLE_FAISS}")
print(f"  ENABLE_CACHE: {cfg.ENABLE_CACHE}")
print(f"  ENABLE_PROGRESS: {cfg.ENABLE_PROGRESS}")

# 测试便捷函数
print("\n[便捷函数测试]:")
test_cache = get_cache_dir("test")
print(f"  get_cache_dir('test'): {test_cache}")
print(f"  目录存在: {test_cache.exists()}")

print("\n" + "=" * 60)
print("✅ 配置模块测试完成")
print("=" * 60)
print("\n💡 提示:")
print("  - 修改配置: 编辑 .env 文件")
print("  - 环境变量: 直接设置环境变量覆盖")
print("  - 默认值: 见 src/config.py")


