#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速修复 app_new.py 的所有缩进问题
Quick fix for all indentation issues in app_new.py
"""

def fix_indentation():
    """修复 app_new.py 的缩进问题"""
    
    with open('app_new.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = []
    
    # 修复第44行 - from src.utils.logger import get_logger
    if len(lines) > 43:
        line = lines[43]
        if line.strip() == 'from src.utils.logger import get_logger':
            if not line.startswith('    from'):
                lines[43] = '    from src.utils.logger import get_logger\n'
                fixes_made.append('Line 44: Added indentation to import statement')
    
    # 修复第83行 - else:
    if len(lines) > 82:
        line = lines[82]
        if line.strip() == 'else:':
            if not line.startswith('    else:'):
                lines[82] = '    else:\n'
                fixes_made.append('Line 83: Fixed else indentation (4 spaces)')
    
    # 修复第148行 - top_k = st.slider
    if len(lines) > 147:
        line = lines[147]
        if 'top_k = st.slider' in line and line.startswith('        top_k'):
            lines[147] = '    top_k = st.slider("返回结果数", 3, 10, 5)\n'
            fixes_made.append('Line 148: Fixed top_k slider indentation (4 spaces)')
    
    # 修复第220行 - else:
    if len(lines) > 219:
        line = lines[219]
        if line.strip() == 'else:':
            if not line.startswith('            else:'):
                lines[219] = '            else:\n'
                fixes_made.append('Line 220: Fixed else indentation (12 spaces)')
    
    # 写回文件
    with open('app_new.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # 报告结果
    if fixes_made:
        print('✅ 修复完成 / Fixes applied:')
        for fix in fixes_made:
            print(f'   - {fix}')
    else:
        print('ℹ️  无需修复 / No fixes needed')
    
    return len(fixes_made)

if __name__ == '__main__':
    import sys
    
    print('🔧 快速修复 app_new.py 缩进问题...')
    print('   Quick fixing indentation issues in app_new.py...\n')
    
    try:
        count = fix_indentation()
        
        if count > 0:
            print(f'\n✅ 成功修复 {count} 处问题')
            print(f'   Successfully fixed {count} issue(s)')
            print('\n📝 下一步 / Next steps:')
            print('   1. python -m py_compile app_new.py  # 验证语法')
            print('   2. streamlit run app_new.py         # 启动应用')
        else:
            print('\n✅ 文件已经正确，无需修复')
            print('   File is already correct, no fixes needed')
        
        sys.exit(0)
    
    except Exception as e:
        print(f'\n❌ 错误 / Error: {e}')
        sys.exit(1)

