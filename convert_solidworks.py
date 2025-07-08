#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolidWorks文件转换辅助脚本
"""

import os
import shutil
from pathlib import Path

def prepare_model_directory():
    """准备模型目录结构"""
    
    # 创建模型目录
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # 创建临时目录用于转换
    temp_dir = Path("temp_convert")
    temp_dir.mkdir(exist_ok=True)
    
    print("已创建目录结构:")
    print(f"  models/     - 存放转换后的STL文件")
    print(f"  temp_convert/ - 临时转换目录")
    
    return models_dir, temp_dir

def show_conversion_guide():
    """显示转换指南"""
    print("\n" + "="*60)
    print("SolidWorks文件转换指南")
    print("="*60)
    
    print("\n您的文件列表:")
    print("  RD20-FR3-V6.0-1.SLDPRT")
    print("  RD20-FR3-V6.0-2.SLDPRT") 
    print("  RD20-FR3-V6.0-3.SLDPRT")
    print("  RD20-FR3-V6.0-4.SLDPRT")
    print("  RD20-FR3-V6.0-5.SLDPRT")
    print("  RD20-FR3-V6.0-7.SLDPRT")
    print("  RD20-FR3-V6.0 软件模型.SLDASM")
    
    print("\n推荐转换方案:")
    print("\n1. 在线转换 (CAD Exchanger):")
    print("   - 访问: https://cadexchanger.com/")
    print("   - 上传 .SLDPRT 文件")
    print("   - 选择输出格式: STL")
    print("   - 下载转换后的文件")
    
    print("\n2. 如果有SolidWorks软件:")
    print("   - 打开装配体文件")
    print("   - 右键选择零件 → 另存为 → STL")
    print("   - 坐标系选择: 装配体原点")
    print("   - 单位: 毫米")
    
    print("\n3. 转换后的文件命名建议:")
    print("   RD20-FR3-V6.0-1.SLDPRT → fr3_base.stl")
    print("   RD20-FR3-V6.0-2.SLDPRT → fr3_link1.stl")
    print("   RD20-FR3-V6.0-3.SLDPRT → fr3_link2.stl")
    print("   RD20-FR3-V6.0-4.SLDPRT → fr3_link3.stl")
    print("   RD20-FR3-V6.0-5.SLDPRT → fr3_link4.stl")
    print("   RD20-FR3-V6.0-7.SLDPRT → fr3_gripper.stl")
    
    print("\n4. 转换完成后:")
    print("   - 将STL文件放入 models/ 目录")
    print("   - 运行: python load_real_models.py")
    print("   - 测试模型加载")

def check_stl_files():
    """检查STL文件是否存在"""
    models_dir = Path("models")
    
    expected_files = [
        "fr3_base.stl",
        "fr3_link1.stl", 
        "fr3_link2.stl",
        "fr3_link3.stl",
        "fr3_link4.stl",
        "fr3_gripper.stl"
    ]
    
    print(f"\n检查 models/ 目录中的STL文件:")
    
    found_files = []
    for filename in expected_files:
        filepath = models_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  ✓ {filename} ({size} bytes)")
            found_files.append(filename)
        else:
            print(f"  ✗ {filename} (未找到)")
    
    print(f"\n找到 {len(found_files)} / {len(expected_files)} 个文件")
    
    if found_files:
        print("\n可以运行测试:")
        print("  python load_real_models.py")
    else:
        print("\n请先转换SolidWorks文件为STL格式")
    
    return found_files

def create_batch_rename_script():
    """创建批量重命名脚本"""
    
    script_content = '''@echo off
echo 批量重命名SolidWorks转换的STL文件

rem 假设转换后的文件名为原始名称
if exist "RD20-FR3-V6.0-1.stl" ren "RD20-FR3-V6.0-1.stl" "fr3_base.stl"
if exist "RD20-FR3-V6.0-2.stl" ren "RD20-FR3-V6.0-2.stl" "fr3_link1.stl"  
if exist "RD20-FR3-V6.0-3.stl" ren "RD20-FR3-V6.0-3.stl" "fr3_link2.stl"
if exist "RD20-FR3-V6.0-4.stl" ren "RD20-FR3-V6.0-4.stl" "fr3_link3.stl"
if exist "RD20-FR3-V6.0-5.stl" ren "RD20-FR3-V6.0-5.stl" "fr3_link4.stl"
if exist "RD20-FR3-V6.0-7.stl" ren "RD20-FR3-V6.0-7.stl" "fr3_gripper.stl"

echo 重命名完成
pause
'''
    
    with open("rename_stl_files.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("已创建批量重命名脚本: rename_stl_files.bat")

if __name__ == "__main__":
    print("SolidWorks文件转换助手")
    print("=" * 30)
    
    # 准备目录
    models_dir, temp_dir = prepare_model_directory()
    
    # 显示转换指南
    show_conversion_guide()
    
    # 检查现有STL文件
    found_files = check_stl_files()
    
    # 创建辅助脚本
    create_batch_rename_script()
    
    print("\n" + "="*60)
    print("下一步操作:")
    if not found_files:
        print("1. 使用上述方案转换 .SLDPRT 文件为 .STL")
        print("2. 将转换后的文件放入 models/ 目录")
        print("3. 运行此脚本检查文件: python convert_solidworks.py")
        print("4. 测试模型加载: python load_real_models.py")
    else:
        print("1. 运行模型加载测试: python load_real_models.py")
        print("2. 查看3D显示效果")
        print("3. 集成到主程序")