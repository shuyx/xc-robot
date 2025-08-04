#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合抓取成功率测试
测试不同场景下的手眼协同系统性能
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
    print("将在仅检测模式下运行")
    ROBOT_AVAILABLE = False

class ComprehensiveGrabTester:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.robot = None
        self.initial_tcp_pose = None
        
        # 手眼变换矩阵
        self.hand_eye_transform = np.array([
            [-0.105501, -0.992918,  0.054622,    -250.6],
            [-0.979217,  0.113299,  0.168218,      40.9],
            [-0.173215, -0.035739, -0.984235,    -127.6],
            [ 0.000000,  0.000000,  0.000000,       1.0]
        ])
        
        # 测试场景配置
        self.test_scenarios = [
            {
                "name": "理想条件",
                "description": "单个水杯，良好光照，干净背景",
                "expected_success_rate": 95,
                "detection_params": {
                    "y_detection_ratio": 0.75,
                    "frame_count": 5,
                    "tolerance": 15
                }
            },
            {
                "name": "近距离测试",
                "description": "水杯距离相机30-50cm",
                "expected_success_rate": 90,
                "detection_params": {
                    "y_detection_ratio": 0.75,
                    "frame_count": 5,
                    "tolerance": 12
                }
            },
            {
                "name": "远距离测试", 
                "description": "水杯距离相机80-120cm",
                "expected_success_rate": 85,
                "detection_params": {
                    "y_detection_ratio": 0.75,
                    "frame_count": 7,
                    "tolerance": 20
                }
            },
            {
                "name": "侧向位置",
                "description": "水杯在相机视野边缘",
                "expected_success_rate": 80,
                "detection_params": {
                    "y_detection_ratio": 0.8,
                    "frame_count": 8,
                    "tolerance": 18
                }
            },
            {
                "name": "复杂背景",
                "description": "背景有其他物体干扰",
                "expected_success_rate": 75,
                "detection_params": {
                    "y_detection_ratio": 0.7,
                    "frame_count": 10,
                    "tolerance": 12
                }
            }
        ]
        
        # 测试结果存储
        self.test_results = []
    
    def initialize_camera(self):
        """初始化相机"""
        print("🔍 初始化相机系统...")
        
        self.camera_pipeline = Pipeline()
        config = Config()
        
        depth_profile_list = self.camera_pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        config.enable_stream(depth_profile)
        self.camera_pipeline.start(config)
        
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
            self.record_initial_pose()
            return True
            
        except Exception as e:
            print(f"❌ 机械臂初始化异常: {e}")
            return False
    
    def record_initial_pose(self):
        """记录初始TCP位姿"""
        if not ROBOT_AVAILABLE or self.robot is None:
            return
            
        try:
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error == 0:
                self.initial_tcp_pose = current_tcp.copy()
                print(f"✅ 已记录初始位姿: X={current_tcp[0]:.1f}, Y={current_tcp[1]:.1f}, Z={current_tcp[2]:.1f}")
            else:
                print(f"⚠️ 获取初始位姿失败，错误码: {error}")
        except Exception as e:
            print(f"⚠️ 记录初始位姿异常: {e}")
    
    def camera_to_robot(self, camera_x, camera_y, camera_z):
        """相机坐标(mm) → 机械臂坐标(mm)"""
        camera_homo = np.array([camera_x, camera_y, camera_z, 1])
        robot_homo = self.hand_eye_transform @ camera_homo
        return robot_homo[0], robot_homo[1], robot_homo[2]
    
    def detect_cup_multi_frame(self, detection_params):
        """多帧检测水杯"""
        frame_count = detection_params['frame_count']
        
        valid_detections = []
        
        for frame_idx in range(frame_count):
            try:
                frames = self.camera_pipeline.wait_for_frames(1000)
                depth_frame = frames.get_depth_frame()
                
                if not depth_frame:
                    continue
                
                depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
                height = depth_frame.get_height()
                width = depth_frame.get_width()
                depth_image = depth_data.reshape((height, width))
                
                result = self._analyze_depth_for_cup(depth_image, detection_params)
                
                if result:
                    pixel_x, pixel_y, depth_mm, x_3d, y_3d, z_3d = result
                    valid_detections.append((x_3d * 1000, y_3d * 1000, z_3d * 1000))
                
                time.sleep(0.1)
                
            except Exception as e:
                continue
        
        if len(valid_detections) < max(1, frame_count // 2):
            return None
        
        # 计算平均值
        avg_coords = np.mean(valid_detections, axis=0)
        
        # 转换到机械臂坐标系
        robot_x, robot_y, robot_z = self.camera_to_robot(avg_coords[0], avg_coords[1], avg_coords[2])
        
        return {
            'camera_coords': avg_coords,
            'robot_coords': np.array([robot_x, robot_y, robot_z]),
            'detection_count': len(valid_detections),
            'total_frames': frame_count
        }
    
    def _analyze_depth_for_cup(self, depth_image, detection_params):
        """分析深度图像找水杯"""
        height, width = depth_image.shape
        
        y_detection_ratio = detection_params['y_detection_ratio']
        tolerance = detection_params['tolerance']
        
        # Y坐标限制
        y_limit_pixel = int(height * y_detection_ratio)
        detection_mask = np.zeros_like(depth_image, dtype=bool)
        detection_mask[:y_limit_pixel, :] = True
        
        # 过滤有效深度值
        valid_mask = (depth_image > 200) & (depth_image < 3000) & detection_mask
        valid_depth = depth_image[valid_mask]
        
        if len(valid_depth) < 100:
            return None
        
        # 找最近物体
        closest_depth = np.min(valid_depth)
        
        # 找该深度附近的所有像素
        cup_mask = (np.abs(depth_image - closest_depth) <= tolerance) & detection_mask
        cup_pixels = np.sum(cup_mask)
        
        if cup_pixels < 30:
            return None
        
        # 计算物体中心
        positions = np.where(cup_mask)
        if len(positions[0]) == 0:
            return None
        
        center_y = int(np.mean(positions[0]))
        center_x = int(np.mean(positions[1]))
        
        # 获取中心点深度
        center_depth = depth_image[center_y, center_x]
        if center_depth == 0:
            center_depth = closest_depth
        
        # 转换3D坐标
        z = center_depth / 1000.0
        x = (center_x - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
        y = (center_y - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
        
        if z < 0.1 or z > 2.0:
            return None
        
        return (center_x, center_y, center_depth, x, y, z)
    
    def simulate_robot_movement(self, robot_coords):
        """模拟或执行机械臂移动"""
        if not ROBOT_AVAILABLE or self.robot is None:
            print(f"🤖 模拟移动到: X={robot_coords[0]:.1f}, Y={robot_coords[1]:.1f}, Z={robot_coords[2]:.1f}")
            time.sleep(2)  # 模拟移动时间
            return True, 0.0  # 模拟成功，无误差
        
        try:
            # 获取当前位置
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                return False, float('inf')
            
            # 计算目标位置（只移动Z轴）
            target_tcp = current_tcp.copy()
            target_tcp[2] = robot_coords[2]
            
            move_distance = abs(target_tcp[2] - current_tcp[2])
            
            # 安全检查
            if move_distance < 10 or move_distance > 500:
                return False, float('inf')
            
            # 执行移动
            success = self._execute_smooth_movement(current_tcp, target_tcp, move_distance)
            
            if success:
                # 验证位置精度
                time.sleep(0.5)
                error, final_tcp = self.robot.GetActualToolFlangePose()
                if error == 0:
                    position_error = abs(final_tcp[2] - target_tcp[2])
                    return True, position_error
            
            return False, float('inf')
            
        except Exception as e:
            print(f"机械臂移动异常: {e}")
            return False, float('inf')
    
    def _execute_smooth_movement(self, start_pos, target_pos, distance_mm):
        """执行平滑运动"""
        try:
            # 使用文档推荐的参数
            steps = max(100, int(distance_mm / 2.0))
            servo_speed = 5.0
            cycle_time = 0.020
            
            ret = self.robot.ServoMoveStart()
            if ret != 0:
                return False
            
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
                
                interpolated_pos = []
                for j in range(6):
                    value = start_pos[j] + t_smooth * (target_pos[j] - start_pos[j])
                    interpolated_pos.append(value)
                
                ret = self.robot.ServoCart(mode=0, desc_pos=interpolated_pos, vel=servo_speed)
                if ret == 0:
                    success_count += 1
                
                time.sleep(cycle_time)
            
            self.robot.ServoMoveEnd()
            
            success_rate = success_count / (steps + 1) * 100
            return success_rate > 80
            
        except Exception as e:
            print(f"平滑运动异常: {e}")
            return False
    
    def return_to_initial_pose(self):
        """返回初始位姿"""
        if not ROBOT_AVAILABLE or self.robot is None or self.initial_tcp_pose is None:
            print("🔄 模拟返回初始位姿")
            time.sleep(2)
            return True
        
        try:
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                return False
            
            distance = ((current_tcp[0] - self.initial_tcp_pose[0])**2 + 
                       (current_tcp[1] - self.initial_tcp_pose[1])**2 + 
                       (current_tcp[2] - self.initial_tcp_pose[2])**2)**0.5
            
            return self._execute_smooth_movement(current_tcp, self.initial_tcp_pose, distance)
            
        except Exception as e:
            print(f"返回初始位姿异常: {e}")
            return False
    
    def test_scenario(self, scenario, test_rounds=5):
        """测试特定场景"""
        print(f"\n{'='*60}")
        print(f"🧪 测试场景: {scenario['name']}")
        print(f"📋 场景描述: {scenario['description']}")
        print(f"🎯 预期成功率: {scenario['expected_success_rate']}%")
        print(f"{'='*60}")
        
        results = {
            'scenario_name': scenario['name'],
            'description': scenario['description'],
            'expected_success_rate': scenario['expected_success_rate'],
            'test_rounds': test_rounds,
            'detection_successes': 0,
            'movement_successes': 0,
            'return_successes': 0,
            'total_successes': 0,
            'detection_times': [],
            'movement_errors': [],
            'round_results': []
        }
        
        input(f"\n请按照场景要求设置环境，然后按回车开始测试...")
        
        for round_idx in range(test_rounds):
            print(f"\n{'🔸' * 10} 第 {round_idx + 1}/{test_rounds} 轮测试 {'🔸' * 10}")
            
            round_result = {
                'round': round_idx + 1,
                'detection_success': False,
                'movement_success': False,
                'return_success': False,
                'overall_success': False
            }
            
            # 1. 检测阶段
            print("📷 开始检测水杯...")
            start_time = time.time()
            
            detection_result = self.detect_cup_multi_frame(scenario['detection_params'])
            
            detection_time = time.time() - start_time
            results['detection_times'].append(detection_time)
            
            if detection_result is None:
                print(f"❌ 第{round_idx + 1}轮：检测失败")
                results['round_results'].append(round_result)
                continue
            
            results['detection_successes'] += 1
            round_result['detection_success'] = True
            
            camera_coords = detection_result['camera_coords']
            robot_coords = detection_result['robot_coords']
            
            print(f"✅ 检测成功: 相机({camera_coords[0]:.1f}, {camera_coords[1]:.1f}, {camera_coords[2]:.1f}mm)")
            print(f"             机械臂({robot_coords[0]:.1f}, {robot_coords[1]:.1f}, {robot_coords[2]:.1f}mm)")
            print(f"             检测时间: {detection_time:.2f}秒")
            
            # 2. 移动阶段
            print("🤖 开始机械臂移动...")
            movement_success, movement_error = self.simulate_robot_movement(robot_coords)
            
            results['movement_errors'].append(movement_error)
            
            if not movement_success:
                print(f"❌ 第{round_idx + 1}轮：移动失败")
                results['round_results'].append(round_result)
                continue
            
            results['movement_successes'] += 1
            round_result['movement_success'] = True
            
            print(f"✅ 移动成功: 位置误差 {movement_error:.1f}mm")
            
            # 3. 返回阶段
            print("🔄 返回初始位姿...")
            time.sleep(2)  # 停留时间
            
            return_success = self.return_to_initial_pose()
            
            if return_success:
                results['return_successes'] += 1
                round_result['return_success'] = True
                results['total_successes'] += 1
                round_result['overall_success'] = True
                print(f"✅ 第{round_idx + 1}轮：整体成功")
            else:
                print(f"❌ 第{round_idx + 1}轮：返回失败")
            
            results['round_results'].append(round_result)
            
            # 轮次间休息
            if round_idx < test_rounds - 1:
                print("⏳ 等待5秒进行下一轮测试...")
                time.sleep(5)
        
        # 计算统计信息
        results['detection_success_rate'] = (results['detection_successes'] / test_rounds) * 100
        results['movement_success_rate'] = (results['movement_successes'] / results['detection_successes']) * 100 if results['detection_successes'] > 0 else 0
        results['return_success_rate'] = (results['return_successes'] / results['movement_successes']) * 100 if results['movement_successes'] > 0 else 0
        results['overall_success_rate'] = (results['total_successes'] / test_rounds) * 100
        results['avg_detection_time'] = np.mean(results['detection_times']) if results['detection_times'] else 0
        results['avg_movement_error'] = np.mean([e for e in results['movement_errors'] if e != float('inf')]) if results['movement_errors'] else 0
        
        print(f"\n📊 场景测试结果:")
        print(f"   检测成功率: {results['detection_success_rate']:.1f}% ({results['detection_successes']}/{test_rounds})")
        print(f"   移动成功率: {results['movement_success_rate']:.1f}%")
        print(f"   返回成功率: {results['return_success_rate']:.1f}%")
        print(f"   整体成功率: {results['overall_success_rate']:.1f}% ({results['total_successes']}/{test_rounds})")
        print(f"   平均检测时间: {results['avg_detection_time']:.2f}秒")
        print(f"   平均位置误差: {results['avg_movement_error']:.1f}mm")
        
        # 与预期对比
        success_diff = results['overall_success_rate'] - scenario['expected_success_rate']
        if success_diff >= 0:
            print(f"   ✅ 超出预期 {success_diff:.1f}%")
        else:
            print(f"   ⚠️ 低于预期 {abs(success_diff):.1f}%")
        
        return results
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 综合抓取成功率测试")
        print("🎯 目标：测试不同场景下的手眼协同系统性能")
        
        if not self.initialize_camera():
            print("❌ 相机初始化失败")
            return False
        
        robot_ready = self.initialize_robot()
        if not robot_ready:
            print("⚠️ 机械臂初始化失败，将在模拟模式下运行")
        
        print(f"\n📋 测试计划:")
        print(f"   测试场景数量: {len(self.test_scenarios)}")
        print(f"   每场景测试轮数: 5轮")
        print(f"   总测试次数: {len(self.test_scenarios) * 5}次")
        
        confirm = input("\n确认开始综合测试？(y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 测试已取消")
            return False
        
        # 执行各场景测试
        for i, scenario in enumerate(self.test_scenarios):
            print(f"\n{'🌟' * 15} 场景 {i+1}/{len(self.test_scenarios)} {'🌟' * 15}")
            
            result = self.test_scenario(scenario)
            self.test_results.append(result)
        
        # 生成综合报告
        self.generate_comprehensive_report()
        return True
    
    def generate_comprehensive_report(self):
        """生成综合测试报告"""
        print("\n" + "="*80)
        print("📊 综合抓取成功率测试报告")
        print("="*80)
        
        if not self.test_results:
            print("❌ 没有可用的测试结果")
            return
        
        # 总体统计
        total_tests = sum(result['test_rounds'] for result in self.test_results)
        total_successes = sum(result['total_successes'] for result in self.test_results)
        overall_success_rate = (total_successes / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 总体性能:")
        print(f"   总测试次数: {total_tests}")
        print(f"   总成功次数: {total_successes}")
        print(f"   整体成功率: {overall_success_rate:.1f}%")
        
        # 各场景性能排名
        sorted_results = sorted(self.test_results, key=lambda x: x['overall_success_rate'], reverse=True)
        
        print(f"\n🏆 场景性能排名:")
        print("-" * 80)
        print(f"{'排名':<4} {'场景名称':<15} {'成功率':<8} {'预期':<6} {'差值':<8} {'检测时间':<8} {'位置误差':<8}")
        print("-" * 80)
        
        for rank, result in enumerate(sorted_results, 1):
            success_rate = result['overall_success_rate']
            expected = result['expected_success_rate']
            diff = success_rate - expected
            detection_time = result['avg_detection_time']
            movement_error = result['avg_movement_error']
            
            diff_str = f"+{diff:.1f}%" if diff >= 0 else f"{diff:.1f}%"
            
            print(f"{rank:<4} {result['scenario_name']:<15} {success_rate:<7.1f}% {expected:<5}% "
                  f"{diff_str:<8} {detection_time:<7.2f}s {movement_error:<7.1f}mm")
        
        # 详细分析
        print(f"\n📈 详细分析:")
        
        # 最佳场景
        best_scenario = sorted_results[0]
        print(f"🥇 最佳场景: {best_scenario['scenario_name']}")
        print(f"   整体成功率: {best_scenario['overall_success_rate']:.1f}%")
        print(f"   检测成功率: {best_scenario['detection_success_rate']:.1f}%")
        print(f"   移动成功率: {best_scenario['movement_success_rate']:.1f}%")
        
        # 最具挑战的场景
        worst_scenario = sorted_results[-1]
        print(f"\n🚨 最具挑战场景: {worst_scenario['scenario_name']}")
        print(f"   整体成功率: {worst_scenario['overall_success_rate']:.1f}%")
        print(f"   主要问题: ", end="")
        if worst_scenario['detection_success_rate'] < 80:
            print("检测稳定性")
        elif worst_scenario['movement_success_rate'] < 80:
            print("移动控制")
        else:
            print("返回精度")
        
        # 性能指标统计
        all_detection_rates = [r['detection_success_rate'] for r in self.test_results]
        all_movement_rates = [r['movement_success_rate'] for r in self.test_results if r['detection_successes'] > 0]
        all_detection_times = []
        all_movement_errors = []
        
        for result in self.test_results:
            all_detection_times.extend(result['detection_times'])
            all_movement_errors.extend([e for e in result['movement_errors'] if e != float('inf')])
        
        print(f"\n📊 性能指标统计:")
        print(f"   检测成功率: 平均 {np.mean(all_detection_rates):.1f}%, 最高 {np.max(all_detection_rates):.1f}%, 最低 {np.min(all_detection_rates):.1f}%")
        if all_movement_rates:
            print(f"   移动成功率: 平均 {np.mean(all_movement_rates):.1f}%, 最高 {np.max(all_movement_rates):.1f}%, 最低 {np.min(all_movement_rates):.1f}%")
        if all_detection_times:
            print(f"   检测时间: 平均 {np.mean(all_detection_times):.2f}s, 最快 {np.min(all_detection_times):.2f}s, 最慢 {np.max(all_detection_times):.2f}s")
        if all_movement_errors:
            print(f"   位置误差: 平均 {np.mean(all_movement_errors):.1f}mm, 最佳 {np.min(all_movement_errors):.1f}mm, 最差 {np.max(all_movement_errors):.1f}mm")
        
        # 改进建议
        print(f"\n💡 系统改进建议:")
        
        avg_detection_rate = np.mean(all_detection_rates)
        if avg_detection_rate < 85:
            print(f"   🔍 检测算法需要优化:")
            print(f"     - 调整检测参数（容差、区域限制）")
            print(f"     - 增加多帧平均数量")
            print(f"     - 考虑使用卡尔曼滤波")
        
        if all_movement_rates and np.mean(all_movement_rates) < 85:
            print(f"   🤖 机械臂控制需要优化:")
            print(f"     - 调整伺服运动参数")
            print(f"     - 增加移动前的安全检查")
            print(f"     - 优化轨迹规划算法")
        
        if all_movement_errors and np.mean(all_movement_errors) > 10:
            print(f"   📐 手眼标定需要优化:")
            print(f"     - 收集更多标定点")
            print(f"     - 使用高级标定算法")
            print(f"     - 考虑分区域标定")
        
        # 应用建议
        print(f"\n🎮 应用部署建议:")
        if overall_success_rate >= 90:
            print(f"   ✅ 系统已达到生产就绪水平")
            print(f"   建议优先在理想条件下部署")
        elif overall_success_rate >= 75:
            print(f"   ⚠️ 系统基本可用，需要在特定场景下优化")
            print(f"   建议针对性改进最具挑战的场景")
        else:
            print(f"   🚨 系统需要进一步优化才能实际应用")
            print(f"   建议全面检查检测和控制算法")
        
        # 保存详细报告
        self.save_test_report()
    
    def save_test_report(self):
        """保存测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_grab_test_report_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.test_results,
            'summary': {
                'total_tests': sum(result['test_rounds'] for result in self.test_results),
                'total_successes': sum(result['total_successes'] for result in self.test_results),
                'overall_success_rate': (sum(result['total_successes'] for result in self.test_results) / 
                                        sum(result['test_rounds'] for result in self.test_results)) * 100
            }
        }
        
        filepath = os.path.join(current_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存: {filepath}")
    
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
    tester = ComprehensiveGrabTester()
    
    try:
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