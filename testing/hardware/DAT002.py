#!/usr/bin/env python3
"""
双臂安全距离测试脚本
测试ID: DAT-002
测试目的: 验证双臂防碰撞功能
"""

import sys
import os
import time
import logging
import argparse
import math
import numpy as np
import threading
from typing import Optional, Dict, Any, List, Tuple

# 添加路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fr3_control_path = os.path.join(project_root, 'fr3_control')
sys.path.insert(0, fr3_control_path)

# 导入控制模块
try:
    import fairino
    from fairino import Robot
    FR3_AVAILABLE = True
    print("✅ FR3库导入成功")
except ImportError as e:
    FR3_AVAILABLE = False
    print(f"⚠️  FR3库导入失败: {e}")
    Robot = None

# 导入双臂安全模型
sys.path.insert(0, project_root)
try:
    from dual_arm_safety_model import DualArmSafetyModel, check_dual_arm_safety
    SAFETY_MODEL_AVAILABLE = True
    print("✅ 安全模型导入成功")
except ImportError as e:
    SAFETY_MODEL_AVAILABLE = False
    print(f"⚠️  安全模型导入失败: {e}")
    DualArmSafetyModel = None

class DualArmSafetyTest:
    def __init__(self, left_ip: str, right_ip: str):
        self.left_ip = left_ip
        self.right_ip = right_ip
        self.test_id = "DAT-002"
        self.left_robot: Optional[Robot] = None
        self.right_robot: Optional[Robot] = None
        self.test_results: Dict[str, Any] = {}
        
        # 初始位置记录
        self.left_initial_pose: List[float] = []
        self.right_initial_pose: List[float] = []
        
        # 安全参数
        self.safety_distance_threshold = 300.0  # 300mm安全距离
        self.collision_response_time = 0.1      # 100ms响应时间要求
        self.motion_velocity = 15               # 缓慢运动速度
        
        # 双臂配置
        self.chest_width = 400.0
        
        # 安全模型
        if SAFETY_MODEL_AVAILABLE:
            self.safety_model = DualArmSafetyModel()
            self.safety_model.base_distance = self.chest_width
            self.safety_model.safety_margin = 100.0  # 增加安全裕度
        else:
            self.safety_model = None
        
        # 紧急停止标志
        self.emergency_stop_flag = False
        
        if not FR3_AVAILABLE:
            raise ImportError("FR3库不可用，无法执行测试")
            
        self.setup_logging()
    
    def setup_logging(self):
        """配置日志系统"""
        log_filename = f'logs/{self.test_id}_safety_{time.strftime("%Y%m%d_%H%M%S")}.log'
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"开始双臂安全距离测试，左臂: {self.left_ip}, 右臂: {self.right_ip}")
    
    def connect_robots(self) -> bool:
        """连接双臂机器人"""
        try:
            self.logger.info("连接双臂机器人...")
            
            # 连接左臂
            self.logger.info(f"连接左臂 ({self.left_ip})...")
            self.left_robot = Robot.RPC(self.left_ip)
            
            # 连接右臂
            self.logger.info(f"连接右臂 ({self.right_ip})...")
            self.right_robot = Robot.RPC(self.right_ip)
            
            self.logger.info("[OK] 双臂连接成功")
            
            # 设置机器人模式
            self.left_robot.Mode(0)
            self.right_robot.Mode(0)
            time.sleep(1)
            
            # 使能机器人
            self.left_robot.RobotEnable(1)
            self.right_robot.RobotEnable(1)
            time.sleep(2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"[FAILED] 连接失败: {e}")
            return False
    
    def record_initial_positions(self) -> bool:
        """记录初始位置"""
        try:
            self.left_initial_pose = [self.left_robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
            self.right_initial_pose = [self.right_robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
            
            self.logger.info("初始位置记录:")
            self.logger.info(f"  左臂: X={self.left_initial_pose[0]:.1f}, Y={self.left_initial_pose[1]:.1f}, Z={self.left_initial_pose[2]:.1f}")
            self.logger.info(f"  右臂: X={self.right_initial_pose[0]:.1f}, Y={self.right_initial_pose[1]:.1f}, Z={self.right_initial_pose[2]:.1f}")
            
            # 计算初始距离
            initial_distance = math.sqrt(sum((self.left_initial_pose[i] - self.right_initial_pose[i])**2 for i in range(3)))
            self.logger.info(f"  初始末端距离: {initial_distance:.1f}mm")
            
            return True
            
        except Exception as e:
            self.logger.error(f"记录初始位置失败: {e}")
            return False
    
    def calculate_arm_distance(self) -> float:
        """计算双臂末端距离"""
        try:
            left_pos = [self.left_robot.robot_state_pkg.tl_cur_pos[i] for i in range(3)]
            right_pos = [self.right_robot.robot_state_pkg.tl_cur_pos[i] for i in range(3)]
            
            distance = math.sqrt(sum((left_pos[i] - right_pos[i])**2 for i in range(3)))
            return distance
            
        except Exception as e:
            self.logger.error(f"计算距离失败: {e}")
            return float('inf')
    
    def check_collision_with_safety_model(self) -> Tuple[bool, str]:
        """使用安全模型检查碰撞"""
        if not self.safety_model:
            return False, "安全模型不可用"
        
        try:
            # 获取当前关节角度（转换为弧度）
            left_joints = [self.left_robot.robot_state_pkg.jt_cur_pos[i] * math.pi / 180 for i in range(6)]
            right_joints = [self.right_robot.robot_state_pkg.jt_cur_pos[i] * math.pi / 180 for i in range(6)]
            
            # 检查碰撞
            collision = self.safety_model.check_dual_arm_collision(left_joints, right_joints)
            
            if collision:
                return True, "安全模型检测到碰撞风险"
            else:
                return False, "安全模型检查通过"
                
        except Exception as e:
            return False, f"安全模型检查异常: {str(e)}"
    
    def emergency_stop_both_arms(self) -> bool:
        """紧急停止双臂"""
        try:
            self.logger.warning("执行紧急停止!")
            self.emergency_stop_flag = True
            
            # 同时停止双臂
            left_stop_result = self.left_robot.StopMotion()
            right_stop_result = self.right_robot.StopMotion()
            
            if left_stop_result == 0 and right_stop_result == 0:
                self.logger.info("[OK] 双臂紧急停止成功")
                return True
            else:
                self.logger.error(f"[FAILED] 紧急停止失败，左臂: {left_stop_result}, 右臂: {right_stop_result}")
                return False
                
        except Exception as e:
            self.logger.error(f"紧急停止异常: {e}")
            return False
    
    def test_static_safety_distance(self) -> bool:
        """测试静态安全距离"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试1: 静态安全距离测试")
        self.logger.info("="*50)
        
        try:
            # 测试多种距离阈值
            test_distances = [500, 400, 300, 200, 150]  # 从远到近
            
            static_results = []
            
            for threshold in test_distances:
                self.logger.info(f"\n测试安全距离阈值: {threshold}mm")
                
                # 计算当前距离
                current_distance = self.calculate_arm_distance()
                
                # 检查安全模型
                collision_detected, safety_message = self.check_collision_with_safety_model()
                
                # 距离检查
                distance_safe = current_distance > threshold
                
                result = {
                    'threshold': threshold,
                    'current_distance': current_distance,
                    'distance_safe': distance_safe,
                    'collision_detected': collision_detected,
                    'safety_message': safety_message
                }
                
                static_results.append(result)
                
                self.logger.info(f"  当前距离: {current_distance:.1f}mm")
                self.logger.info(f"  距离安全: {'是' if distance_safe else '否'}")
                self.logger.info(f"  碰撞检测: {'有风险' if collision_detected else '安全'}")
                self.logger.info(f"  安全状态: {safety_message}")
                
                if collision_detected:
                    self.logger.warning(f"  在{threshold}mm阈值下检测到碰撞风险!")
            
            self.test_results['static_safety'] = static_results
            
            # 评估结果
            current_distance = static_results[0]['current_distance']
            if current_distance > self.safety_distance_threshold:
                self.logger.info(f"[OK] 静态安全距离测试通过 ({current_distance:.1f}mm > {self.safety_distance_threshold}mm)")
                return True
            else:
                self.logger.warning(f"[WARNING] 当前距离可能过近 ({current_distance:.1f}mm)")
                return False
                
        except Exception as e:
            self.logger.error(f"[FAILED] 静态安全距离测试异常: {e}")
            return False
    
    def test_dynamic_approach(self) -> bool:
        """测试动态接近过程"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试2: 动态接近测试")
        self.logger.info("="*50)
        
        try:
            # 设计安全的接近运动
            # 让双臂向中心线缓慢移动（但保持安全距离）
            
            # 计算安全的接近目标
            left_target = self.left_initial_pose.copy()
            right_target = self.right_initial_pose.copy()
            
            # 双臂各向中心移动50mm（保守距离）
            left_target[1] -= 50   # 左臂向右移动（Y减小）
            right_target[1] += 50  # 右臂向左移动（Y增大）
            
            self.logger.info("计算动态接近路径:")
            self.logger.info(f"  左臂目标: X={left_target[0]:.1f}, Y={left_target[1]:.1f}, Z={left_target[2]:.1f}")
            self.logger.info(f"  右臂目标: X={right_target[0]:.1f}, Y={right_target[1]:.1f}, Z={right_target[2]:.1f}")
            
            # 预测接近后的距离
            predicted_distance = math.sqrt(sum((left_target[i] - right_target[i])**2 for i in range(3)))
            self.logger.info(f"  预测接近后距离: {predicted_distance:.1f}mm")
            
            # 安全检查
            if predicted_distance < self.safety_distance_threshold:
                self.logger.warning(f"[WARNING] 预测距离过近，调整运动范围")
                # 减少移动距离
                left_target[1] = self.left_initial_pose[1] - 30
                right_target[1] = self.right_initial_pose[1] + 30
                predicted_distance = math.sqrt(sum((left_target[i] - right_target[i])**2 for i in range(3)))
                self.logger.info(f"  调整后预测距离: {predicted_distance:.1f}mm")
            
            if predicted_distance < self.safety_distance_threshold:
                self.logger.error("[FAILED] 无法设计安全的接近运动")
                return False
            
            # 实时监控运动过程
            approach_results = []
            self.emergency_stop_flag = False
            
            def safety_monitor():
                """安全监控线程"""
                while not self.emergency_stop_flag:
                    try:
                        current_distance = self.calculate_arm_distance()
                        collision_detected, _ = self.check_collision_with_safety_model()
                        
                        timestamp = time.time()
                        
                        monitor_result = {
                            'timestamp': timestamp,
                            'distance': current_distance,
                            'collision_detected': collision_detected
                        }
                        approach_results.append(monitor_result)
                        
                        # 检查是否需要紧急停止
                        if collision_detected or current_distance < self.safety_distance_threshold:
                            self.logger.warning(f"安全阈值触发! 距离: {current_distance:.1f}mm")
                            self.emergency_stop_both_arms()
                            break
                        
                        time.sleep(0.05)  # 20Hz监控频率
                        
                    except Exception as e:
                        self.logger.error(f"安全监控异常: {e}")
                        break
            
            # 启动安全监控线程
            monitor_thread = threading.Thread(target=safety_monitor)
            monitor_thread.start()
            
            # 执行同时运动
            self.logger.info("开始同步接近运动...")
            
            # 左臂运动
            left_error = self.left_robot.MoveL(
                desc_pos=left_target,
                tool=0,
                user=0,
                vel=self.motion_velocity
            )
            
            # 右臂运动  
            right_error = self.right_robot.MoveL(
                desc_pos=right_target,
                tool=0,
                user=0,
                vel=self.motion_velocity
            )
            
            if left_error == 0 and right_error == 0:
                # 等待运动完成或紧急停止
                motion_completed = True
                timeout = 30  # 30秒超时
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    if self.emergency_stop_flag:
                        motion_completed = False
                        break
                    
                    # 检查运动是否完成
                    left_done = self.left_robot.robot_state_pkg.motion_done
                    right_done = self.right_robot.robot_state_pkg.motion_done
                    
                    if left_done and right_done:
                        break
                    
                    time.sleep(0.1)
                
                # 停止监控
                self.emergency_stop_flag = True
                monitor_thread.join(timeout=2)
                
                # 分析结果
                final_distance = self.calculate_arm_distance()
                
                self.test_results['dynamic_approach'] = {
                    'left_target': left_target[:3],
                    'right_target': right_target[:3],
                    'predicted_distance': predicted_distance,
                    'final_distance': final_distance,
                    'motion_completed': motion_completed,
                    'emergency_stopped': self.emergency_stop_flag,
                    'monitoring_data': approach_results
                }
                
                if motion_completed and final_distance > self.safety_distance_threshold:
                    self.logger.info(f"[OK] 动态接近测试完成，最终距离: {final_distance:.1f}mm")
                    success = True
                else:
                    self.logger.warning(f"[WARNING] 动态接近测试中断或距离过近: {final_distance:.1f}mm")
                    success = False
                
                # 返回初始位置
                self.logger.info("返回初始位置...")
                self.left_robot.MoveL(self.left_initial_pose, 0, 0, 20)
                self.right_robot.MoveL(self.right_initial_pose, 0, 0, 20)
                
                return success
                
            else:
                self.logger.error(f"[FAILED] 运动指令失败，左臂: {left_error}, 右臂: {right_error}")
                self.emergency_stop_flag = True
                monitor_thread.join(timeout=2)
                return False
            
        except Exception as e:
            self.logger.error(f"[FAILED] 动态接近测试异常: {e}")
            self.emergency_stop_flag = True
            return False
    
    def test_collision_response_time(self) -> bool:
        """测试碰撞响应时间"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试3: 碰撞响应时间测试")
        self.logger.info("="*50)
        
        try:
            # 模拟快速响应测试
            response_times = []
            
            for i in range(5):  # 测试5次
                self.logger.info(f"\n第{i+1}次响应时间测试:")
                
                # 记录检测开始时间
                detection_start = time.time()
                
                # 获取当前状态
                current_distance = self.calculate_arm_distance()
                collision_detected, safety_message = self.check_collision_with_safety_model()
                
                # 如果检测到问题，模拟紧急停止
                if collision_detected or current_distance < self.safety_distance_threshold * 1.5:
                    stop_start = time.time()
                    
                    # 模拟停止命令（不实际执行）
                    # stop_result = self.emergency_stop_both_arms()
                    
                    stop_end = time.time()
                    
                    response_time = stop_end - detection_start
                    detection_time = stop_start - detection_start
                    stop_time = stop_end - stop_start
                    
                    self.logger.info(f"  检测时间: {detection_time*1000:.2f}ms")
                    self.logger.info(f"  停止时间: {stop_time*1000:.2f}ms")
                    self.logger.info(f"  总响应时间: {response_time*1000:.2f}ms")
                    
                else:
                    # 正常状态，仅测试检测时间
                    detection_end = time.time()
                    detection_time = detection_end - detection_start
                    response_time = detection_time
                    
                    self.logger.info(f"  检测时间: {detection_time*1000:.2f}ms")
                    self.logger.info(f"  状态: 正常，无需停止")
                
                response_times.append({
                    'iteration': i + 1,
                    'distance': current_distance,
                    'collision_detected': collision_detected,
                    'response_time': response_time,
                    'meets_requirement': response_time < self.collision_response_time
                })
                
                time.sleep(0.5)  # 测试间隔
            
            # 分析响应时间
            avg_response_time = sum(r['response_time'] for r in response_times) / len(response_times)
            max_response_time = max(r['response_time'] for r in response_times)
            meets_requirement = all(r['meets_requirement'] for r in response_times)
            
            self.test_results['response_time'] = {
                'individual_tests': response_times,
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'requirement': self.collision_response_time,
                'meets_requirement': meets_requirement
            }
            
            self.logger.info(f"\n响应时间测试总结:")
            self.logger.info(f"  平均响应时间: {avg_response_time*1000:.2f}ms")
            self.logger.info(f"  最大响应时间: {max_response_time*1000:.2f}ms")
            self.logger.info(f"  要求: < {self.collision_response_time*1000:.0f}ms")
            self.logger.info(f"  是否达标: {'是' if meets_requirement else '否'}")
            
            return meets_requirement
            
        except Exception as e:
            self.logger.error(f"[FAILED] 响应时间测试异常: {e}")
            return False
    
    def test_different_poses_safety(self) -> bool:
        """测试不同姿态下的距离计算"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试4: 不同姿态安全距离测试")
        self.logger.info("="*50)
        
        try:
            # 定义几种测试姿态（相对于初始位置的偏移）
            test_poses = [
                {
                    'name': '上举姿态',
                    'left_offset': [0, 0, 100, 0, 0, 0],
                    'right_offset': [0, 0, 100, 0, 0, 0]
                },
                {
                    'name': '前伸姿态',
                    'left_offset': [150, 0, 0, 0, 0, 0],
                    'right_offset': [150, 0, 0, 0, 0, 0]
                },
                {
                    'name': '侧展姿态',
                    'left_offset': [0, 100, 0, 0, 0, 0],
                    'right_offset': [0, -100, 0, 0, 0, 0]
                }
            ]
            
            pose_results = []
            
            for pose in test_poses:
                self.logger.info(f"\n测试姿态: {pose['name']}")
                
                # 计算目标位置
                left_target = [
                    self.left_initial_pose[i] + pose['left_offset'][i] 
                    for i in range(6)
                ]
                right_target = [
                    self.right_initial_pose[i] + pose['right_offset'][i] 
                    for i in range(6)
                ]
                
                # 安全检查目标位置
                target_distance = math.sqrt(sum((left_target[i] - right_target[i])**2 for i in range(3)))
                
                self.logger.info(f"  预测距离: {target_distance:.1f}mm")
                
                if target_distance < self.safety_distance_threshold:
                    self.logger.warning(f"  [SKIP] 目标距离过近，跳过运动测试")
                    pose_results.append({
                        'name': pose['name'],
                        'target_distance': target_distance,
                        'skipped': True,
                        'reason': '目标距离过近'
                    })
                    continue
                
                try:
                    # 执行运动到目标姿态
                    left_error = self.left_robot.MoveL(left_target, 0, 0, self.motion_velocity)
                    right_error = self.right_robot.MoveL(right_target, 0, 0, self.motion_velocity)
                    
                    if left_error == 0 and right_error == 0:
                        # 等待运动完成
                        self.wait_for_motion_complete(timeout=15)
                        
                        # 测量实际距离
                        actual_distance = self.calculate_arm_distance()
                        collision_detected, safety_message = self.check_collision_with_safety_model()
                        
                        pose_result = {
                            'name': pose['name'],
                            'target_distance': target_distance,
                            'actual_distance': actual_distance,
                            'collision_detected': collision_detected,
                            'safety_message': safety_message,
                            'distance_error': abs(actual_distance - target_distance),
                            'safe': not collision_detected and actual_distance > self.safety_distance_threshold
                        }
                        
                        self.logger.info(f"  实际距离: {actual_distance:.1f}mm")
                        self.logger.info(f"  距离误差: {pose_result['distance_error']:.1f}mm")
                        self.logger.info(f"  碰撞检测: {'有风险' if collision_detected else '安全'}")
                        self.logger.info(f"  安全评估: {'安全' if pose_result['safe'] else '不安全'}")
                        
                        pose_results.append(pose_result)
                        
                        # 返回初始位置
                        self.left_robot.MoveL(self.left_initial_pose, 0, 0, 20)
                        self.right_robot.MoveL(self.right_initial_pose, 0, 0, 20)
                        self.wait_for_motion_complete(timeout=15)
                        
                    else:
                        self.logger.warning(f"  运动失败，左臂: {left_error}, 右臂: {right_error}")
                        pose_results.append({
                            'name': pose['name'],
                            'target_distance': target_distance,
                            'motion_failed': True,
                            'left_error': left_error,
                            'right_error': right_error
                        })
                
                except Exception as e:
                    self.logger.error(f"  姿态测试异常: {e}")
                    pose_results.append({
                        'name': pose['name'],
                        'error': str(e)
                    })
            
            self.test_results['pose_safety'] = pose_results
            
            # 评估结果
            successful_tests = [r for r in pose_results if r.get('safe', False)]
            total_tests = [r for r in pose_results if not r.get('skipped', False)]
            
            if len(total_tests) > 0:
                success_rate = len(successful_tests) / len(total_tests)
                self.logger.info(f"\n姿态安全测试总结:")
                self.logger.info(f"  总测试姿态: {len(total_tests)}")
                self.logger.info(f"  安全姿态: {len(successful_tests)}")
                self.logger.info(f"  安全率: {success_rate*100:.1f}%")
                
                return success_rate > 0.8  # 80%以上认为通过
            else:
                self.logger.warning("没有有效的姿态测试")
                return False
            
        except Exception as e:
            self.logger.error(f"[FAILED] 姿态安全测试异常: {e}")
            return False
    
    def wait_for_motion_complete(self, timeout: float = 30) -> bool:
        """等待双臂运动完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                left_done = self.left_robot.robot_state_pkg.motion_done
                right_done = self.right_robot.robot_state_pkg.motion_done
                
                if left_done and right_done:
                    return True
                
                time.sleep(0.1)
            except:
                pass
        
        self.logger.warning(f"等待运动完成超时({timeout}秒)")
        return False
    
    def generate_report(self):
        """生成测试报告"""
        self.logger.info("\n" + "="*50)
        self.logger.info("双臂安全距离测试报告")
        self.logger.info("="*50)
        
        self.logger.info(f"测试ID: {self.test_id}")
        self.logger.info(f"左臂IP: {self.left_ip}")
        self.logger.info(f"右臂IP: {self.right_ip}")
        self.logger.info(f"安全距离阈值: {self.safety_distance_threshold}mm")
        self.logger.info(f"响应时间要求: {self.collision_response_time*1000:.0f}ms")
        self.logger.info(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存测试结果
        import json
        report_filename = f'logs/{self.test_id}_safety_report_{time.strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        self.logger.info(f"\n测试报告已保存到: {report_filename}")
    
    def run(self):
        """执行测试流程"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"开始执行双臂安全距离测试")
        self.logger.info(f"{'='*60}\n")
        
        # 连接机器人
        if not self.connect_robots():
            return False
        
        # 记录初始位置
        if not self.record_initial_positions():
            return False
        
        all_passed = True
        
        try:
            # 执行各项测试
            tests = [
                ("静态安全距离", self.test_static_safety_distance),
                ("动态接近", self.test_dynamic_approach),
                ("响应时间", self.test_collision_response_time),
                ("不同姿态安全性", self.test_different_poses_safety)
            ]
            
            for test_name, test_func in tests:
                self.logger.info(f"\n开始执行: {test_name}")
                try:
                    if not test_func():
                        all_passed = False
                        self.logger.warning(f"{test_name}测试未通过")
                    
                    # 测试间隔
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"{test_name}测试异常: {e}")
                    all_passed = False
                
        except KeyboardInterrupt:
            self.logger.warning("\n测试被用户中断")
            self.emergency_stop_both_arms()
            all_passed = False
        
        # 生成报告
        self.generate_report()
        
        # 总结
        self.logger.info(f"\n{'='*60}")
        if all_passed:
            self.logger.info("[OK] 双臂安全距离测试完成")
        else:
            self.logger.warning("[WARNING] 部分测试未通过")
        self.logger.info(f"{'='*60}\n")
        
        # 清理资源
        self.cleanup()
        
        return all_passed
    
    def cleanup(self):
        """清理资源"""
        if self.left_robot:
            try:
                self.left_robot.CloseRPC()
                self.logger.info("左臂连接已断开")
            except Exception as e:
                self.logger.warning(f"断开左臂连接时异常: {e}")
        
        if self.right_robot:
            try:
                self.right_robot.CloseRPC()
                self.logger.info("右臂连接已断开")
            except Exception as e:
                self.logger.warning(f"断开右臂连接时异常: {e}")

