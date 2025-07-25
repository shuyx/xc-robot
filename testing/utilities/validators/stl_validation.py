#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL文件验证和分析工具
用于检查FR3机械臂STL模型的完整性和质量
"""

import os
import struct
import numpy as np
from typing import Dict, List, Tuple

class STLValidator:
    """STL文件验证器"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.required_files = [
            "fr3_base.stl",
            "fr3_link1.stl", 
            "fr3_link2.stl",
            "fr3_link3.stl",
            "fr3_link4.stl",
            "fr3_link5.stl",
            "fr3_link6.stl"
        ]
    
    def validate_all_files(self) -> Dict:
        """验证所有必需的STL文件"""
        results = {}
        
        print("🔍 开始验证FR3机械臂STL文件...")
        print("=" * 50)
        
        for filename in self.required_files:
            file_path = os.path.join(self.models_dir, filename)
            results[filename] = self.validate_single_file(file_path)
            
        self.print_summary(results)
        return results
    
    def validate_single_file(self, file_path: str) -> Dict:
        """验证单个STL文件"""
        result = {
            "path": file_path,
            "exists": False,
            "file_size": 0,
            "format": None,
            "triangle_count": 0,
            "bounds": None,
            "is_valid": False,
            "issues": []
        }
        
        if not os.path.exists(file_path):
            result["issues"].append("文件不存在")
            return result
        
        result["exists"] = True
        result["file_size"] = os.path.getsize(file_path)
        
        try:
            # 检测STL格式并读取
            if self.is_binary_stl(file_path):
                result["format"] = "Binary"
                triangles, header = self.read_binary_stl(file_path)
            else:
                result["format"] = "ASCII"
                triangles = self.read_ascii_stl(file_path)
            
            result["triangle_count"] = len(triangles)
            result["bounds"] = self.calculate_bounds(triangles)
            
            # 质量检查
            result["issues"].extend(self.check_quality(triangles, result))
            result["is_valid"] = len(result["issues"]) == 0
            
        except Exception as e:
            result["issues"].append(f"读取错误: {str(e)}")
        
        return result
    
    def is_binary_stl(self, file_path: str) -> bool:
        """检测STL文件格式"""
        with open(file_path, 'rb') as f:
            header = f.read(80)
            if header.lower().startswith(b'solid'):
                # 可能是ASCII，进一步检查
                f.seek(0)
                try:
                    content = f.read(1024).decode('ascii')
                    return 'endsolid' not in content.lower()
                except:
                    return True
            return True
    
    def read_binary_stl(self, file_path: str) -> Tuple[List, str]:
        """读取Binary STL文件"""
        triangles = []
        
        with open(file_path, 'rb') as f:
            # 读取80字节header
            header = f.read(80).decode('ascii', errors='ignore').strip()
            
            # 读取三角形数量
            triangle_count_data = f.read(4)
            if len(triangle_count_data) != 4:
                raise ValueError("文件格式错误：无法读取三角形数量")
            
            triangle_count = struct.unpack('<I', triangle_count_data)[0]
            
            # 读取三角形数据
            for i in range(triangle_count):
                try:
                    # 法向量 (3 floats)
                    normal = struct.unpack('<3f', f.read(12))
                    
                    # 三个顶点 (9 floats)
                    v1 = struct.unpack('<3f', f.read(12))
                    v2 = struct.unpack('<3f', f.read(12))
                    v3 = struct.unpack('<3f', f.read(12))
                    
                    # 属性字节计数 (2 bytes, 通常为0)
                    f.read(2)
                    
                    triangles.append({
                        'normal': normal,
                        'vertices': [v1, v2, v3]
                    })
                    
                except struct.error:
                    raise ValueError(f"读取第{i+1}个三角形时出错")
        
        return triangles, header
    
    def read_ascii_stl(self, file_path: str) -> List:
        """读取ASCII STL文件"""
        triangles = []
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        lines = content.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip().lower()
            
            if line.startswith('facet normal'):
                # 解析法向量
                normal_parts = line.split()[2:5]
                normal = tuple(float(x) for x in normal_parts)
                
                vertices = []
                i += 1  # 跳过 "outer loop"
                
                # 读取三个顶点
                for _ in range(3):
                    i += 1
                    vertex_line = lines[i].strip()
                    if vertex_line.startswith('vertex'):
                        vertex_parts = vertex_line.split()[1:4]
                        vertex = tuple(float(x) for x in vertex_parts)
                        vertices.append(vertex)
                
                triangles.append({
                    'normal': normal,
                    'vertices': vertices
                })
                
                i += 2  # 跳过 "endloop" 和 "endfacet"
            else:
                i += 1
        
        return triangles
    
    def calculate_bounds(self, triangles: List) -> Dict:
        """计算模型边界框"""
        if not triangles:
            return None
        
        all_vertices = []
        for triangle in triangles:
            all_vertices.extend(triangle['vertices'])
        
        vertices_array = np.array(all_vertices)
        
        return {
            'min': vertices_array.min(axis=0).tolist(),
            'max': vertices_array.max(axis=0).tolist(),
            'size': (vertices_array.max(axis=0) - vertices_array.min(axis=0)).tolist(),
            'center': vertices_array.mean(axis=0).tolist()
        }
    
    def check_quality(self, triangles: List, result: Dict) -> List[str]:
        """检查STL文件质量"""
        issues = []
        
        # 检查文件大小
        if result["file_size"] > 10 * 1024 * 1024:  # 10MB
            issues.append(f"文件过大: {result['file_size']/1024/1024:.1f}MB > 10MB")
        
        # 检查三角形数量
        if result["triangle_count"] == 0:
            issues.append("文件为空：没有三角形")
        elif result["triangle_count"] > 100000:
            issues.append(f"三角形过多: {result['triangle_count']} > 100K")
        
        # 检查边界框
        if result["bounds"]:
            size = result["bounds"]["size"]
            if max(size) > 1000:  # 1米
                issues.append(f"模型过大: 最大尺寸 {max(size):.1f}mm")
            if min(size) < 1:  # 1mm
                issues.append(f"模型过小: 最小尺寸 {min(size):.1f}mm")
        
        # 检查退化三角形
        degenerate_count = 0
        for triangle in triangles[:min(1000, len(triangles))]:  # 采样检查
            v1, v2, v3 = triangle['vertices']
            area = self.triangle_area(v1, v2, v3)
            if area < 1e-6:
                degenerate_count += 1
        
        if degenerate_count > 0:
            issues.append(f"发现 {degenerate_count} 个退化三角形")
        
        return issues
    
    def triangle_area(self, v1: Tuple, v2: Tuple, v3: Tuple) -> float:
        """计算三角形面积"""
        # 使用叉积计算面积
        a = np.array(v2) - np.array(v1)
        b = np.array(v3) - np.array(v1)
        cross = np.cross(a, b)
        
        # 处理2D和3D情况
        if cross.ndim == 0:  # 2D情况
            return abs(cross) / 2
        else:  # 3D情况
            return np.linalg.norm(cross) / 2
    
    def print_summary(self, results: Dict):
        """打印验证结果摘要"""
        print("\n📊 验证结果摘要:")
        print("=" * 50)
        
        total_files = len(results)
        valid_files = sum(1 for r in results.values() if r["is_valid"])
        existing_files = sum(1 for r in results.values() if r["exists"])
        
        print(f"📁 总文件数: {total_files}")
        print(f"✅ 存在文件: {existing_files}")
        print(f"🎯 有效文件: {valid_files}")
        print(f"❌ 问题文件: {total_files - valid_files}")
        
        print("\n📋 详细信息:")
        print("-" * 50)
        
        for filename, result in results.items():
            status = "✅" if result["is_valid"] else "❌"
            size_mb = result["file_size"] / 1024 / 1024 if result["file_size"] > 0 else 0
            
            print(f"{status} {filename}")
            
            if result["exists"]:
                print(f"    📊 大小: {size_mb:.2f}MB")
                print(f"    🔢 格式: {result['format']}")
                print(f"    📐 三角形: {result['triangle_count']:,}")
                
                if result["bounds"]:
                    size = result["bounds"]["size"]
                    print(f"    📏 尺寸: {size[0]:.1f} × {size[1]:.1f} × {size[2]:.1f} mm")
                
                if result["issues"]:
                    print(f"    ⚠️  问题: {', '.join(result['issues'])}")
            else:
                print(f"    ❌ 文件不存在")
            
            print()
    
    def generate_report(self, results: Dict, output_file: str = "stl_validation_report.txt"):
        """生成验证报告文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("FR3机械臂STL文件验证报告\n")
            f.write("=" * 40 + "\n\n")
            
            # 写入摘要
            total_files = len(results)
            valid_files = sum(1 for r in results.values() if r["is_valid"])
            existing_files = sum(1 for r in results.values() if r["exists"])
            
            f.write(f"总文件数: {total_files}\n")
            f.write(f"存在文件: {existing_files}\n")
            f.write(f"有效文件: {valid_files}\n")
            f.write(f"问题文件: {total_files - valid_files}\n\n")
            
            # 写入详细信息
            for filename, result in results.items():
                f.write(f"文件: {filename}\n")
                f.write(f"  存在: {'是' if result['exists'] else '否'}\n")
                
                if result["exists"]:
                    f.write(f"  大小: {result['file_size']:,} 字节\n")
                    f.write(f"  格式: {result['format']}\n")
                    f.write(f"  三角形数: {result['triangle_count']:,}\n")
                    f.write(f"  有效: {'是' if result['is_valid'] else '否'}\n")
                    
                    if result["bounds"]:
                        bounds = result["bounds"]
                        f.write(f"  边界: [{bounds['min']}, {bounds['max']}]\n")
                        f.write(f"  尺寸: {bounds['size']}\n")
                        f.write(f"  中心: {bounds['center']}\n")
                    
                    if result["issues"]:
                        f.write(f"  问题: {'; '.join(result['issues'])}\n")
                
                f.write("\n")
        
        print(f"📄 报告已保存到: {output_file}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FR3机械臂STL文件验证工具")
    parser.add_argument("--models-dir", default="models", help="STL文件目录")
    parser.add_argument("--report", help="生成报告文件名")
    
    args = parser.parse_args()
    
    # 创建验证器
    validator = STLValidator(args.models_dir)
    
    # 执行验证
    results = validator.validate_all_files()
    
    # 生成报告
    if args.report:
        validator.generate_report(results, args.report)

if __name__ == "__main__":
    main()