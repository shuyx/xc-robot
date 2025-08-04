#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版手眼协同系统
改进点：
1. 使用完整手眼变换矩阵（12mm精度）
2. 多帧平均提高检测稳定性
3. 优化机械臂控制参数
4. 添加卡尔曼滤波
"""

import sys
import os
import time
import numpy as np
from pyorbbecsdk import *

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

class KalmanFilter:
    """简单的卡尔曼滤波器，用于平滑3D坐标"""
    def __init__(self):
        self.x = None  # 状态 [x, y, z]
        self.P = np.eye(3) * 1000  # 协方差矩阵
        self.Q = np.eye(3) * 0.1   # 过程噪声
        self.R = np.eye(3) * 10    # 测量噪声
    
    def update(self, measurement):
        """更新滤波器"""
        if self.x is None:
            self.x = np.array(measurement)
            return self.x
        
        # 预测步骤
        x_pred = self.x
        P_pred = self.P + self.Q
        
        # 更新步骤
        K = P_pred @ np.linalg.inv(P_pred + self.R)
        self.x = x_pred + K @ (np.array(measurement) - x_pred)
        self.P = (np.eye(3) - K) @ P_pred
        
        return self.x

class EnhancedHandEyeSystem:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.robot = None
        self.initial_tcp_pose = None
        
        # 检测参数
        self.y_detection_ratio = 0.75    # 检测区域限制
        self.detection_frames = 5        # 多帧平均
        self.kalman_filter = KalmanFilter()
        
        # 实测手眼变换矩阵 (相机mm → 机械臂mm, 精度12mm)
        self.hand_eye_transform = np.array([
            [-0.105501, -0.992918,  0.054622,    -250.6],
            [-0.979217,  0.113299,  0.168218,      40.9],
            [-0.173215, -0.035739, -0.984235,    -127.6],
            [ 0.000000,  0.000000,  0.000000,       1.0]
        ])
        
        print("✅ 使用完整手眼变换矩阵（精度12mm）")
        
    def camera_to_robot(self, camera_x, camera_y, camera_z):
        """相机坐标(mm) → 机械臂坐标(mm)"""
        camera_homo = np.array([camera_x, camera_y, camera_z, 1])
        robot_homo = self.hand_eye_transform @ camera_homo
        return robot_homo[0], robot_homo[1], robot_homo[2]
    
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
    
    def initialize_robot(self):
        """初始化机械臂"""
        if not ROBOT_AVAILABLE:
            print("⚠️ 机械臂库不可用，跳过机械臂初始化")
            return False
            
        print("🤖 初始化机械臂...")
        
        try:
            # 连接机械臂
            print("🔗 正在连接机械臂...")
            self.robot = Robot.RPC('192.168.58.2')
            
            if not hasattr(self.robot, 'is_conect') or not self.robot.is_conect:
                print("❌ 机械臂连接失败")
                return False
            print("✅ 机械臂连接成功")
            
            # 设置自动模式并使能
            print("⚡ 准备机械臂...")
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
            
            time.sleep(1.5)  # 按照文档建议等待时间
            
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
    
    def detect_cup_with_multi_frame(self):
        """多帧平均检测水杯，提高稳定性"""
        print(f"🔍 开始多帧检测水杯（{self.detection_frames}帧平均）...")
        
        valid_detections = []
        
        for frame_idx in range(self.detection_frames):
            print(f"   捕获第 {frame_idx + 1}/{self.detection_frames} 帧...")
            
            try:
                # 获取深度帧
                frames = self.camera_pipeline.wait_for_frames(1000)
                depth_frame = frames.get_depth_frame()
                
                if not depth_frame:
                    print(f"   第{frame_idx + 1}帧：未获取到深度帧")
                    continue
                
                # 转换深度数据
                depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
                height = depth_frame.get_height()
                width = depth_frame.get_width()
                depth_image = depth_data.reshape((height, width))
                
                # 分析深度数据找水杯
                result = self._analyze_depth_for_cup(depth_image)
                
                if result:
                    pixel_x, pixel_y, depth_mm, x_3d, y_3d, z_3d = result
                    valid_detections.append((x_3d, y_3d, z_3d))
                    print(f"   第{frame_idx + 1}帧：检测到水杯 - 距离 {z_3d*1000:.0f}mm")
                else:
                    print(f"   第{frame_idx + 1}帧：未检测到水杯")
                
                time.sleep(0.1)  # 帧间间隔
                
            except Exception as e:
                print(f"   第{frame_idx + 1}帧：检测异常 - {e}")
                continue
        
        if len(valid_detections) < 2:
            print("❌ 有效检测帧数不足，检测失败")
            return None
        
        # 计算平均值
        avg_coords = np.mean(valid_detections, axis=0)
        print(f"✅ 多帧平均结果：x={avg_coords[0]:.3f}, y={avg_coords[1]:.3f}, z={avg_coords[2]:.3f}")
        
        # 应用卡尔曼滤波
        filtered_coords = self.kalman_filter.update(avg_coords)
        print(f"✅ 卡尔曼滤波后：x={filtered_coords[0]:.3f}, y={filtered_coords[1]:.3f}, z={filtered_coords[2]:.3f}")
        
        # 转换到机械臂坐标系
        camera_x_mm = filtered_coords[0] * 1000
        camera_y_mm = filtered_coords[1] * 1000
        camera_z_mm = filtered_coords[2] * 1000
        
        robot_x, robot_y, robot_z = self.camera_to_robot(camera_x_mm, camera_y_mm, camera_z_mm)
        
        print(f"📍 手眼变换结果:")
        print(f"   相机坐标: ({camera_x_mm:.1f}, {camera_y_mm:.1f}, {camera_z_mm:.1f})mm")
        print(f"   机械臂坐标: ({robot_x:.1f}, {robot_y:.1f}, {robot_z:.1f})mm")
        
        return {
            'camera_coords': (camera_x_mm, camera_y_mm, camera_z_mm),
            'robot_coords': (robot_x, robot_y, robot_z),
            'detection_count': len(valid_detections)
        }
    
    def _analyze_depth_for_cup(self, depth_image):
        """分析深度图像找水杯（增强版）"""
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
        
        # 3. 找最近物体（使用更严格的筛选）
        closest_depth = np.min(valid_depth)
        
        # 4. 在最近点周围取更多样本提高精度
        tolerance = 15  # 减小容差提高精度
        cup_mask = (np.abs(depth_image - closest_depth) <= tolerance) & detection_mask
        cup_pixels = np.sum(cup_mask)
        
        # 5. 检查物体大小合理性（放宽限制）
        if cup_pixels < 30:
            return None
        
        # 6. 计算物体中心（使用加权平均）
        positions = np.where(cup_mask)
        if len(positions[0]) == 0:
            return None
        
        # 使用深度加权的中心计算
        depths = depth_image[positions]
        weights = 1.0 / (depths + 1)  # 距离越近权重越大
        
        center_y = int(np.average(positions[0], weights=weights))
        center_x = int(np.average(positions[1], weights=weights))
        
        # 7. 获取中心点深度（周围点的中位数）
        region_size = 5
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
        
        # 8. 转换3D坐标
        z = center_depth / 1000.0
        x = (center_x - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
        y = (center_y - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
        
        # 9. 距离合理性检查
        if z < 0.1 or z > 2.0:
            return None
        
        return (center_x, center_y, center_depth, x, y, z)
    
    def move_robot_to_target(self, robot_coords):
        """使用完整手眼标定结果控制机械臂"""
        if not ROBOT_AVAILABLE or self.robot is None:
            print("⚠️ 机械臂不可用，仅模拟移动")
            target_x, target_y, target_z = robot_coords
            print(f"模拟移动到目标位置: X={target_x:.1f}, Y={target_y:.1f}, Z={target_z:.1f}")
            return True
        
        target_x, target_y, target_z = robot_coords
        print(f"🚀 使用手眼标定控制机械臂移动到目标位置")
        print(f"   目标坐标: X={target_x:.1f}, Y={target_y:.1f}, Z={target_z:.1f}")
        
        try:
            # 获取当前TCP位置
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                print(f"❌ 获取TCP位置失败，错误码: {error}")
                return False
            
            print(f"当前TCP位置: X={current_tcp[0]:.1f}, Y={current_tcp[1]:.1f}, Z={current_tcp[2]:.1f}")
            
            # 计算目标位置（只移动Z轴，保持X、Y不变）
            target_tcp = current_tcp.copy()
            target_tcp[2] = target_z  # 直接使用手眼标定的Z坐标
            
            # 计算移动距离
            move_distance = abs(target_tcp[2] - current_tcp[2])
            
            print(f"计算的目标TCP位置: X={target_tcp[0]:.1f}, Y={target_tcp[1]:.1f}, Z={target_tcp[2]:.1f}")
            print(f"Z轴移动距离: {move_distance:.1f}mm")
            
            # 安全检查
            if move_distance < 10:
                print("⚠️ 移动距离太小，跳过移动")
                return True
            
            if move_distance > 500:
                print("⚠️ 移动距离太大，限制为500mm")
                if target_tcp[2] < current_tcp[2]:
                    target_tcp[2] = current_tcp[2] - 500
                else:
                    target_tcp[2] = current_tcp[2] + 500
                move_distance = 500
            
            # 使用文档推荐的最佳参数
            return self._smooth_servo_motion(current_tcp, target_tcp, move_distance)
            
        except Exception as e:
            print(f"❌ 机械臂控制异常: {e}")
            return False
    
    def _smooth_servo_motion(self, start_pos, target_pos, distance_mm):
        """平滑ServoCart运动的最佳实践（基于文档调参）"""
        
        # 1. 合理的轨迹参数（文档推荐）
        steps = max(100, int(distance_mm / 2.0))  # 每2mm一个点
        servo_speed = 5.0                         # 最低安全速度
        cycle_time = 0.020                        # 20ms周期给足处理时间
        
        print(f"使用文档推荐参数：steps={steps}, speed={servo_speed}, cycle={cycle_time*1000:.0f}ms")
        
        # 2. 启动伺服模式
        ret = self.robot.ServoMoveStart()
        if ret != 0:
            print(f"❌ 伺服运动开始失败，错误码: {ret}")
            return False
        print("✅ 伺服模式已启动")
        
        # 3. 执行平滑轨迹
        success_count = 0
        for i in range(steps + 1):
            t = i / steps
            
            # 五次多项式插值（文档推荐）
            if t <= 0.0:
                t_smooth = 0.0
            elif t >= 1.0:
                t_smooth = 1.0
            else:
                t_smooth = 6 * t**5 - 15 * t**4 + 10 * t**3
            
            # 计算插值位置
            interpolated_pos = []
            for j in range(6):
                value = start_pos[j] + t_smooth * (target_pos[j] - start_pos[j])
                interpolated_pos.append(value)
            
            # 发送伺服指令
            ret = self.robot.ServoCart(mode=0, desc_pos=interpolated_pos, vel=servo_speed)
            if ret == 0:
                success_count += 1
            elif i % 20 == 0:
                print(f"⚠️ 轨迹点 {i} 执行失败，错误码: {ret}")
            
            if i % (steps // 4) == 0:
                progress = (i / steps) * 100
                print(f"进度: {progress:.1f}% (成功率: {success_count/(i+1)*100:.1f}%)")
            
            # 关键：等待足够的处理时间
            time.sleep(cycle_time)
        
        # 4. 结束伺服模式
        ret = self.robot.ServoMoveEnd()
        if ret != 0:
            print(f"⚠️ 伺服运动结束警告，错误码: {ret}")
        else:
            print("✅ 伺服模式已结束")
        
        # 统计结果
        success_rate = success_count / (steps + 1) * 100
        print(f"✅ 轨迹执行完成，成功率: {success_rate:.1f}%")
        
        # 验证最终位置
        time.sleep(0.5)
        error, final_tcp = self.robot.GetActualToolFlangePose()
        if error == 0:
            print(f"最终TCP位置: X={final_tcp[0]:.1f}, Y={final_tcp[1]:.1f}, Z={final_tcp[2]:.1f}")
            
            z_error = abs(final_tcp[2] - target_pos[2])
            print(f"Z轴位置误差: {z_error:.1f}mm")
            
            if z_error < 5.0:
                print("✅ 运动完成，精度良好！")
                return True
            else:
                print("⚠️ 运动完成，但精度有待改善")
                return True
        
        return success_rate > 80  # 成功率阈值
    
    def return_to_initial_pose(self):
        """返回到初始位姿（使用相同的优化参数）"""
        if not ROBOT_AVAILABLE or self.robot is None or self.initial_tcp_pose is None:
            print("⚠️ 机械臂不可用或未记录初始位姿，仅模拟返回")
            return True
            
        print("🔄 返回初始位姿...")
        
        try:
            # 获取当前位置
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                print(f"❌ 获取当前TCP位置失败，错误码: {error}")
                return False
            
            print(f"当前位置: X={current_tcp[0]:.1f}, Y={current_tcp[1]:.1f}, Z={current_tcp[2]:.1f}")
            print(f"目标位置: X={self.initial_tcp_pose[0]:.1f}, Y={self.initial_tcp_pose[1]:.1f}, Z={self.initial_tcp_pose[2]:.1f}")
            
            # 计算返回距离
            distance = ((current_tcp[0] - self.initial_tcp_pose[0])**2 + 
                       (current_tcp[1] - self.initial_tcp_pose[1])**2 + 
                       (current_tcp[2] - self.initial_tcp_pose[2])**2)**0.5
            
            print(f"返回距离: {distance:.1f}mm")
            
            # 使用相同的平滑运动函数
            return self._smooth_servo_motion(current_tcp, self.initial_tcp_pose, distance)
            
        except Exception as e:
            print(f"❌ 返回初始位姿异常: {e}")
            return False
    
    def run_enhanced_detection_and_control(self):
        """执行增强版检测和控制流程"""
        print("=" * 60)
        print("🎯 增强版手眼协同系统")
        print("🔧 特性：完整手眼标定 + 多帧平均 + 卡尔曼滤波 + 优化控制")
        print("=" * 60)
        
        try:
            # 1. 多帧检测水杯
            detection_result = self.detect_cup_with_multi_frame()
            if detection_result is None:
                print("❌ 水杯检测失败，无法继续")
                return False
            
            camera_coords = detection_result['camera_coords']
            robot_coords = detection_result['robot_coords']
            detection_count = detection_result['detection_count']
            
            print(f"\n📋 检测结果:")
            print(f"   有效检测帧数: {detection_count}/{self.detection_frames}")
            print(f"   相机坐标: X={camera_coords[0]:.1f}, Y={camera_coords[1]:.1f}, Z={camera_coords[2]:.1f}mm")
            print(f"   机械臂坐标: X={robot_coords[0]:.1f}, Y={robot_coords[1]:.1f}, Z={robot_coords[2]:.1f}mm")
            
            # 2. 显示操作信息
            print(f"\n🚀 开始自动执行手眼协同控制...")
            
            # 3. 执行机械臂控制
            success = self.move_robot_to_target(robot_coords)
            
            if success:
                print("\n✅ 机械臂移动完成！")
                
                # 4. 等待3秒
                print("\n⏳ 等待3秒...")
                time.sleep(3.0)
                print("✅ 等待完成")
                
                # 5. 返回初始位姿
                print("\n🔄 开始返回初始位姿...")
                return_success = self.return_to_initial_pose()
                
                if return_success:
                    print("\n🎉 增强版手眼协同系统执行完成！")
                    return True
                else:
                    print("\n⚠️ 机械臂移动成功，但返回初始位姿失败")
                    return False
            else:
                print("\n❌ 机械臂控制失败")
                return False
                
        except Exception as e:
            print(f"❌ 系统异常: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理系统资源...")
        
        # 清理相机
        if self.camera_pipeline:
            try:
                self.camera_pipeline.stop()
                print("✅ 相机已关闭")
            except:
                pass
        
        # 清理机械臂
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
    system = EnhancedHandEyeSystem()
    
    try:
        print("🚀 启动增强版手眼协同系统\n")
        
        # 初始化相机
        if not system.initialize_camera():
            print("❌ 相机初始化失败")
            return 1
        
        # 初始化机械臂
        robot_ready = system.initialize_robot()
        if not robot_ready:
            print("⚠️ 机械臂初始化失败，将在仅检测模式下运行")
        
        print("\n" + "="*60)
        print("系统就绪！")
        if ROBOT_AVAILABLE and robot_ready:
            print("✅ 相机 + 机械臂模式（增强版）")
        else:
            print("⚠️ 仅相机检测模式")
        print("="*60)
        
        # 提示用户
        print("\n📋 增强功能说明:")
        print("1. 多帧平均检测（5帧）提高稳定性")
        print("2. 卡尔曼滤波平滑坐标跳跃")
        print("3. 完整手眼变换矩阵（12mm精度）")
        print("4. 优化机械臂控制参数（文档最佳实践）")
        print("5. 自动返回初始位姿")
        
        print("\n🚀 立即开始增强检测...")
        
        # 执行检测和控制
        success = system.run_enhanced_detection_and_control()
        
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
        system.cleanup()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 程序终止")
        sys.exit(1)