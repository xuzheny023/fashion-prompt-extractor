#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo: How to use fabric labels and aliases in UI
演示：如何在UI中使用面料标签和别名
"""
from src.fabric_labels import (
    get_label, get_aliases, search_fabric, 
    format_fabric_name, get_all_fabrics_with_labels
)

print("="*70)
print("面料标签和别名系统演示 / Fabric Labels & Aliases Demo")
print("="*70)

# 演示1：显示面料中文名（用于UI展示）
print("\n【演示1】UI 显示面料中文名：")
print("-"*70)
fabrics = ["denim", "silk", "chiffon", "leather", "cotton"]
for fabric_id in fabrics:
    chinese = get_label(fabric_id)
    print(f"  {fabric_id:<15} → {chinese}")

print("\n💡 在UI中使用：")
print("   label = get_label(fabric_id)  # 获取中文标签")
print("   display_name = f\"{label} ({fabric_id})\"  # 组合显示")

# 演示2：搜索功能（支持中英文和别名）
print("\n" + "="*70)
print("【演示2】搜索功能（支持中文、英文、别名）：")
print("-"*70)
test_queries = [
    "牛仔",      # 中文标签
    "denim",    # 英文ID
    "丹宁",      # 别名
    "silk",     # 英文
    "真丝",      # 中文
    "雪纺",      # 中文（会匹配多个）
    "羊毛呢",    # 别名
]

for query in test_queries:
    results = search_fabric(query)
    if results:
        display = [f"{get_label(r)} ({r})" for r in results]
        print(f"  '{query}' → {', '.join(display)}")
    else:
        print(f"  '{query}' → (无结果)")

print("\n💡 在UI中使用：")
print("   # 用户输入搜索框")
print("   user_input = \"牛仔\"")
print("   results = search_fabric(user_input)")
print("   # 显示结果：[(fabric_id, label), ...]")

# 演示3：别名提示（帮助用户理解）
print("\n" + "="*70)
print("【演示3】别名提示（鼠标悬停或详情页）：")
print("-"*70)
fabrics_with_aliases = ["denim", "silk", "organza", "velvet", "polyester"]
for fabric_id in fabrics_with_aliases:
    label = get_label(fabric_id)
    aliases = get_aliases(fabric_id)
    if aliases:
        print(f"  {label} ({fabric_id})")
        print(f"    别名：{', '.join(aliases)}")
    else:
        print(f"  {label} ({fabric_id})")
        print(f"    别名：(无)")

print("\n💡 在UI中使用：")
print("   # 鼠标悬停显示别名")
print("   aliases = get_aliases(fabric_id)")
print("   tooltip = f\"别名：{', '.join(aliases)}\"")

# 演示4：格式化选项（用于不同场景）
print("\n" + "="*70)
print("【演示4】不同场景的显示格式：")
print("-"*70)
fabric = "denim"
formats = {
    "chinese": "下拉列表、标签",
    "english": "API、日志",
    "both": "详情页（中文优先）",
    "both_reverse": "技术文档（英文优先）"
}

for style, usage in formats.items():
    name = format_fabric_name(fabric, style)
    print(f"  {style:<15} → {name:<25} (用于：{usage})")

print("\n💡 在UI中使用：")
print("   # 根据场景选择格式")
print("   dropdown_label = format_fabric_name(fabric_id, 'chinese')")
print("   detail_label = format_fabric_name(fabric_id, 'both')")

# 演示5：完整列表（用于筛选器、下拉菜单）
print("\n" + "="*70)
print("【演示5】生成UI组件（筛选器/下拉菜单）：")
print("-"*70)
all_fabrics = get_all_fabrics_with_labels()
print(f"  总共 {len(all_fabrics)} 个面料类别")
print(f"\n  前10个示例：")
for fabric_id, label in all_fabrics[:10]:
    print(f"    • {label:<15} ({fabric_id})")

print("\n💡 在UI中使用：")
print("   # 生成下拉菜单选项")
print("   fabrics = get_all_fabrics_with_labels()")
print("   for fabric_id, label in fabrics:")
print("       add_dropdown_option(value=fabric_id, label=label)")

# 演示6：实际应用场景
print("\n" + "="*70)
print("【演示6】实际应用场景示例：")
print("-"*70)

print("\n场景A：显示检索结果")
print("  假设CLIP检索结果：['denim', 'corduroy', 'cotton']")
results = ['denim', 'corduroy', 'cotton']
for i, fabric_id in enumerate(results, 1):
    label = get_label(fabric_id)
    print(f"    {i}. {label} ({fabric_id})")

print("\n场景B：用户搜索 '牛仔'")
query = "牛仔"
search_results = search_fabric(query)
print(f"  搜索 '{query}' 的结果：")
for fabric_id in search_results:
    label = get_label(fabric_id)
    aliases = get_aliases(fabric_id)
    alias_str = f" [别名：{', '.join(aliases)}]" if aliases else ""
    print(f"    • {label} ({fabric_id}){alias_str}")

print("\n场景C：面料标签云（按拼音排序）")
fabrics = get_all_fabrics_with_labels()
print("  ", end="")
for i, (fabric_id, label) in enumerate(fabrics[:20], 1):
    print(f"{label}", end="  ")
    if i % 5 == 0:
        print("\n  ", end="")

print("\n\n" + "="*70)
print("💡 总结：")
print("  1. 使用 get_label() 获取中文显示")
print("  2. 使用 search_fabric() 支持中文搜索")
print("  3. 使用 get_aliases() 显示别名提示")
print("  4. 使用 format_fabric_name() 根据场景选择格式")
print("  5. 使用 get_all_fabrics_with_labels() 生成列表")
print("="*70)


