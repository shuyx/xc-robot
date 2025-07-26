#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Lua Full System Test
基于webapp lua调用的全系统集成测试

整合FR3双臂、Hermes底盘、视觉系统、夹爪的完整lua测试
"""

import time
import logging
import threading
import socket
import json
from pathlib import Path
from fairino import Robot
from typing import Dict, Any, Optional, Tuple, List

class LuaFullSystemTest:
    """全系统Lua集成测试类"""
    
    def __init__(self, 
                 left_arm_ip: str = "192.168.58.3",
                 right_arm_ip: str = "192.168.58.2", 
                 chassis_ip: str = "192.168.31.211",
                 chassis_port: int = 1448):
        """
        初始化全系统lua集成测试
        
        Args:
            left_arm_ip: 左臂机器人IP地址
            right_arm_ip: 右臂机器人IP地址
            chassis_ip: Hermes底盘IP地址
            chassis_port: 底盘通信端口
        """
        self.left_arm_ip = left_arm_ip
        self.right_arm_ip = right_arm_ip
        self.chassis_ip = chassis_ip
        self.chassis_port = chassis_port
        
        # 机器人连接
        self.left_robot: Optional[Robot] = None
        self.right_robot: Optional[Robot] = None
        self.chassis_socket: Optional[socket.socket] = None
        
        # 测试配置
        self.test_name = "INTEGRATION_LUA_FULL"
        self.lua_scripts = {
            'left_arm': 'integration_left_arm.lua',
            'right_arm': 'integration_right_arm.lua',
            'coordination': 'integration_coordination.lua'
        }
        
        # 集成测试场景
        self.test_scenarios = [
            {
                'name': 'system_initialization',
                'description': '系统初始化检查',
                'components': ['left_arm', 'right_arm', 'chassis', 'vision']
            },
            {
                'name': 'dual_arm_pickup',
                'description': '双臂协作抓取',
                'components': ['left_arm', 'right_arm', 'vision', 'gripper']
            },
            {
                'name': 'mobile_manipulation',
                'description': '移动操作',
                'components': ['chassis', 'left_arm', 'vision']
            },
            {
                'name': 'collaborative_assembly',
                'description': '协作装配',
                'components': ['left_arm', 'right_arm', 'chassis', 'vision', 'gripper']
            }
        ]
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__name__)
        
        # 线程同步
        self.component_results = {}
        self.scenario_lock = threading.Lock()
        
    def _create_integration_left_arm_script(self) -> str:
        """创建左臂集成测试的lua脚本"""
        lua_script = """
-- Integration Test - Left Arm Script
-- 左臂集成测试lua脚本

