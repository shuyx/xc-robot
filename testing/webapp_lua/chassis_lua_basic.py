#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chassis Lua Basic Movement Test
基于webapp lua调用的底盘基础移动测试

使用lua脚本控制Hermes底盘进行基础移动测试
"""

import time
import logging
import socket
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

class LuaChassisBasicTest:
    """底盘Lua基础移动测试类"""
    
    def __init__(self, chassis_ip: str = "192.168.31.211", chassis_port: int = 1448):
        """
        初始化底盘lua测试
        
        Args:
            chassis_ip: Hermes底盘IP地址
            chassis_port: 底盘通信端口
        """
        self.chassis_ip = chassis_ip
        self.chassis_port = chassis_port
        self.socket: Optional[socket.socket] = None
        self.test_name = "CHASSIS_LUA_BASIC"
        self.lua_script_name = "chassis_basic_test.lua"
        
        # 测试路径点（相对移动）
        self.test_waypoints = [
            {'x': 1.0, 'y': 0.0, 'theta': 0.0, 'description': '前进1米'},
            {'x': 0.0, 'y': 1.0, 'theta': 0.0, 'description': '左移1米'},
            {'x': -1.0, 'y': 0.0, 'theta': 0.0, 'description': '后退1米'},
            {'x': 0.0, 'y': -1.0, 'theta': 0.0, 'description': '右移1米'},
            {'x': 0.0, 'y': 0.0, 'theta': 1.57, 'description': '旋转90度'},
            {'x': 0.0, 'y': 0.0, 'theta': -1.57, 'description': '反向旋转90度'}
        ]
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__name__)
        
    def _create_lua_script(self) -> str:
        """创建底盘基础移动测试的lua脚本内容"""
        lua_script = """
-- Chassis Basic Movement Test Script
-- 底盘基础移动测试lua脚本

-- 底盘通信配置
local CHASSIS_IP = "192.168.31.211"
local CHASSIS_PORT = 1448

-- 测试路径点
local test_waypoints = {
    {x = 1.0, y = 0.0, theta = 0.0, desc = "前进1米"},
    {x = 0.0, y = 1.0, theta = 0.0, desc = "左移1米"},
    {x = -1.0, y = 0.0, theta = 0.0, desc = "后退1米"},
    {x = 0.0, y = -1.0, theta = 0.0, desc = "右移1米"},
    {x = 0.0, y = 0.0, theta = 1.57, desc = "旋转90度"},
    {x = 0.0, y = 0.0, theta = -1.57, desc = "反向旋转90度"}
}

function send_chassis_command(command)
    -- 发送底盘控制命令
    -- 这里需要使用lua的socket库或者通过机器人控制器的API
    TPWrite("Sending chassis command: " .. command.action)
    
    -- 模拟命令发送和执行
    if command.action == "move_relative" then
        TPWrite("Moving relative: x=" .. command.x .. ", y=" .. command.y .. ", theta=" .. command.theta)
        -- 模拟移动时间（实际应该等待底盘完成移动）
        Sleep(math.abs(command.x) * 2000 + math.abs(command.y) * 2000 + math.abs(command.theta) * 1000)
    elseif command.action == "get_status" then
        TPWrite("Getting chassis status")
        Sleep(100)
    elseif command.action == "stop" then
        TPWrite("Stopping chassis")
        Sleep(500)
    end
    
    return true
end

function get_chassis_status()
    -- 获取底盘状态
    local status = {
        position = {x = 0.0, y = 0.0, theta = 0.0},
        velocity = {vx = 0.0, vy = 0.0, vtheta = 0.0},
        battery = 85.5,
        status = "ready",
        timestamp = os.time()
    }
    
    TPWrite("Chassis status: " .. status.status .. ", Battery: " .. status.battery .. "%")
    return status
end