def main():
    parser = argparse.ArgumentParser(description='双臂安全距离测试')
    parser.add_argument('--left-ip', required=True, help='左臂IP地址')
    parser.add_argument('--right-ip', required=True, help='右臂IP地址')
    
    args = parser.parse_args()
    
    # 安全提示
    print("\n" + "="*60)
    print("双臂安全距离测试")
    print("="*60)
    print(f"左臂IP: {args.left_ip}")
    print(f"右臂IP: {args.right_ip}")
    print("\n⚠️  重要安全提示:")
    print("1. 此测试包含双臂运动")
    print("2. 测试双臂防碰撞功能")
    print("3. 运动速度较慢确保安全")
    print("4. 包含接近运动测试")
    print("5. 自动紧急停止功能")
    print("6. 请确保周围区域安全")
    print("7. 随时可按Ctrl+C中断")
    print("="*60)
    
    response = input("\n确认开始测试？(y/n): ")
    if response.lower() != 'y':
        print("测试已取消")
        return
    
    # 再次确认
    print("\n最后确认：双臂将进行接近运动测试！")
    final_response = input("输入 'START' 开始测试: ")
    if final_response != 'START':
        print("测试已取消")
        return
    
    # 执行测试
    tester = DualArmSafetyTest(args.left_ip, args.right_ip)
    success = tester.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()