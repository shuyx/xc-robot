#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版手眼协同控制系统
功能：检测深度图像最近点 → 3D坐标 → 手眼变换 → 机械臂移动
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
    ROBOT_AVAILABLE = False

class SimpleHandEyeController:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.robot = None
        self.initial_tcp_pose = None
        
        # 检测区域限制参数（只检测上75%区域）
        self.y_detection_ratio = 0.75
        
        # 手眼变换矩阵 (相机mm → 机械臂mm, 精度12mm)
        self.hand_eye_transform = np.array([
            [-0.105501, -0.992918,  0.054622,    -250.6],
            [-0.979217,  0.113299,  0.168218,      40.9],
            [-0.173215, -0.035739, -0.984235,    -127.6],
            [ 0.000000,  0.000000,  0.000000,       1.0]
        ])
        
        print("✅ 简化版手眼协同控制器初始化完成")
    
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
    
    def detect_nearest_point(self):
        """检测深度图像中的最近点"""
        print("🔍 检测最近点...")
        
        try:
            # 获取深度帧
            frames = self.camera_pipeline.wait_for_frames(1000)
            depth_frame = frames.get_depth_frame()
            
            if not depth_frame:
                print("❌ 未获取到深度帧")
                return None
            
            # 转换深度数据
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            height = depth_frame.get_height()
            width = depth_frame.get_width()
            depth_image = depth_data.reshape((height, width))
            
            print(f"深度图像尺寸: {width}x{height}")
            
            # 1. 创建Y坐标限制掩码 - 只检测上75%区域
            y_limit_pixel = int(height * self.y_detection_ratio)
            detection_mask = np.zeros_like(depth_image, dtype=bool)
            detection_mask[:y_limit_pixel, :] = True
            
            print(f"检测区域限制: 上{self.y_detection_ratio*100:.0f}%区域 (像素Y < {y_limit_pixel})")
            
            # 2. 在限制区域内过滤有效深度值 (20cm - 3m)
            valid_mask = (depth_image > 200) & (depth_image < 3000) & detection_mask
            valid_depth = depth_image[valid_mask]
            
            if len(valid_depth) < 100:
                print("❌ 限制区域内深度数据太少")
                return None
            
            print(f"有效深度点数: {len(valid_depth)}")
            
            # 3. 在限制区域内找最近物体
            closest_depth = np.min(valid_depth)
            print(f"最近深度值: {closest_depth}mm")
            
            # 4. 找最近点的位置
            closest_positions = np.where((depth_image == closest_depth) & detection_mask)
            
            if len(closest_positions[0]) == 0:
                print("❌ 未找到最近点位置")
                return None
            
            # 取第一个最近点
            center_y = closest_positions[0][0]
            center_x = closest_positions[1][0]
            
            print(f"最近点像素坐标: ({center_x}, {center_y})")
            
            # 5. 转换为3D坐标
            z = closest_depth / 1000.0  # 转换为米
            x = (center_x - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
            y = (center_y - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
            
            # 转换为毫米
            camera_coords_mm = np.array([x * 1000, y * 1000, z * 1000])
            
            print(f"相机3D坐标: X={camera_coords_mm[0]:.1f}, Y={camera_coords_mm[1]:.1f}, Z={camera_coords_mm[2]:.1f}mm")
            
            # 6. 距离合理性检查
            if z < 0.1 or z > 2.0:
                print(f"❌ Z距离不合理: {z:.3f}m")
                return None
            
            print("✅ 最近点检测成功")
            
            return {
                'pixel_coords': (center_x, center_y),
                'camera_coords_mm': camera_coords_mm,
                'depth_mm': closest_depth
            }
            
        except Exception as e:
            print(f"❌ 检测异常: {e}")
            return None
    
    def move_robot_to_target(self, target_coords):
        """控制机械臂移动到目标坐标"""
        if not ROBOT_AVAILABLE or self.robot is None:
            print("⚠️ 机械臂不可用，仅模拟移动")
            print(f"模拟移动到: X={target_coords[0]:.1f}, Y={target_coords[1]:.1f}, Z={target_coords[2]:.1f}")
            return True
        
        print(f"🤖 控制机械臂移动到目标位置")
        print(f"目标坐标: X={target_coords[0]:.1f}, Y={target_coords[1]:.1f}, Z={target_coords[2]:.1f}")
        
        try:
            # 获取当前TCP位置
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                print(f"❌ 获取TCP位置失败，错误码: {error}")
                return False
            
            print(f"当前TCP位置: X={current_tcp[0]:.1f}, Y={current_tcp[1]:.1f}, Z={current_tcp[2]:.1f}")
            
            # 直接使用手眼变换得到的目标坐标，保持姿态不变
            target_tcp = current_tcp.copy()
            target_tcp[0] = target_coords[0]  # X坐标
            target_tcp[1] = target_coords[1]  # Y坐标
            target_tcp[2] = target_coords[2]  # Z坐标
            
            # 计算移动距离
            move_distance = ((target_tcp[0] - current_tcp[0])**2 + 
                           (target_tcp[1] - current_tcp[1])**2 + 
                           (target_tcp[2] - current_tcp[2])**2)**0.5
            
            print(f"移动距离: {move_distance:.1f}mm")
            
            # 安全检查
            if move_distance < 10:
                print("⚠️ 移动距离太小，跳过移动")
                return True
            
            if move_distance > 500:
                print("⚠️ 移动距离太大，限制为500mm")
                # 按比例缩放到安全距离
                scale = 500 / move_distance
                target_tcp[0] = current_tcp[0] + scale * (target_coords[0] - current_tcp[0])
                target_tcp[1] = current_tcp[1] + scale * (target_coords[1] - current_tcp[1])
                target_tcp[2] = current_tcp[2] + scale * (target_coords[2] - current_tcp[2])
                move_distance = 500
                print(f"缩放后目标: X={target_tcp[0]:.1f}, Y={target_tcp[1]:.1f}, Z={target_tcp[2]:.1f}")
            
            # 使用优化的ServoCart参数
            return self._smooth_servo_motion(current_tcp, target_tcp, move_distance)
            
        except Exception as e:
            print(f"❌ 机械臂控制异常: {e}")
            return False
    
    def _smooth_servo_motion(self, start_pos, target_pos, distance_mm):
        """平滑ServoCart运动（基于文档最佳实践）"""
        
        # 文档推荐的最佳参数
        steps = max(100, int(distance_mm / 2.0))  # 每2mm一个点
        servo_speed = 5.0                         # 最低安全速度
        cycle_time = 0.020                        # 20ms周期给足处理时间
        
        print(f"使用参数：steps={steps}, speed={servo_speed}, cycle={cycle_time*1000:.0f}ms")
        
        # 启动伺服模式
        ret = self.robot.ServoMoveStart()
        if ret != 0:
            print(f"❌ 伺服运动开始失败，错误码: {ret}")
            return False
        print("✅ 伺服模式已启动")
        
        # 执行平滑轨迹
        success_count = 0
        for i in range(steps + 1):
            t = i / steps
            
            # 五次多项式插值确保运动平滑
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
                print(f"进度: {progress:.1f}%")
            
            # 关键：等待足够的处理时间
            time.sleep(cycle_time)
        
        # 结束伺服模式
        ret = self.robot.ServoMoveEnd()
        if ret != 0:
            print(f"⚠️ 伺服运动结束警告，错误码: {ret}")
        else:
            print("✅ 伺服模式已结束")
        
        # 统计结果
        success_rate = success_count / (steps + 1) * 100
        print(f"轨迹执行成功率: {success_rate:.1f}%")
        
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
            
            return self._smooth_servo_motion(current_tcp, self.initial_tcp_pose, distance)
            
        except Exception as e:
            print(f"❌ 返回初始位姿异常: {e}")
            return False
    
    def run_hand_eye_control(self):
        """运行完整的手眼协同控制流程"""
        print("=" * 60)
        print("🎯 简化版手眼协同控制系统")
        print("📋 流程：检测最近点 → 坐标转换 → 机械臂移动")
        print("=" * 60)
        
        try:
            # 1. 检测最近点
            detection_result = self.detect_nearest_point()
            if detection_result is None:
                print("❌ 最近点检测失败")
                return False
            
            pixel_coords = detection_result['pixel_coords']
            camera_coords_mm = detection_result['camera_coords_mm']
            depth_mm = detection_result['depth_mm']
            
            print(f"\n📍 检测结果:")
            print(f"   像素坐标: ({pixel_coords[0]}, {pixel_coords[1]})")
            print(f"   深度值: {depth_mm}mm")
            print(f"   相机坐标: ({camera_coords_mm[0]:.1f}, {camera_coords_mm[1]:.1f}, {camera_coords_mm[2]:.1f})mm")
            
            # 2. 手眼坐标转换
            robot_x, robot_y, robot_z = self.camera_to_robot(
                camera_coords_mm[0], camera_coords_mm[1], camera_coords_mm[2]
            )
            robot_coords = np.array([robot_x, robot_y, robot_z])
            
            print(f"\n🔄 手眼变换结果:")
            print(f"   机械臂坐标: ({robot_coords[0]:.1f}, {robot_coords[1]:.1f}, {robot_coords[2]:.1f})mm")
            
            # 3. 执行机械臂控制
            print(f"\n🚀 开始执行机械臂控制...")
            success = self.move_robot_to_target(robot_coords)
            
            if success:
                print("\n✅ 机械臂移动完成！")
                
                # 4. 等待3秒
                print("\n⏳ 等待3秒...")
                time.sleep(3.0)
                
                # 5. 返回初始位姿
                print("\n🔄 返回初始位姿...")
                return_success = self.return_to_initial_pose()
                
                if return_success:
                    print("\n🎉 手眼协同控制完成！")
                    return True
                else:
                    print("\n⚠️ 机械臂移动成功，但返回失败")
                    return False
            else:
                print("\n❌ 机械臂控制失败")
                return False
                
        except Exception as e:
            print(f"❌ 系统异常: {e}")
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
    controller = SimpleHandEyeController()
    
    try:
        print("🚀 启动简化版手眼协同控制系统\n")
        
        # 初始化相机
        if not controller.initialize_camera():
            print("❌ 相机初始化失败")
            return 1
        
        # 初始化机械臂
        robot_ready = controller.initialize_robot()
        if not robot_ready:
            print("⚠️ 机械臂初始化失败，将在仅检测模式下运行")
        
        print("\n" + "="*50)
        print("系统就绪！")
        if ROBOT_AVAILABLE and robot_ready:
            print("✅ 相机 + 机械臂模式")
        else:
            print("⚠️ 仅相机检测模式")
        print("="*50)
        
        print("\n📋 使用说明:")
        print("1. 将目标物体放置在相机前方")
        print("2. 确保物体是离相机最近的")
        print("3. 系统将检测最近点并控制机械臂移动")
        
        input("\n准备好后按回车开始...")
        
        # 执行手眼协同控制
        success = controller.run_hand_eye_control()
        
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
        controller.cleanup()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 程序终止")
        sys.exit(1)