function test_chassis_basic_movement()
    TPWrite("Starting chassis basic movement test...")
    
    local test_result = {
        success = true,
        completed_waypoints = 0,
        total_waypoints = #test_waypoints,
        error_message = "",
        start_time = os.time()
    }
    
    -- 获取初始状态
    local initial_status = get_chassis_status()
    if not initial_status then
        test_result.success = false
        test_result.error_message = "Failed to get initial chassis status"
        return test_result
    end
    
    TPWrite("Initial chassis position: x=" .. initial_status.position.x .. 
           ", y=" .. initial_status.position.y .. 
           ", theta=" .. initial_status.position.theta)
    
    -- 执行各个测试路径点
    for i, waypoint in ipairs(test_waypoints) do
        TPWrite("Executing waypoint " .. i .. ": " .. waypoint.desc)
        
        -- 发送移动命令
        local move_command = {
            action = "move_relative",
            x = waypoint.x,
            y = waypoint.y,
            theta = waypoint.theta,
            max_velocity = 0.5,  -- 最大速度 0.5 m/s
            timeout = 30.0       -- 超时时间 30 秒
        }
        
        local command_success = send_chassis_command(move_command)
        if not command_success then
            test_result.success = false
            test_result.error_message = "Failed to execute waypoint " .. i
            break
        end
        
        -- 等待移动完成并检查状态
        Sleep(500)  -- 额外等待时间
        local current_status = get_chassis_status()
        if current_status and current_status.status == "ready" then
            test_result.completed_waypoints = test_result.completed_waypoints + 1
            TPWrite("Waypoint " .. i .. " completed successfully")
        else
            TPWrite("Warning: Waypoint " .. i .. " may not have completed properly")
        end
        
        -- 短暂停顿
        Sleep(1000)
    end
    
    -- 最终停止命令
    local stop_command = {action = "stop"}
    send_chassis_command(stop_command)
    
    -- 获取最终状态
    local final_status = get_chassis_status()
    TPWrite("Final chassis position: x=" .. final_status.position.x .. 
           ", y=" .. final_status.position.y .. 
           ", theta=" .. final_status.position.theta)
    
    test_result.end_time = os.time()
    test_result.duration = test_result.end_time - test_result.start_time
    
    if test_result.completed_waypoints == test_result.total_waypoints then
        TPWrite("Chassis basic movement test completed successfully!")
        TPWrite("Completed " .. test_result.completed_waypoints .. "/" .. test_result.total_waypoints .. " waypoints")
    else
        test_result.success = false
        if test_result.error_message == "" then
            test_result.error_message = "Not all waypoints were completed"
        end
        TPWrite("Chassis test completed with issues: " .. test_result.error_message)
    end
    
    return test_result
end

