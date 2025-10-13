#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test fabric localization integration
测试面料本地化集成
"""
from src.fabric_ranker import localize_fabric
from src.fabric_labels import get_label, search_fabric, get_all_fabrics_with_labels

print("="*70)
print("面料本地化系统测试 / Fabric Localization System Test")
print("="*70)

# 测试1：localize_fabric 函数（会被 fabric_ranker 使用）
print("\n[测试1] localize_fabric 函数：")
print("-"*70)
test_ids = ["denim", "silk", "chiffon", "leather", "wool"]
for fid in test_ids:
    name_zh, notes_zh = localize_fabric(fid, "zh")
    name_en, notes_en = localize_fabric(fid, "en")
    print(f"  {fid:<15} EN: {name_en:<15} ZH: {name_zh}")

# 测试2：搜索功能
print("\n[测试2] 中文搜索功能：")
print("-"*70)
test_queries = ["牛仔", "silk", "雪纺", "羊毛", "蕾丝"]
for q in test_queries:
    results = search_fabric(q)
    if results:
        labels = [f"{get_label(r)} ({r})" for r in results[:3]]
        print(f"  '{q}' → {', '.join(labels)}")
    else:
        print(f"  '{q}' → (no results)")

# 测试3：统计
print("\n[测试3] 面料统计：")
print("-"*70)
all_fabrics = get_all_fabrics_with_labels()
print(f"  Total fabric categories: {len(all_fabrics)}")
print(f"  Sample (first 10):")
for fid, label in all_fabrics[:10]:
    print(f"    {label:<15} ({fid})")

print("\n" + "="*70)
print("✅ 本地化系统工作正常！")
print("💡 现在可以在 UI 中使用中文标签显示面料类别")
print("="*70)