function integration_left_arm_test()
    TPWrite("Starting left arm integration test...")
    
    local test_results = {
        initialization = false,
        vision_coordination = false,
        pickup_operation = false,
        assembly_support = false,
        error_recovery = false
    }
    
    -- 1. 初始化检查
    TPWrite("Left arm: Performing initialization check...")
    local error, version = GetSDKVersion()
    if error == 0 then
        test_results.initialization = true
        TPWrite("Left arm initialized successfully, SDK: " .. version)
    else
        TPWrite("Left arm initialization failed, error: " .. error)
        return test_results
    end
    
    -- 获取初始位置
    local pos_error, home_pos = GetActualJointPosDegree(0)
    if pos_error ~= 0 then
        TPWrite("Failed to get left arm home position")
        return test_results
    end
    
    -- 2. 视觉协调测试
    TPWrite("Left arm: Testing vision coordination...")
    -- 移动到视觉观察位置
    local vision_pos = {home_pos[1] + 20.0, home_pos[2] - 15.0, home_pos[3] + 10.0, 
                       home_pos[4], home_pos[5], home_pos[6]}
    local vision_error = MoveJTraj(0, vision_pos, 25.0, 25.0, 100.0, 0.0, 0.0, 1, 0)
    if vision_error == 0 then
        test_results.vision_coordination = true
        TPWrite("Left arm vision coordination successful")
        Sleep(2000)  -- 模拟视觉处理时间
    else
        TPWrite("Left arm vision coordination failed, error: " .. vision_error)
    end
    
    -- 3. 抓取操作测试
    TPWrite("Left arm: Testing pickup operation...")
    local pickup_pos = {home_pos[1] + 10.0, home_pos[2] + 20.0, home_pos[3] - 5.0,
                       home_pos[4], home_pos[5], home_pos[6]}
    local pickup_error = MoveJTraj(0, pickup_pos, 20.0, 20.0, 100.0, 0.0, 0.0, 1, 0)
    if pickup_error == 0 then
        TPWrite("Left arm pickup position reached")
        -- 模拟夹爪操作
        Sleep(1000)
        test_results.pickup_operation = true
        TPWrite("Left arm pickup operation completed")
    else
        TPWrite("Left arm pickup operation failed, error: " .. pickup_error)
    end
    
    -- 4. 装配支持测试
    TPWrite("Left arm: Testing assembly support...")
    local assembly_pos = {home_pos[1] - 5.0, home_pos[2] + 10.0, home_pos[3] + 15.0,
                         home_pos[4] + 10.0, home_pos[5], home_pos[6]}
    local assembly_error = MoveJTraj(0, assembly_pos, 15.0, 15.0, 100.0, 0.0, 0.0, 1, 0)
    if assembly_error == 0 then
        test_results.assembly_support = true
        TPWrite("Left arm assembly support successful")
        Sleep(1500)
    else
        TPWrite("Left arm assembly support failed, error: " .. assembly_error)
    end
    
    -- 5. 错误恢复测试
    TPWrite("Left arm: Testing error recovery...")
    -- 故意执行一个可能失败的操作然后恢复
    local recovery_error = StopMotion()
    if recovery_error == 0 then
        Sleep(500)
        -- 恢复到安全位置
        local safe_error = MoveJTraj(0, home_pos, 10.0, 10.0, 100.0, 0.0, 0.0, 1, 0)
        if safe_error == 0 then
            test_results.error_recovery = true
            TPWrite("Left arm error recovery successful")
        end
    end
    
    TPWrite("Left arm integration test completed")
    return test_results
end

-- 执行左臂集成测试
local results = integration_left_arm_test()
TPWrite("Left arm integration results:")
for key, value in pairs(results) do
    TPWrite("  " .. key .. ": " .. tostring(value))
end
"""
        return lua_script
    
    def _create_integration_right_arm_script(self) -> str:
        """创建右臂集成测试的lua脚本"""
        lua_script = """
-- Integration Test - Right Arm Script
-- 右臂集成测试lua脚本

