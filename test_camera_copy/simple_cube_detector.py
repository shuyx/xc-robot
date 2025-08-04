#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于点云的小方块识别与3D坐标提取系统 (简化版)
功能：使用基础numpy和scipy进行点云处理，识别白色正方体并提取3D坐标
"""

import sys
import os
import time
import numpy as np
from pyorbbecsdk import *
from scipy.spatial.distance import cdist
from scipy.cluster.hierarchy import fclusterdata
from sklearn.linear_model import RANSACRegressor
from sklearn.decomposition import PCA

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

class SimpleCubeDetector:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.robot = None
        
        # 检测参数配置
        self.min_depth = 200      # 20cm
        self.max_depth = 700      # 70cm
        self.target_size = 50     # 5cm方块
        self.size_tolerance = 5   # ±5mm误差
        
        # 点云处理参数
        self.voxel_size = 0.005   # 5mm下采样
        self.statistical_nb_neighbors = 20
        self.statistical_std_ratio = 2.0
        self.plane_distance_threshold = 0.01  # 10mm
        self.dbscan_eps = 0.02    # 20mm
        self.dbscan_min_points = 10
        
        # 手眼变换矩阵 (与现有代码保持一致)
        self.hand_eye_transform = np.array([
            [-0.105501, -0.992918,  0.054622,    -250.6],
            [-0.979217,  0.113299,  0.168218,      40.9],
            [-0.173215, -0.035739, -0.984235,    -127.6],
            [ 0.000000,  0.000000,  0.000000,       1.0]
        ])
        
        print("✅ 简化版立方体检测器初始化完成")
    
    def camera_to_robot(self, camera_x, camera_y, camera_z):
        """相机坐标(mm) → 机械臂坐标(mm)"""
        camera_homo = np.array([camera_x, camera_y, camera_z, 1])
        robot_homo = self.hand_eye_transform @ camera_homo
        return robot_homo[0], robot_homo[1], robot_homo[2]
    
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
            height = depth_frame.get_height()
            width = depth_frame.get_width()
            depth_image = depth_data.reshape((height, width))
            
            # 转换彩色数据
            color_image = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
            color_image = color_image.reshape((height, width, 3))
            
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
            
            return points, colors
            
        except Exception as e:
            print(f"❌ 点云转换失败: {e}")
            return None, None
    
    def voxel_downsample(self, points, voxel_size):
        """体素下采样"""
        try:
            # 计算体素网格坐标
            voxel_coords = np.floor(points / voxel_size).astype(np.int32)
            
            # 创建唯一的体素键
            voxel_keys = voxel_coords[:, 0] * 73856093 ^ voxel_coords[:, 1] * 19349663 ^ voxel_coords[:, 2] * 83492791
            
            # 找到每个体素的第一个点
            unique_keys, unique_indices = np.unique(voxel_keys, return_index=True)
            
            return points[unique_indices]
            
        except Exception as e:
            print(f"❌ 下采样失败: {e}")
            return points
    
    def remove_statistical_outliers(self, points, nb_neighbors=20, std_ratio=2.0):
        """移除统计离群点"""
        try:
            if len(points) < nb_neighbors:
                return points
            
            # 计算每个点到其k近邻的平均距离
            distances = cdist(points, points)
            np.fill_diagonal(distances, np.inf)
            
            # 获取k近邻
            k_nearest_indices = np.argpartition(distances, nb_neighbors, axis=1)[:, :nb_neighbors]
            k_nearest_distances = np.take_along_axis(distances, k_nearest_indices, axis=1)
            
            # 计算平均距离
            mean_distances = np.mean(k_nearest_distances, axis=1)
            
            # 计算全局均值和标准差
            global_mean = np.mean(mean_distances)
            global_std = np.std(mean_distances)
            
            # 保留在阈值内的点
            threshold = global_mean + std_ratio * global_std
            valid_mask = mean_distances < threshold
            
            return points[valid_mask]
            
        except Exception as e:
            print(f"❌ 统计滤波失败: {e}")
            return points
    
    def fit_plane_ransac(self, points):
        """使用RANSAC拟合平面"""
        try:
            if len(points) < 3:
                return None, None
            
            # 使用RANSAC拟合平面
            # 平面方程: ax + by + cz + d = 0
            X = points[:, :2]  # x, y
            y = points[:, 2]   # z
            
            # 使用RANSAC回归
            ransac = RANSACRegressor()
            ransac.fit(X, y)
            
            # 获取平面参数
            # 从回归系数获取法向量
            a = -ransac.estimator_.coef_[0]
            b = -ransac.estimator_.coef_[1]
            c = 1.0
            d = -ransac.estimator_.intercept_
            
            # 归一化
            norm = np.sqrt(a**2 + b**2 + c**2)
            a, b, c, d = a/norm, b/norm, c/norm, d/norm
            
            # 计算点到平面的距离
            plane_distances = np.abs(points[:, 0] * a + points[:, 1] * b + points[:, 2] * c + d)
            
            # 找到平面内点
            inliers = plane_distances < self.plane_distance_threshold
            
            return np.array([a, b, c, d]), inliers
            
        except Exception as e:
            print(f"❌ 平面拟合失败: {e}")
            return None, None
    
    def cluster_dbscan(self, points, eps=0.02, min_samples=10):
        """使用DBSCAN进行聚类"""
        try:
            if len(points) < min_samples:
                return []
            
            # 使用层次聚类作为DBSCAN的替代
            # 计算距离矩阵
            distances = cdist(points, points)
            
            # 使用层次聚类
            # 设置距离阈值
            distance_threshold = eps
            
            # 进行聚类
            labels = fclusterdata(distances, distance_threshold, criterion='distance')
            
            # 获取聚类结果
            clusters = []
            unique_labels = np.unique(labels)
            
            for label in unique_labels:
                if label == -1:  # 噪声点
                    continue
                cluster_indices = np.where(labels == label)[0]
                if len(cluster_indices) >= min_samples:
                    clusters.append(points[cluster_indices])
            
            return clusters
            
        except Exception as e:
            print(f"❌ 聚类失败: {e}")
            return []
    
    def compute_obb(self, points):
        """计算有向包围盒"""
        try:
            if len(points) < 4:
                return None
            
            # 使用PCA计算主方向
            pca = PCA(n_components=3)
            pca.fit(points)
            
            # 获取主方向
            axes = pca.components_
            
            # 将点转换到PCA坐标系
            centered_points = points - np.mean(points, axis=0)
            rotated_points = centered_points @ axes.T
            
            # 计算AABB
            min_coords = np.min(rotated_points, axis=0)
            max_coords = np.max(rotated_points, axis=0)
            
            # 计算尺寸
            extent = max_coords - min_coords
            
            # 计算中心点
            center = np.mean(points, axis=0)
            
            return {
                'center': center,
                'extent': extent,
                'axes': axes
            }
            
        except Exception as e:
            print(f"❌ 包围盒计算失败: {e}")
            return None
    
    def preprocess_point_cloud(self, points):
        """预处理点云：深度过滤、去噪、下采样"""
        try:
            # 1. 深度过滤
            depth_mask = (points[:, 2] >= self.min_depth/1000.0) & (points[:, 2] <= self.max_depth/1000.0)
            
            if np.sum(depth_mask) < 100:
                print("❌ 深度过滤后点数太少")
                return None
            
            filtered_points = points[depth_mask]
            print(f"深度过滤后点数: {len(filtered_points)}")
            
            # 2. 统计滤波去噪
            cleaned_points = self.remove_statistical_outliers(
                filtered_points, 
                nb_neighbors=self.statistical_nb_neighbors,
                std_ratio=self.statistical_std_ratio
            )
            print(f"统计滤波后点数: {len(cleaned_points)}")
            
            # 3. 下采样
            downsampled_points = self.voxel_downsample(cleaned_points, voxel_size=self.voxel_size)
            print(f"下采样后点数: {len(downsampled_points)}")
            
            return downsampled_points
            
        except Exception as e:
            print(f"❌ 点云预处理失败: {e}")
            return None
    
    def remove_table_plane(self, points):
        """移除桌面平面"""
        try:
            # 使用RANSAC检测平面
            plane_params, inliers = self.fit_plane_ransac(points)
            
            if plane_params is None or len(inliers) < len(points) * 0.3:
                print("⚠️ 未检测到明显的桌面平面")
                return points
            
            # 移除平面点
            object_points = points[~inliers]
            print(f"移除桌面平面后点数: {len(object_points)}")
            
            return object_points
            
        except Exception as e:
            print(f"❌ 平面移除失败: {e}")
            return points
    
    def cluster_objects(self, points):
        """物体聚类"""
        try:
            clusters = self.cluster_dbscan(
                points, 
                eps=self.dbscan_eps, 
                min_samples=self.dbscan_min_points
            )
            
            print(f"检测到 {len(clusters)} 个物体簇")
            
            return clusters
            
        except Exception as e:
            print(f"❌ 物体聚类失败: {e}")
            return []
    
    def detect_cube_in_cluster(self, cluster_points):
        """在单个簇中检测立方体"""
        try:
            # 计算有向包围盒
            obb_result = self.compute_obb(cluster_points)
            
            if obb_result is None:
                return {'detected': False}
            
            # 获取包围盒尺寸
            extent = obb_result['extent'] * 1000.0  # m -> mm
            
            print(f"包围盒尺寸: {extent[0]:.1f} x {extent[1]:.1f} x {extent[2]:.1f} mm")
            
            # 检查是否符合立方体尺寸
            size_range = [self.target_size - self.size_tolerance, self.target_size + self.size_tolerance]
            
            if (size_range[0] <= extent[0] <= size_range[1] and
                size_range[0] <= extent[1] <= size_range[1] and
                size_range[0] <= extent[2] <= size_range[1]):
                
                print("✅ 检测到目标立方体!")
                
                # 获取立方体中心点
                center = obb_result['center'] * 1000.0  # m -> mm
                
                return {
                    'detected': True,
                    'center_mm': center,
                    'extent_mm': extent,
                    'points': cluster_points
                }
            else:
                print("❌ 尺寸不符合要求")
                return {'detected': False}
                
        except Exception as e:
            print(f"❌ 立方体检测失败: {e}")
            return {'detected': False}
    
    def detect_objects(self):
        """完整的物体检测流程"""
        print("🔍 开始物体检测...")
        
        try:
            # 1. 获取RGB-D帧
            depth_image, color_image = self.get_rgbd_frames()
            if depth_image is None or color_image is None:
                return None
            
            print(f"图像尺寸: {depth_image.shape}")
            
            # 2. 转换为点云
            points, colors = self.depth_to_point_cloud(depth_image, color_image)
            if points is None:
                return None
            
            print(f"原始点云点数: {len(points)}")
            
            # 3. 预处理点云
            processed_points = self.preprocess_point_cloud(points)
            if processed_points is None:
                return None
            
            # 4. 移除桌面平面
            object_points = self.remove_table_plane(processed_points)
            
            # 5. 物体聚类
            clusters = self.cluster_objects(object_points)
            
            # 6. 在每个簇中检测立方体
            detected_objects = []
            for i, cluster in enumerate(clusters):
                print(f"\n--- 检测簇 {i+1} ---")
                result = self.detect_cube_in_cluster(cluster)
                if result['detected']:
                    detected_objects.append(result)
            
            # 7. 返回检测结果
            if detected_objects:
                print(f"\n✅ 检测到 {len(detected_objects)} 个目标立方体")
                return detected_objects
            else:
                print("\n❌ 未检测到目标立方体")
                return None
                
        except Exception as e:
            print(f"❌ 物体检测失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
    detector = SimpleCubeDetector()
    
    try:
        print("🚀 启动简化版点云物体检测系统\n")
        
        # 初始化相机
        if not detector.initialize_camera():
            print("❌ 相机初始化失败")
            return 1
        
        print("\n" + "="*50)
        print("系统就绪！")
        print("功能：基于点云的小方块识别与3D坐标提取")
        print("="*50)
        
        print("\n📋 使用说明:")
        print("1. 将白色正方体(5cm x 5cm x 5cm)放置在相机前方20-70cm处")
        print("2. 确保物体在桌面上，背景相对干净")
        print("3. 系统将自动检测物体并输出3D坐标")
        
        while True:
            print("\n" + "-"*50)
            user_input = input("按回车开始检测，输入'q'退出: ").strip()
            
            if user_input.lower() == 'q':
                break
            
            print("\n🔍 开始检测...")
            
            # 执行物体检测
            detected_objects = detector.detect_objects()
            
            if detected_objects:
                print("\n🎯 检测结果:")
                for i, obj in enumerate(detected_objects):
                    center = obj['center_mm']
                    extent = obj['extent_mm']
                    
                    print(f"\n物体 {i+1}:")
                    print(f"  3D坐标 (相机坐标系): X={center[0]:.1f}, Y={center[1]:.1f}, Z={center[2]:.1f} mm")
                    print(f"  尺寸: {extent[0]:.1f} x {extent[1]:.1f} x {extent[2]:.1f} mm")
                    
                    # 转换为机械臂坐标
                    robot_x, robot_y, robot_z = detector.camera_to_robot(center[0], center[1], center[2])
                    print(f"  3D坐标 (机械臂坐标系): X={robot_x:.1f}, Y={robot_y:.1f}, Z={robot_z:.1f} mm")
                
                print("\n✅ 检测完成！")
            else:
                print("❌ 未检测到目标物体")
                print("建议：")
                print("1. 检查物体是否在视野范围内")
                print("2. 确保物体尺寸为5cm x 5cm x 5cm")
                print("3. 调整光照条件")
                print("4. 确保物体与背景有足够的深度差异")
        
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