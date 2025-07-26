#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAT001 Lua Dual Arm Synchronization Test
基于webapp lua调用的双臂同步测试

使用lua脚本实现双臂协调运动测试，替代传统的Python状态读取方式
"""

import time
import logging
import threading
from pathlib import Path
from fairino import Robot
from typing import Dict, Any, Optional, Tuple, List

class LuaDualArmSyncTest:
    """双臂Lua同步测试类"""
    
    def __init__(self, left_arm_ip: str = "192.168.58.3", right_arm_ip: str = "192.168.58.2"):
        """
        初始化双臂lua同步测试
        
        Args:
            left_arm_ip: 左臂机器人IP地址
            right_arm_ip: 右臂机器人IP地址
        """
        self.left_arm_ip = left_arm_ip
        self.right_arm_ip = right_arm_ip
        self.left_robot: Optional[Robot] = None
        self.right_robot: Optional[Robot] = None
        self.test_name = "DAT001_LUA_SYNC"
        
        # Lua脚本配置
        self.left_lua_script = "dat001_left_sync.lua"
        self.right_lua_script = "dat001_right_sync.lua"
        self.left_program_path = f"/fruser/{self.left_lua_script}"
        self.right_program_path = f"/fruser/{self.right_lua_script}"
        
        # 同步配置
        self.sync_timeout = 120  # 同步超时时间
        self.sync_check_interval = 0.1  # 同步检查间隔
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__name__)
        
        # 线程同步
        self.sync_barrier = threading.Barrier(2)
        self.execution_results = {}
        
    def _create_left_arm_lua_script(self) -> str:
        """创建左臂同步测试的lua脚本"""
        lua_script = """
-- DAT001 Left Arm Synchronization Test Script
-- 左臂同步测试lua脚本

function dual_arm_sync_test_left()
    TPWrite("Left arm sync test starting...")
    
    -- 获取初始关节位置
    local error, init_pos = GetActualJointPosDegree(0)
    if error ~= 0 then
        TPWrite("Failed to get initial position, error: " .. error)
        return false
    end
    
    TPWrite("Left arm initial position acquired")
    
    -- 同步点1: 准备运动
    TPWrite("Left arm ready for sync point 1")
    Sleep(1000)  -- 等待右臂准备
    
    -- 执行第一阶段运动 - 向上抬升
    local move1_joints = {init_pos[1], init_pos[2] - 10.0, init_pos[3], init_pos[4], init_pos[5], init_pos[6]}
    local move_error1 = MoveJTraj(0, move1_joints, 30.0, 30.0, 100.0, 0.0, 0.0, 1, 0)
    if move_error1 ~= 0 then
        TPWrite("Left arm movement 1 failed, error: " .. move_error1)
        return false
    end
    
    TPWrite("Left arm completed movement phase 1")
    Sleep(2000)  -- 等待运动完成
    
    -- 同步点2: 中间位置
    TPWrite("Left arm at sync point 2")
    Sleep(1000)
    
    -- 执行第二阶段运动 - 水平移动
    local move2_joints = {init_pos[1] + 15.0, move1_joints[2], init_pos[3], init_pos[4], init_pos[5], init_pos[6]}
    local move_error2 = MoveJTraj(0, move2_joints, 25.0, 25.0, 100.0, 0.0, 0.0, 1, 0)
    if move_error2 ~= 0 then
        TPWrite("Left arm movement 2 failed, error: " .. move_error2)
        return false
    end
    
    TPWrite("Left arm completed movement phase 2")
    Sleep(2000)
    
    -- 同步点3: 协作完成
    TPWrite("Left arm at sync point 3")
    Sleep(1000)
    
    -- 返回初始位置
    local return_error = MoveJTraj(0, init_pos, 20.0, 20.0, 100.0, 0.0, 0.0, 1, 0)
    if return_error ~= 0 then
        TPWrite("Left arm return movement failed, error: " .. return_error)
        return false
    end
    
    TPWrite("Left arm returned to initial position")
    TPWrite("Left arm sync test completed successfully")
    return true
end

-- 执行左臂同步测试
local result = dual_arm_sync_test_left()
TPWrite("Left arm sync test result: " .. tostring(result))
"""
        return lua_script
    
    def _create_right_arm_lua_script(self) -> str:
        """创建右臂同步测试的lua脚本"""
        lua_script = """
-- DAT001 Right Arm Synchronization Test Script
-- 右臂同步测试lua脚本

