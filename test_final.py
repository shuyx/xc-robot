#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试HTML文件读取功能
"""

import os
import sys
from PyQt5.QtWidgets import QApplication

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

from gui.web_main_window import WebBridge

def test_final():
    """最终测试"""
    
    print("=== 最终测试HTML文件读取 ===")
    
    # 创建Qt应用程序
    app = QApplication(sys.argv)
    
    # 创建WebBridge实例
    bridge = WebBridge()
    
    # 测试README.md
    filename = "README.md"
    print(f"\n--- 测试文件: {filename} ---")
    
    try:
        html_content = bridge.readHtmlFile(filename)
        
        if html_content and len(html_content) > 0:
            print(f"✓ 成功读取HTML文件，内容长度: {len(html_content)}")
            
            # 检查关键元素
            checks = [
                ('<style>', '包含CSS样式'),
                ('<h1', '包含H1标题'),
                ('<h2', '包含H2标题'),
                ('TOC', '包含目录'),
                ('xc-robot', '包含项目名称')
            ]
            
            for check, desc in checks:
                if check in html_content:
                    print(f"  ✓ {desc}")
                else:
                    print(f"  ✗ 缺少: {desc}")
            
            print(f"  前300个字符:\n{html_content[:300]}...")
            
        else:
            print(f"✗ 读取失败")
            
    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_final()