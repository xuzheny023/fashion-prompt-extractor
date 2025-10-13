# -*- coding: utf-8 -*-
"""
UI 组件模块
"""
from .analysis_panel import render_analysis_panel
from .recommend_panel import render_recommend_panel
from .confidence_panel import render_confidence_panel
from .actions_panel import render_actions_panel
from .history_panel import render_history_panel

__all__ = [
    'render_analysis_panel',
    'render_recommend_panel',
    'render_confidence_panel',
    'render_actions_panel',
    'render_history_panel',
]

