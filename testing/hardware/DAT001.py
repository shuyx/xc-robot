#!/usr/bin/env python3
"""
双臂同步连接测试脚本
测试ID: DAT-001
测试目的: 验证双臂同时连接和控制
"""

import sys
import os
import time
import logging
import argparse
import threading
from typing import Optional, Dict, Any, List

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

class DualArmSyncTest:
    def __init__(self, left_ip: str, right_ip: str):
        self.left_ip = left_ip
        self.right_ip = right_ip
        self.test_id = "DAT-001"
        self.left_robot: Optional[Robot] = None
        self.right_robot: Optional[Robot] = None
        self.test_results: Dict[str, Any] = {}
        
        # 连接状态
        self.left_connected = False
        self.right_connected = False
        self.connection_errors = {}
        
        # 双臂配置
        self.chest_width = 400.0  # 胸部宽度400mm
        
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
        log_filename = f'logs/{self.test_id}_dual_arm_{time.strftime("%Y%m%d_%H%M%S")}.log'
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
        self.logger.info(f"开始双臂同步连接测试，左臂: {self.left_ip}, 右臂: {self.right_ip}")
    
    def connect_arm(self, arm_name: str, ip: str) -> bool:
        """连接单个机械臂"""
        try:
            self.logger.info(f"正在连接{arm_name}臂 ({ip})...")
            start_time = time.time()
            
            robot = Robot.RPC(ip)
            connection_time = time.time() - start_time
            
            if arm_name == "left":
                self.left_robot = robot
                self.left_connected = True
            else:
                self.right_robot = robot
                self.right_connected = True
            
            self.logger.info(f"[OK] {arm_name}臂连接成功，耗时: {connection_time:.3f}秒")
            return True
            
        except Exception as e:
            self.logger.error(f"[FAILED] {arm_name}臂连接失败: {e}")
            self.connection_errors[arm_name] = str(e)
            return False
    
    def test_parallel_connection(self) -> bool:
        """测试并行连接"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试1: 并行连接测试")
        self.logger.info("="*50)
        
        # 使用线程并行连接
        threads = []
        results = {}
        
        def connect_with_result(arm_name, ip):
            results[arm_name] = self.connect_arm(arm_name, ip)
        
        # 启动连接线程
        start_time = time.time()
        
        left_thread = threading.Thread(target=connect_with_result, args=("left", self.left_ip))
        right_thread = threading.Thread(target=connect_with_result, args=("right", self.right_ip))
        
        left_thread.start()
        right_thread.start()
        
        # 等待连接完成
        left_thread.join()
        right_thread.join()
        
        total_time = time.time() - start_time
        
        # 统计结果
        both_connected = results.get("left", False) and results.get("right", False)
        
        self.test_results['parallel_connection'] = {
            'left_success': results.get("left", False),
            'right_success': results.get("right", False),
            'both_connected': both_connected,
            'total_time': total_time,
            'errors': self.connection_errors.copy()
        }
        
        if both_connected:
            self.logger.info(f"[OK] 双臂并行连接成功，总耗时: {total_time:.3f}秒")
        else:
            self.logger.error(f"[FAILED] 双臂连接失败")
        
        return both_connected
    
    def test_independent_control(self) -> bool:
        """测试独立控制"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试2: 独立控制测试")
        self.logger.info("="*50)
        
        if not (self.left_connected and self.right_connected):
            self.logger.error("[FAILED] 双臂未完全连接，跳过独立控制测试")
            return False
        
        try:
            # 分别设置两臂模式
            self.logger.info("设置双臂为自动模式...")
            left_mode_result = self.left_robot.Mode(0)
            right_mode_result = self.right_robot.Mode(0)
            
            time.sleep(1)
            
            # 分别使能两臂
            self.logger.info("使能双臂...")
            left_enable_result = self.left_robot.RobotEnable(1)
            right_enable_result = self.right_robot.RobotEnable(1)
            
            time.sleep(2)
            
            # 获取两臂的独立状态
            self.logger.info("获取双臂状态...")
            
            left_state = {
                'robot_state': self.left_robot.robot_state_pkg.robot_state,
                'robot_mode': self.left_robot.robot_state_pkg.robot_mode,
                'program_state': self.left_robot.robot_state_pkg.program_state,
                'main_code': self.left_robot.robot_state_pkg.main_code,
                'sub_code': self.left_robot.robot_state_pkg.sub_code
            }
            
            right_state = {
                'robot_state': self.right_robot.robot_state_pkg.robot_state,
                'robot_mode': self.right_robot.robot_state_pkg.robot_mode,
                'program_state': self.right_robot.robot_state_pkg.program_state,
                'main_code': self.right_robot.robot_state_pkg.main_code,
                'sub_code': self.right_robot.robot_state_pkg.sub_code
            }
            
            self.logger.info("左臂状态:")
            self.logger.info(f"  机器人状态: {left_state['robot_state']}")
            self.logger.info(f"  机器人模式: {left_state['robot_mode']}")
            self.logger.info(f"  故障码: 主={left_state['main_code']}, 子={left_state['sub_code']}")
            
            self.logger.info("右臂状态:")
            self.logger.info(f"  机器人状态: {right_state['robot_state']}")
            self.logger.info(f"  机器人模式: {right_state['robot_mode']}")
            self.logger.info(f"  故障码: 主={right_state['main_code']}, 子={right_state['sub_code']}")
            
            # 验证独立控制
            independent_control_ok = True
            
            # 检查是否都设置为自动模式
            if left_state['robot_mode'] != 0 or right_state['robot_mode'] != 0:
                self.logger.warning("[WARNING] 机器人模式设置异常")
                independent_control_ok = False
            
            # 检查故障状态
            if (left_state['main_code'] != 0 or left_state['sub_code'] != 0 or
                right_state['main_code'] != 0 or right_state['sub_code'] != 0):
                self.logger.warning("[WARNING] 存在故障码")
                independent_control_ok = False
            
            self.test_results['independent_control'] = {
                'left_state': left_state,
                'right_state': right_state,
                'mode_set_success': (left_mode_result == 0 and right_mode_result == 0),
                'enable_success': (left_enable_result == 0 and right_enable_result == 0),
                'control_independent': independent_control_ok
            }
            
            if independent_control_ok:
                self.logger.info("[OK] 双臂独立控制正常")
            else:
                self.logger.warning("[WARNING] 双臂独立控制存在问题")
            
            return independent_control_ok
            
        except Exception as e:
            self.logger.error(f"[FAILED] 独立控制测试异常: {e}")
            return False
    
    def test_synchronized_status(self) -> bool:
        """测试同步状态获取"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试3: 同步状态获取测试")
        self.logger.info("="*50)
        
        if not (self.left_connected and self.right_connected):
            self.logger.error("[FAILED] 双臂未完全连接，跳过同步状态测试")
            return False
        
        try:
            # 多次同步获取状态，测试一致性
            sync_results = []
            
            for i in range(5):  # 测试5次
                start_time = time.time()
                
                # 同时获取双臂状态
                left_tcp = [self.left_robot.robot_state_pkg.tl_cur_pos[j] for j in range(6)]
                left_joints = [self.left_robot.robot_state_pkg.jt_cur_pos[j] for j in range(6)]
                
                right_tcp = [self.right_robot.robot_state_pkg.tl_cur_pos[j] for j in range(6)]
                right_joints = [self.right_robot.robot_state_pkg.jt_cur_pos[j] for j in range(6)]
                
                sync_time = time.time() - start_time
                
                sync_result = {
                    'iteration': i + 1,
                    'sync_time': sync_time,
                    'left_tcp': left_tcp,
                    'left_joints': left_joints,
                    'right_tcp': right_tcp,
                    'right_joints': right_joints
                }
                
                sync_results.append(sync_result)
                
                self.logger.info(f"第{i+1}次同步获取，耗时: {sync_time:.4f}秒")
                self.logger.info(f"  左臂TCP: X={left_tcp[0]:.1f}, Y={left_tcp[1]:.1f}, Z={left_tcp[2]:.1f}")
                self.logger.info(f"  右臂TCP: X={right_tcp[0]:.1f}, Y={right_tcp[1]:.1f}, Z={right_tcp[2]:.1f}")
                
                time.sleep(0.5)
            
            # 分析同步性能
            sync_times = [r['sync_time'] for r in sync_results]
            avg_sync_time = sum(sync_times) / len(sync_times)
            max_sync_time = max(sync_times)
            
            self.test_results['synchronized_status'] = {
                'sync_results': sync_results,
                'avg_sync_time': avg_sync_time,
                'max_sync_time': max_sync_time,
                'update_frequency': 1.0 / avg_sync_time if avg_sync_time > 0 else 0
            }
            
            # 评估性能
            if avg_sync_time < 0.01:  # 10ms内
                self.logger.info(f"[OK] 同步状态获取性能良好，平均耗时: {avg_sync_time*1000:.2f}ms")
                return True
            else:
                self.logger.warning(f"[WARNING] 同步状态获取较慢，平均耗时: {avg_sync_time*1000:.2f}ms")
                return False
            
        except Exception as e:
            self.logger.error(f"[FAILED] 同步状态测试异常: {e}")
            return False
    
    def test_dual_arm_safety(self) -> bool:
        """测试双臂安全距离"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试4: 双臂安全距离测试")
        self.logger.info("="*50)
        
        if not (self.left_connected and self.right_connected):
            self.logger.error("[FAILED] 双臂未完全连接，跳过安全距离测试")
            return False
        
        try:
            # 获取当前双臂位置
            left_tcp = [self.left_robot.robot_state_pkg.tl_cur_pos[j] for j in range(6)]
            right_tcp = [self.right_robot.robot_state_pkg.tl_cur_pos[j] for j in range(6)]
            
            # 计算双臂末端距离
            import math
            distance = math.sqrt(sum((left_tcp[i] - right_tcp[i])**2 for i in range(3)))
            
            self.logger.info(f"当前双臂末端距离: {distance:.1f}mm")
            self.logger.info(f"左臂位置: X={left_tcp[0]:.1f}, Y={left_tcp[1]:.1f}, Z={left_tcp[2]:.1f}")
            self.logger.info(f"右臂位置: X={right_tcp[0]:.1f}, Y={right_tcp[1]:.1f}, Z={right_tcp[2]:.1f}")
            
            # 使用安全模型进行检查
            safety_check_result = {}
            
            if self.safety_model:
                # 获取当前关节角度（转换为弧度）
                left_joints = [self.left_robot.robot_state_pkg.jt_cur_pos[j] * math.pi / 180 for j in range(6)]
                right_joints = [self.right_robot.robot_state_pkg.jt_cur_pos[j] * math.pi / 180 for j in range(6)]
                
                # 检查双臂碰撞
                collision_detected = self.safety_model.check_dual_arm_collision(left_joints, right_joints)
                
                safety_check_result = {
                    'collision_detected': collision_detected,
                    'distance': distance,
                    'safety_threshold': self.safety_model.safety_margin + 2 * self.safety_model.link_radius,
                    'safe': not collision_detected and distance > (self.safety_model.safety_margin + 2 * self.safety_model.link_radius)
                }
                
                if collision_detected:
                    self.logger.error("[FAILED] 检测到碰撞风险!")
                elif safety_check_result['safe']:
                    self.logger.info("[OK] 双臂距离安全")
                else:
                    self.logger.warning("[WARNING] 双臂距离较近，需要注意")
            else:
                # 简单距离检查
                min_safe_distance = 300.0  # 300mm最小安全距离
                safety_check_result = {
                    'distance': distance,
                    'safety_threshold': min_safe_distance,
                    'safe': distance > min_safe_distance
                }
                
                if distance > min_safe_distance:
                    self.logger.info(f"[OK] 双臂距离安全 (>{min_safe_distance}mm)")
                else:
                    self.logger.warning(f"[WARNING] 双臂距离过近 (<{min_safe_distance}mm)")
            
            # 测试工作空间分离
            workspace_separation_ok = True
            
            # 检查左臂是否在左侧区域
            if left_tcp[1] <= 50:  # Y坐标应该>50mm (左侧)
                self.logger.warning("[WARNING] 左臂不在左侧安全区域")
                workspace_separation_ok = False
            
            # 检查右臂是否在右侧区域
            if right_tcp[1] >= -50:  # Y坐标应该<-50mm (右侧)
                self.logger.warning("[WARNING] 右臂不在右侧安全区域")
                workspace_separation_ok = False
            
            if workspace_separation_ok:
                self.logger.info("[OK] 双臂工作空间分离正常")
            
            self.test_results['dual_arm_safety'] = {
                'left_position': left_tcp[:3],
                'right_position': right_tcp[:3],
                'end_effector_distance': distance,
                'safety_check': safety_check_result,
                'workspace_separation': workspace_separation_ok
            }
            
            return safety_check_result.get('safe', True) and workspace_separation_ok
            
        except Exception as e:
            self.logger.error(f"[FAILED] 双臂安全距离测试异常: {e}")
            return False
    
    def test_communication_interference(self) -> bool:
        """测试通信干扰"""
        self.logger.info("\n" + "="*50)
        self.logger.info("测试5: 通信干扰测试")
        self.logger.info("="*50)
        
        if not (self.left_connected and self.right_connected):
            self.logger.error("[FAILED] 双臂未完全连接，跳过通信干扰测试")
            return False
        
        try:
            # 并发访问测试
            interference_results = []
            
            def concurrent_status_read(arm_name, robot, results_list):
                """并发状态读取"""
                try:
                    start_time = time.time()
                    
                    # 连续读取状态
                    for i in range(10):
                        tcp_pos = [robot.robot_state_pkg.tl_cur_pos[j] for j in range(6)]
                        joint_pos = [robot.robot_state_pkg.jt_cur_pos[j] for j in range(6)]
                        
                    read_time = time.time() - start_time
                    
                    results_list.append({
                        'arm': arm_name,
                        'success': True,
                        'time': read_time,
                        'reads_per_second': 10 / read_time if read_time > 0 else 0
                    })
                    
                except Exception as e:
                    results_list.append({
                        'arm': arm_name,
                        'success': False,
                        'error': str(e)
                    })
            
            # 启动并发读取
            threads = []
            
            left_thread = threading.Thread(
                target=concurrent_status_read, 
                args=("left", self.left_robot, interference_results)
            )
            right_thread = threading.Thread(
                target=concurrent_status_read, 
                args=("right", self.right_robot, interference_results)
            )
            
            start_time = time.time()
            left_thread.start()
            right_thread.start()
            
            left_thread.join()
            right_thread.join()
            total_time = time.time() - start_time
            
            # 分析结果
            successful_arms = [r for r in interference_results if r.get('success', False)]
            
            if len(successful_arms) == 2:
                avg_read_rate = sum(r['reads_per_second'] for r in successful_arms) / 2
                self.logger.info(f"[OK] 并发通信测试成功")
                self.logger.info(f"  平均读取速率: {avg_read_rate:.1f} 次/秒")
                
                for result in successful_arms:
                    self.logger.info(f"  {result['arm']}臂: {result['reads_per_second']:.1f} 次/秒")
                
                communication_ok = avg_read_rate > 50  # 50次/秒以上认为正常
            else:
                self.logger.error("[FAILED] 并发通信测试失败")
                for result in interference_results:
                    if not result.get('success', False):
                        self.logger.error(f"  {result['arm']}臂错误: {result.get('error', 'Unknown')}")
                communication_ok = False
            
            self.test_results['communication_interference'] = {
                'test_results': interference_results,
                'total_time': total_time,
                'communication_ok': communication_ok
            }
            
            return communication_ok
            
        except Exception as e:
            self.logger.error(f"[FAILED] 通信干扰测试异常: {e}")
            return False
    
    def generate_report(self):
        """生成测试报告"""
        self.logger.info("\n" + "="*50)
        self.logger.info("双臂同步测试报告")
        self.logger.info("="*50)
        
        self.logger.info(f"测试ID: {self.test_id}")
        self.logger.info(f"左臂IP: {self.left_ip}")
        self.logger.info(f"右臂IP: {self.right_ip}")
        self.logger.info(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存测试结果
        import json
        report_filename = f'logs/{self.test_id}_dual_arm_report_{time.strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        self.logger.info(f"\n测试报告已保存到: {report_filename}")
    
    def run(self):
        """执行测试流程"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"开始执行双臂同步连接测试")
        self.logger.info(f"{'='*60}\n")
        
        all_passed = True
        
        try:
            # 执行各项测试
            tests = [
                ("并行连接", self.test_parallel_connection),
                ("独立控制", self.test_independent_control),
                ("同步状态获取", self.test_synchronized_status),
                ("双臂安全距离", self.test_dual_arm_safety),
                ("通信干扰", self.test_communication_interference)
            ]
            
            for test_name, test_func in tests:
                self.logger.info(f"\n开始执行: {test_name}")
                try:
                    if not test_func():
                        all_passed = False
                        self.logger.warning(f"{test_name}测试未通过")
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
            self.logger.info("[OK] 双臂同步测试完成")
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
    parser = argparse.ArgumentParser(description='双臂同步连接测试')
    parser.add_argument('--left-ip', required=True, help='左臂IP地址')
    parser.add_argument('--right-ip', required=True, help='右臂IP地址')
    
    args = parser.parse_args()
    
    # 安全提示
    print("\n" + "="*60)
    print("双臂同步连接测试")
    print("="*60)
    print(f"左臂IP: {args.left_ip}")
    print(f"右臂IP: {args.right_ip}")
    print("\n⚠️  测试内容:")
    print("1. 双臂并行连接测试")
    print("2. 独立控制验证")
    print("3. 同步状态获取")
    print("4. 双臂安全距离检查")
    print("5. 通信干扰测试")
    print("6. 此测试不包含运动，仅状态读取")
    print("="*60)
    
    response = input("\n确认开始测试？(y/n): ")
    if response.lower() != 'y':
        print("测试已取消")
        return
    
    # 执行测试
    tester = DualArmSyncTest(args.left_ip, args.right_ip)
    success = tester.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()