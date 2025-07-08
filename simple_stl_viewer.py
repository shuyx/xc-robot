#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的STL文件查看器 - 不依赖PyQt5
"""

import sys
import os

def check_stl_file(filename):
    """检查STL文件基本信息"""
    if not os.path.exists(filename):
        print(f"文件不存在: {filename}")
        return False
    
    file_size = os.path.getsize(filename)
    print(f"文件: {filename}")
    print(f"大小: {file_size / (1024*1024):.2f} MB")
    
    # 检查是否为ASCII格式
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('solid'):
                print("格式: ASCII STL")
                
                # 计算三角形数量
                triangle_count = 0
                for line in f:
                    if line.strip().startswith('facet normal'):
                        triangle_count += 1
                        
                print(f"三角形数量: {triangle_count}")
                return True
            else:
                print("格式: 二进制STL")
                return True
                
    except:
        print("格式: 二进制STL")
        return True

def load_stl_with_vtk(filename):
    """使用VTK加载STL文件"""
    try:
        import vtk
        
        # 创建STL读取器
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        reader.Update()
        
        # 获取模型信息
        polydata = reader.GetOutput()
        num_points = polydata.GetNumberOfPoints()
        num_cells = polydata.GetNumberOfCells()
        
        print(f"VTK加载成功:")
        print(f"  顶点数: {num_points}")
        print(f"  三角形数: {num_cells}")
        
        # 获取边界框
        bounds = polydata.GetBounds()
        print(f"  边界框: X[{bounds[0]:.1f}, {bounds[1]:.1f}] Y[{bounds[2]:.1f}, {bounds[3]:.1f}] Z[{bounds[4]:.1f}, {bounds[5]:.1f}]")
        
        # 计算中心点
        center = [(bounds[0]+bounds[1])/2, (bounds[2]+bounds[3])/2, (bounds[4]+bounds[5])/2]
        print(f"  中心点: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
        
        return True
        
    except ImportError:
        print("VTK未安装，无法加载3D模型")
        return False
    except Exception as e:
        print(f"VTK加载失败: {e}")
        return False

def main():
    print("STL文件查看器")
    print("=" * 40)
    
    # 检查models目录
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"创建了 {models_dir} 目录")
    
    # 查找STL文件
    stl_files = []
    for filename in os.listdir(models_dir):
        if filename.lower().endswith('.stl'):
            stl_files.append(os.path.join(models_dir, filename))
    
    if not stl_files:
        print(f"在 {models_dir} 目录中未找到STL文件")
        print("请将转换后的STL文件放入此目录，例如:")
        print("  models/fr3_base.stl")
        print("  models/fr3_link1.stl")
        print("  等等...")
        return
    
    print(f"找到 {len(stl_files)} 个STL文件:")
    for i, filename in enumerate(stl_files):
        print(f"{i+1}. {os.path.basename(filename)}")
    
    # 检查每个文件
    for filename in stl_files:
        print("\n" + "-" * 40)
        success = check_stl_file(filename)
        if success:
            load_stl_with_vtk(filename)

if __name__ == "__main__":
    main()