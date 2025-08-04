#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的测试脚本，不使用可能缺失的常量
"""

try:
    print("=== 尝试基础导入 ===")
    from pyorbbecsdk import Context, Pipeline
    print("✅ 基础类导入成功")
    
    # 测试Context创建
    print("\n=== 测试Context ===")
    ctx = Context()
    print("✅ Context创建成功")
    
    # 查询设备
    device_list = ctx.query_devices()
    device_count = device_list.get_count()
    print(f"发现 {device_count} 个设备")
    
    if device_count > 0:
        device = device_list.get_device_by_index(0)
        device_info = device.get_device_info()
        print(f"✅ 设备名称: {device_info.get_name()}")
        print("🎉 基础功能正常!")
    else:
        print("⚠️ 无设备但SDK基础功能正常")
        
except ImportError as e:
    print(f"❌ 导入失败: {e}")
except Exception as e:
    print(f"❌ 运行失败: {e}")
    import traceback
    traceback.print_exc()