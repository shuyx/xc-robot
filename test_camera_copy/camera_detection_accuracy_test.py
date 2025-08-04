#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相机检测精度和稳定性测试脚本
测试不同检测方法的稳定性和精度
"""

import sys
import os
import time
import numpy as np
import cv2
from pyorbbecsdk import *

class CameraAccuracyTester:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.test_results = []
        
        # 测试配置
        self.test_configs = [
            {
                "name": "单帧检测",
                "frame_count": 1,
                "use_kalman": False,
                "use_median": False
            },
            {
                "name": "3帧平均",
                "frame_count": 3,
                "use_kalman": False,
                "use_median": False
            },
            {
                "name": "5帧平均",
                "frame_count": 5,
                "use_kalman": False,
                "use_median": False
            },
            {
                "name": "5帧+中位数",
                "frame_count": 5,
                "use_kalman": False,
                "use_median": True
            },
            {
                "name": "5帧+卡尔曼",
                "frame_count": 5,
                "use_kalman": True,
                "use_median": False
            }
        ]
        
        # 卡尔曼滤波器
        self.kalman_filter = None
        
        # 检测参数
        self.y_detection_ratio = 0.75
    
    def initialize_kalman_filter(self):
        """初始化卡尔曼滤波器"""
        self.kalman_filter = cv2.KalmanFilter(6, 3)  # 6状态，3测量
        
        # 状态转移矩阵 (位置和速度)
        self.kalman_filter.transitionMatrix = np.array([
            [1, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 1],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]
        ], dtype=np.float32)
        
        # 测量矩阵
        self.kalman_filter.measurementMatrix = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0]
        ], dtype=np.float32)
        
        # 过程噪声
        self.kalman_filter.processNoiseCov = np.eye(6, dtype=np.float32) * 0.1
        
        # 测量噪声
        self.kalman_filter.measurementNoiseCov = np.eye(3, dtype=np.float32) * 10
        
        # 误差协方差
        self.kalman_filter.errorCovPost = np.eye(6, dtype=np.float32) * 1000
    
    def initialize_camera(self):
        """初始化相机"""
        print("🔍 初始化相机系统...")
        
        self.camera_pipeline = Pipeline()
        config = Config()
        
        # 配置深度流
        depth_profile_list = self.camera_pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        if depth_profile_list is None:
            raise Exception("无法获取深度传感器")
        
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        if depth_profile is None:
            raise Exception("无法获取默认深度配置")
        
        config.enable_stream(depth_profile)
        self.camera_pipeline.start(config)
        
        # 获取相机内参
        try:
            depth_video_profile = depth_profile.as_video_stream_profile()
            self.camera_intrinsics = depth_video_profile.get_intrinsics()
            print(f"✅ 相机内参: fx={self.camera_intrinsics.fx:.1f}, fy={self.camera_intrinsics.fy:.1f}")
        except:
            # 使用估算值
            self.camera_intrinsics = type('obj', (object,), {
                'fx': 500.0, 'fy': 500.0, 
                'ppx': 320.0, 'ppy': 240.0
            })()
            print("✅ 使用估算相机内参")
        
        # 预热相机
        print("相机预热中...")
        for _ in range(10):
            self.camera_pipeline.wait_for_frames(100)
        
        print("✅ 相机初始化完成")
        return True
    
    def capture_single_detection(self):
        """捕获单次检测结果"""
        try:
            # 获取深度帧
            frames = self.camera_pipeline.wait_for_frames(1000)
            depth_frame = frames.get_depth_frame()
            
            if not depth_frame:
                return None
            
            # 转换深度数据
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            height = depth_frame.get_height()
            width = depth_frame.get_width()
            depth_image = depth_data.reshape((height, width))
            
            # 分析深度数据找水杯
            result = self._analyze_depth_for_cup(depth_image)
            
            if result:
                pixel_x, pixel_y, depth_mm, x_3d, y_3d, z_3d = result
                return np.array([x_3d * 1000, y_3d * 1000, z_3d * 1000])  # 转换为mm
            else:
                return None
                
        except Exception as e:
            print(f"检测异常: {e}")
            return None
    
    def _analyze_depth_for_cup(self, depth_image):
        """分析深度图像找水杯"""
        height, width = depth_image.shape
        
        # 1. 创建Y坐标限制掩码
        y_limit_pixel = int(height * self.y_detection_ratio)
        detection_mask = np.zeros_like(depth_image, dtype=bool)
        detection_mask[:y_limit_pixel, :] = True
        
        # 2. 在限制区域内过滤有效深度值
        valid_mask = (depth_image > 200) & (depth_image < 3000) & detection_mask
        valid_depth = depth_image[valid_mask]
        
        if len(valid_depth) < 100:
            return None
        
        # 3. 找最近物体
        closest_depth = np.min(valid_depth)
        
        # 4. 找该深度附近的所有像素
        tolerance = 15
        cup_mask = (np.abs(depth_image - closest_depth) <= tolerance) & detection_mask
        cup_pixels = np.sum(cup_mask)
        
        if cup_pixels < 30:
            return None
        
        # 5. 计算物体中心（加权平均）
        positions = np.where(cup_mask)
        if len(positions[0]) == 0:
            return None
        
        # 使用深度加权
        depths = depth_image[positions]
        weights = 1.0 / (depths + 1)
        
        center_y = int(np.average(positions[0], weights=weights))
        center_x = int(np.average(positions[1], weights=weights))
        
        # 6. 获取中心点深度（周围点的中位数）
        region_size = 3
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
        
        # 7. 转换3D坐标
        z = center_depth / 1000.0
        x = (center_x - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
        y = (center_y - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
        
        # 8. 距离合理性检查
        if z < 0.1 or z > 2.0:
            return None
        
        return (center_x, center_y, center_depth, x, y, z)
    
    def test_detection_method(self, config, test_rounds=10):
        """测试特定检测方法"""
        print(f"\n{'='*50}")
        print(f"🧪 测试方法: {config['name']}")
        print(f"{'='*50}")
        
        all_measurements = []
        detection_times = []
        
        # 重置卡尔曼滤波器
        if config['use_kalman']:
            self.initialize_kalman_filter()
        
        for round_idx in range(test_rounds):
            print(f"第 {round_idx + 1}/{test_rounds} 轮测试...")
            
            start_time = time.time()
            
            # 收集多帧数据
            frame_detections = []
            for frame_idx in range(config['frame_count']):
                detection = self.capture_single_detection()
                if detection is not None:
                    frame_detections.append(detection)
                time.sleep(0.1)  # 帧间间隔
            
            end_time = time.time()
            detection_times.append(end_time - start_time)
            
            if len(frame_detections) == 0:
                print(f"  第{round_idx + 1}轮：无有效检测")
                continue
            
            # 数据处理
            if config['use_median']:
                # 使用中位数
                final_coords = np.median(frame_detections, axis=0)
            else:
                # 使用平均值
                final_coords = np.mean(frame_detections, axis=0)
            
            # 卡尔曼滤波
            if config['use_kalman'] and self.kalman_filter is not None:
                # 预测
                self.kalman_filter.predict()
                
                # 更新
                measurement = final_coords.reshape(-1, 1).astype(np.float32)
                self.kalman_filter.correct(measurement)
                
                # 获取滤波结果
                state = self.kalman_filter.statePost
                final_coords = np.array([state[0, 0], state[1, 0], state[2, 0]])
            
            all_measurements.append(final_coords)
            
            print(f"  第{round_idx + 1}轮：X={final_coords[0]:.1f}, Y={final_coords[1]:.1f}, Z={final_coords[2]:.1f}mm "
                  f"(用时: {detection_times[-1]:.2f}s)")
        
        # 计算统计信息
        if len(all_measurements) < 2:
            print(f"❌ 有效测量数据不足")
            return None
        
        measurements = np.array(all_measurements)
        
        # 统计分析
        mean_coords = np.mean(measurements, axis=0)
        std_coords = np.std(measurements, axis=0)
        
        # 稳定性评估（标准差）
        stability_score = np.sqrt(np.sum(std_coords**2))
        
        # 检测成功率
        success_rate = len(all_measurements) / test_rounds * 100
        
        # 平均检测时间
        avg_detection_time = np.mean(detection_times)
        
        result = {
            'config_name': config['name'],
            'success_rate': success_rate,
            'mean_coords': mean_coords,
            'std_coords': std_coords,
            'stability_score': stability_score,
            'avg_detection_time': avg_detection_time,
            'valid_measurements': len(all_measurements),
            'total_rounds': test_rounds
        }
        
        print(f"\n📊 测试结果:")
        print(f"  成功率: {success_rate:.1f}% ({len(all_measurements)}/{test_rounds})")
        print(f"  平均坐标: X={mean_coords[0]:.1f}, Y={mean_coords[1]:.1f}, Z={mean_coords[2]:.1f}mm")
        print(f"  标准差: X={std_coords[0]:.1f}, Y={std_coords[1]:.1f}, Z={std_coords[2]:.1f}mm")
        print(f"  稳定性评分: {stability_score:.1f}mm (越小越稳定)")
        print(f"  平均检测时间: {avg_detection_time:.2f}秒")
        
        return result
    
    def run_comprehensive_test(self):
        """运行综合精度测试"""
        print("🚀 相机检测精度和稳定性测试")
        print("🎯 目标：比较不同检测方法的稳定性和精度")
        
        if not self.initialize_camera():
            return False
        
        print(f"\n📋 测试说明:")
        print(f"1. 将水杯放置在相机前方固定位置")
        print(f"2. 每种方法将进行10轮检测")
        print(f"3. 统计成功率、平均值、标准差等指标")
        print(f"4. 请保持水杯位置不变")
        
        # 等待用户准备
        input("\n准备好后按回车开始测试...")
        
        print(f"\n将测试 {len(self.test_configs)} 种检测方法...")
        
        for i, config in enumerate(self.test_configs):
            print(f"\n{'🔸' * 15} 测试 {i+1}/{len(self.test_configs)} {'🔸' * 15}")
            
            result = self.test_detection_method(config)
            if result:
                self.test_results.append(result)
                print(f"✅ '{config['name']}' 测试完成")
            else:
                print(f"❌ '{config['name']}' 测试失败")
            
            # 测试间休息
            if i < len(self.test_configs) - 1:
                print("⏳ 等待3秒后进行下一组测试...")
                time.sleep(3)
        
        # 生成测试报告
        self.generate_test_report()
        return True
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("📊 相机检测精度和稳定性测试报告")
        print("="*80)
        
        if not self.test_results:
            print("❌ 没有可用的测试结果")
            return
        
        # 按稳定性评分排序（越小越好）
        sorted_results = sorted(self.test_results, key=lambda x: x['stability_score'])
        
        print(f"\n🏆 性能排名（按稳定性）:")
        print("-" * 80)
        print(f"{'排名':<4} {'方法名称':<12} {'成功率':<8} {'稳定性':<10} {'平均距离':<10} {'检测时间':<8}")
        print("-" * 80)
        
        for rank, result in enumerate(sorted_results, 1):
            avg_distance = result['mean_coords'][2]  # Z坐标
            print(f"{rank:<4} {result['config_name']:<12} {result['success_rate']:<7.1f}% "
                  f"{result['stability_score']:<9.1f}mm {avg_distance:<9.1f}mm {result['avg_detection_time']:<7.2f}s")
        
        # 详细分析
        print(f"\n📈 详细分析:")
        best_stable = sorted_results[0]
        best_success = max(self.test_results, key=lambda x: x['success_rate'])
        fastest = min(self.test_results, key=lambda x: x['avg_detection_time'])
        
        print(f"🎯 最稳定方法: {best_stable['config_name']}")
        print(f"   稳定性评分: {best_stable['stability_score']:.1f}mm")
        print(f"   坐标标准差: X={best_stable['std_coords'][0]:.1f}, Y={best_stable['std_coords'][1]:.1f}, Z={best_stable['std_coords'][2]:.1f}mm")
        
        print(f"\n🏅 最高成功率: {best_success['config_name']}")
        print(f"   成功率: {best_success['success_rate']:.1f}%")
        
        print(f"\n⚡ 最快检测: {fastest['config_name']}")
        print(f"   检测时间: {fastest['avg_detection_time']:.2f}秒")
        
        # 坐标分析
        print(f"\n📍 坐标统计:")
        for result in sorted_results:
            print(f"   {result['config_name']}:")
            print(f"     平均: X={result['mean_coords'][0]:.1f}, Y={result['mean_coords'][1]:.1f}, Z={result['mean_coords'][2]:.1f}mm")
            print(f"     标准差: X={result['std_coords'][0]:.1f}, Y={result['std_coords'][1]:.1f}, Z={result['std_coords'][2]:.1f}mm")
        
        # 推荐建议
        print(f"\n💡 推荐建议:")
        high_stability = [r for r in sorted_results if r['stability_score'] < 10.0]
        
        if high_stability:
            print(f"   ✅ 推荐使用高稳定性方法（稳定性<10mm）:")
            for result in high_stability:
                print(f"     • {result['config_name']} (稳定性: {result['stability_score']:.1f}mm)")
        
        high_success = [r for r in self.test_results if r['success_rate'] >= 80.0]
        if high_success:
            print(f"   🎯 高成功率方法（≥80%）:")
            for result in high_success:
                print(f"     • {result['config_name']} (成功率: {result['success_rate']:.1f}%)")
        
        # 根据应用场景推荐
        print(f"\n🎮 应用场景推荐:")
        print(f"   • 高精度抓取: 推荐 {best_stable['config_name']} (最稳定)")
        print(f"   • 实时应用: 推荐 {fastest['config_name']} (最快)")
        print(f"   • 一般应用: 推荐 5帧平均 (平衡性能)")
    
    def cleanup(self):
        """清理资源"""
        if self.camera_pipeline:
            try:
                self.camera_pipeline.stop()
                print("✅ 相机已关闭")
            except:
                pass

def main():
    tester = CameraAccuracyTester()
    
    try:
        print("🧪 相机检测精度和稳定性测试程序")
        print("📊 将测试多种检测方法的性能差异")
        
        confirm = input("\n确认开始精度测试？请确保水杯已放置在固定位置 (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 测试已取消")
            return 1
        
        success = tester.run_comprehensive_test()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断测试")
        return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 程序终止")
        sys.exit(1)