function dual_arm_sync_test_right()
    TPWrite("Right arm sync test starting...")
    
    -- 获取初始关节位置
    local error, init_pos = GetActualJointPosDegree(0)
    if error ~= 0 then
        TPWrite("Failed to get initial position, error: " .. error)
        return false
    end
    
    TPWrite("Right arm initial position acquired")
    
    -- 同步点1: 准备运动
    TPWrite("Right arm ready for sync point 1")
    Sleep(1000)  -- 等待左臂准备
    
    -- 执行第一阶段运动 - 向上抬升（与左臂对称）
    local move1_joints = {init_pos[1], init_pos[2] - 10.0, init_pos[3], init_pos[4], init_pos[5], init_pos[6]}
    local move_error1 = MoveJTraj(0, move1_joints, 30.0, 30.0, 100.0, 0.0, 0.0, 1, 0)
    if move_error1 ~= 0 then
        TPWrite("Right arm movement 1 failed, error: " .. move_error1)
        return false
    end
    
    TPWrite("Right arm completed movement phase 1")
    Sleep(2000)  -- 等待运动完成
    
    -- 同步点2: 中间位置
    TPWrite("Right arm at sync point 2")
    Sleep(1000)
    
    -- 执行第二阶段运动 - 水平移动（与左臂相反方向）
    local move2_joints = {init_pos[1] - 15.0, move1_joints[2], init_pos[3], init_pos[4], init_pos[5], init_pos[6]}
    local move_error2 = MoveJTraj(0, move2_joints, 25.0, 25.0, 100.0, 0.0, 0.0, 1, 0)
    if move_error2 ~= 0 then
        TPWrite("Right arm movement 2 failed, error: " .. move_error2)
        return false
    end
    
    TPWrite("Right arm completed movement phase 2")
    Sleep(2000)
    
    -- 同步点3: 协作完成
    TPWrite("Right arm at sync point 3")
    Sleep(1000)
    
    -- 返回初始位置
    local return_error = MoveJTraj(0, init_pos, 20.0, 20.0, 100.0, 0.0, 0.0, 1, 0)
    if return_error ~= 0 then
        TPWrite("Right arm return movement failed, error: " .. return_error)
        return false
    end
    
    TPWrite("Right arm returned to initial position")
    TPWrite("Right arm sync test completed successfully")
    return true
end

