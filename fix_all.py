#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""完整修复 app_new.py 的所有缩进问题"""

with open('app_new.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixes = []

# 修复第44行
if len(lines) > 43 and lines[43].strip() == 'from src.utils.logger import get_logger':
    if not lines[43].startswith('    from'):
        lines[43] = '    from src.utils.logger import get_logger\n'
        fixes.append('Line 44')

# 修复第83行
if len(lines) > 82 and lines[82].strip() == 'else:':
    if not lines[82].startswith('    else:'):
        lines[82] = '    else:\n'
        fixes.append('Line 83')

# 修复第148行
if len(lines) > 147 and 'top_k = st.slider' in lines[147]:
    if lines[147].startswith('        top_k'):
        lines[147] = '    top_k = st.slider("返回结果数", 3, 10, 5)\n'
        fixes.append('Line 148')

# 修复第220行
if len(lines) > 219 and lines[219].strip() == 'else:':
    if not lines[219].startswith('            else:'):
        lines[219] = '            else:\n'
        fixes.append('Line 220')

# 修复第251行
if len(lines) > 250 and 'render_recommend_panel' in lines[250]:
    if lines[250].startswith('        render'):
        lines[250] = '    render_recommend_panel(\n'
        fixes.append('Line 251')

# 修复第252行
if len(lines) > 251 and 'image=st.session_state' in lines[251]:
    if not lines[251].startswith('        image='):
        lines[251] = '        image=st.session_state.get("_active_image_for_infer", image),\n'
        fixes.append('Line 252')

with open('app_new.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

if fixes:
    print(f'✅ 修复了 {len(fixes)} 处: {", ".join(fixes)}')
else:
    print('ℹ️  无需修复')

