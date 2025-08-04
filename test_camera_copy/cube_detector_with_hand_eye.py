#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于点云的小方块识别与3D坐标提取系统 - 增强版
功能：使用Open3D进行点云处理，识别白色正方体并提取3D坐标，添加完整的手眼转换功能
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

class PointCloudObjectDetector:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.robot = None
        
        # 检测参数配置
        self.min_depth = 200      # 20cm
        self.max_depth = 700      # 70cm
        self.target_size = 50     # 5cm方块
        self.size_tolerance = 20  # ±20mm误差 (增大容错)
        
        # 点云处理参数
        self.voxel_size = 0.004   # 4mm下采样 (更宽松)
        self.statistical_nb_neighbors = 15
        self.statistical_std_ratio = 2.5
        self.plane_distance_threshold = 0.015  # 15mm (更宽松)
        self.dbscan_eps = 0.02    # 20mm (更大的聚类半径)
        self.dbscan_min_points = 30  # 更少的最小点数
        
        # 手眼变换矩阵 (相机mm → 机械臂mm, 精度12mm)
        self.hand_eye_transform = np.array([
            [-0.105501, -0.992918,  0.054622,    -250.6],
            [-0.979217,  0.113299,  0.168218,      40.9],
            [-0.173215, -0.035739, -0.984235,    -127.6],
            [ 0.000000,  0.000000,  0.000000,       1.0]
        ])
        
        # 多帧检测参数
        self.multi_frame_enabled = True      # 启用多帧检测
        self.num_frames = 5                 # 检测帧数
        self.frame_interval = 0.1          # 帧间隔(秒)
        self.position_tolerance = 50.0     # 位置一致性容差(mm)
        self.stability_threshold = 0.7      # 稳定性阈值
        
        print("✅ 点云物体检测器初始化完成")
        print("📐 手眼变换矩阵已配置，精度12mm")
    
    def camera_to_robot(self, camera_x, camera_y, camera_z):
        """相机坐标(mm) → 机械臂坐标(mm)"""
        camera_homo = np.array([camera_x, camera_y, camera_z, 1])
        robot_homo = self.hand_eye_transform @ camera_homo
        return robot_homo[0], robot_homo[1], robot_homo[2]
    
    def robot_to_camera(self, robot_x, robot_y, robot_z):
        """机械臂坐标(mm) → 相机坐标(mm)"""
        robot_homo = np.array([robot_x, robot_y, robot_z, 1])
        # 计算逆变换
        try:
            inv_transform = np.linalg.inv(self.hand_eye_transform)
            camera_homo = inv_transform @ robot_homo
            return camera_homo[0], camera_homo[1], camera_homo[2]
        except:
            print("❌ 手眼变换矩阵求逆失败")
            return robot_x, robot_y, robot_z
    
    def transform_matrix_to_robot(self, camera_transform_matrix):
        """相机坐标系下的变换矩阵 → 机械臂坐标系下的变换矩阵"""
        try:
            # T_robot = T_hand_eye * T_camera
            robot_transform = self.hand_eye_transform @ camera_transform_matrix
            return robot_transform
        except Exception as e:
            print(f"❌ 变换矩阵转换失败: {e}")
            return camera_transform_matrix
    
    def get_hand_eye_transform_info(self):
        """获取手眼变换矩阵信息"""
        print("\n📐 手眼变换矩阵信息:")
        print(f"变换矩阵 (4x4):")
        for i, row in enumerate(self.hand_eye_transform):
            print(f"  [{i}] {row}")
        
        # 提取旋转矩阵和平移向量
        rotation_matrix = self.hand_eye_transform[:3, :3]
        translation_vector = self.hand_eye_transform[:3, 3]
        
        print(f"\n旋转矩阵:")
        for i, row in enumerate(rotation_matrix):
            print(f"  [{i}] {row}")
        
        print(f"\n平移向量 (mm): [{translation_vector[0]:.1f}, {translation_vector[1]:.1f}, {translation_vector[2]:.1f}]")
        
        # 计算欧拉角
        try:
            from scipy.spatial.transform import Rotation
            r = Rotation.from_matrix(rotation_matrix)
            euler_angles = r.as_euler('xyz', degrees=True)
            print(f"\n欧拉角 (度): Rx={euler_angles[0]:.1f}°, Ry={euler_angles[1]:.1f}°, Rz={euler_angles[2]:.1f}°")
        except:
            print("\n欧拉角计算失败 (需要scipy)")
        
        print(f"\n变换精度: 12mm")
        return rotation_matrix, translation_vector
    
    def camera_3d_to_pixel(self, camera_x_mm, camera_y_mm, camera_z_mm):
        """相机3D坐标(mm) → 深度图像像素坐标"""
        # 转换为米
        x_m = camera_x_mm / 1000.0
        y_m = camera_y_mm / 1000.0
        z_m = camera_z_mm / 1000.0
        
        # 使用相机内参投影到像素平面
        # u = fx * (x/z) + ppx
        # v = fy * (y/z) + ppy
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
            
            # 转换彩色数据
            color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
            color_height = color_frame.get_height()
            color_width = color_frame.get_width()
            
            print(f"深度图像尺寸: {depth_height}x{depth_width}")
            print(f"彩色图像尺寸: {color_height}x{color_width}")
            print(f"彩色数据大小: {len(color_data)} 字节")
            print(f"预期大小 (HxWx3): {color_height * color_width * 3} 字节")
            
            # 检查数据格式
            format_type = color_frame.get_format()
            print(f"彩色图像格式: {format_type}")
            
            # 根据格式处理数据
            if len(color_data) != color_height * color_width * 3:
                print(f"⚠️ 数据大小不匹配，尝试其他处理方式")
                
                # 尝试不同格式
                if format_type == 'RGB888':
                    # 标准RGB格式
                    pass
                elif 'MJPG' in str(format_type) or 'JPEG' in str(format_type):
                    # 压缩格式 - 尝试多种解压方式
                    import cv2
                    
                    # 方法1: 直接解压
                    try:
                        color_image = cv2.imdecode(color_data, cv2.IMREAD_COLOR)
                        if color_image is not None:
                            print(f"方法1解压成功，图像尺寸: {color_image.shape}")
                        else:
                            raise Exception("方法1解压返回None")
                    except:
                        # 方法2: 转换为numpy数组后再解压
                        try:
                            color_array = np.frombuffer(color_data, dtype=np.uint8)
                            color_image = cv2.imdecode(color_array, cv2.IMREAD_COLOR)
                            if color_image is not None:
                                print(f"方法2解压成功，图像尺寸: {color_image.shape}")
                            else:
                                raise Exception("方法2解压返回None")
                        except:
                            # 方法3: 使用PIL
                            try:
                                from PIL import Image
                                import io
                                image = Image.open(io.BytesIO(color_data))
                                color_image = np.array(image)
                                if len(color_image.shape) == 2:  # 灰度图
                                    color_image = cv2.cvtColor(color_image, cv2.COLOR_GRAY2RGB)
                                elif color_image.shape[2] == 4:  # RGBA
                                    color_image = color_image[:, :, :3]
                                print(f"方法3解压成功，图像尺寸: {color_image.shape}")
                            except Exception as e:
                                print(f"❌ 所有解压方法都失败了: {e}")
                                # 返回None但继续深度检测
                                color_image = np.zeros((depth_height, depth_width, 3), dtype=np.uint8)
                                print("使用空白彩色图像继续检测")
                else:
                    # 尝试作为单通道处理
                    try:
                        color_image = color_data.reshape((color_height, color_width))
                        # 转换为3通道
                        import cv2
                        color_image = cv2.cvtColor(color_image, cv2.COLOR_GRAY2RGB)
                        print(f"转换为3通道后尺寸: {color_image.shape}")
                    except:
                        print(f"❌ 无法处理彩色数据，格式: {format_type}")
                        # 返回None但继续深度检测
                        color_image = np.zeros((depth_height, depth_width, 3), dtype=np.uint8)
                        print("使用空白彩色图像继续检测")
            else:
                # 标准RGB处理
                color_image = color_data.reshape((color_height, color_width, 3))
            
            # 如果尺寸不同，调整彩色图像以匹配深度图像
            if depth_height != color_height or depth_width != color_width:
                from PIL import Image
                color_pil = Image.fromarray(color_image)
                color_pil = color_pil.resize((depth_width, depth_height), Image.Resampling.LANCZOS)
                color_image = np.array(color_pil)
                print(f"调整后的彩色图像尺寸: {color_image.shape}")
            
            return depth_image, color_image
            
        except Exception as e:
            print(f"❌ 获取RGB-D帧失败: {e}")
            return None, None
    
    def depth_to_point_cloud(self, depth_image, color_image):
        """将深度图像转换为点云"""
        try:
            # 获取图像尺寸
            height, width = depth_image.shape
            
            # 创建像素坐标网格
            u, v = np.meshgrid(np.arange(width), np.arange(height))
            
            # 转换为相机坐标系
            z = depth_image.astype(np.float32) / 1000.0  # mm -> m
            
            # 避免除零
            valid_mask = (depth_image > 0) & (depth_image < 5000)  # 0-5m
            z = np.where(valid_mask, z, np.nan)
            
            # 计算x,y坐标
            x = (u - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
            y = (v - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
            
            # 创建点云数据
            points = np.stack([x[valid_mask], y[valid_mask], z[valid_mask]], axis=-1)
            colors = color_image[valid_mask].astype(np.float32) / 255.0
            
            # 创建Open3D点云
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            pcd.colors = o3d.utility.Vector3dVector(colors)
            
            return pcd
            
        except Exception as e:
            print(f"❌ 点云转换失败: {e}")
            return None
    
    def preprocess_point_cloud(self, pcd):
        """预处理点云：深度过滤、去噪、下采样"""
        try:
            # 1. 深度过滤
            points = np.asarray(pcd.points)
            depth_mask = (points[:, 2] >= self.min_depth/1000.0) & (points[:, 2] <= self.max_depth/1000.0)
            
            if np.sum(depth_mask) < 100:
                print("❌ 深度过滤后点数太少")
                return None
            
            filtered_pcd = pcd.select_by_index(np.where(depth_mask)[0])
            print(f"深度过滤后点数: {len(filtered_pcd.points)}")
            
            # 2. 统计滤波去噪
            cleaned_pcd, _ = filtered_pcd.remove_statistical_outlier(
                nb_neighbors=self.statistical_nb_neighbors,
                std_ratio=self.statistical_std_ratio
            )
            print(f"统计滤波后点数: {len(cleaned_pcd.points)}")
            
            # 3. 下采样
            downsampled_pcd = cleaned_pcd.voxel_down_sample(voxel_size=self.voxel_size)
            print(f"下采样后点数: {len(downsampled_pcd.points)}")
            
            return downsampled_pcd
            
        except Exception as e:
            print(f"❌ 点云预处理失败: {e}")
            return None
    
    def remove_table_plane(self, pcd):
        """移除桌面平面"""
        try:
            # 使用RANSAC检测平面
            plane_model, inliers = pcd.segment_plane(
                distance_threshold=self.plane_distance_threshold,
                ransac_n=3,
                num_iterations=1000
            )
            
            if len(inliers) < len(pcd.points) * 0.3:  # 如果平面点数太少
                print("⚠️ 未检测到明显的桌面平面")
                return pcd
            
            # 移除平面点
            object_pcd = pcd.select_by_index(inliers, invert=True)
            print(f"移除桌面平面后点数: {len(object_pcd.points)}")
            
            return object_pcd
            
        except Exception as e:
            print(f"❌ 平面移除失败: {e}")
            return pcd
    
    def cluster_objects(self, pcd):
        """物体聚类"""
        try:
            # 使用DBSCAN进行聚类
            labels = np.array(pcd.cluster_dbscan(
                eps=self.dbscan_eps,
                min_points=self.dbscan_min_points
            ))
            
            # 获取聚类结果
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
            # 过滤掉太小的簇
            if len(cluster_pcd.points) < 50:
                print(f"❌ 簇点数太少: {len(cluster_pcd.points)}")
                return {'detected': False}
            
            # 计算有向包围盒
            obb = cluster_pcd.get_oriented_bounding_box()
            
            # 获取包围盒尺寸
            extent = obb.extent * 1000.0  # m -> mm
            center = obb.center * 1000.0  # m -> mm
            
            print(f"包围盒尺寸: {extent[0]:.1f} x {extent[1]:.1f} x {extent[2]:.1f} mm")
            
            # 基本过滤：排除明显不合理的尺寸
            max_dim = max(extent)
            min_dim = min(extent)
            
            # 计算体积和平均尺寸
            volume = extent[0] * extent[1] * extent[2]
            avg_size = np.mean(extent)
            size_error = abs(avg_size - self.target_size)
            
            print(f"平均尺寸: {avg_size:.1f} mm, 目标: {self.target_size} mm")
            print(f"尺寸误差: {size_error:.1f} mm")
            print(f"体积: {volume:.1f} mm³")
            
            # 宽松的过滤条件
            if max_dim > 300 or min_dim < 3:  # 最大尺寸不超过300mm，最小不小于3mm
                print(f"❌ 尺寸超出合理范围")
                return {'detected': False}
            
            if max_dim / min_dim > 5.0:  # 长宽比不超过5
                print(f"❌ 形状过于细长")
                return {'detected': False}
            
            # 检查是否可能为目标物体（更宽松的条件）
            # 方法1：平均尺寸接近目标
            size_ok = size_error <= self.size_tolerance
            
            # 方法2：体积接近目标体积 (50³ = 125000 mm³)
            target_volume = self.target_size ** 3
            volume_error = abs(volume - target_volume) / target_volume
            volume_ok = volume_error <= 0.5  # 体积误差不超过50%
            
            # 方法3：至少有一个维度在目标范围内
            dim_close = any(abs(dim - self.target_size) <= self.size_tolerance for dim in extent)
            
            # 检测结果
            is_possible_target = size_ok or (volume_ok and dim_close)
            
            if is_possible_target:
                print("✅ 检测到可能的目标立方体!")
                
                # 获取旋转矩阵
                rotation_matrix = obb.R
                
                # 创建4x4齐次变换矩阵
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
                print("❌ 尺寸不符合要求")
                return {'detected': False}
                
        except Exception as e:
            print(f"❌ 立方体检测失败: {e}")
            return {'detected': False}
    
    def _calculate_confidence(self, avg_size, size_error, volume_error, extent):
        """计算检测置信度 - 优化版本"""
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
    
    def multi_frame_detection(self):
        """多帧检测与平均处理"""
        if not self.multi_frame_enabled:
            print("🔍 单帧检测模式")
            return self.detect_objects()
        
        print(f"🔍 多帧检测模式 ({self.num_frames}帧)")
        
        # 存储多帧检测结果
        frame_results = []
        valid_detections = []
        
        for frame_idx in range(self.num_frames):
            print(f"\n--- 第 {frame_idx + 1}/{self.num_frames} 帧检测 ---")
            
            # 执行单帧检测（静默模式）
            result = self.detect_objects(verbose=False)
            
            if result and result.get('best_target'):
                best_target = result['best_target']
                frame_results.append({
                    'frame_index': frame_idx,
                    'center': best_target['center_mm'].copy(),
                    'extent': best_target['extent_mm'].copy(),
                    'confidence': best_target['confidence'],
                    'volume': best_target['volume_mm3'],
                    'transform_matrix': best_target['transform_matrix'].copy()
                })
                valid_detections.append(best_target)
                
                print(f"✅ 检测成功: 位置({best_target['center_mm'][0]:.1f}, {best_target['center_mm'][1]:.1f}, {best_target['center_mm'][2]:.1f}) mm, 置信度: {best_target['confidence']:.2f}")
            else:
                print("❌ 本帧未检测到目标")
                frame_results.append({'frame_index': frame_idx, 'detection_failed': True})
            
            # 帧间隔等待（除了最后一帧）
            if frame_idx < self.num_frames - 1:
                time.sleep(self.frame_interval)
        
        # 分析多帧检测结果
        return self._analyze_multi_frame_results(frame_results, valid_detections)
    
    def _analyze_multi_frame_results(self, frame_results, valid_detections):
        """分析多帧检测结果并计算平均值"""
        print(f"\n📊 多帧检测结果分析:")
        print(f"总帧数: {len(frame_results)}, 有效检测: {len(valid_detections)}")
        
        if len(valid_detections) < 2:
            print("⚠️ 有效检测数量不足，返回单帧结果")
            if valid_detections:
                return {
                    'multi_frame_result': True,
                    'best_target': valid_detections[0],
                    'valid_frames': len(valid_detections),
                    'stability_score': 0.0,
                    'position_std': np.array([np.inf, np.inf, np.inf]),
                    'recommendation': '检测数量不足，建议重新检测'
                }
            else:
                return {
                    'multi_frame_result': True,
                    'best_target': None,
                    'valid_frames': 0,
                    'stability_score': 0.0,
                    'position_std': np.array([np.inf, np.inf, np.inf]),
                    'recommendation': '未检测到目标，请检查物体位置'
                }
        
        # 提取位置数据
        positions = np.array([det['center_mm'] for det in valid_detections])
        confidences = np.array([det['confidence'] for det in valid_detections])
        
        # 计算位置统计信息
        mean_position = np.mean(positions, axis=0)
        position_std = np.std(positions, axis=0)
        max_std = np.max(position_std)
        
        # 计算稳定性评分
        stability_score = self._calculate_stability_score(position_std, confidences)
        
        print(f"平均位置: X={mean_position[0]:.1f}, Y={mean_position[1]:.1f}, Z={mean_position[2]:.1f} mm")
        print(f"位置标准差: σx={position_std[0]:.1f}, σy={position_std[1]:.1f}, σz={position_std[2]:.1f} mm")
        print(f"最大标准差: {max_std:.1f} mm")
        print(f"稳定性评分: {stability_score:.2f}")
        
        # 异常值检测和过滤
        filtered_positions, filtered_confidences, filtered_extents, filtered_transforms = self._filter_outliers(
            positions, confidences, valid_detections
        )
        
        if len(filtered_positions) > 0:
            # 计算加权平均（最近帧权重更高）
            weights = np.linspace(0.5, 1.0, len(filtered_confidences))
            weights = weights / np.sum(weights)
            
            final_position = np.average(filtered_positions, axis=0, weights=weights)
            final_confidence = np.mean(filtered_confidences)
            
            # 计算平均尺寸
            if len(filtered_extents) > 0:
                avg_extent = np.mean(filtered_extents, axis=0)
                avg_volume = np.prod(avg_extent)
            else:
                avg_extent = np.mean([det['extent_mm'] for det in valid_detections], axis=0)
                avg_volume = np.mean([det['volume_mm3'] for det in valid_detections])
            
            # 创建平均后的目标对象
            averaged_target = {
                'center_mm': final_position,
                'extent_mm': avg_extent,
                'confidence': final_confidence,
                'volume_mm3': avg_volume,
                'is_averaged': True,
                'original_frame_count': len(valid_detections),
                'filtered_frame_count': len(filtered_positions),
                'stability_score': stability_score
            }
            
            # 计算平均变换矩阵
            if len(filtered_transforms) > 0:
                avg_transform = self._average_transform_matrices(filtered_transforms, weights)
                averaged_target['transform_matrix'] = avg_transform
            
            print(f"✅ 多帧平均结果:")
            print(f"  最终位置: X={final_position[0]:.1f}, Y={final_position[1]:.1f}, Z={final_position[2]:.1f} mm")
            print(f"  平均尺寸: {avg_extent[0]:.1f} x {avg_extent[1]:.1f} x {avg_extent[2]:.1f} mm")
            print(f"  最终置信度: {final_confidence:.2f}")
            print(f"  使用帧数: {len(filtered_positions)}/{len(valid_detections)}")
            
            # 生成建议
            recommendation = self._generate_recommendation(stability_score, max_std, len(valid_detections))
            
            return {
                'multi_frame_result': True,
                'best_target': averaged_target,
                'valid_frames': len(valid_detections),
                'filtered_frames': len(filtered_positions),
                'stability_score': stability_score,
                'position_std': position_std,
                'recommendation': recommendation,
                'frame_details': frame_results
            }
        else:
            print("❌ 异常值过滤后无有效数据")
            return {
                'multi_frame_result': True,
                'best_target': None,
                'valid_frames': len(valid_detections),
                'stability_score': 0.0,
                'position_std': position_std,
                'recommendation': '检测结果不稳定，建议重新检测'
            }
    
    def _calculate_stability_score(self, position_std, confidences):
        """计算稳定性评分"""
        # 基于位置稳定性的评分
        position_stability = max(0, 1 - (np.max(position_std) / self.position_tolerance))
        
        # 基于置信度稳定性的评分
        confidence_stability = 1.0 - np.std(confidences) if len(confidences) > 1 else 1.0
        confidence_mean = np.mean(confidences)
        
        # 综合评分
        overall_stability = (position_stability * 0.6 + confidence_stability * 0.2 + confidence_mean * 0.2)
        
        return min(1.0, max(0.0, overall_stability))
    
    def _filter_outliers(self, positions, confidences, valid_detections):
        """过滤异常值"""
        if len(positions) <= 2:
            return positions, confidences, [det['extent_mm'] for det in valid_detections], [det['transform_matrix'] for det in valid_detections]
        
        # 计算每个点到中心的距离
        center = np.mean(positions, axis=0)
        distances = np.linalg.norm(positions - center, axis=1)
        
        # 使用统计方法识别异常值
        distance_mean = np.mean(distances)
        distance_std = np.std(distances)
        
        # 异常值阈值（2倍标准差）
        outlier_threshold = distance_mean + 2 * distance_std
        
        # 过滤异常值
        valid_indices = distances <= outlier_threshold
        
        filtered_positions = positions[valid_indices]
        filtered_confidences = confidences[valid_indices]
        filtered_extents = [valid_detections[i]['extent_mm'] for i in range(len(valid_detections)) if valid_indices[i]]
        filtered_transforms = [valid_detections[i]['transform_matrix'] for i in range(len(valid_detections)) if valid_indices[i]]
        
        removed_count = len(positions) - len(filtered_positions)
        if removed_count > 0:
            print(f"📊 过滤掉 {removed_count} 个异常值")
        
        return filtered_positions, filtered_confidences, filtered_extents, filtered_transforms
    
    def _average_transform_matrices(self, transform_matrices, weights):
        """平均变换矩阵"""
        if len(transform_matrices) == 1:
            return transform_matrices[0]
        
        # 对旋转部分使用四元数插值，对平移部分使用加权平均
        rotations = []
        translations = []
        
        for transform in transform_matrices:
            rotations.append(transform[:3, :3])
            translations.append(transform[:3, 3])
        
        # 加权平均平移部分
        avg_translation = np.average(translations, axis=0, weights=weights)
        
        # 简单平均旋转部分（或者使用第一个）
        avg_rotation = rotations[0]  # 简化处理
        
        # 构建平均变换矩阵
        avg_transform = np.eye(4)
        avg_transform[:3, :3] = avg_rotation
        avg_transform[:3, 3] = avg_translation
        
        return avg_transform
    
    def _generate_recommendation(self, stability_score, max_std, valid_frames):
        """生成检测建议"""
        if stability_score >= 0.8:
            return "检测结果优秀，可用于精确抓取"
        elif stability_score >= 0.6:
            return "检测结果良好，可用于抓取"
        elif stability_score >= 0.4:
            return "检测结果一般，建议重新检测以提高精度"
        elif valid_frames >= 3:
            return f"检测稳定性较低(σ={max_std:.1f}mm)，建议检查物体固定"
        else:
            return "检测成功次数太少，建议重新检测"
    
    def detect_objects(self, verbose=True):
        """完整的物体检测流程"""
        if verbose:
            print("🔍 开始物体检测...")
        
        try:
            # 1. 获取RGB-D帧
            depth_image, color_image = self.get_rgbd_frames()
            if depth_image is None or color_image is None:
                return None
            
            print(f"图像尺寸: {depth_image.shape}")
            
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
            
            # 6. 在每个簇中检测立方体
            detected_objects = []
            all_clusters_info = []
            
            for i, cluster in enumerate(clusters):
                print(f"\n--- 检测簇 {i+1} ---")
                result = self.detect_cube_in_cluster(cluster)
                
                # 无论是否检测到目标，都收集簇信息
                if len(cluster.points) >= 50:  # 只分析有足够点数的簇
                    cluster_center = np.mean(np.asarray(cluster.points), axis=0) * 1000.0  # 转换为mm
                    cluster_obb = cluster.get_oriented_bounding_box()
                    cluster_extent = cluster_obb.extent * 1000.0
                    
                    cluster_info = {
                        'cluster_id': i+1,
                        'center_mm': cluster_center,
                        'extent_mm': cluster_extent,
                        'point_count': len(cluster.points),
                        'avg_size_mm': np.mean(cluster_extent),
                        'volume_mm3': np.prod(cluster_extent),
                        'is_target': result['detected']
                    }
                    
                    if result['detected']:
                        cluster_info.update({
                            'confidence': result['confidence'],
                            'detailed_center': result['center_mm'],
                            'transform_matrix': result['transform_matrix']
                        })
                        detected_objects.append(result)
                    
                    all_clusters_info.append(cluster_info)
            
            # 7. 自动选择最佳目标
            best_target = None
            if detected_objects:
                print(f"\n✅ 检测到 {len(detected_objects)} 个目标立方体")
                
                # 自动选择置信度最高的目标
                best_target = max(detected_objects, key=lambda x: x['confidence'])
                print(f"\n🎯 自动选择最佳目标:")
                print(f"  置信度: {best_target['confidence']:.2f}")
                print(f"  中心坐标: X={best_target['center_mm'][0]:.1f}, Y={best_target['center_mm'][1]:.1f}, Z={best_target['center_mm'][2]:.1f} mm")
                print(f"  包围盒尺寸: {best_target['extent_mm'][0]:.1f} x {best_target['extent_mm'][1]:.1f} x {best_target['extent_mm'][2]:.1f} mm")
                print(f"  体积: {best_target['volume_mm3']:.1f} mm³")
                
                # 计算并显示最佳目标的像素坐标
                best_pixel_u, best_pixel_v = self.camera_3d_to_pixel(
                    best_target['center_mm'][0], 
                    best_target['center_mm'][1], 
                    best_target['center_mm'][2]
                )
                print(f"  深度图像像素坐标: ({best_pixel_u}, {best_pixel_v})")
                
                # 计算机械臂坐标
                best_robot_x, best_robot_y, best_robot_z = self.camera_to_robot(
                    best_target['center_mm'][0], 
                    best_target['center_mm'][1], 
                    best_target['center_mm'][2]
                )
                print(f"  机械臂坐标: X={best_robot_x:.1f}, Y={best_robot_y:.1f}, Z={best_robot_z:.1f} mm")
                
                print(f"\n💡 建议：在相机软件中验证像素位置 ({best_pixel_u}, {best_pixel_v}) 是否对应目标物体")
                
            else:
                print("\n❌ 未检测到符合条件的目标立方体")
            
            # 显示所有簇的信息供用户参考
            if all_clusters_info:
                print(f"\n📋 所有检测到的物体簇信息 ({len(all_clusters_info)} 个):")
                print("-" * 100)
                for cluster in all_clusters_info:
                    print(f"\n簇 {cluster['cluster_id']}:")
                    print(f"  点数: {cluster['point_count']}")
                    print(f"  中心坐标: X={cluster['center_mm'][0]:.1f}, Y={cluster['center_mm'][1]:.1f}, Z={cluster['center_mm'][2]:.1f} mm")
                    print(f"  包围盒尺寸: {cluster['extent_mm'][0]:.1f} x {cluster['extent_mm'][1]:.1f} x {cluster['extent_mm'][2]:.1f} mm")
                    print(f"  平均尺寸: {cluster['avg_size_mm']:.1f} mm")
                    print(f"  体积: {cluster['volume_mm3']:.1f} mm³")
                    
                    # 计算像素坐标
                    pixel_u, pixel_v = self.camera_3d_to_pixel(
                        cluster['center_mm'][0], 
                        cluster['center_mm'][1], 
                        cluster['center_mm'][2]
                    )
                    print(f"  深度图像像素坐标: ({pixel_u}, {pixel_v})")
                    
                    if cluster['is_target']:
                        print(f"  ✅ 可能是目标物体 (置信度: {cluster.get('confidence', 0):.2f})")
                        robot_x, robot_y, robot_z = self.camera_to_robot(
                            cluster['detailed_center'][0], 
                            cluster['detailed_center'][1], 
                            cluster['detailed_center'][2]
                        )
                        print(f"  机械臂坐标: X={robot_x:.1f}, Y={robot_y:.1f}, Z={robot_z:.1f} mm")
                        
                        # 也计算目标物体的像素坐标
                        target_pixel_u, target_pixel_v = self.camera_3d_to_pixel(
                            cluster['detailed_center'][0], 
                            cluster['detailed_center'][1], 
                            cluster['detailed_center'][2]
                        )
                        print(f"  目标物体像素坐标: ({target_pixel_u}, {target_pixel_v})")
                    else:
                        print(f"  ❌ 不符合目标要求")
                        
                        # 即使不符合要求，也提供机械臂坐标供参考
                        robot_x, robot_y, robot_z = self.camera_to_robot(
                            cluster['center_mm'][0], 
                            cluster['center_mm'][1], 
                            cluster['center_mm'][2]
                        )
                        print(f"  参考机械臂坐标: X={robot_x:.1f}, Y={robot_y:.1f}, Z={robot_z:.1f} mm")
                    
                    # 添加深度信息验证
                    print(f"  💡 在相机软件中查看像素位置 ({pixel_u}, {pixel_v}) 附近的深度值")
            
            return {
                'detected_objects': detected_objects,
                'all_clusters': all_clusters_info,
                'best_target': best_target,
                'processed_pcd': processed_pcd
            }
                
        except Exception as e:
            print(f"❌ 物体检测失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def visualize_detection(self, pcd, detected_objects):
        """可视化检测结果"""
        try:
            # 创建可视化窗口
            vis = o3d.visualization.Visualizer()
            vis.create_window()
            
            # 添加原始点云
            vis.add_geometry(pcd)
            
            # 添加检测到的立方体包围盒
            for obj in detected_objects:
                vis.add_geometry(obj['obb'])
            
            # 设置视角
            ctr = vis.get_view_control()
            ctr.set_zoom(0.8)
            
            # 显示
            vis.run()
            vis.destroy_window()
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        if self.camera_pipeline:
            try:
                self.camera_pipeline.stop()
                print("✅ 相机已关闭")
            except:
                pass

def main():
    """主函数"""
    detector = PointCloudObjectDetector()
    
    try:
        print("🚀 启动点云物体检测系统\n")
        
        # 初始化相机
        if not detector.initialize_camera():
            print("❌ 相机初始化失败")
            return 1
        
        print("\n" + "="*50)
        print("系统就绪！")
        print("功能：基于点云的小方块识别与3D坐标提取 - 增强版")
        print("="*50)
        
        # 显示手眼变换矩阵信息
        detector.get_hand_eye_transform_info()
        
        print("\n📋 使用说明:")
        print("1. 将白色正方体(5cm x 5cm x 5cm)放置在相机前方20-70cm处")
        print("2. 确保物体在桌面上，背景相对干净")
        print("3. 系统将使用多帧检测提高精度，自动检测物体并选择最佳目标")
        print("4. 显示稳定性评分和建议，帮助判断检测质量")
        print("5. 检测结果会自动进行手眼坐标转换，显示机械臂坐标")
        
        while True:
            print("\n" + "-"*50)
            user_input = input("按回车开始检测，输入'q'退出: ").strip()
            
            if user_input.lower() == 'q':
                break
            
            print("\n🔍 开始检测...")
            
            # 执行多帧检测
            detection_result = detector.multi_frame_detection()
            
            if detection_result and detection_result.get('best_target'):
                print("\n🎯 多帧检测完成！")
                
                best_target = detection_result['best_target']
                
                # 显示检测结果摘要
                print(f"\n✅ 最终检测结果:")
                print(f"  检测模式: {'多帧平均' if best_target.get('is_averaged') else '单帧'}")
                print(f"  稳定性评分: {detection_result.get('stability_score', 0):.2f}")
                print(f"  有效帧数: {detection_result.get('valid_frames', 0)}/{detector.num_frames}")
                print(f"  最终置信度: {best_target['confidence']:.2f}")
                
                # 显示详细位置信息
                print(f"  最终位置: X={best_target['center_mm'][0]:.1f}, Y={best_target['center_mm'][1]:.1f}, Z={best_target['center_mm'][2]:.1f} mm")
                print(f"  平均尺寸: {best_target['extent_mm'][0]:.1f} x {best_target['extent_mm'][1]:.1f} x {best_target['extent_mm'][2]:.1f} mm")
                print(f"  体积: {best_target['volume_mm3']:.1f} mm³")
                
                # 显示位置稳定性
                position_std = detection_result.get('position_std', np.array([0, 0, 0]))
                print(f"  位置稳定性: σx={position_std[0]:.1f}, σy={position_std[1]:.1f}, σz={position_std[2]:.1f} mm")
                
                # 计算并显示像素坐标
                best_pixel_u, best_pixel_v = detector.camera_3d_to_pixel(
                    best_target['center_mm'][0], 
                    best_target['center_mm'][1], 
                    best_target['center_mm'][2]
                )
                print(f"  深度图像像素坐标: ({best_pixel_u}, {best_pixel_v})")
                
                # 计算机械臂坐标
                best_robot_x, best_robot_y, best_robot_z = detector.camera_to_robot(
                    best_target['center_mm'][0], 
                    best_target['center_mm'][1], 
                    best_target['center_mm'][2]
                )
                print(f"  🎯 机械臂目标坐标: X={best_robot_x:.1f}, Y={best_robot_y:.1f}, Z={best_robot_z:.1f} mm")
                
                # 计算目标物体的变换矩阵（如果有的话）
                if 'transform_matrix' in best_target:
                    robot_transform = detector.transform_matrix_to_robot(best_target['transform_matrix'])
                    robot_position = robot_transform[:3, 3]
                    print(f"  🔄 完整变换矩阵位置: X={robot_position[0]:.1f}, Y={robot_position[1]:.1f}, Z={robot_position[2]:.1f} mm")
                
                # 显示建议
                recommendation = detection_result.get('recommendation', '')
                print(f"\n💡 建议: {recommendation}")
                
                # 如果是多帧平均结果，显示额外信息
                if best_target.get('is_averaged'):
                    print(f"📊 多帧统计: 使用了{best_target.get('filtered_frame_count', 0)}/{best_target.get('original_frame_count', 0)}帧有效数据")
                
                print(f"\n💡 验证建议: 在相机软件中查看像素位置 ({best_pixel_u}, {best_pixel_v}) 是否对应目标物体")
                
            else:
                print("\n❌ 未检测到符合条件的目标物体")
                
                # 显示失败原因
                if detection_result:
                    recommendation = detection_result.get('recommendation', '')
                    if recommendation:
                        print(f"💡 分析结果: {recommendation}")
                
                print("建议：")
                print("1. 检查物体是否在视野范围内")
                print("2. 确保物体尺寸为5cm x 5cm x 5cm")
                print("3. 调整光照条件")
                print("4. 确保物体与背景有足够的深度差异")
                print("5. 尝试调整相机的检测距离(20-70cm)")
                print("6. 检查物体是否固定稳定，避免晃动")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断程序")
        return 1
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        detector.cleanup()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 程序终止")
        sys.exit(1)