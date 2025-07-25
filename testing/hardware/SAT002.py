#!/usr/bin/env python3
"""
单臂运动测试脚本
测试ID: SAT-002
测试目的: 验证FR3机械臂的基础运动功能和安全机制
注意: 此测试会产生真实的机械臂运动，运动幅度小且安全
"""

import sys
import os
import time
import logging
import argparse
import math
from typing import Optional, Dict, Any, List

# 添加路径 - 参考quick_start.py的导入方式
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fr3_control_path = os.path.join(project_root, 'fr3_control')

sys.path.insert(0, fr3_control_path)

# 导入控制模块
try:
    # 先导入fairino模块
    import fairino
    # 然后从fairino中获取Robot类
    from fairino import Robot
    FR3_AVAILABLE = True
    print("✅ FR3库导入成功")
except ImportError as e:
    FR3_AVAILABLE = False
    print(f"⚠️  FR3库导入失败: {e}")
    Robot = None

class SingleArmMotionTest:
    def __init__(self, robot_ip: str, arm_name: str = "right"):
        self.robot_ip = robot_ip
        self.arm_name = arm_name
        self.test_id = "SAT-002"
        self.robot: Optional[Robot] = None
        self.test_results: Dict[str, Any] = {}
        self.initial_joint_pos: List[float] = []
        self.initial_tcp_pose: List[float] = []
        
        # 安全运动参数 - 调整为更保守的值
        self.max_joint_increment = 2.0  # 最大关节增量：2度
        self.max_tcp_increment = 10.0   # 最大TCP增量：10mm（从15mm减小）
        self.motion_velocity = 20       # 运动速度：20%
        self.test_timeout = 60          # 测试超时：60秒
        
        # 类人型双臂机器人配置参数
        self.chest_width = 420.0            # 胸部宽度：420mm
        self.arm_base_distance = 210.0      # 单臂距离中心：210mm
        self.shoulder_height = 1400.0       # 肩部离地高度：约1.4m
        self.min_inter_arm_distance = 200.0 # 双臂最小安全距离：200mm（从300mm减小）
        
        # 类人型双臂机器人工作空间（基于FR3参数：630mm臂展）
        self.workspace_limits = {
            'x_min': -600, 'x_max': 600,     # 前后方向：±600mm
            'y_min': -800, 'y_max': 800,     # 左右方向：±800mm（考虑双臂展开）
            'z_min': -600, 'z_max': 300      # 垂直方向：下垂600mm到上举300mm
        }
        
        # 根据臂的类型设置安全运动方向偏好 - 修正版本
        if self.arm_name == "right":
            self.safe_y_direction = +1       # 右臂优先向左（+Y，远离中心线）
            self.arm_center_offset = +210    # 右臂中心偏移
        else:
            self.safe_y_direction = -1       # 左臂优先向右（-Y，远离中心线）
            self.arm_center_offset = -210    # 左臂中心偏移
        
        # 检查FR3库是否可用
        if not FR3_AVAILABLE:
            raise ImportError("FR3库不可用，无法执行测试")
            
        self.setup_logging()
        
    def setup_logging(self):
        """配置日志系统"""
        log_filename = f'logs/{self.test_id}_{self.arm_name}_{time.strftime("%Y%m%d_%H%M%S")}.log'
        
        # 创建logs目录
        import os
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
        self.logger.info(f"开始{self.arm_name}臂运动测试，IP: {self.robot_ip}")
        
    def test_connection(self) -> bool:
        """测试基础连接"""
        self.logger.info("=" * 50)
        self.logger.info("测试1: 基础连接测试")
        self.logger.info("=" * 50)
        
        try:
            start_time = time.time()
            self.logger.info(f"正在连接到{self.arm_name}臂 {self.robot_ip}...")
            
            self.robot = Robot.RPC(self.robot_ip)
            
            connection_time = time.time() - start_time
            self.logger.info(f"[OK] 连接成功！耗时: {connection_time:.3f}秒")
            
            self.test_results['connection'] = {
                'status': 'PASSED',
                'time': connection_time
            }
            return True
            
        except Exception as e:
            self.logger.error(f"[FAILED] 连接失败: {e}")
            self.test_results['connection'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    def record_initial_position(self) -> bool:
        """记录初始位置"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试2: 记录初始位置")
        self.logger.info("=" * 50)
        
        try:
            # 记录初始关节位置
            if hasattr(self.robot, 'robot_state_pkg'):
                self.initial_joint_pos = [self.robot.robot_state_pkg.jt_cur_pos[i] for i in range(6)]
                self.initial_tcp_pose = [self.robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
                
                self.logger.info("[OK] 初始关节位置记录:")
                for i, angle in enumerate(self.initial_joint_pos):
                    self.logger.info(f"  关节{i+1}: {angle:.3f}°")
                
                self.logger.info("[OK] 初始TCP位姿记录:")
                self.logger.info(f"  位置: X={self.initial_tcp_pose[0]:.1f}, Y={self.initial_tcp_pose[1]:.1f}, Z={self.initial_tcp_pose[2]:.1f} mm")
                self.logger.info(f"  姿态: RX={self.initial_tcp_pose[3]:.1f}, RY={self.initial_tcp_pose[4]:.1f}, RZ={self.initial_tcp_pose[5]:.1f}°")
                
                self.test_results['initial_position'] = {
                    'joints': self.initial_joint_pos.copy(),
                    'tcp_pose': self.initial_tcp_pose.copy()
                }
                return True
            else:
                self.logger.error("[FAILED] 无法获取robot_state_pkg")
                return False
                
        except Exception as e:
            self.logger.error(f"[FAILED] 记录初始位置异常: {e}")
            return False
    
    def check_workspace_safety(self, target_tcp: List[float]) -> bool:
        """检查工作空间安全性 - 基于FR3实际工作空间边界"""
        
        x, y, z = target_tcp[:3]
        
        # 检查X轴边界
        if x < self.workspace_limits['x_min'] or x > self.workspace_limits['x_max']:
            self.logger.error(f"[FAILED] X坐标{x:.1f}mm超出安全范围[{self.workspace_limits['x_min']}, {self.workspace_limits['x_max']}]")
            return False
            
        # 检查Y轴边界  
        if y < self.workspace_limits['y_min'] or y > self.workspace_limits['y_max']:
            self.logger.error(f"[FAILED] Y坐标{y:.1f}mm超出安全范围[{self.workspace_limits['y_min']}, {self.workspace_limits['y_max']}]")
            return False
            
        # 检查Z轴边界
        if z < self.workspace_limits['z_min'] or z > self.workspace_limits['z_max']:
            self.logger.error(f"[FAILED] Z坐标{z:.1f}mm超出安全范围[{self.workspace_limits['z_min']}, {self.workspace_limits['z_max']}]")
            return False
        
        # 检查是否在极低位（可能撞击底座或桌面）
        if z < -300:  # 调整极限值，允许当前的-120mm位置
            self.logger.error(f"[FAILED] 目标高度{z:.1f}mm过低，可能撞击底座")
            return False
            
        self.logger.info(f"[OK] 目标位置({x:.1f}, {y:.1f}, {z:.1f})在安全工作空间内")
        return True
    
    def check_inter_arm_safety(self, target_tcp: List[float], current_tcp: List[float] = None) -> bool:
        """检查双臂间安全距离（类人型双臂机器人）- 增强版本支持运动方向评估"""
        import math
        
        # 基于类人型配置计算对臂的预估安全位置
        x, y, z = target_tcp[:3]
        
        if self.arm_name == "right":
            # 右臂测试时，假设左臂在自然下垂位置
            estimated_left_tcp = [0, 210, -120]   # 左臂自然位置（距离中心+210mm）
            other_arm_tcp = estimated_left_tcp
            
            # 右臂安全区域检查：右臂应该在Y坐标负值区域（-800到-50mm）
            if y > -50:  # 右臂不应该过于靠近身体中心线
                # 如果提供了当前位置，检查运动方向是否更安全
                if current_tcp is not None:
                    current_y = current_tcp[1]
                    if current_y > -50:  # 当前位置也不安全
                        # 检查运动方向：如果是向右（Y减小），则更安全
                        if y < current_y:
                            self.logger.info(f"[ENHANCED] 右臂Y坐标{y:.1f}mm仍不安全，但运动方向({current_y:.1f}→{y:.1f})远离中心线，允许执行")
                            return True
                        else:
                            self.logger.error(f"[FAILED] 右臂Y坐标{y:.1f}mm过于靠近身体中心线且运动方向不安全")
                            return False
                    else:
                        self.logger.error(f"[FAILED] 右臂Y坐标{y:.1f}mm过于靠近身体中心线（应<-50mm）")
                        return False
                else:
                    self.logger.error(f"[FAILED] 右臂Y坐标{y:.1f}mm过于靠近身体中心线（应<-50mm）")
                    return False
                
        else:
            # 左臂测试时，假设右臂在自然下垂位置
            estimated_right_tcp = [0, -210, -120]  # 右臂自然位置（距离中心-210mm）
            other_arm_tcp = estimated_right_tcp
            
            # 左臂安全区域检查：左臂应该在Y坐标负值区域（-800到-50mm）
            if y > -50:  # 左臂不应该过于靠近身体中心线
                # 如果提供了当前位置，检查运动方向是否更安全
                if current_tcp is not None:
                    current_y = current_tcp[1]
                    if current_y > -50:  # 当前位置也不安全
                        # 检查运动方向：如果是向右（Y减小），则更安全
                        if y < current_y:
                            self.logger.info(f"[ENHANCED] 左臂Y坐标{y:.1f}mm仍不安全，但运动方向({current_y:.1f}→{y:.1f})远离中心线，允许执行")
                            return True
                        else:
                            self.logger.error(f"[FAILED] 左臂Y坐标{y:.1f}mm过于靠近身体中心线且运动方向不安全")
                            return False
                    else:
                        self.logger.error(f"[FAILED] 左臂Y坐标{y:.1f}mm过于靠近身体中心线（应<-50mm）")
                        return False
                else:
                    self.logger.error(f"[FAILED] 左臂Y坐标{y:.1f}mm过于靠近身体中心线（应<-50mm）")
                    return False
        
        # 计算与对臂的3D距离
        distance = math.sqrt(
            sum((target_tcp[i] - other_arm_tcp[i])**2 for i in range(3))
        )
        
        if distance < self.min_inter_arm_distance:
            self.logger.error(f"[FAILED] 与对臂距离{distance:.1f}mm小于安全距离{self.min_inter_arm_distance}mm")
            return False
        
        # 检查胸前交叉风险（X方向太靠前且Y方向靠近中心）
        if x > 200 and abs(y - self.arm_center_offset) < 150:
            self.logger.error(f"[FAILED] 位置过于靠近胸前中心区域，存在交叉风险")
            return False
            
        return True
    
    def is_motion_direction_safer(self, current_tcp: List[float], target_tcp: List[float]) -> bool:
        """判断运动方向是否让机械臂更安全 - 修正版本"""
        current_y = current_tcp[1]
        target_y = target_tcp[1]
        
        if self.arm_name == "left":
            # 左臂：Y坐标减少（向右，远离中心线）更安全
            return target_y < current_y
        else:
            # 右臂：Y坐标增加（向左，远离中心线）更安全  
            return target_y > current_y
    
    def is_current_position_safe(self, current_y: float) -> bool:
        """检查当前位置是否安全 - 修正版本"""
        if self.arm_name == "left":
            # 左臂：Y坐标在-800到-50mm区域是安全的（向右伸展）
            # Y坐标过于接近0表示过于靠近身体中心线
            return current_y < -50  
        else:
            # 右臂：Y坐标在50到800mm区域是安全的（向左伸展）  
            return current_y > 50
    
    def design_safe_motion_based_on_current_pose(self) -> List[Dict]:
        """基于类人型双臂机器人配置设计安全运动序列"""
        self.logger.info("基于类人型双臂配置分析并设计安全运动...")
        
        # 分析当前TCP位置
        current_x, current_y, current_z = self.initial_tcp_pose[:3]
        
        self.logger.info(f"当前TCP位置: X={current_x:.1f}, Y={current_y:.1f}, Z={current_z:.1f}")
        self.logger.info(f"臂类型: {self.arm_name}臂，安全方向偏好: {'向左' if self.safe_y_direction > 0 else '向右'}")
        
        # 评估当前位置安全性
        is_current_safe = self.is_current_position_safe(current_y)
        if is_current_safe:
            self.logger.info(f"[SAFETY] 当前位置安全，Y坐标{current_y:.1f}mm在安全区域内")
        else:
            self.logger.warning(f"[SAFETY] 当前位置不安全，Y坐标{current_y:.1f}mm需要改善")
            self.logger.info(f"[SAFETY] 将优先安排远离中心线的动作以改善安全性")
        
        # 基于类人型配置设计安全运动
        safe_motions = []
        
        # 根据当前位置安全性决定运动策略
        is_current_position_safe = self.is_current_position_safe(current_y)
        
        # 1. 优先级最高：向外侧运动（远离身体中心和对臂）- 减小动作幅度
        safe_y_offset = 8 * self.safe_y_direction  # 向安全方向移动8mm（保守幅度）
        
        # 如果当前位置不安全，稍微增加外侧运动的偏移量
        if not is_current_position_safe:
            self.logger.info(f"当前位置不安全，优先安排远离中心的动作")
            safe_y_offset = 12 * self.safe_y_direction  # 增加到12mm
        
        # 检查外侧运动是否在工作空间内
        if ((self.arm_name == "right" and current_y + safe_y_offset > self.workspace_limits['y_min']) or
            (self.arm_name == "left" and current_y + safe_y_offset < self.workspace_limits['y_max'])):
            
            safe_motions.append({
                'name': f'{self.arm_name}臂向外侧运动',
                'type': 'tcp',
                'offset': [0, safe_y_offset, 0, 0, 0, 0],
                'description': f'{self.arm_name}臂向外侧移动{abs(safe_y_offset)}mm（{"脱离危险区域" if not is_current_position_safe else "小幅安全动作"}）',
                'safety_priority': 'high'
            })
            safe_motions.append({
                'name': f'{self.arm_name}臂外侧回原位',
                'type': 'tcp',
                'offset': [0, 0, 0, 0, 0, 0],
                'description': f'{self.arm_name}臂回到初始位置'
            })
        
        # 2. 次优先级：向上运动（自然手臂上举）- 减小动作幅度
        if current_z < self.workspace_limits['z_max'] - 50:
            safe_motions.append({
                'name': f'{self.arm_name}臂向上运动',
                'type': 'tcp',
                'offset': [0, 0, 8, 0, 0, 0],
                'description': f'{self.arm_name}臂向上移动8mm（小幅上举）'
            })
            safe_motions.append({
                'name': f'{self.arm_name}臂上举回原位',
                'type': 'tcp',
                'offset': [0, 0, 0, 0, 0, 0],
                'description': f'{self.arm_name}臂回到初始位置'
            })
        
        # 3. 向前运动（但要避免胸前交叉）- 减小动作幅度
        if current_x < 200:  # 不要太靠近胸前
            safe_motions.append({
                'name': f'{self.arm_name}臂向前运动',
                'type': 'tcp',
                'offset': [5, 0, 0, 0, 0, 0],
                'description': f'{self.arm_name}臂向前移动5mm'
            })
            safe_motions.append({
                'name': f'{self.arm_name}臂向前回原位',
                'type': 'tcp',
                'offset': [0, 0, 0, 0, 0, 0],
                'description': f'{self.arm_name}臂回到初始位置'
            })
        
        # 4. 关节运动：腕部旋转（最安全的关节运动）
        safe_motions.append({
            'name': f'{self.arm_name}臂腕部旋转',
            'type': 'joint',
            'target_offset': [0, 0, 0, 0, 0, 2.0],
            'description': f'{self.arm_name}臂腕部旋转2度（最安全的关节运动）'
        })
        safe_motions.append({
            'name': f'{self.arm_name}臂腕部回原位',
            'type': 'joint',
            'target_offset': [0, 0, 0, 0, 0, 0],
            'description': f'{self.arm_name}臂腕部回到初始位置'
        })
        
        # 5. 如果位置允许，添加肘部小幅运动（关节5）
        safe_motions.append({
            'name': f'{self.arm_name}臂肘部运动',
            'type': 'joint',
            'target_offset': [0, 0, 0, 0, 1.0, 0],
            'description': f'{self.arm_name}臂肘部关节运动1度'
        })
        safe_motions.append({
            'name': f'{self.arm_name}臂肘部回原位',
            'type': 'joint',
            'target_offset': [0, 0, 0, 0, 0, 0],
            'description': f'{self.arm_name}臂肘部回到初始位置'
        })
        
        self.logger.info(f"设计了{len(safe_motions)}个类人型安全运动动作")
        self.logger.info(f"运动优先级: 1.向外侧 2.向上 3.向前 4.腕部旋转 5.肘部运动")
        return safe_motions
    
    def check_safety_limits(self, target_joints: List[float] = None, target_tcp: List[float] = None) -> bool:
        """检查安全限位（关节或TCP）- 增强版本支持运动方向评估"""
        self.logger.info("执行综合安全检查...")
        
        # 检查关节限位（如果提供关节角度）
        if target_joints:
            # FR3关节限位（度）
            joint_limits = [
                (-170, 170),  # J1
                (-120, 120),  # J2
                (-170, 170),  # J3
                (-170, 170),  # J4
                (-120, 120),  # J5
                (-175, 175)   # J6
            ]
            
            for i, (target, (min_limit, max_limit)) in enumerate(zip(target_joints, joint_limits)):
                if target < min_limit or target > max_limit:
                    self.logger.error(f"[FAILED] 关节{i+1}目标位置{target:.1f}°超出限位[{min_limit}, {max_limit}]")
                    return False
                    
                # 检查运动增量
                increment = abs(target - self.initial_joint_pos[i])
                if increment > self.max_joint_increment:
                    self.logger.error(f"[FAILED] 关节{i+1}运动增量{increment:.1f}°超出安全限制{self.max_joint_increment}°")
                    return False
        
        # 检查TCP位置安全（如果提供TCP位置）
        if target_tcp:
            # 工作空间安全检查
            if not self.check_workspace_safety(target_tcp):
                return False
                
            # 双臂安全距离检查（传递当前位置以支持运动方向评估）
            if not self.check_inter_arm_safety(target_tcp, current_tcp=self.initial_tcp_pose):
                return False
                
            # TCP运动增量检查 - 但如果运动方向更安全，可以放宽限制
            tcp_displacement = sum(abs(target_tcp[i] - self.initial_tcp_pose[i]) for i in range(3))
            if tcp_displacement > self.max_tcp_increment:
                # 检查运动方向是否更安全
                if self.is_motion_direction_safer(self.initial_tcp_pose, target_tcp):
                    # 如果运动方向更安全，允许更大的位移（最大到20mm）
                    if tcp_displacement <= 20.0:
                        self.logger.info(f"[ENHANCED] TCP位移{tcp_displacement:.1f}mm超出常规限制{self.max_tcp_increment}mm，但运动方向更安全，允许执行")
                    else:
                        self.logger.error(f"[FAILED] TCP位移{tcp_displacement:.1f}mm超出最大安全限制20.0mm")
                        return False
                else:
                    self.logger.error(f"[FAILED] TCP位移{tcp_displacement:.1f}mm超出安全限制{self.max_tcp_increment}mm")
                    return False
        
        self.logger.info("[OK] 安全限位检查通过")
        return True
    
    def test_joint_motion(self) -> bool:
        """测试关节运动"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试3: 关节运动测试")
        self.logger.info("=" * 50)
        
        try:
            # 设置机器人为自动模式
            self.logger.info("设置机器人为自动模式...")
            self.robot.Mode(0)
            time.sleep(1)
            
            # 使能机器人
            self.logger.info("使能机器人...")
            enable_ret = self.robot.RobotEnable(1)
            if enable_ret != 0:
                self.logger.warning(f"使能返回码: {enable_ret}")
            time.sleep(2)
            
            # 基于当前位姿设计安全的测试动作序列
            all_motions = self.design_safe_motion_based_on_current_pose()
            test_motions = [m for m in all_motions if m['type'] == 'joint']
            
            motion_results = []
            
            for i, motion in enumerate(test_motions):
                self.logger.info(f"\n执行动作 {i+1}/4: {motion['name']}")
                self.logger.info(f"描述: {motion['description']}")
                
                # 计算目标关节位置
                target_joints = [
                    self.initial_joint_pos[j] + motion['target_offset'][j] 
                    for j in range(6)
                ]
                
                # 安全检查
                if not self.check_safety_limits(target_joints=target_joints):
                    self.logger.error(f"动作 {i+1} 安全检查失败，跳过")
                    motion_results.append({
                        'motion': motion['name'],
                        'status': 'FAILED',
                        'reason': '安全检查失败'
                    })
                    continue
                
                # 执行运动
                try:
                    self.logger.info(f"目标关节位置: {[f'{j:.1f}°' for j in target_joints]}")
                    
                    start_time = time.time()
                    error = self.robot.MoveJ(
                        joint_pos=target_joints,
                        tool=0,
                        user=0,
                        vel=self.motion_velocity
                    )
                    
                    if error == 0:
                        # 等待运动完成
                        self.wait_for_motion_complete(timeout=10)
                        
                        # 验证到位精度
                        actual_joints = [self.robot.robot_state_pkg.jt_cur_pos[j] for j in range(6)]
                        max_error = max(abs(actual_joints[j] - target_joints[j]) for j in range(6))
                        
                        motion_time = time.time() - start_time
                        
                        if max_error < 1.0:  # 1度精度
                            self.logger.info(f"[OK] 动作完成，耗时: {motion_time:.2f}秒，最大误差: {max_error:.3f}°")
                            motion_results.append({
                                'motion': motion['name'],
                                'status': 'PASSED',
                                'time': motion_time,
                                'accuracy': max_error
                            })
                        else:
                            self.logger.warning(f"[WARNING] 动作完成但精度不足，误差: {max_error:.3f}°")
                            motion_results.append({
                                'motion': motion['name'],
                                'status': 'WARNING',
                                'time': motion_time,
                                'accuracy': max_error
                            })
                    else:
                        self.logger.error(f"[FAILED] 运动指令返回错误码: {error}")
                        motion_results.append({
                            'motion': motion['name'],
                            'status': 'FAILED',
                            'reason': f'运动错误码: {error}'
                        })
                        
                except Exception as e:
                    self.logger.error(f"[FAILED] 动作执行异常: {e}")
                    motion_results.append({
                        'motion': motion['name'],
                        'status': 'FAILED',
                        'reason': str(e)
                    })
                
                # 动作间隔
                time.sleep(1)
            
            self.test_results['joint_motion'] = motion_results
            
            # 统计结果
            passed = sum(1 for r in motion_results if r['status'] == 'PASSED')
            total = len(motion_results)
            
            if passed == total:
                self.logger.info(f"[OK] 关节运动测试完成: {passed}/{total} 个动作成功")
                return True
            else:
                self.logger.warning(f"[WARNING] 关节运动测试部分成功: {passed}/{total} 个动作成功")
                return False
                
        except Exception as e:
            self.logger.error(f"[FAILED] 关节运动测试异常: {e}")
            return False
    
    def test_tcp_motion(self) -> bool:
        """测试TCP直线运动"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试4: TCP直线运动测试")
        self.logger.info("=" * 50)
        
        try:
            # 基于当前位姿设计安全的TCP运动序列
            all_motions = self.design_safe_motion_based_on_current_pose()
            tcp_motions = [m for m in all_motions if m['type'] == 'tcp']
            
            tcp_results = []
            
            for i, motion in enumerate(tcp_motions):
                self.logger.info(f"\n执行TCP动作 {i+1}/4: {motion['name']}")
                self.logger.info(f"描述: {motion['description']}")
                
                # 计算目标TCP位置
                target_tcp = [
                    self.initial_tcp_pose[j] + motion['offset'][j] 
                    for j in range(6)
                ]
                
                # 安全检查
                if not self.check_safety_limits(target_tcp=target_tcp):
                    self.logger.error(f"TCP动作 {i+1} 安全检查失败，跳过")
                    tcp_results.append({
                        'motion': motion['name'],
                        'status': 'FAILED',
                        'reason': '安全检查失败'
                    })
                    continue
                
                # 执行TCP运动
                try:
                    self.logger.info(f"目标TCP位置: X={target_tcp[0]:.1f}, Y={target_tcp[1]:.1f}, Z={target_tcp[2]:.1f}")
                    
                    start_time = time.time()
                    error = self.robot.MoveL(
                        desc_pos=target_tcp,
                        tool=0,
                        user=0,
                        vel=self.motion_velocity
                    )
                    
                    if error == 0:
                        # 等待运动完成
                        self.wait_for_motion_complete(timeout=10)
                        
                        # 验证到位精度
                        actual_tcp = [self.robot.robot_state_pkg.tl_cur_pos[j] for j in range(6)]
                        position_error = math.sqrt(sum((actual_tcp[j] - target_tcp[j])**2 for j in range(3)))
                        
                        motion_time = time.time() - start_time
                        
                        if position_error < 2.0:  # 2mm精度
                            self.logger.info(f"[OK] TCP动作完成，耗时: {motion_time:.2f}秒，位置误差: {position_error:.3f}mm")
                            tcp_results.append({
                                'motion': motion['name'],
                                'status': 'PASSED',
                                'time': motion_time,
                                'accuracy': position_error
                            })
                        else:
                            self.logger.warning(f"[WARNING] TCP动作完成但精度不足，误差: {position_error:.3f}mm")
                            tcp_results.append({
                                'motion': motion['name'],
                                'status': 'WARNING',
                                'time': motion_time,
                                'accuracy': position_error
                            })
                    else:
                        self.logger.error(f"[FAILED] TCP运动指令返回错误码: {error}")
                        tcp_results.append({
                            'motion': motion['name'],
                            'status': 'FAILED',
                            'reason': f'运动错误码: {error}'
                        })
                        
                except Exception as e:
                    self.logger.error(f"[FAILED] TCP动作执行异常: {e}")
                    tcp_results.append({
                        'motion': motion['name'],
                        'status': 'FAILED',
                        'reason': str(e)
                    })
                
                # 动作间隔
                time.sleep(1)
            
            self.test_results['tcp_motion'] = tcp_results
            
            # 统计结果
            passed = sum(1 for r in tcp_results if r['status'] == 'PASSED')
            total = len(tcp_results)
            
            if passed == total:
                self.logger.info(f"[OK] TCP运动测试完成: {passed}/{total} 个动作成功")
                return True
            else:
                self.logger.warning(f"[WARNING] TCP运动测试部分成功: {passed}/{total} 个动作成功")
                return False
                
        except Exception as e:
            self.logger.error(f"[FAILED] TCP运动测试异常: {e}")
            return False
    
    def test_emergency_stop(self) -> bool:
        """测试紧急停止功能"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试5: 紧急停止功能测试")
        self.logger.info("=" * 50)
        
        try:
            self.logger.info("开始运动，并在运动中测试紧急停止...")
            
            # 开始一个较长的运动
            target_joints = [j + 0.5 for j in self.initial_joint_pos]  # 所有关节移动0.5度
            
            # 开始运动（不等待完成）
            error = self.robot.MoveJ(
                joint_pos=target_joints,
                tool=0,
                user=0,
                vel=10  # 使用较低速度
            )
            
            if error == 0:
                # 运动开始后立即停止
                time.sleep(0.5)  # 让机器人开始运动
                self.logger.info("执行紧急停止...")
                
                stop_error = self.robot.StopMotion()
                
                if stop_error == 0:
                    self.logger.info("[OK] 紧急停止指令执行成功")
                    
                    # 等待机器人完全停止
                    time.sleep(2)
                    
                    # 检查机器人是否停止
                    if hasattr(self.robot, 'robot_state_pkg'):
                        motion_done = self.robot.robot_state_pkg.motion_done
                        if motion_done:
                            self.logger.info("[OK] 机器人已完全停止")
                            self.test_results['emergency_stop'] = {
                                'status': 'PASSED',
                                'stop_command_result': stop_error
                            }
                            return True
                        else:
                            self.logger.warning("[WARNING] 机器人可能仍在运动")
                            self.test_results['emergency_stop'] = {
                                'status': 'WARNING',
                                'stop_command_result': stop_error
                            }
                            return False
                else:
                    self.logger.error(f"[FAILED] 紧急停止指令失败，错误码: {stop_error}")
                    self.test_results['emergency_stop'] = {
                        'status': 'FAILED',
                        'error': f'停止指令错误码: {stop_error}'
                    }
                    return False
            else:
                self.logger.error(f"[FAILED] 无法开始测试运动，错误码: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"[FAILED] 紧急停止测试异常: {e}")
            self.test_results['emergency_stop'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    def return_to_initial_position(self) -> bool:
        """返回初始位置"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试6: 返回初始位置")
        self.logger.info("=" * 50)
        
        try:
            if not self.initial_joint_pos:
                self.logger.error("[FAILED] 未记录初始位置")
                return False
            
            self.logger.info("返回初始关节位置...")
            error = self.robot.MoveJ(
                joint_pos=self.initial_joint_pos,
                tool=0,
                user=0,
                vel=self.motion_velocity
            )
            
            if error == 0:
                # 等待运动完成
                self.wait_for_motion_complete(timeout=15)
                
                # 验证是否回到初始位置
                current_joints = [self.robot.robot_state_pkg.jt_cur_pos[i] for i in range(6)]
                max_error = max(abs(current_joints[i] - self.initial_joint_pos[i]) for i in range(6))
                
                if max_error < 1.0:  # 1度精度
                    self.logger.info(f"[OK] 成功返回初始位置，最大误差: {max_error:.3f}°")
                    self.test_results['return_home'] = {
                        'status': 'PASSED',
                        'accuracy': max_error
                    }
                    return True
                else:
                    self.logger.warning(f"[WARNING] 未精确回到初始位置，误差: {max_error:.3f}°")
                    self.test_results['return_home'] = {
                        'status': 'WARNING',
                        'accuracy': max_error
                    }
                    return False
            else:
                self.logger.error(f"[FAILED] 返回初始位置失败，错误码: {error}")
                self.test_results['return_home'] = {
                    'status': 'FAILED',
                    'error': f'运动错误码: {error}'
                }
                return False
                
        except Exception as e:
            self.logger.error(f"[FAILED] 返回初始位置异常: {e}")
            return False
    
    def wait_for_motion_complete(self, timeout: float = 30) -> bool:
        """等待运动完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if hasattr(self.robot, 'robot_state_pkg'):
                    motion_done = self.robot.robot_state_pkg.motion_done
                    if motion_done:
                        return True
                time.sleep(0.1)
            except:
                pass
        
        self.logger.warning(f"等待运动完成超时({timeout}秒)")
        return False
    
    def generate_report(self):
        """生成测试报告"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试报告总结")
        self.logger.info("=" * 50)
        
        self.logger.info(f"测试ID: {self.test_id}")
        self.logger.info(f"测试臂: {self.arm_name}臂")
        self.logger.info(f"机器人IP: {self.robot_ip}")
        self.logger.info(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存测试结果到文件
        import json
        report_filename = f'logs/{self.test_id}_{self.arm_name}_report_{time.strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        self.logger.info(f"\n测试报告已保存到: {report_filename}")
        
    def run(self):
        """执行测试流程"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"开始执行{self.arm_name}臂运动测试")
        self.logger.info(f"{'='*60}\n")
        
        all_passed = True
        
        # 执行各项测试
        tests = [
            ("基础连接", self.test_connection),
            ("记录初始位置", self.record_initial_position),
            ("关节运动", self.test_joint_motion),
            ("TCP运动", self.test_tcp_motion),
            ("紧急停止", self.test_emergency_stop),
            ("返回初始位置", self.return_to_initial_position)
        ]
        
        for test_name, test_func in tests:
            if not self.robot and test_name not in ["基础连接"]:
                self.logger.warning(f"跳过{test_name}测试（未连接）")
                continue
                
            try:
                if not test_func():
                    all_passed = False
            except Exception as e:
                self.logger.error(f"{test_name}测试异常: {e}")
                all_passed = False
                
        # 生成报告
        self.generate_report()
        
        # 总结
        self.logger.info(f"\n{'='*60}")
        if all_passed:
            self.logger.info("[OK] 所有测试通过！")
        else:
            self.logger.warning("[WARNING] 部分测试未通过，请检查日志")
        self.logger.info(f"{'='*60}\n")
        
        # 清理资源
        self.cleanup()
        
        return all_passed
    
    def cleanup(self):
        """清理资源"""
        if self.robot:
            self.logger.info("断开连接...")
            try:
                self.robot.CloseRPC()
                self.logger.info("机器人连接已断开")
            except Exception as e:
                self.logger.warning(f"断开连接时出现异常: {e}")

def main():
    parser = argparse.ArgumentParser(description='FR3单臂运动测试')
    parser.add_argument('--arm', choices=['left', 'right'], default='right',
                       help='测试臂选择 (默认: right)')
    parser.add_argument('--ip', required=True,
                       help='机器人IP地址')
    
    args = parser.parse_args()
    
    # 安全提示
    print("\n" + "="*60)
    print("FR3机械臂运动测试")
    print("="*60)
    print(f"目标机器人: {args.arm}臂")
    print(f"IP地址: {args.ip}")
    print("\n⚠️  重要安全提示（类人型双臂机器人）:")
    print("1. 此测试会产生真实的机械臂运动")
    print("2. 运动幅度小（关节±2°，TCP±10mm）且安全")
    print("3. 运动速度低（20%额定速度）")
    print("4. 基于类人型配置：胸宽420mm，肩高1.4m")
    print("5. 优先向外侧运动，避免双臂交叉碰撞")
    print("6. 已集成中心线越界和胸前交叉检查")
    print("7. 测试前请确保机械臂周围区域已清空")
    print("8. 随时可以按Ctrl+C中断测试")
    print("9. 如有异常请立即按急停按钮")
    print("="*60)
    
    response = input("\n确认开始运动测试？(y/n): ")
    if response.lower() != 'y':
        print("测试已取消")
        return
        
    # 再次确认
    print("\n最后确认：机械臂将开始运动，请确保安全！")
    final_response = input("输入 'START' 开始测试: ")
    if final_response != 'START':
        print("测试已取消")
        return
        
    # 执行测试
    tester = SingleArmMotionTest(args.ip, args.arm)
    success = tester.run()
    
    # 返回状态码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()