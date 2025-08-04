#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2.0高级手眼协同抓取系统
功能：基于点云几何特征拟合的立方体检测与6DoF抓取控制
升级：从简单深度检测升级为完整的点云处理和位姿估计
"""

import sys
import os
import time
import numpy as np
from pyorbbecsdk import *
import open3d as o3d

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
    ROBOT_AVAILABLE = False

class AdvancedHandEyeGraspingSystem:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.robot = None
        self.initial_tcp_pose = None
        
        # 检测参数配置（基于调试经验优化）
        self.min_depth = 200              # 20cm
        self.max_depth = 700              # 70cm
        self.target_size = 50             # 5cm方块
        self.size_tolerance = 20           # ±20mm误差
        
        # 点云处理参数（优化版）
        self.voxel_size = 0.004           # 4mm下采样
        self.statistical_nb_neighbors = 15
        self.statistical_std_ratio = 2.5
        self.plane_distance_threshold = 0.015
        self.dbscan_eps = 0.02
        self.dbscan_min_points = 30
        
        # 机械臂控制参数
        self.approach_distance = 100      # 接近距离100mm
        self.grasp_distance = 50          # 抓取距离50mm
        self.lift_distance = 100          # 提升距离100mm
        self.servo_speed = 5.0            # 伺服速度
        self.servo_cycle_time = 0.02     # 伺服周期20ms
        
        # 手眼变换矩阵（与1.0版本保持一致）
        self.hand_eye_transform = np.array([
            [-0.105501, -0.992918,  0.054622,    -250.6],
            [-0.979217,  0.113299,  0.168218,      40.9],
            [-0.173215, -0.035739, -0.984235,    -127.6],
            [ 0.000000,  0.000000,  0.000000,       1.0]
        ])
        
        # 安全参数
        self.max_reach_distance = 500     # 最大移动距离500mm
        self.min_z_distance = 100         # 最小Z距离100mm
        
        print("✅ 2.0高级手眼协同抓取系统初始化完成")
    
    def camera_to_robot(self, camera_x, camera_y, camera_z):
        """相机坐标(mm) → 机械臂坐标(mm)"""
        camera_homo = np.array([camera_x, camera_y, camera_z, 1])
        robot_homo = self.hand_eye_transform @ camera_homo
        return robot_homo[0], robot_homo[1], robot_homo[2]
    
    def camera_3d_to_pixel(self, camera_x_mm, camera_y_mm, camera_z_mm):
        """相机3D坐标(mm) → 深度图像像素坐标"""
        x_m = camera_x_mm / 1000.0
        y_m = camera_y_mm / 1000.0
        z_m = camera_z_mm / 1000.0
        
        pixel_u = self.camera_intrinsics.fx * (x_m / z_m) + self.camera_intrinsics.ppx
        pixel_v = self.camera_intrinsics.fy * (y_m / z_m) + self.camera_intrinsics.ppy
        
        return int(round(pixel_u)), int(round(pixel_v))
    
    def initialize_camera(self):
        """初始化相机"""
        print("🔍 初始化相机...")
        
        self.camera_pipeline = Pipeline()
        config = Config()
        
        # 配置深度流和彩色流
        depth_profile_list = self.camera_pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        color_profile_list = self.camera_pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        color_profile = color_profile_list.get_default_video_stream_profile()
        
        config.enable_stream(depth_profile)
        config.enable_stream(color_profile)
        self.camera_pipeline.start(config)
        
        # 获取相机内参
        try:
            depth_video_profile = depth_profile.as_video_stream_profile()
            self.camera_intrinsics = depth_video_profile.get_intrinsics()
            print(f"✅ 相机内参: fx={self.camera_intrinsics.fx:.1f}, fy={self.camera_intrinsics.fy:.1f}")
        except:
            self.camera_intrinsics = type('obj', (object,), {
                'fx': 500.0, 'fy': 500.0, 
                'ppx': 320.0, 'ppy': 240.0,
                'width': 640, 'height': 480
            })()
            print("✅ 使用估算相机内参")
        
        # 预热相机
        for _ in range(5):
            self.camera_pipeline.wait_for_frames(100)
        
        print("✅ 相机初始化完成")
        return True
    
    def initialize_robot(self):
        """初始化机械臂"""
        if not ROBOT_AVAILABLE:
            print("⚠️ 机械臂库不可用")
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
            
            # 记录初始位姿
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error == 0:
                self.initial_tcp_pose = current_tcp.copy()
                print(f"✅ 记录初始位姿: X={current_tcp[0]:.1f}, Y={current_tcp[1]:.1f}, Z={current_tcp[2]:.1f}")
            
            return True
            
        except Exception as e:
            print(f"❌ 机械臂初始化异常: {e}")
            return False
    
    def get_rgbd_frames(self):
        """获取RGB-D帧数据"""
        try:
            frames = self.camera_pipeline.wait_for_frames(1000)
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            
            if not depth_frame or not color_frame:
                print("❌ 未获取到完整的RGB-D帧")
                return None, None
            
            # 转换深度数据
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_height = depth_frame.get_height()
            depth_width = depth_frame.get_width()
            depth_image = depth_data.reshape((depth_height, depth_width))
            
            # 转换彩色数据（简化处理）
            color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
            color_height = color_frame.get_height()
            color_width = color_frame.get_width()
            
            # 处理彩色图像
            if len(color_data) == color_height * color_width * 3:
                color_image = color_data.reshape((color_height, color_width, 3))
            else:
                # 尝试处理压缩格式
                try:
                    import cv2
                    color_array = np.frombuffer(color_data, dtype=np.uint8)
                    color_image = cv2.imdecode(color_array, cv2.IMREAD_COLOR)
                    if color_image is None:
                        raise Exception("解压失败")
                except:
                    # 使用空白图像
                    color_image = np.zeros((depth_height, depth_width, 3), dtype=np.uint8)
            
            # 调整尺寸匹配
            if depth_height != color_height or depth_width != color_width:
                from PIL import Image
                color_pil = Image.fromarray(color_image)
                color_pil = color_pil.resize((depth_width, depth_height), Image.Resampling.LANCZOS)
                color_image = np.array(color_pil)
            
            return depth_image, color_image
            
        except Exception as e:
            print(f"❌ 获取RGB-D帧失败: {e}")
            return None, None
    
    def depth_to_point_cloud(self, depth_image, color_image):
        """将深度图像转换为点云"""
        try:
            height, width = depth_image.shape
            u, v = np.meshgrid(np.arange(width), np.arange(height))
            
            z = depth_image.astype(np.float32) / 1000.0
            valid_mask = (depth_image > 0) & (depth_image < 5000)
            z = np.where(valid_mask, z, np.nan)
            
            x = (u - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
            y = (v - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
            
            points = np.stack([x[valid_mask], y[valid_mask], z[valid_mask]], axis=-1)
            colors = color_image[valid_mask].astype(np.float32) / 255.0
            
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            pcd.colors = o3d.utility.Vector3dVector(colors)
            
            return pcd
            
        except Exception as e:
            print(f"❌ 点云转换失败: {e}")
            return None
    
    def preprocess_point_cloud(self, pcd):
        """预处理点云"""
        try:
            points = np.asarray(pcd.points)
            depth_mask = (points[:, 2] >= self.min_depth/1000.0) & (points[:, 2] <= self.max_depth/1000.0)
            
            if np.sum(depth_mask) < 100:
                print("❌ 深度过滤后点数太少")
                return None
            
            filtered_pcd = pcd.select_by_index(np.where(depth_mask)[0])
            print(f"深度过滤后点数: {len(filtered_pcd.points)}")
            
            cleaned_pcd, _ = filtered_pcd.remove_statistical_outlier(
                nb_neighbors=self.statistical_nb_neighbors,
                std_ratio=self.statistical_std_ratio
            )
            print(f"统计滤波后点数: {len(cleaned_pcd.points)}")
            
            downsampled_pcd = cleaned_pcd.voxel_down_sample(voxel_size=self.voxel_size)
            print(f"下采样后点数: {len(downsampled_pcd.points)}")
            
            return downsampled_pcd
            
        except Exception as e:
            print(f"❌ 点云预处理失败: {e}")
            return None
    
    def remove_table_plane(self, pcd):
        """移除桌面平面"""
        try:
            plane_model, inliers = pcd.segment_plane(
                distance_threshold=self.plane_distance_threshold,
                ransac_n=3,
                num_iterations=1000
            )
            
            if len(inliers) < len(pcd.points) * 0.3:
                print("⚠️ 未检测到明显的桌面平面")
                return pcd
            
            object_pcd = pcd.select_by_index(inliers, invert=True)
            print(f"移除桌面平面后点数: {len(object_pcd.points)}")
            
            return object_pcd
            
        except Exception as e:
            print(f"❌ 平面移除失败: {e}")
            return pcd
    
    def cluster_objects(self, pcd):
        """物体聚类"""
        try:
            labels = np.array(pcd.cluster_dbscan(
                eps=self.dbscan_eps,
                min_points=self.dbscan_min_points
            ))
            
            max_label = labels.max()
            print(f"检测到 {max_label + 1} 个物体簇")
            
            clusters = []
            for i in range(max_label + 1):
                cluster_indices = np.where(labels == i)[0]
                cluster_pcd = pcd.select_by_index(cluster_indices)
                clusters.append(cluster_pcd)
            
            return clusters
            
        except Exception as e:
            print(f"❌ 物体聚类失败: {e}")
            return []
    
    def detect_cube_in_cluster(self, cluster_pcd):
        """在单个簇中检测立方体"""
        try:
            if len(cluster_pcd.points) < 50:
                return {'detected': False}
            
            obb = cluster_pcd.get_oriented_bounding_box()
            extent = obb.extent * 1000.0
            center = obb.center * 1000.0
            
            print(f"包围盒尺寸: {extent[0]:.1f} x {extent[1]:.1f} x {extent[2]:.1f} mm")
            
            max_dim = max(extent)
            min_dim = min(extent)
            volume = extent[0] * extent[1] * extent[2]
            avg_size = np.mean(extent)
            size_error = abs(avg_size - self.target_size)
            
            print(f"平均尺寸: {avg_size:.1f} mm, 目标: {self.target_size} mm")
            print(f"尺寸误差: {size_error:.1f} mm")
            print(f"体积: {volume:.1f} mm³")
            
            # 过滤条件
            if max_dim > 300 or min_dim < 3:
                return {'detected': False}
            
            if max_dim / min_dim > 5.0:
                return {'detected': False}
            
            # 多维度判断
            size_ok = size_error <= self.size_tolerance
            target_volume = self.target_size ** 3
            volume_error = abs(volume - target_volume) / target_volume
            volume_ok = volume_error <= 0.5
            dim_close = any(abs(dim - self.target_size) <= self.size_tolerance for dim in extent)
            
            is_possible_target = size_ok or (volume_ok and dim_close)
            
            if is_possible_target:
                print("✅ 检测到可能的目标立方体!")
                
                rotation_matrix = obb.R
                transform_matrix = np.eye(4)
                transform_matrix[:3, :3] = rotation_matrix
                transform_matrix[:3, 3] = center
                
                return {
                    'detected': True,
                    'center_mm': center,
                    'extent_mm': extent,
                    'transform_matrix': transform_matrix,
                    'obb': obb,
                    'confidence': self._calculate_confidence(avg_size, size_error, volume_error, extent),
                    'volume_mm3': volume,
                    'avg_size_mm': avg_size
                }
            else:
                return {'detected': False}
                
        except Exception as e:
            print(f"❌ 立方体检测失败: {e}")
            return {'detected': False}
    
    def _calculate_confidence(self, avg_size, size_error, volume_error, extent):
        """计算检测置信度"""
        size_confidence = max(0, 1 - (size_error / self.size_tolerance))
        
        dimensions = sorted(extent)
        size_ratio_1 = dimensions[1] / dimensions[0]
        size_ratio_2 = dimensions[2] / dimensions[1]
        ratio_error_1 = abs(size_ratio_1 - 1.0)
        ratio_error_2 = abs(size_ratio_2 - 1.0)
        shape_confidence = max(0, 1 - (ratio_error_1 + ratio_error_2) / 2)
        
        target_volume = self.target_size ** 3
        actual_volume = np.prod(extent)
        if actual_volume > 0 and target_volume > 0:
            volume_ratio = actual_volume / target_volume
            log_volume_error = abs(np.log(volume_ratio))
            volume_confidence = max(0, 1 - log_volume_error / 0.5)
        else:
            volume_confidence = 0
        
        size_std = np.std(extent)
        size_mean = np.mean(extent)
        size_consistency = max(0, 1 - (size_std / size_mean) * 3)
        
        overall_confidence = (
            size_confidence * 0.3 +
            shape_confidence * 0.3 +
            volume_confidence * 0.2 +
            size_consistency * 0.2
        )
        
        return min(1.0, max(0.0, overall_confidence))
    
    def detect_target_cube(self):
        """检测目标立方体"""
        print("🔍 开始目标立方体检测...")
        
        try:
            # 1. 获取RGB-D帧
            depth_image, color_image = self.get_rgbd_frames()
            if depth_image is None or color_image is None:
                return None
            
            # 2. 转换为点云
            pcd = self.depth_to_point_cloud(depth_image, color_image)
            if pcd is None:
                return None
            
            # 3. 预处理点云
            processed_pcd = self.preprocess_point_cloud(pcd)
            if processed_pcd is None:
                return None
            
            # 4. 移除桌面平面
            object_pcd = self.remove_table_plane(processed_pcd)
            
            # 5. 物体聚类
            clusters = self.cluster_objects(object_pcd)
            
            # 6. 检测立方体
            detected_objects = []
            for i, cluster in enumerate(clusters):
                print(f"\n--- 检测簇 {i+1} ---")
                result = self.detect_cube_in_cluster(cluster)
                if result['detected']:
                    detected_objects.append(result)
            
            # 7. 选择最佳目标
            if detected_objects:
                best_target = max(detected_objects, key=lambda x: x['confidence'])
                print(f"\n🎯 选择最佳目标 (置信度: {best_target['confidence']:.2f}):")
                print(f"  中心坐标: X={best_target['center_mm'][0]:.1f}, Y={best_target['center_mm'][1]:.1f}, Z={best_target['center_mm'][2]:.1f} mm")
                print(f"  包围盒尺寸: {best_target['extent_mm'][0]:.1f} x {best_target['extent_mm'][1]:.1f} x {best_target['extent_mm'][2]:.1f} mm")
                
                # 计算像素坐标
                pixel_u, pixel_v = self.camera_3d_to_pixel(
                    best_target['center_mm'][0], 
                    best_target['center_mm'][1], 
                    best_target['center_mm'][2]
                )
                print(f"  像素坐标: ({pixel_u}, {pixel_v})")
                
                # 计算机械臂坐标
                robot_x, robot_y, robot_z = self.camera_to_robot(
                    best_target['center_mm'][0], 
                    best_target['center_mm'][1], 
                    best_target['center_mm'][2]
                )
                print(f"  机械臂坐标: X={robot_x:.1f}, Y={robot_y:.1f}, Z={robot_z:.1f} mm")
                
                return best_target
            else:
                print("\n❌ 未检测到目标立方体")
                return None
                
        except Exception as e:
            print(f"❌ 检测失败: {e}")
            return None
    
    def calculate_grasp_poses(self, target_center):
        """计算抓取位姿序列"""
        try:
            # 获取目标在机械臂坐标系中的坐标
            target_robot = np.array(self.camera_to_robot(
                target_center[0], target_center[1], target_center[2]
            ))
            
            print(f"\n🎯 计算抓取位姿...")
            print(f"目标位置: X={target_robot[0]:.1f}, Y={target_robot[1]:.1f}, Z={target_robot[2]:.1f} mm")
            
            # 获取当前机械臂位姿
            if ROBOT_AVAILABLE and self.robot:
                error, current_tcp = self.robot.GetActualToolFlangePose()
                if error != 0:
                    print("❌ 获取当前位姿失败")
                    return None
            else:
                current_tcp = np.array([0, 0, 0, 0, 0, 0])
            
            # 计算抓取位姿序列
            # 1. 接近位姿（目标上方100mm）
            approach_pose = current_tcp.copy()
            approach_pose[0] = target_robot[0]
            approach_pose[1] = target_robot[1]
            approach_pose[2] = target_robot[2] + self.approach_distance
            
            # 2. 抓取位姿（目标位置）
            grasp_pose = current_tcp.copy()
            grasp_pose[0] = target_robot[0]
            grasp_pose[1] = target_robot[1]
            grasp_pose[2] = target_robot[2]
            
            # 3. 提升位姿（抓取后提升100mm）
            lift_pose = grasp_pose.copy()
            lift_pose[2] = grasp_pose[2] + self.lift_distance
            
            print(f"接近位姿: X={approach_pose[0]:.1f}, Y={approach_pose[1]:.1f}, Z={approach_pose[2]:.1f} mm")
            print(f"抓取位姿: X={grasp_pose[0]:.1f}, Y={grasp_pose[1]:.1f}, Z={grasp_pose[2]:.1f} mm")
            print(f"提升位姿: X={lift_pose[0]:.1f}, Y={lift_pose[1]:.1f}, Z={lift_pose[2]:.1f} mm")
            
            return {
                'approach': approach_pose,
                'grasp': grasp_pose,
                'lift': lift_pose
            }
            
        except Exception as e:
            print(f"❌ 计算抓取位姿失败: {e}")
            return None
    
    def execute_grasping_sequence(self, grasp_poses):
        """执行抓取序列"""
        if not ROBOT_AVAILABLE or self.robot is None:
            print("⚠️ 机械臂不可用，仅模拟抓取序列")
            print("模拟抓取序列:")
            print(f"  1. 移动到接近位姿: X={grasp_poses['approach'][0]:.1f}, Y={grasp_poses['approach'][1]:.1f}, Z={grasp_poses['approach'][2]:.1f}")
            print(f"  2. 移动到抓取位姿: X={grasp_poses['grasp'][0]:.1f}, Y={grasp_poses['grasp'][1]:.1f}, Z={grasp_poses['grasp'][2]:.1f}")
            print(f"  3. 抓取并提升到: X={grasp_poses['lift'][0]:.1f}, Y={grasp_poses['lift'][1]:.1f}, Z={grasp_poses['lift'][2]:.1f}")
            return True
        
        print("\n🤖 开始执行抓取序列...")
        
        try:
            # 获取当前位姿
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                print("❌ 获取当前位姿失败")
                return False
            
            # 1. 移动到接近位姿
            print("📍 步骤1: 移动到接近位姿...")
            success = self._smooth_move_to_pose(current_tcp, grasp_poses['approach'])
            if not success:
                print("❌ 接近位姿移动失败")
                return False
            
            time.sleep(1)
            
            # 2. 移动到抓取位姿
            print("📍 步骤2: 移动到抓取位姿...")
            error, current_tcp = self.robot.GetActualToolFlangePose()
            success = self._smooth_move_to_pose(current_tcp, grasp_poses['grasp'])
            if not success:
                print("❌ 抓取位姿移动失败")
                return False
            
            time.sleep(1)
            
            # 3. 模拟抓取（这里可以添加夹爪控制）
            print("📍 步骤3: 执行抓取...")
            print("  (夹爪闭合指令)")
            time.sleep(2)
            
            # 4. 提升到安全位姿
            print("📍 步骤4: 提升到安全位姿...")
            error, current_tcp = self.robot.GetActualToolFlangePose()
            success = self._smooth_move_to_pose(current_tcp, grasp_poses['lift'])
            if not success:
                print("❌ 提升位姿移动失败")
                return False
            
            print("\n✅ 抓取序列执行完成！")
            return True
            
        except Exception as e:
            print(f"❌ 抓取序列执行失败: {e}")
            return False
    
    def _smooth_move_to_pose(self, start_pose, target_pose):
        """平滑移动到目标位姿"""
        try:
            # 计算移动距离
            distance = ((target_pose[0] - start_pose[0])**2 + 
                       (target_pose[1] - start_pose[1])**2 + 
                       (target_pose[2] - start_pose[2])**2)**0.5
            
            if distance < 10:
                print("⚠️ 移动距离太小，跳过")
                return True
            
            if distance > self.max_reach_distance:
                print(f"⚠️ 移动距离过大，限制为{self.max_reach_distance}mm")
                scale = self.max_reach_distance / distance
                target_pose = target_pose.copy()
                target_pose[0] = start_pose[0] + scale * (target_pose[0] - start_pose[0])
                target_pose[1] = start_pose[1] + scale * (target_pose[1] - start_pose[1])
                target_pose[2] = start_pose[2] + scale * (target_pose[2] - start_pose[2])
                distance = self.max_reach_distance
            
            # 使用ServoCart进行平滑移动
            steps = max(50, int(distance / 5.0))
            
            # 启动伺服模式
            ret = self.robot.ServoMoveStart()
            if ret != 0:
                print(f"❌ 伺服模式启动失败: {ret}")
                return False
            
            # 执行平滑轨迹
            success_count = 0
            for i in range(steps + 1):
                t = i / steps
                
                # 五次多项式插值
                if t <= 0.0:
                    t_smooth = 0.0
                elif t >= 1.0:
                    t_smooth = 1.0
                else:
                    t_smooth = 6 * t**5 - 15 * t**4 + 10 * t**3
                
                # 计算插值位姿
                interpolated_pose = []
                for j in range(6):
                    value = start_pose[j] + t_smooth * (target_pose[j] - start_pose[j])
                    interpolated_pose.append(value)
                
                # 发送伺服指令
                ret = self.robot.ServoCart(mode=0, desc_pos=interpolated_pose, vel=self.servo_speed)
                if ret == 0:
                    success_count += 1
                
                time.sleep(self.servo_cycle_time)
            
            # 结束伺服模式
            ret = self.robot.ServoMoveEnd()
            if ret != 0:
                print(f"⚠️ 伺服模式结束警告: {ret}")
            
            success_rate = success_count / (steps + 1) * 100
            print(f"轨迹执行成功率: {success_rate:.1f}%")
            
            return success_rate > 80
            
        except Exception as e:
            print(f"❌ 平滑移动失败: {e}")
            return False
    
    def return_to_initial_pose(self):
        """返回初始位姿"""
        if not ROBOT_AVAILABLE or self.robot is None or self.initial_tcp_pose is None:
            print("⚠️ 机械臂不可用或未记录初始位姿")
            return True
            
        print("🔄 返回初始位姿...")
        
        try:
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                return False
            
            distance = ((current_tcp[0] - self.initial_tcp_pose[0])**2 + 
                       (current_tcp[1] - self.initial_tcp_pose[1])**2 + 
                       (current_tcp[2] - self.initial_tcp_pose[2])**2)**0.5
            
            return self._smooth_move_to_pose(current_tcp, self.initial_tcp_pose, distance)
            
        except Exception as e:
            print(f"❌ 返回初始位姿失败: {e}")
            return False
    
    def run_advanced_grasping(self):
        """运行高级手眼协同抓取流程"""
        print("=" * 60)
        print("🎯 2.0高级手眼协同抓取系统")
        print("📋 流程：点云检测 → 立方体识别 → 位姿估计 → 抓取执行")
        print("=" * 60)
        
        try:
            # 1. 检测目标立方体
            target_cube = self.detect_target_cube()
            if target_cube is None:
                print("❌ 目标立方体检测失败")
                return False
            
            # 2. 计算抓取位姿
            grasp_poses = self.calculate_grasp_poses(target_cube['center_mm'])
            if grasp_poses is None:
                print("❌ 抓取位姿计算失败")
                return False
            
            # 3. 执行抓取序列
            print(f"\n🚀 开始执行抓取序列...")
            success = self.execute_grasping_sequence(grasp_poses)
            
            if success:
                print("\n✅ 抓取序列执行完成！")
                
                # 4. 等待3秒
                print("\n⏳ 等待3秒...")
                time.sleep(3.0)
                
                # 5. 返回初始位姿
                print("\n🔄 返回初始位姿...")
                return_success = self.return_to_initial_pose()
                
                if return_success:
                    print("\n🎉 2.0高级手眼协同抓取完成！")
                    return True
                else:
                    print("\n⚠️ 抓取成功，但返回失败")
                    return False
            else:
                print("\n❌ 抓取序列执行失败")
                return False
                
        except Exception as e:
            print(f"❌ 系统异常: {e}")
            import traceback
            traceback.print_exc()
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
    """主函数"""
    grasping_system = AdvancedHandEyeGraspingSystem()
    
    try:
        print("🚀 启动2.0高级手眼协同抓取系统\n")
        
        # 初始化相机
        if not grasping_system.initialize_camera():
            print("❌ 相机初始化失败")
            return 1
        
        # 初始化机械臂
        robot_ready = grasping_system.initialize_robot()
        if not robot_ready:
            print("⚠️ 机械臂初始化失败，将在仅检测模式下运行")
        
        print("\n" + "="*50)
        print("系统就绪！")
        if ROBOT_AVAILABLE and robot_ready:
            print("✅ 完整抓取模式（相机 + 机械臂）")
        else:
            print("⚠️ 仅检测模式")
        print("="*50)
        
        print("\n📋 使用说明:")
        print("1. 将白色正方体(5cm x 5cm x 5cm)放置在相机前方20-70cm处")
        print("2. 确保物体在桌面上，背景相对干净")
        print("3. 系统将自动检测物体并执行抓取序列")
        print("4. 支持6DoF位姿估计和平滑抓取控制")
        
        input("\n准备好后按回车开始...")
        
        # 执行高级抓取
        success = grasping_system.run_advanced_grasping()
        
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
        grasping_system.cleanup()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 程序终止")
        sys.exit(1)