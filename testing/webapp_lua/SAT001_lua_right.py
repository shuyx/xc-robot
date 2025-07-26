#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAT001 Lua Right Arm Connection Test
基于webapp lua调用的右臂连接测试

替代传统的Python状态读取方式，使用lua脚本执行和监控
"""

import time
import logging
from pathlib import Path
from fairino import Robot
from typing import Dict, Any, Optional, Tuple

class LuaRightArmTest:
    """右臂Lua连接测试类"""
    
    def __init__(self, robot_ip: str = "192.168.58.2"):
        """
        初始化右臂lua测试
        
        Args:
            robot_ip: 右臂机器人IP地址
        """
        self.robot_ip = robot_ip
        self.robot: Optional[Robot] = None
        self.test_name = "SAT001_LUA_RIGHT"
        self.lua_script_name = "sat001_right_test.lua"
        self.lua_program_path = f"/fruser/{self.lua_script_name}"
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__name__)
        
    def _create_lua_script(self) -> str:
        """创建右臂连接测试的lua脚本内容"""
        lua_script = """
-- SAT001 Right Arm Connection Test Script
-- 右臂连接测试lua脚本

function test_right_arm_connection()
    -- 初始化测试结果
    local test_result = {
        connection_status = false,
        sdk_version = "",
        robot_state = "",
        joint_positions = {},
        error_code = 0,
        test_timestamp = os.time()
    }
    
    -- 获取SDK版本信息
    local error_code, version = GetSDKVersion()
    if error_code == 0 then
        test_result.sdk_version = version
        test_result.connection_status = true
        TPWrite("Right arm SDK version: " .. version)
    else
        test_result.error_code = error_code
        TPWrite("Failed to get SDK version, error: " .. error_code)
        return test_result
    end
    
    -- 获取机器人状态
    local state_error, robot_state = GetRobotState()
    if state_error == 0 then
        test_result.robot_state = robot_state
        TPWrite("Right arm robot state: " .. robot_state)
    else
        test_result.error_code = state_error
        TPWrite("Failed to get robot state, error: " .. state_error)
    end
    
    -- 获取关节位置
    local joint_error, joint_pos = GetActualJointPosDegree(0)
    if joint_error == 0 then
        test_result.joint_positions = joint_pos
        TPWrite("Right arm joint positions retrieved successfully")
        for i = 1, 6 do
            TPWrite("Joint " .. i .. ": " .. joint_pos[i] .. " degrees")
        end
    else
        test_result.error_code = joint_error
        TPWrite("Failed to get joint positions, error: " .. joint_error)
    end
    
    -- 测试基础运动功能（小幅度关节运动）
    if test_result.connection_status then
        local move_error = RelMoveJTraj(0, {-1.0, 0, 0, 0, 0, 0}, 20.0, 20.0, 100.0, 0.0, 0.0, 1, 0)
        if move_error == 0 then
            TPWrite("Right arm basic movement test passed")
            Sleep(1000)  -- 等待1秒
            -- 回到原位
            RelMoveJTraj(0, {1.0, 0, 0, 0, 0, 0}, 20.0, 20.0, 100.0, 0.0, 0.0, 1, 0)
        else
            test_result.error_code = move_error
            TPWrite("Right arm movement test failed, error: " .. move_error)
        end
    end
    
    TPWrite("Right arm connection test completed")
    return test_result
end

