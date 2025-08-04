#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python版本的环境设置脚本
自动配置Orbbec SDK所需的环境变量
"""

import os
import sys
from pathlib import Path

def setup_orbbec_environment():
    """设置Orbbec SDK环境"""
    
    # 获取SDK根目录
    sdk_root = Path(__file__).parent.absolute()
    
    print(f"SDK根目录: {sdk_root}")
    
    # 1. 设置PYTHONPATH
    pythonpath = os.environ.get('PYTHONPATH', '')
    if str(sdk_root) not in pythonpath:
        if pythonpath:
            os.environ['PYTHONPATH'] = str(sdk_root) + ';' + pythonpath
        else:
            os.environ['PYTHONPATH'] = str(sdk_root)
        print(f"✅ 设置PYTHONPATH: {os.environ['PYTHONPATH']}")
    
    # 2. 添加到sys.path
    if str(sdk_root) not in sys.path:
        sys.path.insert(0, str(sdk_root))
        print(f"✅ 添加到sys.path: {sdk_root}")
    
    # 3. 设置DLL路径
    dll_paths = [
        sdk_root / "sdk" / "lib" / "win_x64",
        sdk_root / "sdk" / "lib" / "win_x64" / "extensions" / "depthengine",
        sdk_root / "sdk" / "lib" / "win_x64" / "extensions" / "filters", 
        sdk_root / "sdk" / "lib" / "win_x64" / "extensions" / "firmwareupdater",
        sdk_root / "sdk" / "lib" / "win_x64" / "extensions" / "frameprocessor"
    ]
    
    current_path = os.environ.get('PATH', '')
    path_modified = False
    
    for dll_path in dll_paths:
        if dll_path.exists() and str(dll_path) not in current_path:
            current_path = str(dll_path) + ';' + current_path
            path_modified = True
            print(f"✅ 添加DLL路径: {dll_path}")
            
            # 对于Python 3.8+，也使用add_dll_directory
            try:
                os.add_dll_directory(str(dll_path))
                print(f"✅ 添加DLL目录: {dll_path}")
            except AttributeError:
                # Python < 3.8 不支持 add_dll_directory
                pass
    
    if path_modified:
        os.environ['PATH'] = current_path
    
    print("🎉 Orbbec SDK环境配置完成!")
    return True

def test_import():
    """测试SDK导入"""
    try:
        from pyorbbecsdk import *
        print("✅ pyorbbecsdk导入成功!")
        
        # 测试设备连接
        ctx = Context()
        device_list = ctx.query_devices()
        device_count = device_list.get_count()
        print(f"发现 {device_count} 个设备")
        
        return True
    except Exception as e:
        print(f"❌ SDK导入失败: {e}")
        return False

if __name__ == "__main__":
    print("=== Orbbec SDK 环境配置工具 ===")
    
    if setup_orbbec_environment():
        test_import()
    
    print("\n现在可以在任何子目录中使用SDK了!")
    print("建议将此脚本的setup_orbbec_environment()函数导入到你的项目中使用。")