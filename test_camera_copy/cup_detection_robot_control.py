#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水杯检测 + 机械臂控制集成脚本
功能：检测水杯距离，自动控制机械臂前伸到合适位置
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
    print("请确保fr3_control文件夹存在")

try:
    from fairino import Robot
    print("✅ fairino库导入成功")
    ROBOT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ fairino库导入失败: {e}")
    print("将在仅检测模式下运行")
    ROBOT_AVAILABLE = False

class CupDetectionController:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.robot = None
        self.hand_eye_offset = 110.0  # 手眼转换偏移 11cm = 110mm
        self.initial_tcp_pose = None  # 记录初始TCP位姿
        
        # 检测区域限制参数
        self.y_detection_ratio = 0.75    # 只检测画面上75%的区域，避免桌面
        
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
        for _ in range(5):
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
            
            time.sleep(1.0)
            
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
    
    def return_to_initial_pose(self):
        """返回到初始位姿"""
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
            
            # 启动伺服模式
            ret = self.robot.ServoMoveStart()
            if ret != 0:
                print(f"❌ 伺服运动开始失败，错误码: {ret}")
                return False
            print("✅ 伺服模式已启动（返回）")
            
            # 计算返回距离
            distance = ((current_tcp[0] - self.initial_tcp_pose[0])**2 + 
                       (current_tcp[1] - self.initial_tcp_pose[1])**2 + 
                       (current_tcp[2] - self.initial_tcp_pose[2])**2)**0.5
            
            # 生成返回轨迹
            steps = max(100, int(distance / 2.0))  # 适中的轨迹点数量
            servo_speed = 5.0  # 最低安全速度
            cycle_time = 0.020  # 增加伺服周期时间，给机械臂更多处理时间
            
            print(f"返回距离: {distance:.1f}mm，生成{steps}个轨迹点...")
            
            for i in range(steps + 1):
                t = i / steps
                
                # 使用更平滑的五次多项式曲线，确保加速度连续
                # 五次多项式: 6t^5 - 15t^4 + 10t^3
                if t <= 0.0:
                    t_smooth = 0.0
                elif t >= 1.0:
                    t_smooth = 1.0
                else:
                    t_smooth = 6 * t**5 - 15 * t**4 + 10 * t**3
                
                interpolated_pos = []
                for j in range(6):
                    interpolated_value = current_tcp[j] + t_smooth * (self.initial_tcp_pose[j] - current_tcp[j])
                    interpolated_pos.append(interpolated_value)
                
                # 发送伺服指令
                ret = self.robot.ServoCart(mode=0, desc_pos=interpolated_pos, vel=servo_speed)
                if ret != 0 and i % 20 == 0:
                    print(f"⚠️ 返回轨迹点 {i} 执行失败，错误码: {ret}")
                
                if i % (steps // 4) == 0:
                    progress = (i / steps) * 100
                    print(f"返回进度: {progress:.1f}%")
                
                time.sleep(cycle_time)
            
            print("✅ 返回轨迹跟随完成")
            
            # 结束伺服模式
            ret = self.robot.ServoMoveEnd()
            if ret != 0:
                print(f"⚠️ 返回伺服运动结束警告，错误码: {ret}")
            else:
                print("✅ 返回伺服模式已结束")
            
            # 验证返回位置
            time.sleep(0.5)
            error, final_tcp = self.robot.GetActualToolFlangePose()
            if error == 0:
                print(f"返回后TCP位置: X={final_tcp[0]:.1f}, Y={final_tcp[1]:.1f}, Z={final_tcp[2]:.1f}")
                
                pos_error = ((final_tcp[0] - self.initial_tcp_pose[0])**2 + 
                            (final_tcp[1] - self.initial_tcp_pose[1])**2 + 
                            (final_tcp[2] - self.initial_tcp_pose[2])**2)**0.5
                print(f"返回位置误差: {pos_error:.1f}mm")
                
                if pos_error < 10.0:
                    print("✅ 返回初始位姿完成，精度良好！")
                    return True
                else:
                    print("⚠️ 返回初始位姿完成，但精度有待改善")
                    return True
            
            return True
            
        except Exception as e:
            print(f"❌ 返回初始位姿异常: {e}")
            return False
    
    def detect_cup_distance(self):
        """检测水杯距离"""
        print("🔍 开始检测水杯...")
        
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
            
            # 分析深度数据找水杯
            result = self._analyze_depth_for_cup(depth_image)
            
            if result:
                pixel_x, pixel_y, depth_mm, x_3d, y_3d, z_3d = result
                
                print(f"🎯 检测到水杯!")
                print(f"   像素坐标: ({pixel_x}, {pixel_y})")
                print(f"   深度值: {depth_mm}mm")
                print(f"   3D坐标: ({x_3d:.3f}, {y_3d:.3f}, {z_3d:.3f})m")
                print(f"   距离: {z_3d:.3f}m ({z_3d*1000:.0f}mm)")
                
                return z_3d * 1000  # 返回距离(mm)
            else:
                print("❌ 未检测到水杯")
                return None
                
        except Exception as e:
            print(f"❌ 检测异常: {e}")
            return None
    
    def _analyze_depth_for_cup(self, depth_image):
        """分析深度图像找水杯，添加Y坐标限制避免检测到桌子"""
        height, width = depth_image.shape
        
        # 1. 创建Y坐标限制掩码 - 排除画面下方的区域（避免桌子）
        y_limit_pixel = int(height * self.y_detection_ratio)
        
        # 创建区域掩码
        detection_mask = np.zeros_like(depth_image, dtype=bool)
        detection_mask[:y_limit_pixel, :] = True  # 只在上75%区域检测
        
        print(f"   检测区域限制: 上方{self.y_detection_ratio*100:.0f}%区域 (像素Y < {y_limit_pixel})")
        
        # 2. 在限制区域内过滤有效深度值 (20cm - 3m)
        valid_mask = (depth_image > 200) & (depth_image < 3000) & detection_mask
        valid_depth = depth_image[valid_mask]
        
        if len(valid_depth) < 100:
            print("   限制区域内深度数据太少")
            return None
        
        # 3. 在限制区域内找最近物体
        closest_depth = np.min(valid_depth)
        
        # 4. 找该深度附近的所有像素 (±2cm容差)，但仍限制在检测区域内
        tolerance = 20
        cup_mask = (np.abs(depth_image - closest_depth) <= tolerance) & detection_mask
        cup_pixels = np.sum(cup_mask)
        
        print(f"   区域限制后 - 最近深度: {closest_depth}mm, 相关像素: {cup_pixels}个")
        
        # 5. 检查物体大小合理性
        if cup_pixels < 50 or cup_pixels > 50000:
            print("   物体大小不合理")
            return None
        
        # 6. 计算物体中心
        positions = np.where(cup_mask)
        center_y = int(np.mean(positions[0]))
        center_x = int(np.mean(positions[1]))
        
        # 7. 获取中心点深度
        center_depth = depth_image[center_y, center_x]
        if center_depth == 0:
            center_depth = closest_depth
        
        # 8. 转换3D坐标
        z = center_depth / 1000.0  # 转米
        x = (center_x - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
        y = (center_y - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
        
        print(f"   3D坐标计算: x={x:.3f}, y={y:.3f}, z={z:.3f}")
        
        # 9. 距离合理性检查
        if z < 0.1 or z > 2.0:
            print(f"   Z距离不合理: {z:.3f}m")
            return None
        
        print(f"   ✅ 检测成功")
        
        return (center_x, center_y, center_depth, x, y, z)
    
    def calculate_robot_move_distance(self, cup_distance_mm):
        """计算机械臂移动距离"""
        if cup_distance_mm is None:
            return None
        
        # 手眼转换：检测距离 - 11cm偏移
        move_distance_mm = cup_distance_mm - self.hand_eye_offset
        
        print(f"📏 距离计算:")
        print(f"   检测到的距离: {cup_distance_mm:.0f}mm")
        print(f"   手眼偏移: {self.hand_eye_offset:.0f}mm")
        print(f"   机械臂移动距离: {move_distance_mm:.0f}mm")
        
        # 安全检查
        if move_distance_mm < 50:  # 最小移动5cm
            print("⚠️ 移动距离太小，可能过于接近")
            return None
        
        if move_distance_mm > 800:  # 最大移动80cm
            print("⚠️ 移动距离太大，超出安全范围")
            return None
        
        return move_distance_mm
    
    def move_robot_forward(self, distance_mm):
        """控制机械臂前伸指定距离"""
        if not ROBOT_AVAILABLE or self.robot is None:
            print("⚠️ 机械臂不可用，仅模拟移动")
            print(f"模拟移动: Z轴负方向 {distance_mm:.0f}mm")
            return True
        
        print(f"🚀 开始控制机械臂前伸 {distance_mm:.0f}mm")
        
        try:
            # 获取当前TCP位置
            print("📍 获取当前TCP位置...")
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                print(f"❌ 获取TCP位置失败，错误码: {error}")
                return False
            
            print(f"当前TCP位置: X={current_tcp[0]:.1f}, Y={current_tcp[1]:.1f}, Z={current_tcp[2]:.1f}")
            
            # 计算目标位置（Z轴负方向移动）
            target_tcp = current_tcp.copy()
            target_tcp[2] = current_tcp[2] - distance_mm  # Z轴负方向移动
            
            print(f"目标TCP位置: X={target_tcp[0]:.1f}, Y={target_tcp[1]:.1f}, Z={target_tcp[2]:.1f}")
            print(f"Z轴移动距离: {distance_mm:.1f}mm")
            
            # 启动伺服模式
            ret = self.robot.ServoMoveStart()
            if ret != 0:
                print(f"❌ 伺服运动开始失败，错误码: {ret}")
                return False
            print("✅ 伺服模式已启动")
            
            # 生成轨迹点
            steps = max(100, int(distance_mm / 2.0))  # 适中的轨迹点数量
            servo_speed = 5.0  # 最低安全速度
            cycle_time = 0.020  # 增加伺服周期时间，给机械臂更多处理时间
            
            print(f"生成{steps}个轨迹点...")
            
            for i in range(steps + 1):
                t = i / steps
                
                # 使用更平滑的五次多项式曲线，确保加速度连续
                # 五次多项式: 6t^5 - 15t^4 + 10t^3
                if t <= 0.0:
                    t_smooth = 0.0
                elif t >= 1.0:
                    t_smooth = 1.0
                else:
                    t_smooth = 6 * t**5 - 15 * t**4 + 10 * t**3
                
                interpolated_pos = []
                for j in range(6):
                    interpolated_value = current_tcp[j] + t_smooth * (target_tcp[j] - current_tcp[j])
                    interpolated_pos.append(interpolated_value)
                
                # 发送伺服指令
                ret = self.robot.ServoCart(mode=0, desc_pos=interpolated_pos, vel=servo_speed)
                if ret != 0 and i % 20 == 0:
                    print(f"⚠️ 轨迹点 {i} 执行失败，错误码: {ret}")
                
                if i % (steps // 4) == 0:
                    progress = (i / steps) * 100
                    print(f"进度: {progress:.1f}%")
                
                time.sleep(cycle_time)
            
            print("✅ 轨迹跟随完成")
            
            # 结束伺服模式
            ret = self.robot.ServoMoveEnd()
            if ret != 0:
                print(f"⚠️ 伺服运动结束警告，错误码: {ret}")
            else:
                print("✅ 伺服模式已结束")
            
            # 验证最终位置
            time.sleep(0.5)
            error, final_tcp = self.robot.GetActualToolFlangePose()
            if error == 0:
                print(f"最终TCP位置: X={final_tcp[0]:.1f}, Y={final_tcp[1]:.1f}, Z={final_tcp[2]:.1f}")
                
                z_error = abs(final_tcp[2] - target_tcp[2])
                print(f"Z轴位置误差: {z_error:.1f}mm")
                
                if z_error < 5.0:
                    print("✅ 运动完成，精度良好！")
                    return True
                else:
                    print("⚠️ 运动完成，但精度有待改善")
                    return True
            
            return True
            
        except Exception as e:
            print(f"❌ 机械臂控制异常: {e}")
            return False
    
    def run_detection_and_control(self):
        """执行完整的检测和控制流程"""
        print("=" * 50)
        print("🎯 水杯检测 + 机械臂控制系统")
        print("=" * 50)
        
        try:
            # 1. 检测水杯距离
            cup_distance = self.detect_cup_distance()
            if cup_distance is None:
                print("❌ 水杯检测失败，无法继续")
                return False
            
            # 2. 计算机械臂移动距离
            move_distance = self.calculate_robot_move_distance(cup_distance)
            if move_distance is None:
                print("❌ 移动距离计算失败，安全考虑停止操作")
                return False
            
            # 3. 显示操作信息（自动执行）
            print(f"\n📋 执行信息:")
            print(f"   检测距离: {cup_distance:.0f}mm")
            print(f"   移动距离: {move_distance:.0f}mm")
            print(f"   移动方向: Z轴负方向（前伸）")
            print(f"\n🚀 开始自动执行...")
            
            # 4. 执行机械臂控制
            success = self.move_robot_forward(move_distance)
            
            if success:
                print("\n✅ 机械臂前伸完成！")
                
                # 5. 等待3秒
                print("\n⏳ 等待3秒...")
                time.sleep(3.0)
                print("✅ 等待完成")
                
                # 6. 返回初始位姿
                print("\n🔄 开始返回初始位姿...")
                return_success = self.return_to_initial_pose()
                
                if return_success:
                    print("\n🎉 水杯检测和机械臂控制完成！机械臂已返回初始位姿")
                    return True
                else:
                    print("\n⚠️ 机械臂前伸成功，但返回初始位姿失败")
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
    controller = CupDetectionController()
    
    try:
        print("🚀 启动水杯检测+机械臂控制系统\n")
        
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
        
        # 提示用户
        print("\n📋 使用说明:")
        print("1. 将水杯放置在相机前方")
        print("2. 确保水杯是离相机最近的物体")
        print("3. 系统将自动检测距离并控制机械臂前伸")
        print("4. 前伸距离 = 检测距离 - 11cm")
        
        print("\n🚀 立即开始检测...")
        
        # 执行检测和控制
        success = controller.run_detection_and_control()
        
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