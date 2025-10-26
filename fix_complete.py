#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""完整修复 app_new.py 的所有缩进问题"""

with open('app_new.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixes_made = []

# 修复第44行
if len(lines) > 43 and lines[43].strip() == 'from src.utils.logger import get_logger':
    lines[43] = '    from src.utils.logger import get_logger\n'
    fixes_made.append('Line 44: Added indentation')

# 修复第83行
if len(lines) > 82:
    if lines[82].strip() == 'else:' and not lines[82].startswith('    else:'):
        lines[82] = '    else:\n'
        fixes_made.append('Line 83: Fixed else indentation')

# 修复第148行
if len(lines) > 147:
    if lines[147].strip().startswith('top_k') and lines[147].startswith('        top_k'):
        lines[147] = '    top_k = st.slider("返回结果数", 3, 10, 5)\n'
        fixes_made.append('Line 148: Fixed top_k indentation')

with open('app_new.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

if fixes_made:
    for fix in fixes_made:
        print(f'✅ {fix}')
else:
    print('ℹ️  No fixes needed')

print('✅ Complete')

