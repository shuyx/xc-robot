#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂控制参数稳定性测试脚本
基于 servocart正确调参（慢速版）.md 的最佳实践
测试不同参数组合的成功率和精度
"""

import sys
import os
import time
import numpy as np

# 添加FR3控制库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.insert(0, fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")
    sys.exit(1)

try:
    from fairino import Robot
    print("✅ fairino库导入成功")
except ImportError as e:
    print(f"❌ fairino库导入失败: {e}")
    sys.exit(1)

class RobotStabilityTester:
    def __init__(self):
        self.robot = None
        self.test_results = []
        
        # 测试参数组合（基于文档推荐）
        self.test_configs = [
            # 配置1：文档推荐的最佳参数
            {
                "name": "文档推荐（最佳）",
                "steps_per_mm": 0.5,  # 每2mm一个点
                "servo_speed": 5.0,   # 最低安全速度
                "cycle_time": 0.020,  # 20ms周期
                "interpolation": "quintic"  # 五次多项式
            },
            
            # 配置2：更保守的参数
            {
                "name": "保守参数",
                "steps_per_mm": 1.0,  # 每1mm一个点
                "servo_speed": 5.0,
                "cycle_time": 0.025,  # 25ms周期
                "interpolation": "quintic"
            },
            
            # 配置3：稍快的参数
            {
                "name": "稍快参数",
                "steps_per_mm": 0.3,  # 每3.3mm一个点
                "servo_speed": 7.0,
                "cycle_time": 0.015,  # 15ms周期
                "interpolation": "quintic"
            },
            
            # 配置4：线性插值对比
            {
                "name": "线性插值对比",
                "steps_per_mm": 0.5,
                "servo_speed": 5.0,
                "cycle_time": 0.020,
                "interpolation": "linear"
            }
        ]
    
    def connect_robot(self):
        """连接机械臂"""
        print("🔗 正在连接机械臂...")
        
        try:
            self.robot = Robot.RPC('192.168.58.2')
            
            if not hasattr(self.robot, 'is_conect') or not self.robot.is_conect:
                print("❌ 连接失败")
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
            
            time.sleep(1.5)
            return True
            
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    def test_servo_motion(self, config, test_distance=100.0):
        """测试特定配置的ServoCart运动"""
        print(f"\n{'='*50}")
        print(f"🧪 测试配置: {config['name']}")
        print(f"{'='*50}")
        
        try:
            # 获取当前TCP位置
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error != 0:
                print(f"❌ 获取TCP位置失败，错误码: {error}")
                return None
            
            print(f"起始TCP位置: X={current_tcp[0]:.1f}, Y={current_tcp[1]:.1f}, Z={current_tcp[2]:.1f}")
            
            # 计算目标位置（Z轴负方向移动test_distance）
            target_tcp = current_tcp.copy()
            target_tcp[2] = current_tcp[2] - test_distance
            
            print(f"目标TCP位置: X={target_tcp[0]:.1f}, Y={target_tcp[1]:.1f}, Z={target_tcp[2]:.1f}")
            print(f"测试移动距离: {test_distance:.1f}mm")
            
            # 执行运动并记录结果
            result = self._execute_servo_motion(current_tcp, target_tcp, test_distance, config)
            
            if result:
                # 返回起始位置
                print(f"\n🔄 返回起始位置...")
                return_result = self._execute_servo_motion(target_tcp, current_tcp, test_distance, config)
                result['return_success'] = return_result is not None
            
            return result
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return None
    
    def _execute_servo_motion(self, start_pos, target_pos, distance_mm, config):
        """执行ServoCart运动并统计结果"""
        
        # 计算参数
        steps = max(50, int(distance_mm * config['steps_per_mm']))
        servo_speed = config['servo_speed']
        cycle_time = config['cycle_time']
        
        print(f"参数配置:")
        print(f"  轨迹点数: {steps}")
        print(f"  伺服速度: {servo_speed}")
        print(f"  周期时间: {cycle_time*1000:.0f}ms")
        print(f"  插值方式: {config['interpolation']}")
        
        # 启动伺服模式
        start_time = time.time()
        ret = self.robot.ServoMoveStart()
        if ret != 0:
            print(f"❌ 伺服运动开始失败，错误码: {ret}")
            return None
        
        # 执行轨迹
        success_count = 0
        error_codes = {}
        
        for i in range(steps + 1):
            t = i / steps
            
            # 选择插值方式
            if config['interpolation'] == 'quintic':
                # 五次多项式插值
                if t <= 0.0:
                    t_smooth = 0.0
                elif t >= 1.0:
                    t_smooth = 1.0
                else:
                    t_smooth = 6 * t**5 - 15 * t**4 + 10 * t**3
            else:
                # 线性插值
                t_smooth = t
            
            # 计算插值位置
            interpolated_pos = []
            for j in range(6):
                value = start_pos[j] + t_smooth * (target_pos[j] - start_pos[j])
                interpolated_pos.append(value)
            
            # 发送伺服指令
            ret = self.robot.ServoCart(mode=0, desc_pos=interpolated_pos, vel=servo_speed)
            
            if ret == 0:
                success_count += 1
            else:
                if ret not in error_codes:
                    error_codes[ret] = 0
                error_codes[ret] += 1
                
                if i % 20 == 0:
                    print(f"⚠️ 轨迹点 {i} 执行失败，错误码: {ret}")
            
            time.sleep(cycle_time)
        
        # 结束伺服模式
        ret = self.robot.ServoMoveEnd()
        end_time = time.time()
        
        # 计算统计信息
        total_time = end_time - start_time
        success_rate = success_count / (steps + 1) * 100
        
        print(f"\n📊 执行结果:")
        print(f"  总时间: {total_time:.2f}秒")
        print(f"  成功率: {success_rate:.1f}% ({success_count}/{steps + 1})")
        
        if error_codes:
            print(f"  错误统计:")
            for code, count in error_codes.items():
                print(f"    错误码{code}: {count}次")
        
        # 验证位置精度
        time.sleep(0.5)
        error, final_tcp = self.robot.GetActualToolFlangePose()
        position_error = None
        
        if error == 0:
            position_error = abs(final_tcp[2] - target_pos[2])
            print(f"  位置误差: {position_error:.1f}mm")
            
            if position_error < 5.0:
                print("  ✅ 精度良好")
            elif position_error < 15.0:
                print("  ⚠️ 精度一般")
            else:
                print("  ❌ 精度较差")
        
        return {
            'config_name': config['name'],
            'success_rate': success_rate,
            'total_time': total_time,
            'position_error': position_error,
            'error_codes': error_codes,
            'steps': steps
        }
    
    def run_comprehensive_test(self):
        """运行综合稳定性测试"""
        print("🚀 机械臂控制参数稳定性测试")
        print("🎯 目标：验证不同参数组合的成功率和精度")
        print("📏 测试距离：100mm Z轴负方向移动")
        
        if not self.connect_robot():
            return False
        
        print(f"\n将测试 {len(self.test_configs)} 种参数配置...")
        
        for i, config in enumerate(self.test_configs):
            print(f"\n{'🔸' * 20} 测试 {i+1}/{len(self.test_configs)} {'🔸' * 20}")
            
            # 等待用户确认
            confirm = input(f"\n准备测试 '{config['name']}' 配置，按回车继续或输入'q'退出: ").strip()
            if confirm.lower() == 'q':
                print("🛑 用户取消测试")
                break
            
            result = self.test_servo_motion(config)
            if result:
                self.test_results.append(result)
                print(f"✅ '{config['name']}' 测试完成")
            else:
                print(f"❌ '{config['name']}' 测试失败")
            
            # 短暂休息
            if i < len(self.test_configs) - 1:
                print("⏳ 等待5秒后进行下一组测试...")
                time.sleep(5)
        
        # 生成测试报告
        self.generate_test_report()
        return True
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*70)
        print("📊 机械臂控制参数稳定性测试报告")
        print("="*70)
        
        if not self.test_results:
            print("❌ 没有可用的测试结果")
            return
        
        # 按成功率排序
        sorted_results = sorted(self.test_results, key=lambda x: x['success_rate'], reverse=True)
        
        print(f"\n🏆 性能排名（按成功率）:")
        print("-" * 70)
        print(f"{'排名':<4} {'配置名称':<15} {'成功率':<8} {'时间':<8} {'误差':<8} {'步数':<6}")
        print("-" * 70)
        
        for rank, result in enumerate(sorted_results, 1):
            error_str = f"{result['position_error']:.1f}mm" if result['position_error'] is not None else "N/A"
            print(f"{rank:<4} {result['config_name']:<15} {result['success_rate']:<7.1f}% "
                  f"{result['total_time']:<7.2f}s {error_str:<8} {result['steps']:<6}")
        
        # 详细分析
        print(f"\n📈 详细分析:")
        best_config = sorted_results[0]
        print(f"🥇 最佳配置: {best_config['config_name']}")
        print(f"   成功率: {best_config['success_rate']:.1f}%")
        print(f"   位置误差: {best_config['position_error']:.1f}mm" if best_config['position_error'] else "   位置误差: 未知")
        print(f"   执行时间: {best_config['total_time']:.2f}秒")
        
        # 错误分析
        print(f"\n⚠️ 错误统计:")
        all_errors = {}
        for result in sorted_results:
            for code, count in result['error_codes'].items():
                if code not in all_errors:
                    all_errors[code] = []
                all_errors[code].append((result['config_name'], count))
        
        if all_errors:
            for error_code, occurrences in all_errors.items():
                print(f"   错误码{error_code}:")
                for config_name, count in occurrences:
                    print(f"     {config_name}: {count}次")
        else:
            print("   🎉 所有配置都没有错误！")
        
        # 推荐建议
        print(f"\n💡 推荐建议:")
        high_success_configs = [r for r in sorted_results if r['success_rate'] >= 90]
        
        if high_success_configs:
            print(f"   ✅ 推荐使用以下配置（成功率≥90%）:")
            for config in high_success_configs:
                print(f"     • {config['config_name']} (成功率: {config['success_rate']:.1f}%)")
        else:
            print(f"   ⚠️ 所有配置成功率都低于90%，建议进一步优化参数")
        
        low_error_configs = [r for r in sorted_results if r['position_error'] and r['position_error'] < 5.0]
        if low_error_configs:
            print(f"   🎯 高精度配置（误差<5mm）:")
            for config in low_error_configs:
                print(f"     • {config['config_name']} (误差: {config['position_error']:.1f}mm)")
    
    def cleanup(self):
        """清理资源"""
        if self.robot:
            try:
                self.robot.ServoMoveEnd()
                self.robot.RobotEnable(0)
                self.robot.CloseRPC()
                print("✅ 机械臂连接已关闭")
            except:
                pass

def main():
    tester = RobotStabilityTester()
    
    try:
        print("🧪 机械臂控制参数稳定性测试程序")
        print("📋 基于 servocart正确调参（慢速版）.md 的最佳实践")
        
        confirm = input("\n确认开始稳定性测试？这将进行多组移动测试 (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 测试已取消")
            return 1
        
        success = tester.run_comprehensive_test()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断测试")
        return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 程序终止")
        sys.exit(1)