-- 执行测试
local result = test_right_arm_connection()
TPWrite("Test completed with status: " .. tostring(result.connection_status))
"""
        return lua_script
    
    def connect_robot(self) -> bool:
        """连接到右臂机器人"""
        try:
            self.logger.info(f"正在连接右臂机器人: {self.robot_ip}")
            self.robot = Robot.RPC(self.robot_ip)
            
            # 测试连接
            error, version = self.robot.GetSDKVersion()
            if error == 0:
                self.logger.info(f"右臂连接成功，SDK版本: {version}")
                return True
            else:
                self.logger.error(f"右臂连接失败，错误码: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"连接右臂时发生异常: {str(e)}")
            return False
    
    def upload_lua_script(self) -> bool:
        """上传lua测试脚本到机器人控制器"""
        try:
            # 创建临时lua脚本文件
            script_content = self._create_lua_script()
            temp_script_path = Path(f"/tmp/{self.lua_script_name}")
            
            with open(temp_script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 上传lua脚本
            self.logger.info(f"正在上传lua脚本: {self.lua_script_name}")
            error = self.robot.LuaUpload(filePath=str(temp_script_path))
            
            if error == 0:
                self.logger.info("Lua脚本上传成功")
                # 清理临时文件
                temp_script_path.unlink()
                return True
            else:
                self.logger.error(f"Lua脚本上传失败，错误码: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"上传lua脚本时发生异常: {str(e)}")
            return False
    
    def load_and_run_program(self) -> bool:
        """加载并运行lua程序"""
        try:
            # 设置机器人模式
            self.robot.Mode(state=0)
            
            # 加载lua程序
            self.logger.info(f"正在加载lua程序: {self.lua_program_path}")
            error = self.robot.ProgramLoad(program_name=self.lua_program_path)
            
            if error != 0:
                self.logger.error(f"加载lua程序失败，错误码: {error}")
                return False
            
            # 确认程序已加载
            error, loaded_name = self.robot.GetLoadedProgram()
            if error == 0:
                self.logger.info(f"已加载程序: {loaded_name}")
            
            # 运行程序
            self.logger.info("正在运行lua程序")
            error = self.robot.ProgramRun()
            
            if error == 0:
                self.logger.info("Lua程序开始执行")
                return True
            else:
                self.logger.error(f"运行lua程序失败，错误码: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"加载运行lua程序时发生异常: {str(e)}")
            return False
    
    def monitor_execution(self, timeout: int = 60) -> Dict[str, Any]:
        """监控lua程序执行状态"""
        start_time = time.time()
        execution_log = []
        
        try:
            while time.time() - start_time < timeout:
                # 获取程序状态
                error, state = self.robot.GetProgramState()
                if error != 0:
                    self.logger.error(f"获取程序状态失败，错误码: {error}")
                    break
                
                # 获取当前执行行号
                line_error, current_line = self.robot.GetCurrentLine()
                if line_error == 0:
                    execution_info = {
                        'timestamp': time.time(),
                        'state': state,
                        'line': current_line
                    }
                    execution_log.append(execution_info)
                    self.logger.info(f"程序状态: {state}, 当前行: {current_line}")
                
                # 检查是否完成
                if state in ["completed", "stopped", "error"]:
                    self.logger.info(f"程序执行结束，最终状态: {state}")
                    break
                
                time.sleep(0.5)  # 500ms检查间隔
            
            return {
                'success': state == "completed",
                'final_state': state,
                'execution_log': execution_log,
                'duration': time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"监控程序执行时发生异常: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'execution_log': execution_log,
                'duration': time.time() - start_time
            }
    
    def cleanup_resources(self):
        """清理资源"""
        try:
            if self.robot:
                # 停止程序（如果仍在运行）
                self.robot.StopMotion()
                
                # 删除上传的lua脚本
                delete_error = self.robot.LuaDelete(fileName=self.lua_script_name)
                if delete_error == 0:
                    self.logger.info("Lua脚本清理成功")
                else:
                    self.logger.warning(f"清理lua脚本失败，错误码: {delete_error}")
        
        except Exception as e:
            self.logger.warning(f"清理资源时发生异常: {str(e)}")
    
    def run_test(self) -> Dict[str, Any]:
        """运行完整的右臂lua连接测试"""
        test_result = {
            'test_name': self.test_name,
            'robot_ip': self.robot_ip,
            'start_time': time.time(),
            'success': False,
            'stages': {},
            'error_message': None
        }
        
        try:
            # 阶段1: 连接机器人
            self.logger.info("开始SAT001右臂Lua连接测试")
            if not self.connect_robot():
                test_result['error_message'] = "机器人连接失败"
                return test_result
            test_result['stages']['connection'] = True
            
            # 阶段2: 上传lua脚本
            if not self.upload_lua_script():
                test_result['error_message'] = "Lua脚本上传失败"
                return test_result
            test_result['stages']['upload'] = True
            
            # 阶段3: 加载并运行程序
            if not self.load_and_run_program():
                test_result['error_message'] = "程序加载运行失败"
                return test_result
            test_result['stages']['execution'] = True
            
            # 阶段4: 监控执行
            execution_result = self.monitor_execution()
            test_result['stages']['monitoring'] = execution_result
            
            # 判断总体测试结果
            test_result['success'] = execution_result.get('success', False)
            if not test_result['success']:
                test_result['error_message'] = f"程序执行失败，状态: {execution_result.get('final_state', 'unknown')}"
            
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
    print("=== SAT001 右臂Lua连接测试 ===")
    
    # 创建测试实例
    test = LuaRightArmTest(robot_ip="192.168.58.2")
    
    # 运行测试
    result = test.run_test()
    
    # 打印结果
    print(f"\n测试结果:")
    print(f"测试名称: {result['test_name']}")
    print(f"机器人IP: {result['robot_ip']}")
    print(f"测试状态: {'通过' if result['success'] else '失败'}")
    print(f"执行时间: {result['duration']:.2f}秒")
    
    if not result['success']:
        print(f"错误信息: {result['error_message']}")
    
    if 'stages' in result and 'monitoring' in result['stages']:
        monitoring_result = result['stages']['monitoring']
        print(f"程序执行时长: {monitoring_result.get('duration', 0):.2f}秒")
        print(f"最终状态: {monitoring_result.get('final_state', 'unknown')}")
    
    return result


if __name__ == "__main__":
    main()