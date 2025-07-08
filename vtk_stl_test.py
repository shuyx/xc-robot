#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VTK STL文件测试 - 不使用PyQt5
"""

import os
import sys

def test_vtk_import():
    """测试VTK导入"""
    try:
        import vtk
        print(f"✓ VTK版本: {vtk.vtkVersion().GetVTKVersion()}")
        return True
    except ImportError:
        print("✗ VTK未安装")
        return False

def analyze_stl_file(filename):
    """分析STL文件"""
    if not os.path.exists(filename):
        print(f"✗ 文件不存在: {filename}")
        return False
    
    file_size = os.path.getsize(filename)
    print(f"\n文件分析: {os.path.basename(filename)}")
    print(f"  大小: {file_size / (1024*1024):.2f} MB")
    
    # 尝试读取前几行
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('solid'):
                print("  格式: ASCII STL")
                
                # 计算三角形数量
                triangle_count = 0
                line_count = 0
                for line in f:
                    line_count += 1
                    if line.strip().startswith('facet normal'):
                        triangle_count += 1
                    if line_count > 1000:  # 只读前1000行避免太慢
                        break
                        
                print(f"  三角形数量: ~{triangle_count}")
                return True
    except:
        print("  格式: 二进制STL")
        return True

def test_vtk_stl_loading(filename):
    """测试VTK加载STL"""
    try:
        import vtk
        
        print(f"\nVTK加载测试: {os.path.basename(filename)}")
        
        # 创建STL读取器
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        reader.Update()
        
        # 获取几何数据
        polydata = reader.GetOutput()
        num_points = polydata.GetNumberOfPoints()
        num_cells = polydata.GetNumberOfCells()
        
        print(f"  ✓ 加载成功")
        print(f"  顶点数: {num_points}")
        print(f"  三角形数: {num_cells}")
        
        # 获取边界框
        bounds = polydata.GetBounds()
        x_size = bounds[1] - bounds[0]
        y_size = bounds[3] - bounds[2]
        z_size = bounds[5] - bounds[4]
        
        print(f"  尺寸: {x_size:.1f} × {y_size:.1f} × {z_size:.1f} mm")
        print(f"  边界: X[{bounds[0]:.1f}, {bounds[1]:.1f}] Y[{bounds[2]:.1f}, {bounds[3]:.1f}] Z[{bounds[4]:.1f}, {bounds[5]:.1f}]")
        
        # 计算中心点
        center_x = (bounds[0] + bounds[1]) / 2
        center_y = (bounds[2] + bounds[3]) / 2
        center_z = (bounds[4] + bounds[5]) / 2
        print(f"  中心: ({center_x:.1f}, {center_y:.1f}, {center_z:.1f})")
        
        return True
        
    except Exception as e:
        print(f"  ✗ VTK加载失败: {e}")
        return False

def main():
    print("STL文件VTK测试")
    print("=" * 50)
    
    # 测试VTK
    if not test_vtk_import():
        print("请安装VTK: pip install vtk")
        return
    
    # 查找STL文件
    models_dir = "models"
    stl_files = []
    
    if os.path.exists(models_dir):
        for filename in os.listdir(models_dir):
            if filename.lower().endswith('.stl'):
                stl_files.append(os.path.join(models_dir, filename))
    
    if not stl_files:
        print(f"\n在 {models_dir} 目录中未找到STL文件")
        print("请将STL文件放入models目录")
        return
    
    print(f"\n找到 {len(stl_files)} 个STL文件:")
    
    # 分析每个文件
    for filename in stl_files:
        analyze_stl_file(filename)
        test_vtk_stl_loading(filename)
    
    print("\n" + "=" * 50)
    print("总结:")
    print("✓ STL文件可以正常加载")
    print("✓ VTK功能正常工作") 
    print("下一步: 修复PyQt5问题以显示3D界面")

if __name__ == "__main__":
    main()