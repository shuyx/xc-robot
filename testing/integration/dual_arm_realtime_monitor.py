#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双臂实时监控和坐标关系建立工具
用于连接FR3机械臂，读取实时位置，建立坐标关系
"""

import sys
import time
import json
import threading
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 尝试导入FR3库
try:
    from fairino import Robot
    FR3_AVAILABLE = True
    print("✅ FR3库导入成功")
except ImportError as e:
    FR3_AVAILABLE = False
    print(f"⚠️  FR3库导入失败: {e}")

@dataclass
class ArmPoseData:
    """机械臂位姿数据"""
    timestamp: float
    joint_pos: List[float]        # 关节位置 [J1-J6] 度
    tcp_pose: List[float]         # TCP位姿 [X,Y,Z,RX,RY,RZ] mm/度
    flange_pose: List[float]      # 法兰位姿 [X,Y,Z,RX,RY,RZ] mm/度
    joint_speeds: List[float]     # 关节速度 deg/s
    is_moving: bool               # 是否在运动
    error_code: int               # 错误码

@dataclass 
class DualArmRelation:
    """双臂坐标关系"""
    baseline_distance: float      # 基座间距离 mm
    relative_position: List[float] # 相对位置 [X,Y,Z] mm
    relative_orientation: List[float] # 相对姿态 [RX,RY,RZ] 度
    workspace_overlap: Dict       # 工作空间重叠信息
    safe_zones: Dict              # 安全区域定义

class DualArmRealTimeMonitor:
    """双臂实时监控器"""
    
    def __init__(self, right_ip: str = "192.168.58.2", left_ip: str = "192.168.58.3"):
        self.right_ip = right_ip
        self.left_ip = left_ip
        
        # 机械臂连接
        self.right_arm = None
        self.left_arm = None
        self.right_connected = False
        self.left_connected = False
        
        # 数据存储
        self.right_pose_history = []
        self.left_pose_history = []
        self.max_history_length = 1000
        
        # 监控控制
        self.monitoring_active = False
        self.monitor_thread = None
        self.update_interval = 0.1  # 100ms更新间隔
        
        # 坐标关系
        self.coordinate_relation = None
        self.calibration_points = {"right": [], "left": []}
        
        print("双臂实时监控器初始化完成")
    
    def connect_arms(self) -> Tuple[bool, bool]:
        """连接双臂机械臂"""
        if not FR3_AVAILABLE:
            print("❌ FR3库不可用，无法连接机械臂")
            return False, False
        
        print("🔗 开始连接机械臂...")
        
        # 连接右臂
        try:
            print(f"连接右臂 ({self.right_ip})...")
            self.right_arm = Robot.RPC(self.right_ip)
            
            # 测试连接
            try:
                error, _ = self.right_arm.GetActualJointPosDegree()
                if error == 0:
                    self.right_connected = True
                    print("✅ 右臂连接成功")
                else:
                    print(f"❌ 右臂连接测试失败，错误码: {error}")
            except Exception as test_e:
                print(f"❌ 右臂连接测试异常: {test_e}")
                
        except Exception as e:
            print(f"❌ 右臂连接失败: {e}")
            self.right_connected = False
        
        # 连接左臂
        try:
            print(f"连接左臂 ({self.left_ip})...")
            self.left_arm = Robot.RPC(self.left_ip)
            
            # 测试连接
            try:
                error, _ = self.left_arm.GetActualJointPosDegree()
                if error == 0:
                    self.left_connected = True
                    print("✅ 左臂连接成功")
                else:
                    print(f"❌ 左臂连接测试失败，错误码: {error}")
            except Exception as test_e:
                print(f"❌ 左臂连接测试异常: {test_e}")
                
        except Exception as e:
            print(f"❌ 左臂连接失败: {e}")
            self.left_connected = False
        
        # 连接总结
        connected_count = sum([self.right_connected, self.left_connected])
        print(f"\n📊 连接结果: {connected_count}/2 机械臂连接成功")
        
        if self.right_connected:
            print(f"   ✅ 右臂: {self.right_ip}")
        if self.left_connected:
            print(f"   ✅ 左臂: {self.left_ip}")
        
        return self.right_connected, self.left_connected
    
    def get_arm_pose_data(self, robot, arm_name: str) -> Optional[ArmPoseData]:
        """获取单个机械臂的完整位姿数据"""
        if not robot:
            return None
        
        try:
            timestamp = time.time()
            error_code = 0
            
            # 获取关节位置
            error, joint_pos = robot.GetActualJointPosDegree()
            if error != 0:
                error_code = error
                joint_pos = [0.0] * 6
            
            # 获取TCP位姿
            error, tcp_pose = robot.GetActualTCPPose()
            if error != 0:
                error_code = error
                tcp_pose = [0.0] * 6
            
            # 获取法兰位姿
            try:
                error, flange_pose = robot.GetActualToolFlangePose()
                if error != 0:
                    flange_pose = tcp_pose.copy()  # 备选方案
            except:
                flange_pose = tcp_pose.copy()
            
            # 获取关节速度
            try:
                error, joint_speeds = robot.GetActualJointSpeedsDegree()
                if error != 0:
                    joint_speeds = [0.0] * 6
            except:
                joint_speeds = [0.0] * 6
            
            # 判断是否在运动
            is_moving = any(abs(speed) > 0.1 for speed in joint_speeds)
            
            return ArmPoseData(
                timestamp=timestamp,
                joint_pos=joint_pos,
                tcp_pose=tcp_pose,
                flange_pose=flange_pose,
                joint_speeds=joint_speeds,
                is_moving=is_moving,
                error_code=error_code
            )
            
        except Exception as e:
            print(f"❌ 获取{arm_name}臂位姿数据异常: {e}")
            return None
    
    def get_current_positions(self) -> Tuple[Optional[ArmPoseData], Optional[ArmPoseData]]:
        """获取当前双臂位置"""
        right_data = None
        left_data = None
        
        if self.right_connected:
            right_data = self.get_arm_pose_data(self.right_arm, "右")
        
        if self.left_connected:
            left_data = self.get_arm_pose_data(self.left_arm, "左")
        
        return right_data, left_data
    
    def print_current_status(self):
        """打印当前状态"""
        print("\n" + "="*80)
        print(f"📍 双臂实时状态 - {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)
        
        right_data, left_data = self.get_current_positions()
        
        # 右臂状态
        if right_data:
            print(f"🤖 右臂 ({self.right_ip}):")
            print(f"   关节位置: {[f'{j:.2f}°' for j in right_data.joint_pos]}")
            print(f"   TCP位置:  X={right_data.tcp_pose[0]:.1f}, Y={right_data.tcp_pose[1]:.1f}, Z={right_data.tcp_pose[2]:.1f} mm")
            print(f"   TCP姿态:  RX={right_data.tcp_pose[3]:.1f}, RY={right_data.tcp_pose[4]:.1f}, RZ={right_data.tcp_pose[5]:.1f}°")
            print(f"   运动状态: {'🟢 运动中' if right_data.is_moving else '⚪ 静止'}")
            if right_data.error_code != 0:
                print(f"   ⚠️  错误码: {right_data.error_code}")
        else:
            print(f"❌ 右臂 ({self.right_ip}): 无法获取数据")
        
        print()
        
        # 左臂状态
        if left_data:
            print(f"🤖 左臂 ({self.left_ip}):")
            print(f"   关节位置: {[f'{j:.2f}°' for j in left_data.joint_pos]}")
            print(f"   TCP位置:  X={left_data.tcp_pose[0]:.1f}, Y={left_data.tcp_pose[1]:.1f}, Z={left_data.tcp_pose[2]:.1f} mm")
            print(f"   TCP姿态:  RX={left_data.tcp_pose[3]:.1f}, RY={left_data.tcp_pose[4]:.1f}, RZ={left_data.tcp_pose[5]:.1f}°")
            print(f"   运动状态: {'🟢 运动中' if left_data.is_moving else '⚪ 静止'}")
            if left_data.error_code != 0:
                print(f"   ⚠️  错误码: {left_data.error_code}")
        else:
            print(f"❌ 左臂 ({self.left_ip}): 无法获取数据")
        
        # 双臂关系
        if right_data and left_data:
            distance = self.calculate_tcp_distance(right_data.tcp_pose, left_data.tcp_pose)
            print(f"\n🔗 双臂关系:")
            print(f"   TCP间距离: {distance:.1f} mm")
            
            # 安全评估
            if distance < 200:
                print(f"   ⚠️  安全警告: 距离过近!")
            elif distance < 300:
                print(f"   ⚡ 安全注意: 距离较近")
            else:
                print(f"   ✅ 安全距离")
    
    def calculate_tcp_distance(self, pose1: List[float], pose2: List[float]) -> float:
        """计算两个TCP位置间的距离"""
        if not pose1 or not pose2 or len(pose1) < 3 or len(pose2) < 3:
            return float('inf')
        
        dx = pose1[0] - pose2[0]
        dy = pose1[1] - pose2[1] 
        dz = pose1[2] - pose2[2]
        
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def start_continuous_monitoring(self):
        """开始连续监控"""
        if self.monitoring_active:
            print("⚠️  监控已在运行中")
            return
        
        if not (self.right_connected or self.left_connected):
            print("❌ 没有可用的机械臂连接")
            return
        
        print("🚀 开始连续监控...")
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_continuous_monitoring(self):
        """停止连续监控"""
        if not self.monitoring_active:
            return
        
        print("⏹️  停止连续监控...")
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitoring_loop(self):
        """监控循环"""
        print("📡 监控循环启动")
        
        try:
            while self.monitoring_active:
                # 获取数据
                right_data, left_data = self.get_current_positions()
                
                # 存储历史数据
                if right_data:
                    self.right_pose_history.append(right_data)
                    if len(self.right_pose_history) > self.max_history_length:
                        self.right_pose_history.pop(0)
                
                if left_data:
                    self.left_pose_history.append(left_data)
                    if len(self.left_pose_history) > self.max_history_length:
                        self.left_pose_history.pop(0)
                
                # 打印状态（每秒一次）
                if int(time.time() * 10) % 10 == 0:  # 每秒的第一个100ms周期
                    self.print_current_status()
                
                time.sleep(self.update_interval)
                
        except Exception as e:
            print(f"❌ 监控循环异常: {e}")
        finally:
            print("📡 监控循环结束")
    
    def calibrate_coordinate_relation(self, method: str = "manual"):
        """标定坐标关系"""
        print("\n🎯 开始双臂坐标关系标定...")
        
        if not (self.right_connected and self.left_connected):
            print("❌ 需要双臂都连接才能进行标定")
            return False
        
        if method == "manual":
            return self._manual_calibration()
        elif method == "auto":
            return self._auto_calibration()
        else:
            print("❌ 未知标定方法")
            return False
    
    def _manual_calibration(self) -> bool:
        """手动标定"""
        print("\n📋 手动标定流程:")
        print("1. 将双臂移动到已知参考位置")
        print("2. 记录多个标定点")
        print("3. 计算坐标关系")
        
        calibration_points = {"right": [], "left": []}
        
        while True:
            print(f"\n当前已记录 {len(calibration_points['right'])} 个标定点")
            print("请选择操作:")
            print("1. 记录当前位置为标定点")
            print("2. 完成标定")
            print("3. 取消标定")
            
            choice = input("请选择 (1-3): ").strip()
            
            if choice == "1":
                right_data, left_data = self.get_current_positions()
                if right_data and left_data:
                    calibration_points["right"].append(right_data.tcp_pose[:3])
                    calibration_points["left"].append(left_data.tcp_pose[:3])
                    print(f"✅ 标定点 {len(calibration_points['right'])} 已记录")
                    print(f"   右臂: {right_data.tcp_pose[:3]}")
                    print(f"   左臂: {left_data.tcp_pose[:3]}")
                else:
                    print("❌ 无法获取当前位置数据")
            
            elif choice == "2":
                if len(calibration_points["right"]) >= 3:
                    return self._calculate_coordinate_relation(calibration_points)
                else:
                    print("❌ 至少需要3个标定点")
            
            elif choice == "3":
                print("🚫 标定已取消")
                return False
            
            else:
                print("❌ 无效选择")
    
    def _auto_calibration(self) -> bool:
        """自动标定（移动到预设位置）"""
        print("🤖 自动标定功能开发中...")
        # 这里可以实现自动移动到预设位置进行标定
        return False
    
    def _calculate_coordinate_relation(self, calibration_points: Dict) -> bool:
        """计算坐标关系"""
        print("\n🧮 计算坐标关系...")
        
        try:
            right_points = np.array(calibration_points["right"])
            left_points = np.array(calibration_points["left"])
            
            # 计算平均位置（基座位置估计）
            right_center = np.mean(right_points, axis=0)
            left_center = np.mean(left_points, axis=0)
            
            # 计算基座间相对位置
            relative_position = (left_center - right_center).tolist()
            baseline_distance = np.linalg.norm(relative_position)
            
            # 估算工作空间重叠
            right_workspace_radius = np.max(np.linalg.norm(right_points - right_center, axis=1))
            left_workspace_radius = np.max(np.linalg.norm(left_points - left_center, axis=1))
            
            workspace_overlap = {
                "right_radius": float(right_workspace_radius),
                "left_radius": float(left_workspace_radius),
                "overlap_distance": float(right_workspace_radius + left_workspace_radius - baseline_distance)
            }
            
            # 定义安全区域
            safe_zones = {
                "right_exclusive": {
                    "center": right_center.tolist(),
                    "radius": float(right_workspace_radius * 0.6)
                },
                "left_exclusive": {
                    "center": left_center.tolist(), 
                    "radius": float(left_workspace_radius * 0.6)
                },
                "collaboration": {
                    "center": ((right_center + left_center) / 2).tolist(),
                    "radius": float(min(right_workspace_radius, left_workspace_radius) * 0.4)
                }
            }
            
            # 创建坐标关系对象
            self.coordinate_relation = DualArmRelation(
                baseline_distance=baseline_distance,
                relative_position=relative_position,
                relative_orientation=[0.0, 0.0, 0.0],  # 简化为0，实际需要更复杂计算
                workspace_overlap=workspace_overlap,
                safe_zones=safe_zones
            )
            
            # 输出结果
            print("✅ 坐标关系计算完成!")
            print(f"   基座间距离: {baseline_distance:.1f} mm")
            print(f"   相对位置: X={relative_position[0]:.1f}, Y={relative_position[1]:.1f}, Z={relative_position[2]:.1f} mm")
            print(f"   右臂工作半径: {right_workspace_radius:.1f} mm")
            print(f"   左臂工作半径: {left_workspace_radius:.1f} mm")
            print(f"   工作空间重叠: {workspace_overlap['overlap_distance']:.1f} mm")
            
            return True
            
        except Exception as e:
            print(f"❌ 坐标关系计算失败: {e}")
            return False
    
    def save_calibration_data(self, filename: str = "dual_arm_calibration.json"):
        """保存标定数据"""
        if not self.coordinate_relation:
            print("❌ 没有标定数据可保存")
            return False
        
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "right_ip": self.right_ip,
                "left_ip": self.left_ip,
                "coordinate_relation": asdict(self.coordinate_relation),
                "calibration_points": self.calibration_points
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 标定数据已保存到 {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 保存标定数据失败: {e}")
            return False
    
    def load_calibration_data(self, filename: str = "dual_arm_calibration.json"):
        """加载标定数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 重建坐标关系对象
            relation_data = data["coordinate_relation"]
            self.coordinate_relation = DualArmRelation(**relation_data)
            self.calibration_points = data.get("calibration_points", {"right": [], "left": []})
            
            print(f"✅ 标定数据已从 {filename} 加载")
            print(f"   标定时间: {data['timestamp']}")
            print(f"   基座间距离: {self.coordinate_relation.baseline_distance:.1f} mm")
            
            return True
            
        except Exception as e:
            print(f"❌ 加载标定数据失败: {e}")
            return False
    
    def disconnect_arms(self):
        """断开机械臂连接"""
        print("🔌 断开机械臂连接...")
        
        # 停止监控
        if self.monitoring_active:
            self.stop_continuous_monitoring()
        
        # 断开连接
        try:
            if self.right_arm and self.right_connected:
                self.right_arm.CloseRPC()
                print("✅ 右臂连接已断开")
        except Exception as e:
            print(f"❌ 断开右臂连接失败: {e}")
        
        try:
            if self.left_arm and self.left_connected:
                self.left_arm.CloseRPC()
                print("✅ 左臂连接已断开")
        except Exception as e:
            print(f"❌ 断开左臂连接失败: {e}")
        
        self.right_connected = False
        self.left_connected = False
    
    def run_interactive_session(self):
        """运行交互式会话"""
        print("\n" + "="*80)
        print("🤖 双臂实时监控和坐标关系建立工具")
        print("="*80)
        
        # 连接机械臂
        right_ok, left_ok = self.connect_arms()
        
        if not (right_ok or left_ok):
            print("❌ 无法连接任何机械臂，程序退出")
            return
        
        try:
            while True:
                print("\n" + "="*50)
                print("📋 主菜单")
                print("="*50)
                print("1. 查看当前状态")
                print("2. 开始/停止连续监控")
                print("3. 坐标关系标定")
                print("4. 保存标定数据")
                print("5. 加载标定数据")
                print("6. 查看历史数据统计")
                print("7. 退出程序")
                
                choice = input("\n请选择操作 (1-7): ").strip()
                
                if choice == "1":
                    self.print_current_status()
                
                elif choice == "2":
                    if self.monitoring_active:
                        self.stop_continuous_monitoring()
                    else:
                        self.start_continuous_monitoring()
                
                elif choice == "3":
                    print("\n选择标定方法:")
                    print("1. 手动标定")
                    print("2. 自动标定") 
                    calib_choice = input("请选择 (1-2): ").strip()
                    
                    if calib_choice == "1":
                        self.calibrate_coordinate_relation("manual")
                    elif calib_choice == "2":
                        self.calibrate_coordinate_relation("auto")
                
                elif choice == "4":
                    filename = input("输入保存文件名 (回车使用默认): ").strip()
                    if not filename:
                        filename = "dual_arm_calibration.json"
                    self.save_calibration_data(filename)
                
                elif choice == "5":
                    filename = input("输入加载文件名 (回车使用默认): ").strip()
                    if not filename:
                        filename = "dual_arm_calibration.json"
                    self.load_calibration_data(filename)
                
                elif choice == "6":
                    self._show_history_stats()
                
                elif choice == "7":
                    print("👋 程序退出")
                    break
                
                else:
                    print("❌ 无效选择")
        
        except KeyboardInterrupt:
            print("\n⚠️  用户中断程序")
        
        finally:
            self.disconnect_arms()
    
    def _show_history_stats(self):
        """显示历史数据统计"""
        print("\n📊 历史数据统计:")
        
        if self.right_pose_history:
            print(f"   右臂数据点: {len(self.right_pose_history)} 个")
            last_right = self.right_pose_history[-1]
            print(f"   最后位置: {last_right.tcp_pose[:3]}")
        
        if self.left_pose_history:
            print(f"   左臂数据点: {len(self.left_pose_history)} 个")
            last_left = self.left_pose_history[-1]
            print(f"   最后位置: {last_left.tcp_pose[:3]}")
        
        if self.right_pose_history and self.left_pose_history:
            # 计算最小和最大距离
            distances = []
            for i in range(min(len(self.right_pose_history), len(self.left_pose_history))):
                dist = self.calculate_tcp_distance(
                    self.right_pose_history[i].tcp_pose,
                    self.left_pose_history[i].tcp_pose
                )
                distances.append(dist)
            
            if distances:
                print(f"   最小TCP距离: {min(distances):.1f} mm")
                print(f"   最大TCP距离: {max(distances):.1f} mm")
                print(f"   平均TCP距离: {np.mean(distances):.1f} mm")

def main():
    """主函数"""
    monitor = DualArmRealTimeMonitor()
    monitor.run_interactive_session()

if __name__ == "__main__":
    main()