function integration_right_arm_test()
    TPWrite("Starting right arm integration test...")
    
    local test_results = {
        initialization = false,
        coordination_sync = false,
        precision_operation = false,
        collaborative_work = false,
        safety_monitoring = false
    }
    
    -- 1. 初始化检查
    TPWrite("Right arm: Performing initialization check...")
    local error, version = GetSDKVersion()
    if error == 0 then
        test_results.initialization = true
        TPWrite("Right arm initialized successfully, SDK: " .. version)
    else
        TPWrite("Right arm initialization failed, error: " .. error)
        return test_results
    end
    
    -- 获取初始位置
    local pos_error, home_pos = GetActualJointPosDegree(0)
    if pos_error ~= 0 then
        TPWrite("Failed to get right arm home position")
        return test_results
    end
    
    -- 2. 协调同步测试
    TPWrite("Right arm: Testing coordination sync...")
    -- 与左臂的同步运动
    local sync_pos = {home_pos[1] - 20.0, home_pos[2] - 15.0, home_pos[3] + 10.0,
                     home_pos[4], home_pos[5], home_pos[6]}
    local sync_error = MoveJTraj(0, sync_pos, 25.0, 25.0, 100.0, 0.0, 0.0, 1, 0)
    if sync_error == 0 then
        test_results.coordination_sync = true
        TPWrite("Right arm coordination sync successful")
        Sleep(2000)  -- 与左臂同步等待
    else
        TPWrite("Right arm coordination sync failed, error: " .. sync_error)
    end
    
    -- 3. 精密操作测试
    TPWrite("Right arm: Testing precision operation...")
    local precision_pos = {home_pos[1] - 10.0, home_pos[2] + 25.0, home_pos[3] - 8.0,
                          home_pos[4] + 5.0, home_pos[5] - 5.0, home_pos[6]}
    local precision_error = MoveJTraj(0, precision_pos, 10.0, 10.0, 100.0, 0.0, 0.0, 1, 0)
    if precision_error == 0 then
        TPWrite("Right arm precision position reached")
        -- 模拟精密操作
        Sleep(2000)
        test_results.precision_operation = true
        TPWrite("Right arm precision operation completed")
    else
        TPWrite("Right arm precision operation failed, error: " .. precision_error)
    end
    
    -- 4. 协作工作测试
    TPWrite("Right arm: Testing collaborative work...")
    local collab_pos = {home_pos[1] + 5.0, home_pos[2] + 10.0, home_pos[3] + 15.0,
                       home_pos[4] - 10.0, home_pos[5], home_pos[6]}
    local collab_error = MoveJTraj(0, collab_pos, 15.0, 15.0, 100.0, 0.0, 0.0, 1, 0)
    if collab_error == 0 then
        test_results.collaborative_work = true
        TPWrite("Right arm collaborative work successful")
        Sleep(1500)
    else
        TPWrite("Right arm collaborative work failed, error: " .. collab_error)
    end
    
    -- 5. 安全监控测试
    TPWrite("Right arm: Testing safety monitoring...")
    -- 检查安全状态
    local safety_error, robot_state = GetRobotState()
    if safety_error == 0 then
        TPWrite("Right arm safety state: " .. robot_state)
        -- 返回安全位置
        local safe_error = MoveJTraj(0, home_pos, 10.0, 10.0, 100.0, 0.0, 0.0, 1, 0)
        if safe_error == 0 then
            test_results.safety_monitoring = true
            TPWrite("Right arm safety monitoring successful")
        end
    end
    
    TPWrite("Right arm integration test completed")
    return test_results
end

-- 执行右臂集成测试
local results = integration_right_arm_test()
TPWrite("Right arm integration results:")
for key, value in pairs(results) do
    TPWrite("  " .. key .. ": " .. tostring(value))
