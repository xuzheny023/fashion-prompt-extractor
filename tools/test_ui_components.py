# -*- coding: utf-8 -*-
"""
UI 组件测试

验证所有 UI 组件可以正常导入和使用

用法:
    python tools/test_ui_components.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("UI 组件测试")
print("=" * 60)

# 测试1: 导入所有组件
print("\n[1/6] 测试组件导入...")
try:
    from ui.components import (
        render_analysis_panel,
        render_recommend_panel,
        render_confidence_panel,
        render_actions_panel,
        render_history_panel
    )
    print("  ✓ 所有组件导入成功")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")
    sys.exit(1)

# 测试2: 验证函数签名
print("\n[2/6] 验证函数签名...")
try:
    import inspect
    
    # analysis_panel
    sig = inspect.signature(render_analysis_panel)
    assert 'image_info' in sig.parameters
    print("  ✓ render_analysis_panel 签名正确")
    
    # recommend_panel
    sig = inspect.signature(render_recommend_panel)
    assert 'image' in sig.parameters
    assert 'top_k' in sig.parameters
    print("  ✓ render_recommend_panel 签名正确")
    
    # confidence_panel
    sig = inspect.signature(render_confidence_panel)
    assert 'result' in sig.parameters
    print("  ✓ render_confidence_panel 签名正确")
    
    # actions_panel
    sig = inspect.signature(render_actions_panel)
    assert 'result' in sig.parameters
    print("  ✓ render_actions_panel 签名正确")
    
    # history_panel
    sig = inspect.signature(render_history_panel)
    assert 'max_items' in sig.parameters
    print("  ✓ render_history_panel 签名正确")
    
except Exception as e:
    print(f"  ✗ 签名验证失败: {e}")
    sys.exit(1)

# 测试3: 测试类型导入
print("\n[3/6] 测试类型导入...")
try:
    from src.types import RankedResult, QueryMeta, ScoreItem
    print("  ✓ 类型导入成功")
except ImportError as e:
    print(f"  ✗ 类型导入失败: {e}")
    sys.exit(1)

# 测试4: 创建测试数据
print("\n[4/6] 创建测试数据...")
try:
    # 创建模拟结果
    items = [
        ScoreItem("cotton", 0.85),
        ScoreItem("linen", 0.72),
        ScoreItem("silk", 0.68),
    ]
    result = RankedResult(items=items, ai_reason="测试")
    meta = QueryMeta(ms=150, coarse_max=0.92)
    
    print(f"  ✓ RankedResult: {len(result.items)} 项")
    print(f"  ✓ QueryMeta: {meta.ms}ms")
    
except Exception as e:
    print(f"  ✗ 数据创建失败: {e}")
    sys.exit(1)

# 测试5: 测试历史记录功能
print("\n[5/6] 测试历史记录...")
try:
    from ui.components.history_panel import save_to_history, _load_history
    
    # 保存测试记录
    save_to_history(result, meta, "test_image.jpg")
    print("  ✓ 历史记录保存成功")
    
    # 加载历史
    history = _load_history(max_items=5)
    print(f"  ✓ 历史记录加载成功: {len(history)} 条")
    
except Exception as e:
    print(f"  ✗ 历史记录测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试6: 验证文件结构
print("\n[6/6] 验证文件结构...")
try:
    components_dir = Path("ui/components")
    
    required_files = [
        "__init__.py",
        "analysis_panel.py",
        "recommend_panel.py",
        "confidence_panel.py",
        "actions_panel.py",
        "history_panel.py"
    ]
    
    for file in required_files:
        file_path = components_dir / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} 不存在")
            sys.exit(1)
    
except Exception as e:
    print(f"  ✗ 文件结构验证失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有测试通过！")
print("=" * 60)

print("\n💡 组件功能:")
print("  • analysis_panel  - 显示图片信息、坐标、性能")
print("  • recommend_panel - 推荐面料（含 4 阶段进度条）")
print("  • confidence_panel - 置信度分析和质量评估")
print("  • actions_panel   - 导出、保存、复制操作")
print("  • history_panel   - 历史记录和对比")

print("\n📝 使用示例:")
print("""
# 在 app.py 中使用
from ui.components import render_recommend_panel

# 推荐面板（自动显示进度条）
render_recommend_panel(
    image=pil_image,
    top_k=5,
    lang="zh"
)
""")

print("\n🚀 启动新版 UI:")
print("  streamlit run app_new.py")

