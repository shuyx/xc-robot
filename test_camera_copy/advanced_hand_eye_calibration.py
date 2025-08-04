#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级手眼标定优化工具
目标：将当前12mm误差优化到5mm以内
方法：
1. 收集更多标定点
2. 使用多项式拟合
3. 分区域标定
4. 实时误差反馈
"""

import sys
import os
import time
import numpy as np
from pyorbbecsdk import *
import json
from datetime import datetime

# 添加FR3控制库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.insert(0, fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")

try:
    from fairino import Robot
    print("✅ fairino库导入成功")
    ROBOT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ fairino库导入失败: {e}")
    print("将在仅数据收集模式下运行")
    ROBOT_AVAILABLE = False

class AdvancedHandEyeCalibrator:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.robot = None
        
        # 标定数据存储
        self.calibration_points = []
        self.current_transform = None
        
        # 现有的手眼变换矩阵 (12mm精度)
        self.base_transform = np.array([
            [-0.105501, -0.992918,  0.054622,    -250.6],
            [-0.979217,  0.113299,  0.168218,      40.9],
            [-0.173215, -0.035739, -0.984235,    -127.6],
            [ 0.000000,  0.000000,  0.000000,       1.0]
        ])
        
        # 检测参数
        self.y_detection_ratio = 0.75
        
        print("✅ 高级手眼标定工具初始化完成")
        print(f"🎯 目标：将12mm误差优化到5mm以内")
    
    def initialize_camera(self):
        """初始化相机"""
        print("🔍 初始化相机系统...")
        
        self.camera_pipeline = Pipeline()
        config = Config()
        
        # 配置深度流
        depth_profile_list = self.camera_pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        config.enable_stream(depth_profile)
        self.camera_pipeline.start(config)
        
        # 获取相机内参
        try:
            depth_video_profile = depth_profile.as_video_stream_profile()
            self.camera_intrinsics = depth_video_profile.get_intrinsics()
            print(f"✅ 相机内参: fx={self.camera_intrinsics.fx:.1f}, fy={self.camera_intrinsics.fy:.1f}")
        except:
            self.camera_intrinsics = type('obj', (object,), {
                'fx': 500.0, 'fy': 500.0, 
                'ppx': 320.0, 'ppy': 240.0
            })()
            print("✅ 使用估算相机内参")
        
        # 预热相机
        for _ in range(10):
            self.camera_pipeline.wait_for_frames(100)
        
        print("✅ 相机初始化完成")
        return True
    
    def initialize_robot(self):
        """初始化机械臂"""
        if not ROBOT_AVAILABLE:
            print("⚠️ 机械臂库不可用，跳过机械臂初始化")
            return False
            
        print("🤖 初始化机械臂...")
        
        try:
            self.robot = Robot.RPC('192.168.58.2')
            
            if not hasattr(self.robot, 'is_conect') or not self.robot.is_conect:
                print("❌ 机械臂连接失败")
                return False
            print("✅ 机械臂连接成功")
            
            # 设置自动模式并使能
            ret = self.robot.Mode(0)
            if ret != 0:
                print(f"❌ 设置自动模式失败，错误码: {ret}")
                return False
            
            time.sleep(0.5)
            
            ret = self.robot.RobotEnable(1)
            if ret != 0:
                print(f"❌ 使能失败，错误码: {ret}")
                return False
            print("✅ 机械臂已使能")
            
            time.sleep(1.5)
            return True
            
        except Exception as e:
            print(f"❌ 机械臂初始化异常: {e}")
            return False
    
    def get_precise_camera_coordinates(self, average_frames=10):
        """获取高精度相机坐标（多帧平均）"""
        print(f"📷 捕获{average_frames}帧进行精确测量...")
        
        valid_detections = []
        
        for i in range(average_frames):
            try:
                frames = self.camera_pipeline.wait_for_frames(1000)
                depth_frame = frames.get_depth_frame()
                
                if not depth_frame:
                    continue
                
                depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
                height = depth_frame.get_height()
                width = depth_frame.get_width()
                depth_image = depth_data.reshape((height, width))
                
                result = self._analyze_depth_for_cup(depth_image)
                
                if result:
                    pixel_x, pixel_y, depth_mm, x_3d, y_3d, z_3d = result
                    valid_detections.append([x_3d * 1000, y_3d * 1000, z_3d * 1000])  # 转mm
                    print(f"   第{i+1}帧: Z={z_3d*1000:.1f}mm")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   第{i+1}帧异常: {e}")
                continue
        
        if len(valid_detections) < 3:
            print(f"❌ 有效检测帧数不足: {len(valid_detections)}")
            return None
        
        # 计算平均值和标准差
        detections = np.array(valid_detections)
        mean_coords = np.mean(detections, axis=0)
        std_coords = np.std(detections, axis=0)
        
        print(f"✅ 相机坐标测量完成:")
        print(f"   平均值: X={mean_coords[0]:.1f}, Y={mean_coords[1]:.1f}, Z={mean_coords[2]:.1f}mm")
        print(f"   标准差: X={std_coords[0]:.1f}, Y={std_coords[1]:.1f}, Z={std_coords[2]:.1f}mm")
        print(f"   有效帧数: {len(valid_detections)}/{average_frames}")
        
        return mean_coords
    
    def get_robot_coordinates(self):
        """获取机械臂TCP坐标"""
        if not ROBOT_AVAILABLE or self.robot is None:
            # 手动输入模式
            print("📍 请手动输入机械臂TCP坐标:")
            try:
                x = float(input("   X坐标(mm): "))
                y = float(input("   Y坐标(mm): "))
                z = float(input("   Z坐标(mm): "))
                return np.array([x, y, z])
            except ValueError:
                print("❌ 输入格式错误")
                return None
        
        try:
            error, tcp_coords = self.robot.GetActualToolFlangePose()
            if error != 0:
                print(f"❌ 获取TCP坐标失败，错误码: {error}")
                return None
            
            robot_coords = np.array([tcp_coords[0], tcp_coords[1], tcp_coords[2]])
            print(f"✅ 机械臂坐标: X={robot_coords[0]:.1f}, Y={robot_coords[1]:.1f}, Z={robot_coords[2]:.1f}mm")
            return robot_coords
            
        except Exception as e:
            print(f"❌ 获取机械臂坐标异常: {e}")
            return None
    
    def collect_calibration_point(self, point_name=""):
        """收集单个标定点"""
        print(f"\n{'='*50}")
        print(f"📍 收集标定点{point_name}")
        print(f"{'='*50}")
        
        print("📋 操作步骤:")
        print("1. 将标定物（水杯/标记物）放置在指定位置")
        print("2. 确保物体清晰可见且稳定")
        print("3. 按回车开始测量...")
        
        input("准备好后按回车继续...")
        
        # 获取相机坐标
        camera_coords = self.get_precise_camera_coordinates()
        if camera_coords is None:
            print("❌ 相机坐标获取失败")
            return False
        
        # 获取机械臂坐标
        robot_coords = self.get_robot_coordinates()
        if robot_coords is None:
            print("❌ 机械臂坐标获取失败")
            return False
        
        # 存储标定点
        calibration_point = {
            'name': point_name,
            'camera_coords': camera_coords.tolist(),
            'robot_coords': robot_coords.tolist(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.calibration_points.append(calibration_point)
        
        print(f"✅ 标定点{point_name}收集完成:")
        print(f"   相机坐标: {camera_coords}")
        print(f"   机械臂坐标: {robot_coords}")
        
        return True
    
    def collect_grid_calibration_points(self):
        """收集网格式标定点"""
        print("🎯 网格式标定点收集")
        print("📋 将在不同位置收集多个标定点以提高精度")
        
        # 预定义的标定点位置说明
        positions = [
            "中心位置",
            "左前方",
            "右前方", 
            "左后方",
            "右后方",
            "近距离中心",
            "远距离中心",
            "左侧中等距离",
            "右侧中等距离"
        ]
        
        collected_count = 0
        
        for i, position in enumerate(positions):
            print(f"\n{'🔸' * 20} 标定点 {i+1}/{len(positions)} {'🔸' * 20}")
            print(f"📍 请将标定物放置在: {position}")
            
            choice = input(f"选择操作: [c]收集此点 / [s]跳过 / [q]完成收集: ").strip().lower()
            
            if choice == 'q':
                print("🏁 用户选择完成收集")
                break
            elif choice == 's':
                print("⏭️ 跳过此点")
                continue
            elif choice == 'c':
                if self.collect_calibration_point(f"点{i+1}({position})"):
                    collected_count += 1
                    print(f"✅ 已收集 {collected_count} 个标定点")
                else:
                    print("❌ 标定点收集失败")
            else:
                print("⚠️ 输入无效，跳过此点")
        
        print(f"\n📊 标定点收集总结:")
        print(f"   成功收集: {collected_count} 个标定点")
        print(f"   建议最少: 6 个标定点")
        
        return collected_count >= 4  # 至少4个点才能进行标定
    
    def calculate_advanced_transform(self):
        """计算高级变换矩阵"""
        if len(self.calibration_points) < 4:
            print(f"❌ 标定点不足: {len(self.calibration_points)}/4")
            return None
        
        print(f"🔧 计算高级手眼变换矩阵...")
        print(f"📊 使用 {len(self.calibration_points)} 个标定点")
        
        # 提取坐标数据
        camera_points = np.array([point['camera_coords'] for point in self.calibration_points])
        robot_points = np.array([point['robot_coords'] for point in self.calibration_points])
        
        print(f"\n📍 标定点数据:")
        for i, point in enumerate(self.calibration_points):
            cam = point['camera_coords']
            rob = point['robot_coords']
            print(f"   点{i+1} 相机: ({cam[0]:.1f}, {cam[1]:.1f}, {cam[2]:.1f}) → "
                  f"机械臂: ({rob[0]:.1f}, {rob[1]:.1f}, {rob[2]:.1f})")
        
        # 方法1: 线性最小二乘法
        transform_linear = self._calculate_linear_transform(camera_points, robot_points)
        
        # 方法2: 多项式拟合
        transform_poly = self._calculate_polynomial_transform(camera_points, robot_points)
        
        # 方法3: 分区域优化
        transform_zoned = self._calculate_zoned_transform(camera_points, robot_points)
        
        # 评估各种方法的精度
        methods = [
            ("线性变换", transform_linear),
            ("多项式拟合", transform_poly),
            ("分区域优化", transform_zoned),
            ("现有矩阵", self.base_transform)
        ]
        
        best_method = None
        best_error = float('inf')
        
        print(f"\n📊 变换方法评估:")
        for method_name, transform in methods:
            if transform is not None:
                error = self._evaluate_transform_accuracy(transform, camera_points, robot_points)
                print(f"   {method_name}: 平均误差 {error:.2f}mm")
                
                if error < best_error:
                    best_error = error
                    best_method = (method_name, transform)
        
        if best_method:
            print(f"\n🏆 最佳方法: {best_method[0]} (误差: {best_error:.2f}mm)")
            self.current_transform = best_method[1]
            
            # 如果误差显著改善，更新变换矩阵
            if best_error < 8.0:  # 目标是小于5mm，但8mm以下也是改善
                print(f"✅ 变换矩阵已优化!")
                print(f"   原始误差: ~12mm")
                print(f"   优化后误差: {best_error:.2f}mm")
                print(f"   改善: {12 - best_error:.1f}mm")
                return self.current_transform
            else:
                print(f"⚠️ 优化效果有限，建议收集更多标定点")
                return None
        else:
            print(f"❌ 所有变换方法都失败")
            return None
    
    def _calculate_linear_transform(self, camera_points, robot_points):
        """计算线性变换矩阵"""
        try:
            # 使用最小二乘法求解 A*X = B
            # 其中 X 是变换矩阵，A 是相机齐次坐标，B 是机械臂坐标
            
            # 添加齐次坐标
            ones = np.ones((camera_points.shape[0], 1))
            camera_homo = np.hstack([camera_points, ones])
            
            # 求解变换矩阵的前3行
            transform_3x4 = np.linalg.lstsq(camera_homo, robot_points, rcond=None)[0].T
            
            # 构建4x4变换矩阵
            transform = np.vstack([transform_3x4, [0, 0, 0, 1]])
            
            return transform
            
        except Exception as e:
            print(f"   线性变换计算失败: {e}")
            return None
    
    def _calculate_polynomial_transform(self, camera_points, robot_points):
        """计算多项式拟合变换"""
        try:
            # 使用2次多项式拟合 (包含交叉项)
            n_points = camera_points.shape[0]
            
            # 构建特征矩阵 [x, y, z, x^2, y^2, z^2, xy, xz, yz, 1]
            features = np.zeros((n_points, 10))
            features[:, 0:3] = camera_points  # x, y, z
            features[:, 3:6] = camera_points**2  # x^2, y^2, z^2
            features[:, 6] = camera_points[:, 0] * camera_points[:, 1]  # xy
            features[:, 7] = camera_points[:, 0] * camera_points[:, 2]  # xz
            features[:, 8] = camera_points[:, 1] * camera_points[:, 2]  # yz
            features[:, 9] = 1  # 常数项
            
            # 分别拟合X, Y, Z三个维度
            poly_coeffs = np.zeros((3, 10))
            for i in range(3):
                poly_coeffs[i] = np.linalg.lstsq(features, robot_points[:, i], rcond=None)[0]
            
            # 构建多项式变换函数
            def poly_transform(camera_coords):
                if camera_coords.shape[-1] == 3:
                    # 单点变换
                    x, y, z = camera_coords
                    feat = np.array([x, y, z, x**2, y**2, z**2, x*y, x*z, y*z, 1])
                    return poly_coeffs @ feat
                else:
                    # 多点变换
                    result = np.zeros_like(camera_coords)
                    for i, coords in enumerate(camera_coords):
                        x, y, z = coords
                        feat = np.array([x, y, z, x**2, y**2, z**2, x*y, x*z, y*z, 1])
                        result[i] = poly_coeffs @ feat
                    return result
            
            return poly_transform
            
        except Exception as e:
            print(f"   多项式拟合计算失败: {e}")
            return None
    
    def _calculate_zoned_transform(self, camera_points, robot_points):
        """计算分区域变换"""
        try:
            # 根据距离分区
            distances = np.linalg.norm(camera_points, axis=1)
            median_dist = np.median(distances)
            
            # 分为近距离和远距离两组
            near_mask = distances <= median_dist
            far_mask = distances > median_dist
            
            if np.sum(near_mask) < 2 or np.sum(far_mask) < 2:
                print("   分区域数据不足，使用线性变换")
                return self._calculate_linear_transform(camera_points, robot_points)
            
            # 分别计算两个区域的变换
            near_transform = self._calculate_linear_transform(
                camera_points[near_mask], robot_points[near_mask]
            )
            far_transform = self._calculate_linear_transform(
                camera_points[far_mask], robot_points[far_mask]
            )
            
            if near_transform is None or far_transform is None:
                return None
            
            # 构建分区域变换函数
            def zoned_transform(camera_coords):
                if camera_coords.ndim == 1:
                    # 单点变换
                    dist = np.linalg.norm(camera_coords)
                    if dist <= median_dist:
                        homo = np.append(camera_coords, 1)
                        return (near_transform @ homo)[:3]
                    else:
                        homo = np.append(camera_coords, 1)
                        return (far_transform @ homo)[:3]
                else:
                    # 多点变换
                    result = np.zeros_like(camera_coords)
                    for i, coords in enumerate(camera_coords):
                        dist = np.linalg.norm(coords)
                        if dist <= median_dist:
                            homo = np.append(coords, 1)
                            result[i] = (near_transform @ homo)[:3]
                        else:
                            homo = np.append(coords, 1)
                            result[i] = (far_transform @ homo)[:3]
                    return result
            
            return zoned_transform
            
        except Exception as e:
            print(f"   分区域变换计算失败: {e}")
            return None
    
    def _evaluate_transform_accuracy(self, transform, camera_points, robot_points):
        """评估变换精度"""
        try:
            if callable(transform):
                # 函数类型变换
                predicted_points = transform(camera_points)
            else:
                # 矩阵类型变换
                ones = np.ones((camera_points.shape[0], 1))
                camera_homo = np.hstack([camera_points, ones])
                predicted_points = (transform @ camera_homo.T).T[:, :3]
            
            # 计算误差
            errors = np.linalg.norm(predicted_points - robot_points, axis=1)
            return np.mean(errors)
            
        except Exception as e:
            print(f"   变换精度评估失败: {e}")
            return float('inf')
    
    def _analyze_depth_for_cup(self, depth_image):
        """分析深度图像找水杯（高精度版本）"""
        height, width = depth_image.shape
        
        # Y坐标限制
        y_limit_pixel = int(height * self.y_detection_ratio)
        detection_mask = np.zeros_like(depth_image, dtype=bool)
        detection_mask[:y_limit_pixel, :] = True
        
        # 过滤有效深度值
        valid_mask = (depth_image > 200) & (depth_image < 3000) & detection_mask
        valid_depth = depth_image[valid_mask]
        
        if len(valid_depth) < 100:
            return None
        
        # 找最近物体
        closest_depth = np.min(valid_depth)
        
        # 更严格的容差
        tolerance = 10  # 1cm
        cup_mask = (np.abs(depth_image - closest_depth) <= tolerance) & detection_mask
        cup_pixels = np.sum(cup_mask)
        
        if cup_pixels < 20:
            return None
        
        # 高精度中心计算
        positions = np.where(cup_mask)
        if len(positions[0]) == 0:
            return None
        
        # 使用深度加权的中心计算
        depths = depth_image[positions]
        weights = 1.0 / (depths + 1)
        
        center_y = int(np.average(positions[0], weights=weights))
        center_x = int(np.average(positions[1], weights=weights))
        
        # 多点深度采样提高精度
        region_size = 2
        y_start = max(0, center_y - region_size)
        y_end = min(height, center_y + region_size)
        x_start = max(0, center_x - region_size)
        x_end = min(width, center_x + region_size)
        
        region_depths = depth_image[y_start:y_end, x_start:x_end]
        valid_region_depths = region_depths[region_depths > 0]
        
        if len(valid_region_depths) > 0:
            center_depth = int(np.median(valid_region_depths))
        else:
            center_depth = closest_depth
        
        # 转换3D坐标
        z = center_depth / 1000.0
        x = (center_x - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
        y = (center_y - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
        
        if z < 0.1 or z > 2.0:
            return None
        
        return (center_x, center_y, center_depth, x, y, z)
    
    def save_calibration_data(self, filename=None):
        """保存标定数据"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_calibration_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'calibration_points': self.calibration_points,
            'current_transform': self.current_transform.tolist() if isinstance(self.current_transform, np.ndarray) else None,
            'base_transform': self.base_transform.tolist(),
            'point_count': len(self.calibration_points)
        }
        
        filepath = os.path.join(current_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 标定数据已保存: {filepath}")
        return filepath
    
    def load_calibration_data(self, filename):
        """加载标定数据"""
        filepath = os.path.join(current_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.calibration_points = data.get('calibration_points', [])
            
            if data.get('current_transform'):
                self.current_transform = np.array(data['current_transform'])
            
            print(f"✅ 标定数据已加载: {filepath}")
            print(f"   标定点数量: {len(self.calibration_points)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 加载标定数据失败: {e}")
            return False
    
    def run_advanced_calibration(self):
        """运行高级标定流程"""
        print("🚀 高级手眼标定优化工具")
        print("🎯 目标：将12mm误差优化到5mm以内")
        
        if not self.initialize_camera():
            print("❌ 相机初始化失败")
            return False
        
        robot_ready = self.initialize_robot()
        if not robot_ready:
            print("⚠️ 机械臂初始化失败，将使用手动输入模式")
        
        print("\n📋 操作选项:")
        print("1. 收集新的标定点")
        print("2. 加载已有标定数据")
        print("3. 退出")
        
        choice = input("\n请选择操作 (1-3): ").strip()
        
        if choice == '1':
            print("\n🎯 开始收集新的标定点...")
            if not self.collect_grid_calibration_points():
                print("❌ 标定点收集失败")
                return False
        
        elif choice == '2':
            filename = input("请输入标定数据文件名: ").strip()
            if not self.load_calibration_data(filename):
                print("❌ 加载标定数据失败")
                return False
        
        elif choice == '3':
            print("👋 退出程序")
            return True
        
        else:
            print("❌ 无效选择")
            return False
        
        # 计算优化变换
        if len(self.calibration_points) >= 4:
            print(f"\n🔧 开始计算优化变换矩阵...")
            optimized_transform = self.calculate_advanced_transform()
            
            if optimized_transform is not None:
                # 保存结果
                save_file = self.save_calibration_data()
                print(f"\n✅ 高级标定完成!")
                print(f"📄 数据已保存: {save_file}")
                
                return True
            else:
                print(f"\n⚠️ 标定优化效果有限")
                print(f"💡 建议：")
                print(f"   1. 收集更多标定点（建议8-10个）")
                print(f"   2. 确保标定点分布均匀")
                print(f"   3. 检查标定物放置的稳定性")
                
                return False
        else:
            print(f"❌ 标定点数量不足: {len(self.calibration_points)}/4")
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.camera_pipeline:
            try:
                self.camera_pipeline.stop()
                print("✅ 相机已关闭")
            except:
                pass
        
        if self.robot:
            try:
                self.robot.ServoMoveEnd()
                self.robot.RobotEnable(0)
                self.robot.CloseRPC()
                print("✅ 机械臂连接已关闭")
            except:
                pass

def main():
    calibrator = AdvancedHandEyeCalibrator()
    
    try:
        success = calibrator.run_advanced_calibration()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断程序")
        return 1
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        calibrator.cleanup()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 程序终止")
        sys.exit(1)