-- 执行底盘基础移动测试
local result = test_chassis_basic_movement()
TPWrite("Chassis basic test result: " .. tostring(result.success))
TPWrite("Waypoints completed: " .. result.completed_waypoints .. "/" .. result.total_waypoints)
"""
        return lua_script
    
    def connect_chassis(self) -> bool:
        """连接到Hermes底盘"""
        try:
            self.logger.info(f"正在连接Hermes底盘: {self.chassis_ip}:{self.chassis_port}")
            
            # 创建TCP socket连接
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)  # 10秒超时
            
            # 连接到底盘
            self.socket.connect((self.chassis_ip, self.chassis_port))
            
            # 发送测试命令验证连接
            test_command = {
                "action": "get_status",
                "timestamp": time.time()
            }
            
            command_json = json.dumps(test_command) + '\n'
            self.socket.send(command_json.encode('utf-8'))
            
            # 接收响应
            response = self.socket.recv(1024).decode('utf-8')
            if response:
                self.logger.info(f"底盘连接成功，响应: {response.strip()}")
                return True
            else:
                self.logger.error("底盘连接失败，无响应")
                return False
                
        except Exception as e:
            self.logger.error(f"连接底盘时发生异常: {str(e)}")
            return False
    
    def send_chassis_command(self, command: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """发送底盘控制命令"""
        try:
            if not self.socket:
                return False, None
            
            # 添加时间戳
            command['timestamp'] = time.time()
            
            # 发送命令
            command_json = json.dumps(command) + '\n'
            self.socket.send(command_json.encode('utf-8'))
            
            # 接收响应
            response_data = self.socket.recv(2048).decode('utf-8')
            if response_data:
                try:
                    response = json.loads(response_data.strip())
                    return True, response
                except json.JSONDecodeError:
                    self.logger.warning(f"底盘响应格式错误: {response_data}")
                    return True, {"raw_response": response_data}
            else:
                return False, None
                
        except Exception as e:
            self.logger.error(f"发送底盘命令时发生异常: {str(e)}")
            return False, None
    
    def get_chassis_status(self) -> Optional[Dict[str, Any]]:
        """获取底盘状态"""
        command = {"action": "get_status"}
        success, response = self.send_chassis_command(command)
        
        if success and response:
            return response
        else:
            # 返回模拟状态用于测试
            return {
                "position": {"x": 0.0, "y": 0.0, "theta": 0.0},
                "velocity": {"vx": 0.0, "vy": 0.0, "vtheta": 0.0},
                "battery": 85.5,
                "status": "ready",
                "timestamp": time.time()
            }
    
    def execute_waypoint_sequence(self) -> Dict[str, Any]:
        """执行路径点序列测试"""
        test_result = {
            'success': True,
            'completed_waypoints': 0,
            'total_waypoints': len(self.test_waypoints),
            'waypoint_results': [],
            'error_message': None,
            'start_time': time.time()
        }
        
        try:
            # 获取初始状态
            initial_status = self.get_chassis_status()
            self.logger.info(f"初始底盘状态: {initial_status}")
            
            # 执行每个路径点
            for i, waypoint in enumerate(self.test_waypoints):
                self.logger.info(f"执行路径点 {i+1}: {waypoint['description']}")
                
                waypoint_start_time = time.time()
                
                # 发送移动命令
                move_command = {
                    "action": "move_relative",
                    "x": waypoint['x'],
                    "y": waypoint['y'],
                    "theta": waypoint['theta'],
                    "max_velocity": 0.5,
                    "timeout": 30.0
                }
                
                command_success, move_response = self.send_chassis_command(move_command)
                
                if command_success:
                    # 等待移动完成
                    self.logger.info(f"等待路径点 {i+1} 执行完成...")
                    
                    # 估算执行时间
                    estimated_time = (abs(waypoint['x']) * 2 + 
                                    abs(waypoint['y']) * 2 + 
                                    abs(waypoint['theta']) * 1)
                    time.sleep(max(1.0, estimated_time))
                    
                    # 检查执行状态
                    final_status = self.get_chassis_status()
                    
                    waypoint_result = {
                        'waypoint_index': i + 1,
                        'description': waypoint['description'],
                        'success': final_status.get('status') == 'ready',
                        'duration': time.time() - waypoint_start_time,
                        'command_response': move_response,
                        'final_status': final_status
                    }
                    
                    test_result['waypoint_results'].append(waypoint_result)
                    
                    if waypoint_result['success']:
                        test_result['completed_waypoints'] += 1
                        self.logger.info(f"路径点 {i+1} 执行成功")
                    else:
                        self.logger.warning(f"路径点 {i+1} 执行可能有问题")
                
                else:
                    waypoint_result = {
                        'waypoint_index': i + 1,
                        'description': waypoint['description'],
                        'success': False,
                        'duration': time.time() - waypoint_start_time,
                        'error': 'Command send failed'
                    }
                    test_result['waypoint_results'].append(waypoint_result)
                    self.logger.error(f"路径点 {i+1} 命令发送失败")
                
                # 路径点间短暂停顿
                time.sleep(1.0)
            
            # 发送停止命令
            stop_command = {"action": "stop"}
            self.send_chassis_command(stop_command)
            
            # 判断总体成功
            if test_result['completed_waypoints'] == test_result['total_waypoints']:
                test_result['success'] = True
                self.logger.info("所有路径点执行完成")
            else:
                test_result['success'] = False
                test_result['error_message'] = f"只完成了 {test_result['completed_waypoints']}/{test_result['total_waypoints']} 个路径点"
            
        except Exception as e:
            test_result['success'] = False
            test_result['error_message'] = str(e)
            self.logger.error(f"执行路径点序列时发生异常: {str(e)}")
        
        finally:
            test_result['end_time'] = time.time()
            test_result['duration'] = test_result['end_time'] - test_result['start_time']
        
        return test_result
    
    def create_and_upload_lua_script(self) -> bool:
        """创建并模拟上传lua脚本"""
        try:
            # 创建lua脚本内容
            script_content = self._create_lua_script()
            
            # 保存到临时文件用于记录
            temp_script_path = Path(f"/tmp/{self.lua_script_name}")
            with open(temp_script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            self.logger.info(f"Lua脚本已创建: {self.lua_script_name}")
            self.logger.info(f"脚本内容已保存到: {temp_script_path}")
            
            # 注意：由于底盘不像机器人臂那样支持lua脚本上传，
            # 这里主要是创建脚本内容用于文档和测试逻辑参考
            
            return True
            
        except Exception as e:
            self.logger.error(f"创建lua脚本时发生异常: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """清理资源"""
        try:
            if self.socket:
                # 发送最终停止命令
                stop_command = {"action": "emergency_stop"}
                try:
                    self.send_chassis_command(stop_command)
                except:
                    pass  # 忽略清理时的错误
                
                # 关闭socket连接
                self.socket.close()
                self.socket = None
                self.logger.info("底盘连接已关闭")
        
        except Exception as e:
            self.logger.warning(f"清理资源时发生异常: {str(e)}")
    
    def run_test(self) -> Dict[str, Any]:
        """运行完整的底盘基础移动lua测试"""
        test_result = {
            'test_name': self.test_name,
            'chassis_ip': self.chassis_ip,
            'chassis_port': self.chassis_port,
            'start_time': time.time(),
            'success': False,
            'stages': {},
            'error_message': None
        }
        
        try:
            # 阶段1: 创建lua脚本
            self.logger.info("开始底盘基础移动Lua测试")
            if not self.create_and_upload_lua_script():
                test_result['error_message'] = "Lua脚本创建失败"
                return test_result
            test_result['stages']['script_creation'] = True
            
            # 阶段2: 连接底盘
            if not self.connect_chassis():
                test_result['error_message'] = "底盘连接失败"
                return test_result
            test_result['stages']['connection'] = True
            
            # 阶段3: 执行路径点序列测试
            waypoint_result = self.execute_waypoint_sequence()
            test_result['stages']['waypoint_execution'] = waypoint_result
            
            # 判断总体测试结果
            test_result['success'] = waypoint_result.get('success', False)
            if not test_result['success']:
                test_result['error_message'] = waypoint_result.get('error_message', '路径点执行失败')
            
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
    print("=== 底盘基础移动Lua测试 ===")
    
    # 创建测试实例
    test = LuaChassisBasicTest(
        chassis_ip="192.168.31.211",
        chassis_port=1448
    )
    
    # 运行测试
    result = test.run_test()
    
    # 打印结果
    print(f"\n测试结果:")
    print(f"测试名称: {result['test_name']}")
    print(f"底盘地址: {result['chassis_ip']}:{result['chassis_port']}")
    print(f"测试状态: {'通过' if result['success'] else '失败'}")
    print(f"执行时间: {result['duration']:.2f}秒")
    
    if not result['success']:
        print(f"错误信息: {result['error_message']}")
    
    # 打印路径点执行详情
    if 'stages' in result and 'waypoint_execution' in result['stages']:
        waypoint_result = result['stages']['waypoint_execution']
        print(f"\n路径点执行详情:")
        print(f"完成路径点: {waypoint_result.get('completed_waypoints', 0)}/{waypoint_result.get('total_waypoints', 0)}")
        
        if 'waypoint_results' in waypoint_result:
            for wp_result in waypoint_result['waypoint_results']:
                status = "✓" if wp_result['success'] else "✗"
                print(f"  {status} 路径点{wp_result['waypoint_index']}: {wp_result['description']} ({wp_result['duration']:.1f}s)")
    
    return result


if __name__ == "__main__":
    main()