-- 执行右臂同步测试
local result = dual_arm_sync_test_right()
TPWrite("Right arm sync test result: " .. tostring(result))
"""
        return lua_script
    
    def connect_robots(self) -> Tuple[bool, bool]:
        """连接到双臂机器人"""
        left_connected = False
        right_connected = False
        
        try:
            # 连接左臂
            self.logger.info(f"正在连接左臂机器人: {self.left_arm_ip}")
            self.left_robot = Robot.RPC(self.left_arm_ip)
            error, version = self.left_robot.GetSDKVersion()
            if error == 0:
                self.logger.info(f"左臂连接成功，SDK版本: {version}")
                left_connected = True
            else:
                self.logger.error(f"左臂连接失败，错误码: {error}")
            
            # 连接右臂
            self.logger.info(f"正在连接右臂机器人: {self.right_arm_ip}")
            self.right_robot = Robot.RPC(self.right_arm_ip)
            error, version = self.right_robot.GetSDKVersion()
            if error == 0:
                self.logger.info(f"右臂连接成功，SDK版本: {version}")
                right_connected = True
            else:
                self.logger.error(f"右臂连接失败，错误码: {error}")
                
        except Exception as e:
            self.logger.error(f"连接机器人时发生异常: {str(e)}")
        
        return left_connected, right_connected
    
    def upload_lua_scripts(self) -> Tuple[bool, bool]:
        """上传双臂lua脚本"""
        left_uploaded = False
        right_uploaded = False
        
        try:
            # 上传左臂脚本
            left_script_content = self._create_left_arm_lua_script()
            left_temp_path = Path(f"/tmp/{self.left_lua_script}")
            
            with open(left_temp_path, 'w', encoding='utf-8') as f:
                f.write(left_script_content)
            
            self.logger.info(f"正在上传左臂lua脚本: {self.left_lua_script}")
            error = self.left_robot.LuaUpload(filePath=str(left_temp_path))
            if error == 0:
                self.logger.info("左臂Lua脚本上传成功")
                left_uploaded = True
                left_temp_path.unlink()
            else:
                self.logger.error(f"左臂Lua脚本上传失败，错误码: {error}")
            
            # 上传右臂脚本
            right_script_content = self._create_right_arm_lua_script()
            right_temp_path = Path(f"/tmp/{self.right_lua_script}")
            
            with open(right_temp_path, 'w', encoding='utf-8') as f:
                f.write(right_script_content)
            
            self.logger.info(f"正在上传右臂lua脚本: {self.right_lua_script}")
            error = self.right_robot.LuaUpload(filePath=str(right_temp_path))
            if error == 0:
                self.logger.info("右臂Lua脚本上传成功")
                right_uploaded = True
                right_temp_path.unlink()
            else:
                self.logger.error(f"右臂Lua脚本上传失败，错误码: {error}")
                
        except Exception as e:
            self.logger.error(f"上传lua脚本时发生异常: {str(e)}")
        
        return left_uploaded, right_uploaded
    
    def _monitor_arm_execution(self, robot: Robot, arm_name: str, program_path: str) -> Dict[str, Any]:
        """监控单臂程序执行"""
        start_time = time.time()
        execution_log = []
        
        try:
            # 加载并运行程序
            robot.Mode(state=0)
            error = robot.ProgramLoad(program_name=program_path)
            if error != 0:
                return {
                    'success': False,
                    'error': f'Program load failed: {error}',
                    'arm': arm_name
                }
            
            # 运行程序
            error = robot.ProgramRun()
            if error != 0:
                return {
                    'success': False,
                    'error': f'Program run failed: {error}',
                    'arm': arm_name
                }
            
            self.logger.info(f"{arm_name}开始执行lua程序")
            
            # 监控执行
            while time.time() - start_time < self.sync_timeout:
                error, state = robot.GetProgramState()
                if error != 0:
                    self.logger.error(f"{arm_name}获取程序状态失败，错误码: {error}")
                    break
                
                line_error, current_line = robot.GetCurrentLine()
                if line_error == 0:
                    execution_info = {
                        'timestamp': time.time(),
                        'state': state,
                        'line': current_line,
                        'arm': arm_name
                    }
                    execution_log.append(execution_info)
                    self.logger.info(f"{arm_name} - 状态: {state}, 行: {current_line}")
                
                if state in ["completed", "stopped", "error"]:
                    self.logger.info(f"{arm_name}程序执行结束，状态: {state}")
                    break
                
                time.sleep(self.sync_check_interval)
            
            return {
                'success': state == "completed",
                'final_state': state,
                'execution_log': execution_log,
                'duration': time.time() - start_time,
                'arm': arm_name
            }
            
        except Exception as e:
            self.logger.error(f"{arm_name}监控执行时发生异常: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'execution_log': execution_log,
                'duration': time.time() - start_time,
                'arm': arm_name
            }
    
    def execute_synchronized_test(self) -> Dict[str, Any]:
        """执行同步测试"""
        def left_arm_thread():
            """左臂执行线程"""
            self.execution_results['left'] = self._monitor_arm_execution(
                self.left_robot, "左臂", self.left_program_path
            )
        
        def right_arm_thread():
            """右臂执行线程"""
            self.execution_results['right'] = self._monitor_arm_execution(
                self.right_robot, "右臂", self.right_program_path
            )
        
        # 创建并启动线程
        left_thread = threading.Thread(target=left_arm_thread)
        right_thread = threading.Thread(target=right_arm_thread)
        
        self.logger.info("开始同步执行双臂lua程序")
        
        # 同时启动两个线程
        left_thread.start()
        right_thread.start()
        
        # 等待两个线程完成
        left_thread.join()
        right_thread.join()
        
        return self.execution_results
    
    def analyze_synchronization(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析同步性能"""
        sync_analysis = {
            'time_difference': 0,
            'synchronized': False,
            'sync_quality': 'poor',
            'phase_sync': {}
        }
        
        try:
            left_result = execution_results.get('left', {})
            right_result = execution_results.get('right', {})
            
            if not (left_result.get('success') and right_result.get('success')):
                sync_analysis['synchronized'] = False
                sync_analysis['error'] = "One or both arms failed to complete"
                return sync_analysis
            
            # 计算执行时间差异
            left_duration = left_result.get('duration', 0)
            right_duration = right_result.get('duration', 0)
            sync_analysis['time_difference'] = abs(left_duration - right_duration)
            
            # 判断同步质量
            if sync_analysis['time_difference'] < 1.0:  # 1秒内
                sync_analysis['sync_quality'] = 'excellent'
                sync_analysis['synchronized'] = True
            elif sync_analysis['time_difference'] < 3.0:  # 3秒内
                sync_analysis['sync_quality'] = 'good'
                sync_analysis['synchronized'] = True
            elif sync_analysis['time_difference'] < 5.0:  # 5秒内
                sync_analysis['sync_quality'] = 'fair'
                sync_analysis['synchronized'] = True
            else:
                sync_analysis['sync_quality'] = 'poor'
                sync_analysis['synchronized'] = False
            
            # 分析执行日志中的同步点
            left_log = left_result.get('execution_log', [])
            right_log = right_result.get('execution_log', [])
            
            sync_analysis['left_phases'] = len([log for log in left_log if 'sync point' in str(log)])
            sync_analysis['right_phases'] = len([log for log in right_log if 'sync point' in str(log)])
            
            self.logger.info(f"同步分析完成 - 时间差: {sync_analysis['time_difference']:.2f}s, 质量: {sync_analysis['sync_quality']}")
            
        except Exception as e:
            sync_analysis['error'] = str(e)
            self.logger.error(f"同步分析时发生异常: {str(e)}")
        
        return sync_analysis
    
    def cleanup_resources(self):
        """清理资源"""
        try:
            if self.left_robot:
                self.left_robot.StopMotion()
                delete_error = self.left_robot.LuaDelete(fileName=self.left_lua_script)
                if delete_error == 0:
                    self.logger.info("左臂Lua脚本清理成功")
            
            if self.right_robot:
                self.right_robot.StopMotion()
                delete_error = self.right_robot.LuaDelete(fileName=self.right_lua_script)
                if delete_error == 0:
                    self.logger.info("右臂Lua脚本清理成功")
        
        except Exception as e:
            self.logger.warning(f"清理资源时发生异常: {str(e)}")
    
    def run_test(self) -> Dict[str, Any]:
        """运行完整的双臂同步lua测试"""
        test_result = {
            'test_name': self.test_name,
            'left_arm_ip': self.left_arm_ip,
            'right_arm_ip': self.right_arm_ip,
            'start_time': time.time(),
            'success': False,
            'stages': {},
            'error_message': None,
            'sync_analysis': {}
        }
        
        try:
            # 阶段1: 连接双臂机器人
            self.logger.info("开始DAT001双臂Lua同步测试")
            left_connected, right_connected = self.connect_robots()
            if not (left_connected and right_connected):
                test_result['error_message'] = f"机器人连接失败 - 左臂: {left_connected}, 右臂: {right_connected}"
                return test_result
            test_result['stages']['connection'] = {'left': left_connected, 'right': right_connected}
            
            # 阶段2: 上传lua脚本
            left_uploaded, right_uploaded = self.upload_lua_scripts()
            if not (left_uploaded and right_uploaded):
                test_result['error_message'] = f"Lua脚本上传失败 - 左臂: {left_uploaded}, 右臂: {right_uploaded}"
                return test_result
            test_result['stages']['upload'] = {'left': left_uploaded, 'right': right_uploaded}
            
            # 阶段3: 执行同步测试
            execution_results = self.execute_synchronized_test()
            test_result['stages']['execution'] = execution_results
            
            # 阶段4: 分析同步性能
            sync_analysis = self.analyze_synchronization(execution_results)
            test_result['sync_analysis'] = sync_analysis
            
            # 判断总体测试结果
            test_result['success'] = sync_analysis.get('synchronized', False)
            if not test_result['success']:
                test_result['error_message'] = f"同步测试失败: {sync_analysis.get('error', '同步质量不达标')}"
            
        except Exception as e:
            test_result['error_message'] = f"测试过程发生异常: {str(e)}"
            self.logger.error(f"测试异常: {str(e)}")
        
        finally:
            # 清理资源
            self.cleanup_resources()
            test_result['end_time'] = time.time()
            test_result['duration'] = test_result['end_time'] - test_result['start_time']
        
        return test_result


def main():
    """主函数 - 独立运行测试"""
    print("=== DAT001 双臂Lua同步测试 ===")
    
    # 创建测试实例
    test = LuaDualArmSyncTest(
        left_arm_ip="192.168.58.3",
        right_arm_ip="192.168.58.2"
    )
    
    # 运行测试
    result = test.run_test()
    
    # 打印结果
    print(f"\n测试结果:")
    print(f"测试名称: {result['test_name']}")
    print(f"左臂IP: {result['left_arm_ip']}")
    print(f"右臂IP: {result['right_arm_ip']}")
    print(f"测试状态: {'通过' if result['success'] else '失败'}")
    print(f"总执行时间: {result['duration']:.2f}秒")
    
    if not result['success']:
        print(f"错误信息: {result['error_message']}")
    
    # 打印同步分析结果
    if 'sync_analysis' in result:
        sync_analysis = result['sync_analysis']
        print(f"\n同步分析:")
        print(f"同步状态: {'成功' if sync_analysis.get('synchronized', False) else '失败'}")
        print(f"时间差异: {sync_analysis.get('time_difference', 0):.2f}秒")
        print(f"同步质量: {sync_analysis.get('sync_quality', 'unknown')}")
    
    return result


if __name__ == "__main__":
    main()