end
"""
        return lua_script
    
    def connect_all_systems(self) -> Dict[str, bool]:
        """连接所有系统组件"""
        connection_status = {
            'left_arm': False,
            'right_arm': False,
            'chassis': False
        }
        
        try:
            # 连接左臂
            self.logger.info(f"连接左臂: {self.left_arm_ip}")
            self.left_robot = Robot.RPC(self.left_arm_ip)
            error, version = self.left_robot.GetSDKVersion()
            if error == 0:
                connection_status['left_arm'] = True
                self.logger.info(f"左臂连接成功: {version}")
            else:
                self.logger.error(f"左臂连接失败: {error}")
            
            # 连接右臂
            self.logger.info(f"连接右臂: {self.right_arm_ip}")
            self.right_robot = Robot.RPC(self.right_arm_ip)
            error, version = self.right_robot.GetSDKVersion()
            if error == 0:
                connection_status['right_arm'] = True
                self.logger.info(f"右臂连接成功: {version}")
            else:
                self.logger.error(f"右臂连接失败: {error}")
            
            # 连接底盘
            self.logger.info(f"连接底盘: {self.chassis_ip}:{self.chassis_port}")
            self.chassis_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chassis_socket.settimeout(10.0)
            self.chassis_socket.connect((self.chassis_ip, self.chassis_port))
            
            # 测试底盘连接
            test_command = json.dumps({"action": "get_status"}) + '\n'
            self.chassis_socket.send(test_command.encode('utf-8'))
            response = self.chassis_socket.recv(1024)
            if response:
                connection_status['chassis'] = True
                self.logger.info("底盘连接成功")
            else:
                self.logger.error("底盘连接失败")
                
        except Exception as e:
            self.logger.error(f"连接系统时发生异常: {str(e)}")
        
        return connection_status
    
    def upload_integration_scripts(self) -> Dict[str, bool]:
        """上传集成测试lua脚本"""
        upload_status = {
            'left_arm': False,
            'right_arm': False
        }
        
        try:
            # 上传左臂脚本
            if self.left_robot:
                left_script = self._create_integration_left_arm_script()
                left_temp_path = Path(f"/tmp/{self.lua_scripts['left_arm']}")
                
                with open(left_temp_path, 'w', encoding='utf-8') as f:
                    f.write(left_script)
                
                error = self.left_robot.LuaUpload(filePath=str(left_temp_path))
                if error == 0:
                    upload_status['left_arm'] = True
                    self.logger.info("左臂集成脚本上传成功")
                    left_temp_path.unlink()
                else:
                    self.logger.error(f"左臂脚本上传失败: {error}")
            
            # 上传右臂脚本
            if self.right_robot:
                right_script = self._create_integration_right_arm_script()
                right_temp_path = Path(f"/tmp/{self.lua_scripts['right_arm']}")
                
                with open(right_temp_path, 'w', encoding='utf-8') as f:
                    f.write(right_script)
                
                error = self.right_robot.LuaUpload(filePath=str(right_temp_path))
                if error == 0:
                    upload_status['right_arm'] = True
                    self.logger.info("右臂集成脚本上传成功")
                    right_temp_path.unlink()
                else:
                    self.logger.error(f"右臂脚本上传失败: {error}")
                    
        except Exception as e:
            self.logger.error(f"上传脚本时发生异常: {str(e)}")
        
        return upload_status
    
    def execute_system_initialization_scenario(self) -> Dict[str, Any]:
        """执行系统初始化场景"""
        scenario_result = {
            'name': 'system_initialization',
            'success': False,
            'component_status': {},
            'duration': 0,
            'start_time': time.time()
        }
        
        try:
            self.logger.info("执行系统初始化场景...")
            
            # 检查左臂状态
            if self.left_robot:
                error, left_state = self.left_robot.GetRobotState()
                scenario_result['component_status']['left_arm'] = {
                    'connected': error == 0,
                    'state': left_state if error == 0 else f'error_{error}'
                }
            
            # 检查右臂状态
            if self.right_robot:
                error, right_state = self.right_robot.GetRobotState()
                scenario_result['component_status']['right_arm'] = {
                    'connected': error == 0,
                    'state': right_state if error == 0 else f'error_{error}'
                }
            
            # 检查底盘状态
            if self.chassis_socket:
                try:
                    command = json.dumps({"action": "get_status"}) + '\n'
                    self.chassis_socket.send(command.encode('utf-8'))
                    response = self.chassis_socket.recv(1024).decode('utf-8')
                    scenario_result['component_status']['chassis'] = {
                        'connected': True,
                        'response': response.strip()
                    }
                except:
                    scenario_result['component_status']['chassis'] = {
                        'connected': False,
                        'error': 'Communication failed'
                    }
            
            # 模拟视觉系统检查
            scenario_result['component_status']['vision'] = {
                'connected': True,  # 模拟
                'cameras': ['gemini_335_left', 'gemini_335_right'],
                'status': 'operational'
            }
            
            # 判断初始化是否成功
            all_connected = all(
                comp.get('connected', False) 
                for comp in scenario_result['component_status'].values()
            )
            
            scenario_result['success'] = all_connected
            self.logger.info(f"系统初始化场景完成: {'成功' if all_connected else '失败'}")
            
        except Exception as e:
            scenario_result['error'] = str(e)
            self.logger.error(f"系统初始化场景异常: {str(e)}")
        
        finally:
            scenario_result['duration'] = time.time() - scenario_result['start_time']
        
        return scenario_result
    
    def execute_dual_arm_coordination_scenario(self) -> Dict[str, Any]:
        """执行双臂协调场景"""
        scenario_result = {
            'name': 'dual_arm_coordination',
            'success': False,
            'arm_results': {},
            'synchronization': {},
            'duration': 0,
            'start_time': time.time()
        }
        
        def left_arm_thread():
            """左臂执行线程"""
            if self.left_robot:
                try:
                    # 加载并运行左臂集成脚本
                    self.left_robot.Mode(state=0)
                    error = self.left_robot.ProgramLoad(
                        program_name=f"/fruser/{self.lua_scripts['left_arm']}"
                    )
                    if error == 0:
                        self.left_robot.ProgramRun()
                        
                        # 监控执行
                        start_time = time.time()
                        while time.time() - start_time < 60:  # 60秒超时
                            error, state = self.left_robot.GetProgramState()
                            if error == 0 and state in ["completed", "stopped", "error"]:
                                break
                            time.sleep(0.5)
                        
                        with self.scenario_lock:
                            self.component_results['left_arm'] = {
                                'success': state == "completed",
                                'final_state': state,
                                'duration': time.time() - start_time
                            }
                    else:
                        with self.scenario_lock:
                            self.component_results['left_arm'] = {
                                'success': False,
                                'error': f'Program load failed: {error}'
                            }
                except Exception as e:
                    with self.scenario_lock:
                        self.component_results['left_arm'] = {
                            'success': False,
                            'error': str(e)
                        }
        
        def right_arm_thread():
            """右臂执行线程"""
            if self.right_robot:
                try:
                    # 加载并运行右臂集成脚本
                    self.right_robot.Mode(state=0)
                    error = self.right_robot.ProgramLoad(
                        program_name=f"/fruser/{self.lua_scripts['right_arm']}"
                    )
                    if error == 0:
                        self.right_robot.ProgramRun()
                        
                        # 监控执行
                        start_time = time.time()
                        while time.time() - start_time < 60:  # 60秒超时
                            error, state = self.right_robot.GetProgramState()
                            if error == 0 and state in ["completed", "stopped", "error"]:
                                break
                            time.sleep(0.5)
                        
                        with self.scenario_lock:
                            self.component_results['right_arm'] = {
                                'success': state == "completed",
                                'final_state': state,
                                'duration': time.time() - start_time
                            }
                    else:
                        with self.scenario_lock:
                            self.component_results['right_arm'] = {
                                'success': False,
                                'error': f'Program load failed: {error}'
                            }
                except Exception as e:
                    with self.scenario_lock:
                        self.component_results['right_arm'] = {
                            'success': False,
                            'error': str(e)
                        }
        
        try:
            self.logger.info("执行双臂协调场景...")
            
            # 创建并启动双臂线程
            left_thread = threading.Thread(target=left_arm_thread)
            right_thread = threading.Thread(target=right_arm_thread)
            
            left_thread.start()
            right_thread.start()
            
            # 等待两个线程完成
            left_thread.join()
            right_thread.join()
            
            # 分析结果
            scenario_result['arm_results'] = self.component_results.copy()
            
            # 计算同步性能
            if 'left_arm' in self.component_results and 'right_arm' in self.component_results:
                left_duration = self.component_results['left_arm'].get('duration', 0)
                right_duration = self.component_results['right_arm'].get('duration', 0)
                
                scenario_result['synchronization'] = {
                    'time_difference': abs(left_duration - right_duration),
                    'left_duration': left_duration,
                    'right_duration': right_duration,
                    'synchronized': abs(left_duration - right_duration) < 3.0
                }
            
            # 判断场景成功
            left_success = self.component_results.get('left_arm', {}).get('success', False)
            right_success = self.component_results.get('right_arm', {}).get('success', False)
            sync_success = scenario_result['synchronization'].get('synchronized', False)
            
            scenario_result['success'] = left_success and right_success and sync_success
            
            self.logger.info(f"双臂协调场景完成: {'成功' if scenario_result['success'] else '失败'}")
            
        except Exception as e:
            scenario_result['error'] = str(e)
            self.logger.error(f"双臂协调场景异常: {str(e)}")
        
        finally:
            scenario_result['duration'] = time.time() - scenario_result['start_time']
        
        return scenario_result
    
    def cleanup_resources(self):
        """清理资源"""
        try:
            # 停止机器人程序
            if self.left_robot:
                self.left_robot.StopMotion()
                self.left_robot.LuaDelete(fileName=self.lua_scripts['left_arm'])
                self.logger.info("左臂资源清理完成")
            
            if self.right_robot:
                self.right_robot.StopMotion()
                self.right_robot.LuaDelete(fileName=self.lua_scripts['right_arm'])
                self.logger.info("右臂资源清理完成")
            
            # 关闭底盘连接
            if self.chassis_socket:
                stop_command = json.dumps({"action": "stop"}) + '\n'
                try:
                    self.chassis_socket.send(stop_command.encode('utf-8'))
                except:
                    pass
                self.chassis_socket.close()
                self.chassis_socket = None
                self.logger.info("底盘连接已关闭")
        
        except Exception as e:
            self.logger.warning(f"清理资源时发生异常: {str(e)}")
    
    def run_test(self) -> Dict[str, Any]:
        """运行完整的全系统集成lua测试"""
        test_result = {
            'test_name': self.test_name,
            'start_time': time.time(),
            'success': False,
            'stages': {},
            'scenarios': {},
            'error_message': None,
            'system_info': {
                'left_arm_ip': self.left_arm_ip,
                'right_arm_ip': self.right_arm_ip,
                'chassis_ip': self.chassis_ip,
                'chassis_port': self.chassis_port
            }
        }
        
        try:
            # 阶段1: 连接所有系统
            self.logger.info("开始全系统集成Lua测试")
            connection_status = self.connect_all_systems()
            test_result['stages']['connection'] = connection_status
            
            if not all(connection_status.values()):
                test_result['error_message'] = f"系统连接失败: {connection_status}"
                return test_result
            
            # 阶段2: 上传集成脚本
            upload_status = self.upload_integration_scripts()
            test_result['stages']['upload'] = upload_status
            
            if not all(upload_status.values()):
                test_result['error_message'] = f"脚本上传失败: {upload_status}"
                return test_result
            
            # 场景1: 系统初始化
            init_result = self.execute_system_initialization_scenario()
            test_result['scenarios']['initialization'] = init_result
            
            if not init_result['success']:
                test_result['error_message'] = "系统初始化场景失败"
                return test_result
            
            # 场景2: 双臂协调
            coordination_result = self.execute_dual_arm_coordination_scenario()
            test_result['scenarios']['coordination'] = coordination_result
            
            # 判断总体测试结果
            all_scenarios_passed = all(
                scenario.get('success', False) 
                for scenario in test_result['scenarios'].values()
            )
            
            test_result['success'] = all_scenarios_passed
            
            if not test_result['success']:
                failed_scenarios = [
                    name for name, result in test_result['scenarios'].items() 
                    if not result.get('success', False)
                ]
                test_result['error_message'] = f"场景测试失败: {failed_scenarios}"
            
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
    print("=== 全系统集成Lua测试 ===")
    
    # 创建测试实例
    test = LuaFullSystemTest(
        left_arm_ip="192.168.58.3",
        right_arm_ip="192.168.58.2",
        chassis_ip="192.168.31.211",
        chassis_port=1448
    )
    
    # 运行测试
    result = test.run_test()
    
    # 打印结果
    print(f"\n测试结果:")
    print(f"测试名称: {result['test_name']}")
    print(f"测试状态: {'通过' if result['success'] else '失败'}")
    print(f"总执行时间: {result['duration']:.2f}秒")
    
    if not result['success']:
        print(f"错误信息: {result['error_message']}")
    
    # 打印连接状态
    if 'stages' in result and 'connection' in result['stages']:
        connection_status = result['stages']['connection']
        print(f"\n系统连接状态:")
        for component, connected in connection_status.items():
            status = "✓" if connected else "✗"
            print(f"  {status} {component}: {'已连接' if connected else '连接失败'}")
    
    # 打印场景执行结果
    if 'scenarios' in result:
        print(f"\n场景执行结果:")
        for scenario_name, scenario_result in result['scenarios'].items():
            status = "✓" if scenario_result.get('success', False) else "✗"
            duration = scenario_result.get('duration', 0)
            print(f"  {status} {scenario_name}: {'成功' if scenario_result.get('success', False) else '失败'} ({duration:.1f}s)")
    
    return result


if __name__ == "__main__":
    main()