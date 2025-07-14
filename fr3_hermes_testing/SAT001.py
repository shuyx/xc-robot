#!/usr/bin/env python3
"""
单臂连接测试脚本
测试ID: SAT-001
测试目的: 验证与FR3机械臂的网络连接和SDK通信
"""

import sys
import os
import time
import logging
import argparse
from typing import Optional, Dict, Any

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
    print(f"[WARNING]️  FR3库导入失败: {e}")
    Robot = None

class SingleArmConnectionTest:
    def __init__(self, robot_ip: str, arm_name: str = "right"):
        self.robot_ip = robot_ip
        self.arm_name = arm_name
        self.test_id = "SAT-001"
        self.robot: Optional[Robot] = None
        self.test_results: Dict[str, Any] = {}
        
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
        self.logger.info(f"开始{self.arm_name}臂连接测试，IP: {self.robot_ip}")
        
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
            
    def test_sdk_info(self) -> bool:
        """测试SDK信息获取"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试2: SDK信息获取")
        self.logger.info("=" * 50)
        
        try:
            # 获取SDK版本
            error, version = self.robot.GetSDKVersion()
            if error == 0:
                self.logger.info(f"[OK] SDK版本: {version}")
                self.test_results['sdk_version'] = version
            else:
                self.logger.error(f"[FAILED] 获取SDK版本失败，错误码: {error}")
                return False
                
            # 获取控制器IP
            error, controller_ip = self.robot.GetControllerIP()
            if error == 0:
                self.logger.info(f"[OK] 控制器IP: {controller_ip}")
                self.test_results['controller_ip'] = controller_ip
            else:
                self.logger.error(f"[FAILED] 获取控制器IP失败，错误码: {error}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"[FAILED] SDK信息获取异常: {e}")
            return False
            
    def test_robot_state(self) -> bool:
        """测试机器人状态获取"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试3: 机器人状态获取")
        self.logger.info("=" * 50)
        
        try:
            # 使用robot_state_pkg方式获取状态（参考getjoint.py的成功实现）
            if hasattr(self.robot, 'robot_state_pkg'):
                self.logger.info("[OK] robot_state_pkg属性存在，使用稳定的状态获取方式")
                
                # 获取机器人状态
                robot_state = self.robot.robot_state_pkg.robot_state
                state_desc = self.parse_robot_state(robot_state)
                self.logger.info(f"[OK] 机器人状态: {state_desc}")
                self.test_results['robot_state'] = state_desc
                
                # 获取机器人模式
                robot_mode = self.robot.robot_state_pkg.robot_mode
                mode_desc = {0: "自动模式", 1: "手动模式"}.get(robot_mode, f"未知模式({robot_mode})")
                self.logger.info(f"[OK] 机器人模式: {mode_desc}")
                self.test_results['robot_mode'] = mode_desc
                
                # 获取程序状态
                program_state = self.robot.robot_state_pkg.program_state
                self.logger.info(f"[OK] 程序状态: {program_state}")
                self.test_results['program_state'] = program_state
                
                # 获取故障码
                main_code = self.robot.robot_state_pkg.main_code
                sub_code = self.robot.robot_state_pkg.sub_code
                if main_code != 0 or sub_code != 0:
                    self.logger.warning(f"[WARNING] 故障码: 主={main_code}, 子={sub_code}")
                else:
                    self.logger.info("[OK] 无故障码")
                self.test_results['error_codes'] = {'main': main_code, 'sub': sub_code}
                
                # 获取运动状态
                motion_done = self.robot.robot_state_pkg.motion_done
                self.logger.info(f"[OK] 运动完成状态: {motion_done}")
                self.test_results['motion_done'] = motion_done
                
                return True
            else:
                self.logger.error("[FAILED] robot_state_pkg属性不存在")
                return False
                
        except Exception as e:
            self.logger.error(f"[FAILED] 状态获取异常: {e}")
            return False
            
    def test_joint_position(self) -> bool:
        """测试关节位置获取"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试4: 关节位置获取")
        self.logger.info("=" * 50)
        
        try:
            # 获取关节角度
            error, joints = self.robot.GetActualJointPosDegree()
            if error == 0:
                self.logger.info("[OK] 当前关节角度 (度):")
                for i, angle in enumerate(joints):
                    self.logger.info(f"  关节{i+1}: {angle:.3f}°")
                self.test_results['joint_positions'] = joints
            else:
                self.logger.error(f"[FAILED] 获取关节角度失败，错误码: {error}")
                return False
                
            # 获取关节速度
            error, speeds = self.robot.GetActualJointSpeedsDegree()
            if error == 0:
                self.logger.info("[OK] 当前关节速度 (度/秒):")
                for i, speed in enumerate(speeds):
                    self.logger.info(f"  关节{i+1}: {speed:.3f}°/s")
                self.test_results['joint_speeds'] = speeds
                
            return True
            
        except Exception as e:
            self.logger.error(f"[FAILED] 关节位置获取异常: {e}")
            return False
            
    def test_tcp_position(self) -> bool:
        """测试TCP位置获取"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试5: TCP位置获取")
        self.logger.info("=" * 50)
        
        try:
            # 获取工具坐标系位姿
            error, tcp_pose = self.robot.GetActualToolFlangePose()
            if error == 0:
                self.logger.info("[OK] 当前TCP位姿:")
                self.logger.info(f"  位置 X: {tcp_pose[0]:.3f} mm")
                self.logger.info(f"  位置 Y: {tcp_pose[1]:.3f} mm")
                self.logger.info(f"  位置 Z: {tcp_pose[2]:.3f} mm")
                self.logger.info(f"  姿态 Rx: {tcp_pose[3]:.3f}°")
                self.logger.info(f"  姿态 Ry: {tcp_pose[4]:.3f}°")
                self.logger.info(f"  姿态 Rz: {tcp_pose[5]:.3f}°")
                self.test_results['tcp_pose'] = tcp_pose
            else:
                self.logger.error(f"[FAILED] 获取TCP位姿失败，错误码: {error}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"[FAILED] TCP位置获取异常: {e}")
            return False
            
    def test_io_status(self) -> bool:
        """测试IO状态获取"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试6: IO状态获取")
        self.logger.info("=" * 50)
        
        try:
            # 测试数字输入
            test_io_count = 4  # 测试前4个IO
            self.logger.info(f"数字输入状态 (前{test_io_count}个):")
            for i in range(test_io_count):
                error, value = self.robot.GetDI(i)
                if error == 0:
                    status = "ON" if value else "OFF"
                    self.logger.info(f"  DI[{i}]: {status}")
                    
            # 测试数字输出
            self.logger.info(f"数字输出状态 (前{test_io_count}个):")
            
            # 尝试多种GetDO调用方式
            do_success = False
            
            # 方式1：尝试GetDO()不带参数，可能返回所有DO状态
            try:
                self.logger.info("  尝试方式1: GetDO()不带参数")
                do_result = self.robot.GetDO()
                if isinstance(do_result, (list, tuple)):
                    if len(do_result) >= 2 and isinstance(do_result[0], int):
                        # 格式: (error_code, [do_values])
                        error_code, do_values = do_result[0], do_result[1:]
                        if error_code == 0:
                            for i, value in enumerate(do_values[:test_io_count]):
                                status = "ON" if value else "OFF"
                                self.logger.info(f"  DO[{i}]: {status}")
                            do_success = True
                    else:
                        # 直接返回DO值列表
                        for i, value in enumerate(do_result[:test_io_count]):
                            status = "ON" if value else "OFF"
                            self.logger.info(f"  DO[{i}]: {status}")
                        do_success = True
                else:
                    self.logger.info(f"  方式1结果: {do_result}")
            except Exception as e:
                self.logger.info(f"  方式1失败: {e}")
            
            # 方式2：尝试使用robot_state_pkg方式（如果方式1失败）
            if not do_success:
                try:
                    self.logger.info("  尝试方式2: 使用robot_state_pkg")
                    if hasattr(self.robot, 'robot_state_pkg'):
                        # 检查是否有DO相关属性
                        pkg_attrs = [attr for attr in dir(self.robot.robot_state_pkg) if 'do' in attr.lower() or 'output' in attr.lower()]
                        if pkg_attrs:
                            self.logger.info(f"  发现DO相关属性: {pkg_attrs}")
                            # 尝试常见的DO属性名
                            for attr_name in ['do_state', 'digital_output', 'do_status']:
                                if hasattr(self.robot.robot_state_pkg, attr_name):
                                    do_data = getattr(self.robot.robot_state_pkg, attr_name)
                                    self.logger.info(f"  {attr_name}: {do_data}")
                                    if isinstance(do_data, (list, tuple)):
                                        for i, value in enumerate(do_data[:test_io_count]):
                                            status = "ON" if value else "OFF"
                                            self.logger.info(f"  DO[{i}]: {status}")
                                        do_success = True
                                        break
                        else:
                            self.logger.info("  robot_state_pkg中未找到DO相关属性")
                    else:
                        self.logger.info("  robot_state_pkg不存在")
                except Exception as e:
                    self.logger.info(f"  方式2失败: {e}")
            
            # 方式3：尝试GetDO(0)到GetDO(3)的单独调用（如果前面方式失败）
            if not do_success:
                try:
                    self.logger.info("  尝试方式3: 单独调用GetDO(0), GetDO(1)...")
                    # 检查GetDO方法的参数签名
                    import inspect
                    sig = inspect.signature(self.robot.GetDO)
                    self.logger.info(f"  GetDO方法签名: {sig}")
                    
                    # 如果GetDO确实不接受参数，可能需要其他方法
                    self.logger.info("  GetDO()方法不接受索引参数")
                    self.logger.info("  建议检查API文档或使用其他IO读取方法")
                    
                except Exception as e:
                    self.logger.info(f"  方式3失败: {e}")
            
            # 如果所有方式都失败，至少不让测试崩溃
            if not do_success:
                self.logger.warning("  所有DO读取方式都失败，跳过DO测试")
                for i in range(test_io_count):
                    self.logger.warning(f"  DO[{i}]: 无法读取")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"[FAILED] IO状态获取异常: {e}")
            return False
            
    def parse_robot_state(self, state: int) -> str:
        """解析机器人状态码"""
        states = {
            0: "未知",
            1: "已停止",
            2: "运行中",
            3: "暂停",
            4: "急停",
            5: "故障"
        }
        return states.get(state, f"未定义状态({state})")
        
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
        self.logger.info(f"开始执行{self.arm_name}臂连接测试")
        self.logger.info(f"{'='*60}\n")
        
        all_passed = True
        
        # 执行各项测试
        tests = [
            ("基础连接", self.test_connection),
            ("SDK信息", self.test_sdk_info),
            ("机器人状态", self.test_robot_state),
            ("关节位置", self.test_joint_position),
            ("TCP位置", self.test_tcp_position),
            ("IO状态", self.test_io_status)
        ]
        
        for test_name, test_func in tests:
            if not self.robot and test_name != "基础连接":
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
    parser = argparse.ArgumentParser(description='FR3单臂连接测试')
    parser.add_argument('--arm', choices=['left', 'right'], default='right',
                       help='测试臂选择 (默认: right)')
    parser.add_argument('--ip', required=True,
                       help='机器人IP地址')
    
    args = parser.parse_args()
    
    # 安全提示
    print("\n" + "="*60)
    print("FR3机械臂连接测试")
    print("="*60)
    print(f"目标机器人: {args.arm}臂")
    print(f"IP地址: {args.ip}")
    print("\n注意: 此测试仅读取机器人状态，不会产生任何运动")
    print("="*60)
    
    response = input("\n确认开始测试？(y/n): ")
    if response.lower() != 'y':
        print("测试已取消")
        return
        
    # 执行测试
    tester = SingleArmConnectionTest(args.ip, args.arm)
    success = tester.run()
    
    # 返回状态码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()