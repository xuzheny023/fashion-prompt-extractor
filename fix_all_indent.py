#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复 app_new.py 所有缩进问题"""

with open('app_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有已知的缩进问题
fixes = [
    # 第44行
    ('# 日志和图标\ntry:\nfrom src.utils.logger import get_logger',
     '# 日志和图标\ntry:\n    from src.utils.logger import get_logger'),
    
    # 第83行
    ('        scale = 1.0\nelse:\n        # Image was scaled down',
     '        scale = 1.0\n    else:\n        # Image was scaled down'),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f'✅ 修复: {old[:30]}...')

with open('app_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 所有修复完成')

