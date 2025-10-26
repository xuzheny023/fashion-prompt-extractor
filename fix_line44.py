#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复 app_new.py 第44行缩进"""

with open('app_new.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 检查并修复第44行
if len(lines) > 43:
    line44 = lines[43]
    if line44.strip() == 'from src.utils.logger import get_logger':
        lines[43] = '    from src.utils.logger import get_logger\n'
        print(f'修复前: {repr(line44)}')
        print(f'修复后: {repr(lines[43])}')
    else:
        print(f'第44行内容: {repr(line44)}')
        print('不需要修复或内容不匹配')

with open('app_new.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ 完成')

