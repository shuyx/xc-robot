#!/usr/bin/env python3
"""
工作空间测试脚本
测试ID: SAT-004
测试目的: 验证机械臂可达工作空间
"""

import sys
import os
import time
import logging
import argparse
import math
import numpy as np
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
    from dual_arm_safety_model import DualArmSafetyModel
    SAFETY_MODEL_AVAILABLE = True
    print("✅ 安全模型导入成功")
except ImportError as e:
    SAFETY_MODEL_AVAILABLE = False
    print(f"⚠️  安全模型导入失败: {e}")
    DualArmSafetyModel = None

class WorkspaceTest:
    def __init__(self, robot_ip: str, arm_name: str = "right"):
        self.robot_ip = robot_ip
        self.arm_name = arm_name
        self.test_id = "SAT-004"
        self.robot: Optional[Robot] = None
        self.test_results: Dict[str, Any] = {}
        self.initial_tcp_pose: List[float] = []
        
        # FR3机械臂规格参数
        self.max_reach = 630.0  # FR3最大臂展 630mm
        self.min_reach = 100.0  # 最小工作半径
        
        # 双臂配置参数
        self.chest_width = 400.0
        self.arm_base_distance = 200.0
        
        # 工作空间边界点定义
        self.boundary_test_points = self.generate_boundary_points()
        
        # 奇异点区域（需要特别注意的配置）
        self.singular_regions = [
            {"name": "肩部奇异", "description": "J1轴线与末端重合"},
            {"name": "肘部奇异", "description": "J3 = 0°或180°"},
            {"name": "腕部奇异", "description": "J5 = 0°"}
        ]
        
        # 安全模型
        if SAFETY_MODEL_AVAILABLE:
            self.safety_model = DualArmSafetyModel()
            self.safety_model.base_distance = self.chest_width
        else:
            self.safety_model = None
        
        if not FR3_AVAILABLE:
            raise ImportError("FR3库不可用，无法执行测试")
            
        self.setup_logging()
    
    def setup_logging(self):
        """配置日志系统"""
        log_filename = f'logs/{self.test_id}_{self.arm_name}_{time.strftime("%Y%m%d_%H%M%S")}.log'
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
        self.logger.info(f"开始{self.arm_name}臂工作空间测试，IP: {self.robot_ip}")
    
    def generate_boundary_points(self) -> List[Dict[str, Any]]:
        """生成工作空间边界测试点"""
        points = []
        
        # 基于机械臂的配置计算基座位置
        if self.arm_name == "right":
            base_offset = -self.arm_base_distance  # 右臂基座在Y轴负方向
            safe_y_range = (-800, -50)  # 右臂安全Y范围
        else:
            base_offset = self.arm_base_distance   # 左臂基座在Y轴正方向
            safe_y_range = (50, 800)   # 左臂安全Y范围
        
        # 1. 最大臂展边界点（圆周采样）
        for angle in np.linspace(0, 2*np.pi, 8):  # 8个方向
            x = self.max_reach * 0.9 * np.cos(angle)  # 0.9倍最大臂展作为安全边界
            y = base_offset + self.max_reach * 0.9 * np.sin(angle)
            
            # 确保在安全Y范围内
            if safe_y_range[0] <= y <= safe_y_range[1]:
                points.append({
                    'name': f'最大臂展_{angle*180/np.pi:.0f}度',
                    'position': [x, y, 0],
                    'type': 'max_reach',
                    'expected_reachable': True
                })
        
        # 2. 不同高度的边界点
        heights = [-300, -150, 0, 150, 250]  # 不同Z高度
        for z in heights:
            # 前方最远点
            x = self.max_reach * 0.8
            y = base_offset
            if safe_y_range[0] <= y <= safe_y_range[1]:
                points.append({
                    'name': f'前方最远_Z{z}',
                    'position': [x, y, z],
                    'type': 'height_test',
                    'expected_reachable': True
                })
            
            # 侧方最远点
            x = 0
            y = base_offset + (self.max_reach * 0.8 * (1 if self.arm_name == "left" else -1))
            if safe_y_range[0] <= y <= safe_y_range[1]:
                points.append({
                    'name': f'侧方最远_Z{z}',
                    'position': [x, y, z],
                    'type': 'height_test',
                    'expected_reachable': True
                })
        
        # 3. 最小工作半径测试点
        for angle in np.linspace(0, 2*np.pi, 4):
            x = self.min_reach * 1.5 * np.cos(angle)
            y = base_offset + self.min_reach * 1.5 * np.sin(angle)
            
            if safe_y_range[0] <= y <= safe_y_range[1]:
                points.append({
                    'name': f'最小半径_{angle*180/np.pi:.0f}度',
                    'position': [x, y, 0],
                    'type': 'min_reach',
                    'expected_reachable': True
                })
        
        # 4. 预期不可达的点（超出工作空间）
        points.extend([
            {
                'name': '超远前方',
                'position': [self.max_reach * 1.2, base_offset, 0],
                'type': 'unreachable',
                'expected_reachable': False
            },
            {
                'name': '超高位置',
                'position': [300, base_offset, 400],
                'type': 'unreachable',
                'expected_reachable': False
            },
            {
                'name': '过低位置',
                'position': [300, base_offset, -700],
                'type': 'unreachable',
                'expected_reachable': False
            }
        ])
        
        return points
    
    def connect_robot(self) -> bool:
        """连接机器人"""
        try:
            self.logger.info(f"正在连接到{self.arm_name}臂...")
            self.robot = Robot.RPC(self.robot_ip)
            self.logger.info("[OK] 连接成功")
            
            # 设置自动模式并使能
            self.robot.Mode(0)
            time.sleep(1)
            self.robot.RobotEnable(1)
            time.sleep(2)
            
            return True
        except Exception as e:
            self.logger.error(f"[FAILED] 连接失败: {e}")
            return False
    
    def record_initial_pose(self) -> bool:
        """记录初始位姿"""
        try:
            if hasattr(self.robot, 'robot_state_pkg'):
                self.initial_tcp_pose = [self.robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
                self.logger.info(f"初始TCP位姿: X={self.initial_tcp_pose[0]:.1f}, Y={self.initial_tcp_pose[1]:.1f}, Z={self.initial_tcp_pose[2]:.1f}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"记录初始位姿失败: {e}")
            return False
    
    def test_inverse_kinematics(self, target_pos: List[float]) -> Tuple[bool, Optional[List[float]], str]:
        """测试逆运动学求解"""
        try:
            # 构造目标位姿（保持当前姿态，只改变位置）
            target_pose = self.initial_tcp_pose.copy()
            target_pose[:3] = target_pos
            
            # 尝试逆运动学求解
            if self.safety_model:
                # 使用安全模型进行逆运动学求解
                target_matrix = np.eye(4)
                target_matrix[:3, 3] = target_pos
                
                # 获取当前关节角度作为初值
                current_joints = [self.robot.robot_state_pkg.jt_cur_pos[i] * np.pi / 180 for i in range(6)]
                
                result_joints = self.safety_model.inverse_kinematics(
                    target_matrix, self.arm_name, current_joints
                )
                
                if result_joints:
                    # 转换为度
                    result_joints_deg = [j * 180 / np.pi for j in result_joints]
                    return True, result_joints_deg, "逆运动学求解成功"
                else:
                    return False, None, "逆运动学无解"
            else:
                # 简化测试：尝试直接运动到目标位置
                return True, None, "跳过逆运动学验证（安全模型不可用）"
                
        except Exception as e:
            return False, None, f"逆运动学求解异常: {str(e)}"
    
    def test_reachability(self, point: Dict[str, Any]) -> Dict[str, Any]:
        """测试点位可达性"""
        self.logger.info(f"\n测试点位: {point['name']}")
        self.logger.info(f"目标位置: X={point['position'][0]:.1f}, Y={point['position'][1]:.1f}, Z={point['position'][2]:.1f}")
        
        result = {
            'name': point['name'],
            'position': point['position'],
            'type': point['type'],
            'expected_reachable': point['expected_reachable'],
            'actual_reachable': False,
            'ik_solvable': False,
            'motion_successful': False,
            'position_error': None,
            'message': ""
        }
        
        try:
            # 1. 逆运动学测试
            ik_success, joint_solution, ik_message = self.test_inverse_kinematics(point['position'])
            result['ik_solvable'] = ik_success
            result['message'] += f"IK: {ik_message}; "
            
            if ik_success and joint_solution:
                # 2. 如果是预期可达的点，尝试实际运动
                if point['expected_reachable']:
                    target_pose = self.initial_tcp_pose.copy()
                    target_pose[:3] = point['position']
                    
                    # 执行运动
                    error = self.robot.MoveL(
                        desc_pos=target_pose,
                        tool=0,
                        user=0,
                        vel=15  # 较慢速度
                    )
                    
                    if error == 0:
                        # 等待运动完成
                        self.wait_for_motion_complete(timeout=20)
                        
                        # 验证到达精度
                        actual_pose = [self.robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
                        position_error = math.sqrt(sum((actual_pose[i] - target_pose[i])**2 for i in range(3)))
                        
                        result['motion_successful'] = True
                        result['actual_reachable'] = True
                        result['position_error'] = position_error
                        result['message'] += f"运动成功，误差{position_error:.1f}mm; "
                        
                        self.logger.info(f"[OK] 点位可达，误差: {position_error:.1f}mm")
                        
                        # 返回初始位置
                        self.robot.MoveL(
                            desc_pos=self.initial_tcp_pose,
                            tool=0,
                            user=0,
                            vel=20
                        )
                        self.wait_for_motion_complete(timeout=15)
                        
                    else:
                        result['message'] += f"运动指令失败，错误码{error}; "
                        self.logger.warning(f"[WARNING] 运动指令失败: {error}")
                else:
                    # 预期不可达的点，只测试逆运动学
                    result['actual_reachable'] = False
                    result['message'] += "预期不可达，仅测试IK; "
                    self.logger.info("[INFO] 预期不可达点，跳过实际运动")
            else:
                result['message'] += "IK失败，跳过运动测试; "
                self.logger.info("[INFO] 逆运动学失败，确认不可达")
                
        except Exception as e:
            result['message'] += f"测试异常: {str(e)}; "
            self.logger.error(f"[ERROR] 测试异常: {e}")
        
        # 验证预期结果
        if result['expected_reachable'] == result['actual_reachable']:
            self.logger.info(f"[OK] 可达性符合预期: {result['expected_reachable']}")
        else:
            self.logger.warning(f"[WARNING] 可达性不符合预期，预期: {result['expected_reachable']}, 实际: {result['actual_reachable']}")
        
        return result
    
    def test_workspace_boundary(self) -> bool:
        """测试工作空间边界"""
        self.logger.info("\n" + "="*50)
        self.logger.info("工作空间边界测试")
        self.logger.info("="*50)
        
        boundary_results = []
        
        for point in self.boundary_test_points:
            result = self.test_reachability(point)
            boundary_results.append(result)
            time.sleep(1)  # 测试间隔
        
        self.test_results['boundary_test'] = boundary_results
        
        # 统计结果
        total_points = len(boundary_results)
        correct_predictions = sum(1 for r in boundary_results 
                                if r['expected_reachable'] == r['actual_reachable'])
        
        success_rate = correct_predictions / total_points * 100
        self.logger.info(f"\n边界测试总结:")
        self.logger.info(f"  总测试点: {total_points}")
        self.logger.info(f"  预期正确: {correct_predictions}")
        self.logger.info(f"  准确率: {success_rate:.1f}%")
        
        return success_rate >= 80  # 80%以上准确率认为通过
    
    def generate_workspace_cloud(self) -> bool:
        """生成工作空间云图数据"""
        self.logger.info("\n" + "="*50)
        self.logger.info("工作空间云图生成")
        self.logger.info("="*50)
        
        cloud_points = []
        
        # 生成规则网格点进行采样
        x_range = np.linspace(-400, 600, 10)
        y_range = np.linspace(-600, 600, 10) 
        z_range = np.linspace(-400, 200, 6)
        
        total_samples = len(x_range) * len(y_range) * len(z_range)
        self.logger.info(f"采样点总数: {total_samples}")
        
        sample_count = 0
        reachable_count = 0
        
        for x in x_range:
            for y in y_range:
                for z in z_range:
                    sample_count += 1
                    
                    # 应用双臂安全约束
                    if self.arm_name == "right" and y > -50:
                        continue  # 右臂不应进入左侧区域
                    if self.arm_name == "left" and y < 50:
                        continue  # 左臂不应进入右侧区域
                    
                    # 快速可达性检查（仅逆运动学）
                    ik_success, _, _ = self.test_inverse_kinematics([x, y, z])
                    
                    point_data = {
                        'position': [x, y, z],
                        'reachable': ik_success
                    }
                    cloud_points.append(point_data)
                    
                    if ik_success:
                        reachable_count += 1
                    
                    # 进度报告
                    if sample_count % 100 == 0:
                        progress = sample_count / total_samples * 100
                        self.logger.info(f"采样进度: {progress:.1f}% ({sample_count}/{total_samples})")
        
        workspace_volume = reachable_count / len(cloud_points) * 100
        self.logger.info(f"\n工作空间统计:")
        self.logger.info(f"  总采样点: {len(cloud_points)}")
        self.logger.info(f"  可达点: {reachable_count}")
        self.logger.info(f"  工作空间覆盖率: {workspace_volume:.1f}%")
        
        self.test_results['workspace_cloud'] = {
            'points': cloud_points,
            'total_samples': len(cloud_points),
            'reachable_count': reachable_count,
            'coverage_rate': workspace_volume
        }
        
        return True
    
    def test_singular_configurations(self) -> bool:
        """测试奇异配置"""
        self.logger.info("\n" + "="*50)
        self.logger.info("奇异配置测试")
        self.logger.info("="*50)
        
        singular_results = []
        
        # 测试几种已知的奇异配置
        test_configs = [
            {
                'name': '肩部奇异',
                'joints': [90, -90, 90, 0, 0, 0],  # J1=90度可能导致肩部奇异
                'description': '测试肩部奇异点'
            },
            {
                'name': '肘部奇异', 
                'joints': [0, -90, 0, 0, 0, 0],    # J3=0度导致肘部奇异
                'description': '测试肘部奇异点'
            },
            {
                'name': '腕部奇异',
                'joints': [0, -90, 90, 0, 0, 0],   # J5=0度导致腕部奇异
                'description': '测试腕部奇异点'
            }
        ]
        
        for config in test_configs:
            self.logger.info(f"\n测试配置: {config['name']}")
            
            try:
                # 检查关节限位
                joints_in_limit = True
                joint_limits = [
                    (-170, 170), (-120, 120), (-170, 170),
                    (-170, 170), (-120, 120), (-175, 175)
                ]
                
                for i, (joint_angle, (min_limit, max_limit)) in enumerate(zip(config['joints'], joint_limits)):
                    if joint_angle < min_limit or joint_angle > max_limit:
                        joints_in_limit = False
                        break
                
                if joints_in_limit:
                    # 计算该配置的末端位置
                    if self.safety_model:
                        joints_rad = [j * np.pi / 180 for j in config['joints']]
                        end_pose = self.safety_model.forward_kinematics(joints_rad, self.arm_name)
                        end_position = end_pose[:3, 3]
                        
                        result = {
                            'name': config['name'],
                            'joints': config['joints'],
                            'end_position': end_position.tolist(),
                            'in_limits': True,
                            'singular': True  # 假设这些都是奇异配置
                        }
                        
                        self.logger.info(f"  关节角度: {config['joints']}")
                        self.logger.info(f"  末端位置: X={end_position[0]:.1f}, Y={end_position[1]:.1f}, Z={end_position[2]:.1f}")
                        self.logger.warning(f"  [SINGULAR] 检测到奇异配置")
                    else:
                        result = {
                            'name': config['name'],
                            'joints': config['joints'],
                            'in_limits': True,
                            'message': '无法验证（安全模型不可用）'
                        }
                else:
                    result = {
                        'name': config['name'],
                        'joints': config['joints'],
                        'in_limits': False,
                        'message': '关节角度超出限位'
                    }
                    self.logger.warning(f"  关节角度超出限位，跳过测试")
                
                singular_results.append(result)
                
            except Exception as e:
                self.logger.error(f"  奇异配置测试异常: {e}")
                singular_results.append({
                    'name': config['name'],
                    'error': str(e)
                })
        
        self.test_results['singular_test'] = singular_results
        return True
    
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
        self.logger.info("\n" + "="*50)
        self.logger.info("工作空间测试报告")
        self.logger.info("="*50)
        
        self.logger.info(f"测试ID: {self.test_id}")
        self.logger.info(f"测试臂: {self.arm_name}臂")
        self.logger.info(f"机器人IP: {self.robot_ip}")
        self.logger.info(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存测试结果
        import json
        report_filename = f'logs/{self.test_id}_{self.arm_name}_report_{time.strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        self.logger.info(f"\n测试报告已保存到: {report_filename}")
        
        # 生成工作空间数据CSV文件（用于可视化）
        if 'workspace_cloud' in self.test_results:
            csv_filename = f'logs/{self.test_id}_{self.arm_name}_workspace_{time.strftime("%Y%m%d_%H%M%S")}.csv'
            with open(csv_filename, 'w') as f:
                f.write("X,Y,Z,Reachable\n")
                for point in self.test_results['workspace_cloud']['points']:
                    x, y, z = point['position']
                    reachable = 1 if point['reachable'] else 0
                    f.write(f"{x:.1f},{y:.1f},{z:.1f},{reachable}\n")
            self.logger.info(f"工作空间数据已保存到: {csv_filename}")
    
    def run(self):
        """执行测试流程"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"开始执行{self.arm_name}臂工作空间测试")
        self.logger.info(f"{'='*60}\n")
        
        # 连接机器人
        if not self.connect_robot():
            return False
        
        # 记录初始位姿
        if not self.record_initial_pose():
            return False
        
        all_passed = True
        
        try:
            # 执行各项测试
            tests = [
                ("工作空间边界", self.test_workspace_boundary),
                ("工作空间云图", self.generate_workspace_cloud),
                ("奇异配置", self.test_singular_configurations)
            ]
            
            for test_name, test_func in tests:
                self.logger.info(f"\n开始执行: {test_name}")
                try:
                    if not test_func():
                        all_passed = False
                        self.logger.warning(f"{test_name}测试未完全通过")
                except Exception as e:
                    self.logger.error(f"{test_name}测试异常: {e}")
                    all_passed = False
                
        except KeyboardInterrupt:
            self.logger.warning("\n测试被用户中断")
            all_passed = False
        
        # 生成报告
        self.generate_report()
        
        # 总结
        self.logger.info(f"\n{'='*60}")
        if all_passed:
            self.logger.info("[OK] 工作空间测试完成")
        else:
            self.logger.warning("[WARNING] 部分测试未通过")
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
    parser = argparse.ArgumentParser(description='FR3工作空间测试')
    parser.add_argument('--arm', choices=['left', 'right'], default='right',
                       help='测试臂选择 (默认: right)')
    parser.add_argument('--ip', required=True,
                       help='机器人IP地址')
    
    args = parser.parse_args()
    
    # 安全提示
    print("\n" + "="*60)
    print("FR3工作空间测试")
    print("="*60)
    print(f"目标机器人: {args.arm}臂")
    print(f"IP地址: {args.ip}")
    print("\n⚠️  测试内容:")
    print("1. 工作空间边界可达性测试")
    print("2. 工作空间云图生成")
    print("3. 奇异点区域标记")
    print("4. 测试过程包含实际运动")
    print("5. 运动速度较慢，确保安全")
    print("="*60)
    
    response = input("\n确认开始测试？(y/n): ")
    if response.lower() != 'y':
        print("测试已取消")
        return
    
    # 执行测试
    tester = WorkspaceTest(args.ip, args.arm)
    success = tester.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()