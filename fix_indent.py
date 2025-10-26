#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""临时脚本：修复 app_new.py 的缩进问题"""

with open('app_new.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复第168行的缩进
if lines[167].strip().startswith('except Exception'):
    lines[167] = '        except Exception as e:\n'
    lines[168] = '            st.error(f"❌ 图片加载失败: {e}")\n'
    
with open('app_new.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
    
print('✅ Fixed line 168-169 indentation')

