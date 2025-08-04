#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的置信度计算算法
"""

import numpy as np

class TestConfidenceCalculator:
    def __init__(self):
        self.target_size = 50     # 5cm方块
        self.size_tolerance = 20  # ±20mm误差
    
    def calculate_confidence_old(self, avg_size, size_error, volume_error, extent):
        """原始置信度计算方法"""
        # 基于尺寸误差的置信度
        size_confidence = max(0, 1 - (size_error / self.size_tolerance))
        
        # 基于形状规则度的置信度（越接近立方体置信度越高）
        size_ratios = [max(extent)/min(extent) for _ in range(3)]
        shape_confidence = max(0, 1 - (max(size_ratios) - 1) / 2)  # 长宽比越接近1越好
        
        # 基于体积误差的置信度
        volume_confidence = max(0, 1 - volume_error)
        
        # 综合置信度
        overall_confidence = (size_confidence * 0.4 + shape_confidence * 0.3 + volume_confidence * 0.3)
        
        return min(1.0, max(0.0, overall_confidence))
    
    def calculate_confidence_new(self, avg_size, size_error, volume_error, extent):
        """改进后的置信度计算方法"""
        # 1. 基于尺寸误差的置信度 (更严格的评估)
        size_confidence = max(0, 1 - (size_error / self.size_tolerance))
        
        # 2. 基于形状规则度的置信度（更精确的立方体评估）
        dimensions = sorted(extent)
        size_ratio_1 = dimensions[1] / dimensions[0]  # 中等/最小
        size_ratio_2 = dimensions[2] / dimensions[1]  # 最大/中等
        
        # 理想立方体的所有比例应该接近1
        ratio_error_1 = abs(size_ratio_1 - 1.0)
        ratio_error_2 = abs(size_ratio_2 - 1.0)
        shape_confidence = max(0, 1 - (ratio_error_1 + ratio_error_2) / 2)
        
        # 3. 基于体积误差的置信度（使用对数尺度更合理）
        target_volume = self.target_size ** 3
        actual_volume = np.prod(extent)
        if actual_volume > 0 and target_volume > 0:
            volume_ratio = actual_volume / target_volume
            # 使用对数误差，对小体积差异更敏感
            log_volume_error = abs(np.log(volume_ratio))
            volume_confidence = max(0, 1 - log_volume_error / 0.5)  # 50%的对数误差
        else:
            volume_confidence = 0
        
        # 4. 基于尺寸一致性的置信度（三个维度应该相近）
        size_std = np.std(extent)
        size_mean = np.mean(extent)
        size_consistency = max(0, 1 - (size_std / size_mean) * 3)  # 3倍标准差容忍
        
        # 5. 基于绝对尺寸的置信度（惩罚过大或过小的物体）
        abs_size_error = abs(avg_size - self.target_size) / self.target_size
        abs_size_confidence = max(0, 1 - abs_size_error)
        
        # 6. 加权综合置信度（根据测试结果调整权重）
        overall_confidence = (
            size_confidence * 0.25 +      # 尺寸准确性
            shape_confidence * 0.25 +     # 形状规则度
            volume_confidence * 0.20 +    # 体积匹配度
            size_consistency * 0.20 +     # 尺寸一致性
            abs_size_confidence * 0.10    # 绝对尺寸准确性
        )
        
        return min(1.0, max(0.0, overall_confidence))

def test_clusters():
    """测试不同簇的置信度计算"""
    calculator = TestConfidenceCalculator()
    
    # 根据测试结果定义三个簇
    clusters = [
        {
            'name': '簇1 (原始置信度: 0.35)',
            'extent': np.array([104.3, 47.4, 34.5]),
            'avg_size': 62.1,
            'volume': 170713.0
        },
        {
            'name': '簇2 (原始置信度: 0.74)',
            'extent': np.array([75.1, 51.6, 31.8]),
            'avg_size': 52.8,
            'volume': 123398.7
        },
        {
            'name': '簇5 (原始置信度: 0.00)',
            'extent': np.array([61.3, 46.0, 2.2]),
            'avg_size': 36.5,
            'volume': 6111.3
        }
    ]
    
    target_volume = calculator.target_size ** 3
    
    print("🧪 测试改进后的置信度计算算法")
    print("=" * 80)
    
    for cluster in clusters:
        extent = cluster['extent']
        avg_size = cluster['avg_size']
        volume = cluster['volume']
        
        # 计算各种误差
        size_error = abs(avg_size - calculator.target_size)
        volume_error = abs(volume - target_volume) / target_volume
        
        # 计算置信度
        old_confidence = calculator.calculate_confidence_old(avg_size, size_error, volume_error, extent)
        new_confidence = calculator.calculate_confidence_new(avg_size, size_error, volume_error, extent)
        
        print(f"\n📊 {cluster['name']}")
        print(f"  尺寸: {extent[0]:.1f} x {extent[1]:.1f} x {extent[2]:.1f} mm")
        print(f"  平均尺寸: {avg_size:.1f} mm (目标: {calculator.target_size} mm)")
        print(f"  体积: {volume:.1f} mm³ (目标: {target_volume} mm³)")
        print(f"  尺寸误差: {size_error:.1f} mm")
        print(f"  体积误差: {volume_error:.2%}")
        print(f"  原始置信度: {old_confidence:.3f}")
        print(f"  改进置信度: {new_confidence:.3f}")
        print(f"  置信度变化: {new_confidence - old_confidence:+.3f}")
        
        # 分析变化原因
        if new_confidence > old_confidence:
            print("  ✅ 置信度提升 - 改进算法更准确地识别了这个簇")
        elif new_confidence < old_confidence:
            print("  ❌ 置信度下降 - 改进算法更严格地过滤了这个簇")
        else:
            print("  ➡️ 置信度不变")

def analyze_improvements():
    """分析改进点"""
    print("\n" + "=" * 80)
    print("🔍 改进点分析")
    print("=" * 80)
    
    print("\n1. 形状评估改进:")
    print("   - 原始方法: 只考虑最大/最小比例")
    print("   - 改进方法: 考虑相邻维度的比例，更精确地评估立方体")
    
    print("\n2. 体积评估改进:")
    print("   - 原始方法: 线性体积误差")
    print("   - 改进方法: 对数体积误差，对小体积差异更敏感")
    
    print("\n3. 新增评估维度:")
    print("   - 尺寸一致性: 三个维度的标准差")
    print("   - 绝对尺寸准确性: 相对于目标尺寸的误差")
    
    print("\n4. 权重优化:")
    print("   - 原始权重: 尺寸40%, 形状30%, 体积30%")
    print("   - 改进权重: 尺寸25%, 形状25%, 体积20%, 一致性20%, 绝对10%")
    
    print("\n5. 预期效果:")
    print("   - 簇2 (最佳目标): 置信度应该保持最高或提升")
    print("   - 簇1 (较差目标): 置信度应该下降")
    print("   - 簇5 (扁平物体): 置信度应该保持最低")

if __name__ == "__main__":
    test_clusters()
    analyze_improvements()