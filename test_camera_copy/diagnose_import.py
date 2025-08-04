#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断导入问题的脚本
"""

import sys
import os

print("=== Python环境诊断 ===")
print(f"Python路径: {sys.executable}")
print(f"虚拟环境: {os.environ.get('VIRTUAL_ENV', '未使用')}")
print(f"当前工作目录: {os.getcwd()}")

print("\n=== sys.path 前10个路径 ===")
for i, path in enumerate(sys.path[:10]):
    print(f"{i}: {path}")

print("\n=== 尝试导入pyorbbecsdk ===")
try:
    import pyorbbecsdk
    print(f"✅ 导入成功")
    print(f"模块位置: {pyorbbecsdk.__file__}")
    
    # 检查可用的属性
    attrs = [attr for attr in dir(pyorbbecsdk) if not attr.startswith('_')]
    print(f"可用属性数量: {len(attrs)}")
    print("前20个属性:", attrs[:20])
    
    # 检查具体的常量
    constants_to_check = ['OB_STREAM_DEPTH', 'OB_STREAM_COLOR', 'Context', 'Pipeline']
    for const in constants_to_check:
        if hasattr(pyorbbecsdk, const):
            print(f"✅ {const}: 存在")
        else:
            print(f"❌ {const}: 不存在")
            
except ImportError as e:
    print(f"❌ 导入失败: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")

print("\n=== 环境变量检查 ===")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', '未设置')}")
print(f"PATH中的相关路径: {[p for p in os.environ.get('PATH', '').split(';') if 'sdk' in p.lower() or 'orbbec' in p.lower()]}")