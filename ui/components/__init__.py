# -*- coding: utf-8 -*-
"""
UI Components Package
每个组件独立导入，失败不影响其他组件
"""

# Re-export panel functions (with graceful failure)
try:
    from .analysis_panel import render_analysis_panel  # noqa: F401
except Exception:
    pass

try:
    from .recommend_panel import render_recommend_panel  # noqa: F401
except Exception:
    pass

try:
    from .confidence_panel import render_confidence_panel  # noqa: F401
except Exception:
    pass

try:
    from .actions_panel import render_actions_panel  # noqa: F401
except Exception:
    pass

try:
    from .history_panel import render_history_panel, save_to_history  # noqa: F401
except Exception:
    pass

__all__ = [
    'render_analysis_panel',
    'render_recommend_panel',
    'render_confidence_panel',
    'render_actions_panel',
    'render_history_panel',
    'save_to_history',
    'debug_components',  # Export debug function
]


def debug_components():
    """
    Temporary debug function to verify component structure.
    TODO: Remove after components are stable.
    
    Returns:
        dict with keys: package_file, exports, tree, error (if any)
    """
    result = {
        'package_file': None,
        'exports': [],
        'tree': [],
        'error': None
    }
    
    try:
        from pathlib import Path
        
        # Get package file path
        result['package_file'] = str(Path(__file__).resolve())
        
        # Get exports (render_* and save_to_history)
        exports = []
        g = globals()
        for name in ['render_analysis_panel', 'render_recommend_panel', 
                     'render_confidence_panel', 'render_actions_panel',
                     'render_history_panel', 'save_to_history']:
            if name in g:
                exports.append(name)
        result['exports'] = sorted(exports)
        
        # Get directory tree
        package_dir = Path(__file__).parent
        if package_dir.exists():
            tree = []
            for item in package_dir.iterdir():
                if item.is_file() and item.suffix == '.py':
                    tree.append(item.name)
            result['tree'] = sorted(tree)
        
    except Exception as e:
        result['error'] = f"{type(e).__name__}: {e}"
    
    return result
