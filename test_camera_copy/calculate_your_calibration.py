#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算您的手眼标定数据
"""

import numpy as np
import math

def calculate_hand_eye_calibration():
    """计算手眼标定"""
    print("🎯 手眼标定计算")
    print("=" * 50)
    
    # 您的三个标定点
    camera_points = np.array([
        [58.8, 48.9, 247.0],   # 点1
        [81.9, 43.1, 353.0],   # 点2
        [136.5, 40.6, 282.0]   # 点3
    ])
    
    robot_points = np.array([
        [-290.9, 32.3, -393.5],   # 点1
        [-282.9, 34.2, -486.1],   # 点2
        [-290.8, -51.8, -424.0]   # 点3
    ])
    
    print("📋 输入数据:")
    for i in range(3):
        print(f"点{i+1}: 相机({camera_points[i,0]:5.1f}, {camera_points[i,1]:5.1f}, {camera_points[i,2]:5.1f}) → 机械臂({robot_points[i,0]:6.1f}, {robot_points[i,1]:5.1f}, {robot_points[i,2]:6.1f})")
    
    # 方法1: 简单平移偏移分析
    print(f"\n📐 方法1: 简单平移偏移分析")
    offsets = robot_points - camera_points
    mean_offset = np.mean(offsets, axis=0)
    offset_std = np.std(offsets, axis=0)
    
    print(f"各点偏移:")
    for i in range(3):
        print(f"点{i+1}: ({offsets[i,0]:6.1f}, {offsets[i,1]:6.1f}, {offsets[i,2]:6.1f})")
    
    print(f"平均偏移: ({mean_offset[0]:6.1f}, {mean_offset[1]:6.1f}, {mean_offset[2]:6.1f})")
    print(f"标准差:   ({offset_std[0]:6.1f}, {offset_std[1]:6.1f}, {offset_std[2]:6.1f})")
    print(f"最大误差: {np.max(offset_std):.1f}mm")
    
    # 验证简单偏移的精度
    print(f"\n🧪 简单偏移验证:")
    errors = []
    for i in range(3):
        predicted = camera_points[i] + mean_offset
        actual = robot_points[i]
        error = np.linalg.norm(actual - predicted)
        errors.append(error)
        print(f"点{i+1}: 预测({predicted[0]:6.1f}, {predicted[1]:5.1f}, {predicted[2]:6.1f}) vs 实际({actual[0]:6.1f}, {actual[1]:5.1f}, {actual[2]:6.1f}), 误差{error:.1f}mm")
    
    mean_error = np.mean(errors)
    max_error = np.max(errors)
    print(f"平均误差: {mean_error:.1f}mm")
    print(f"最大误差: {max_error:.1f}mm")
    
    if max_error < 20:
        print("✅ 简单平移偏移精度可接受 (<20mm)")
        use_simple = True
    else:
        print("⚠️ 简单平移偏移精度较差，尝试完整变换")
        use_simple = False
    
    # 方法2: 完整变换矩阵计算
    print(f"\n📊 方法2: 完整变换矩阵计算")
    
    # 计算中心点
    camera_center = np.mean(camera_points, axis=0)
    robot_center = np.mean(robot_points, axis=0)
    
    print(f"相机中心: ({camera_center[0]:5.1f}, {camera_center[1]:5.1f}, {camera_center[2]:5.1f})")
    print(f"机械臂中心: ({robot_center[0]:6.1f}, {robot_center[1]:5.1f}, {robot_center[2]:6.1f})")
    
    # 去中心化
    camera_centered = camera_points - camera_center
    robot_centered = robot_points - robot_center
    
    print(f"\n去中心化后的点:")
    for i in range(3):
        print(f"点{i+1}: 相机({camera_centered[i,0]:6.1f}, {camera_centered[i,1]:6.1f}, {camera_centered[i,2]:6.1f}) → 机械臂({robot_centered[i,0]:6.1f}, {robot_centered[i,1]:6.1f}, {robot_centered[i,2]:6.1f})")
    
    # 使用SVD计算旋转矩阵
    H = camera_centered.T @ robot_centered
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    
    # 确保是右手坐标系
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    
    # 计算平移向量
    t = robot_center - R @ camera_center
    
    # 构建4x4齐次变换矩阵
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    
    print(f"\n🔄 旋转矩阵 R:")
    for i in range(3):
        print(f"   [{R[i,0]:7.4f} {R[i,1]:7.4f} {R[i,2]:7.4f}]")
    
    print(f"\n➡️ 平移向量 t:")
    print(f"   [{t[0]:7.1f} {t[1]:7.1f} {t[2]:7.1f}]")
    
    print(f"\n📋 完整变换矩阵 T:")
    for i in range(4):
        print(f"   [{T[i,0]:7.4f} {T[i,1]:7.4f} {T[i,2]:7.4f} {T[i,3]:8.1f}]")
    
    # 计算旋转角度
    sy = math.sqrt(R[0,0]**2 + R[1,0]**2)
    singular = sy < 1e-6
    
    if not singular:
        x_angle = math.atan2(R[2,1], R[2,2])
        y_angle = math.atan2(-R[2,0], sy)
        z_angle = math.atan2(R[1,0], R[0,0])
    else:
        x_angle = math.atan2(-R[1,2], R[1,1])
        y_angle = math.atan2(-R[2,0], sy)
        z_angle = 0
    
    print(f"\n🔄 旋转角度:")
    print(f"   绕X轴: {math.degrees(x_angle):6.1f}°")
    print(f"   绕Y轴: {math.degrees(y_angle):6.1f}°")
    print(f"   绕Z轴: {math.degrees(z_angle):6.1f}°")
    
    # 验证完整变换精度
    print(f"\n🧪 完整变换验证:")
    transform_errors = []
    for i in range(3):
        # 应用变换
        camera_homo = np.append(camera_points[i], 1)
        robot_predicted_homo = T @ camera_homo
        robot_predicted = robot_predicted_homo[:3]
        
        actual = robot_points[i]
        error = np.linalg.norm(actual - robot_predicted)
        transform_errors.append(error)
        
        print(f"点{i+1}: 预测({robot_predicted[0]:6.1f}, {robot_predicted[1]:5.1f}, {robot_predicted[2]:6.1f}) vs 实际({actual[0]:6.1f}, {actual[1]:5.1f}, {actual[2]:6.1f}), 误差{error:.2f}mm")
    
    transform_mean_error = np.mean(transform_errors)
    transform_max_error = np.max(transform_errors)
    print(f"平均误差: {transform_mean_error:.2f}mm")
    print(f"最大误差: {transform_max_error:.2f}mm")
    
    # 结论和建议
    print(f"\n🎯 结论和建议:")
    
    if max_error < transform_max_error:
        print(f"✅ 推荐使用简单平移偏移:")
        print(f"   机械臂坐标 = 相机坐标 + ({mean_offset[0]:.1f}, {mean_offset[1]:.1f}, {mean_offset[2]:.1f})")
        print(f"   精度: {max_error:.1f}mm")
        
        # 生成代码
        print(f"\n💻 Python代码:")
        print(f"def camera_to_robot(camera_x, camera_y, camera_z):")
        print(f"    robot_x = camera_x + ({mean_offset[0]:.1f})")
        print(f"    robot_y = camera_y + ({mean_offset[1]:.1f})")  
        print(f"    robot_z = camera_z + ({mean_offset[2]:.1f})")
        print(f"    return robot_x, robot_y, robot_z")
        
    else:
        print(f"✅ 推荐使用完整变换矩阵:")
        print(f"   精度: {transform_max_error:.2f}mm")
        print(f"   考虑了旋转关系，更准确")
        
        print(f"\n💻 变换矩阵 (复制到代码中):")
        print(f"import numpy as np")
        print(f"T = np.array([")
        for i in range(4):
            print(f"    [{T[i,0]:9.6f}, {T[i,1]:9.6f}, {T[i,2]:9.6f}, {T[i,3]:9.1f}]{',' if i < 3 else ''}")
        print(f"])")
        print(f"")
        print(f"def camera_to_robot(camera_x, camera_y, camera_z):")
        print(f"    camera_homo = np.array([camera_x, camera_y, camera_z, 1])")
        print(f"    robot_homo = T @ camera_homo")
        print(f"    return robot_homo[0], robot_homo[1], robot_homo[2]")
    
    # 测试示例
    print(f"\n🧪 测试示例 (使用简单偏移):")
    test_camera = [100, 50, 300]
    test_robot = [test_camera[0] + mean_offset[0], test_camera[1] + mean_offset[1], test_camera[2] + mean_offset[2]]
    print(f"相机({test_camera[0]}, {test_camera[1]}, {test_camera[2]}) → 机械臂({test_robot[0]:.1f}, {test_robot[1]:.1f}, {test_robot[2]:.1f})")
    
    return mean_offset, T

if __name__ == "__main__":
    mean_offset, transform_matrix = calculate_hand_eye_calibration()