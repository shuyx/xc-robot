#!/usr/bin/env python3
"""
单臂连接测试脚本
测试ID: SAT-001
测试目的: 验证与FR3机械臂的网络连接和SDK通信
"""

import sys
import time
import logging
import argparse
from typing import Optional, Dict, Any

# 添加项目路径
sys.path.append('..')
from fr3_control.fairino.Robot import Robot

class SingleArmConnectionTest:
    def __init__(self, robot_ip: str, arm_name: str = "right"):
        self.robot_ip = robot_ip
        self.arm_name = arm_name
        self.test_id = "SAT-001"
        self.robot: Optional[Robot] = None
        self.test_results: Dict[str, Any] = {}
        self.setup_logging()
        
    def setup_logging(self):
        """配置日志系统"""
        log_filename = f'logs/{self.test_id}_{self.arm_name}_{time.strftime("%Y%m%d_%H%M%S")}.log'
        
        # 创建logs目录
        import os
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s] %(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
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
            
            self.robot = Robot(self.robot_ip)
            
            connection_time = time.time() - start_time
            self.logger.info(f"✓ 连接成功！耗时: {connection_time:.3f}秒")
            
            self.test_results['connection'] = {
                'status': 'PASSED',
                'time': connection_time
            }
            return True
            
        except Exception as e:
            self.logger.error(f"✗ 连接失败: {e}")
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
                self.logger.info(f"✓ SDK版本: {version}")
                self.test_results['sdk_version'] = version
            else:
                self.logger.error(f"✗ 获取SDK版本失败，错误码: {error}")
                return False
                
            # 获取控制器IP
            error, controller_ip = self.robot.GetControllerIP()
            if error == 0:
                self.logger.info(f"✓ 控制器IP: {controller_ip}")
                self.test_results['controller_ip'] = controller_ip
            else:
                self.logger.error(f"✗ 获取控制器IP失败，错误码: {error}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"✗ SDK信息获取异常: {e}")
            return False
            
    def test_robot_state(self) -> bool:
        """测试机器人状态获取"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("测试3: 机器人状态获取")
        self.logger.info("=" * 50)
        
        try:
            # 获取机器人状态
            error, state = self.robot.GetRobotState()
            if error == 0:
                state_desc = self.parse_robot_state(state)
                self.logger.info(f"✓ 机器人状态: {state_desc}")
                self.test_results['robot_state'] = state_desc
            else:
                self.logger.error(f"✗ 获取机器人状态失败，错误码: {error}")
                return False
                
            # 获取机器人模式
            error, mode = self.robot.Mode()
            if error == 0:
                mode_desc = {0: "自动模式", 1: "手动模式"}.get(mode, f"未知模式({mode})")
                self.logger.info(f"✓ 机器人模式: {mode_desc}")
                self.test_results['robot_mode'] = mode_desc
            else:
                self.logger.error(f"✗ 获取机器人模式失败，错误码: {error}")
                
            # 检查错误状态
            error, error_code = self.robot.GetRobotErrorCode()
            if error == 0:
                if error_code:
                    self.logger.warning(f"⚠ 机器人错误代码: {error_code}")
                else:
                    self.logger.info("✓ 机器人无错误")
                self.test_results['error_code'] = error_code
                
            return True
            
        except Exception as e:
            self.logger.error(f"✗ 状态获取异常: {e}")
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
                self.logger.info("✓ 当前关节角度 (度):")
                for i, angle in enumerate(joints):
                    self.logger.info(f"  关节{i+1}: {angle:.3f}°")
                self.test_results['joint_positions'] = joints
            else:
                self.logger.error(f"✗ 获取关节角度失败，错误码: {error}")
                return False
                
            # 获取关节速度
            error, speeds = self.robot.GetActualJointSpeedsDegree()
            if error == 0:
                self.logger.info("✓ 当前关节速度 (度/秒):")
                for i, speed in enumerate(speeds):
                    self.logger.info(f"  关节{i+1}: {speed:.3f}°/s")
                self.test_results['joint_speeds'] = speeds
                
            return True
            
        except Exception as e:
            self.logger.error(f"✗ 关节位置获取异常: {e}")
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
                self.logger.info("✓ 当前TCP位姿:")
                self.logger.info(f"  位置 X: {tcp_pose[0]:.3f} mm")
                self.logger.info(f"  位置 Y: {tcp_pose[1]:.3f} mm")
                self.logger.info(f"  位置 Z: {tcp_pose[2]:.3f} mm")
                self.logger.info(f"  姿态 Rx: {tcp_pose[3]:.3f}°")
                self.logger.info(f"  姿态 Ry: {tcp_pose[4]:.3f}°")
                self.logger.info(f"  姿态 Rz: {tcp_pose[5]:.3f}°")
                self.test_results['tcp_pose'] = tcp_pose
            else:
                self.logger.error(f"✗ 获取TCP位姿失败，错误码: {error}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"✗ TCP位置获取异常: {e}")
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
            for i in range(test_io_count):
                error, value = self.robot.GetDO(i)
                if error == 0:
                    status = "ON" if value else "OFF"
                    self.logger.info(f"  DO[{i}]: {status}")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"✗ IO状态获取异常: {e}")
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
            self.logger.info("✓ 所有测试通过！")
        else:
            self.logger.warning("⚠ 部分测试未通过，请检查日志")
        self.logger.info(f"{'='*60}\n")
        
        return all_passed

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