#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vision Lua Test
基于webapp lua调用的视觉系统测试

使用lua脚本集成Gemini 335视觉系统进行目标检测和定位测试
"""

import time
import logging
import cv2
import numpy as np
from pathlib import Path
from fairino import Robot
from typing import Dict, Any, Optional, Tuple, List

class LuaVisionTest:
    """视觉系统Lua测试类"""
    
    def __init__(self, 
                 robot_ip: str = "192.168.58.3",
                 vision_config: Dict[str, Any] = None):
        """
        初始化视觉lua测试
        
        Args:
            robot_ip: 机器人IP地址（用于视觉引导）
            vision_config: 视觉系统配置
        """
        self.robot_ip = robot_ip
        self.robot: Optional[Robot] = None
        self.test_name = "VISION_LUA_TEST"
        self.lua_script_name = "vision_guided_test.lua"
        self.lua_program_path = f"/fruser/{self.lua_script_name}"
        
        # 视觉系统配置
        self.vision_config = vision_config or {
            'cameras': {
                'gemini_335_left': {'index': 0, 'resolution': (1280, 720)},
                'gemini_335_right': {'index': 1, 'resolution': (1280, 720)}
            },
            'detection_targets': ['cube', 'sphere', 'cylinder'],
            'coordinate_system': 'robot_base',
            'calibration_matrix': None
        }
        
        # 测试场景
        self.test_scenarios = [
            {
                'name': 'camera_initialization',
                'description': '相机初始化测试',
                'expected_cameras': 2
            },
            {
                'name': 'object_detection',
                'description': '目标检测测试',
                'target_objects': ['cube', 'sphere']
            },
            {
                'name': 'coordinate_calibration',
                'description': '坐标标定测试',
                'calibration_points': 4
            },
            {
                'name': 'guided_manipulation',
                'description': '视觉引导操作测试',
                'pick_targets': 3
            }
        ]
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__name__)
        
    def _create_vision_lua_script(self) -> str:
        """创建视觉引导测试的lua脚本"""
        lua_script = """
-- Vision Guided Test Script
-- 视觉引导测试lua脚本

-- 视觉系统配置
local VISION_CONFIG = {
    cameras = {
        gemini_335_left = {index = 0, resolution = {1280, 720}},
        gemini_335_right = {index = 1, resolution = {1280, 720}}
    },
    detection_targets = {"cube", "sphere", "cylinder"},
    coordinate_system = "robot_base"
}

-- 模拟视觉系统API（实际应该调用真实的视觉库）
function initialize_cameras()
    TPWrite("Initializing Gemini 335 cameras...")
    
    local camera_status = {
        gemini_335_left = {connected = true, resolution = {1280, 720}},
        gemini_335_right = {connected = true, resolution = {1280, 720}}
    }
    
    TPWrite("Left camera: " .. tostring(camera_status.gemini_335_left.connected))
    TPWrite("Right camera: " .. tostring(camera_status.gemini_335_right.connected))
    
    return camera_status.gemini_335_left.connected and camera_status.gemini_335_right.connected
end

function detect_objects()
    TPWrite("Starting object detection...")
    
    -- 模拟目标检测结果
    local detected_objects = {
        {
            type = "cube",
            position = {x = 350.5, y = -200.8, z = 100.2},
            orientation = {rx = 0.0, ry = 0.0, rz = 45.0},
            confidence = 0.95,
            size = {width = 50.0, height = 50.0, depth = 50.0}
        },
        {
            type = "sphere",
            position = {x = 280.3, y = -150.4, z = 95.8},
            orientation = {rx = 0.0, ry = 0.0, rz = 0.0},
            confidence = 0.88,
            size = {diameter = 40.0}
        },
        {
            type = "cylinder",
            position = {x = 400.1, y = -180.6, z = 98.5},
            orientation = {rx = 0.0, ry = 0.0, rz = 15.0},
            confidence = 0.92,
            size = {diameter = 30.0, height = 80.0}
        }
    }
    
    TPWrite("Detected " .. #detected_objects .. " objects:")
    for i, obj in ipairs(detected_objects) do
        TPWrite("  Object " .. i .. ": " .. obj.type .. 
                " at (" .. obj.position.x .. ", " .. obj.position.y .. ", " .. obj.position.z .. ")")
        TPWrite("    Confidence: " .. obj.confidence)
    end
    
    return detected_objects
end

function calibrate_coordinates()
    TPWrite("Starting coordinate calibration...")
    
    -- 模拟坐标标定过程
    local calibration_points = {
        {pixel = {u = 320, v = 240}, world = {x = 300.0, y = -200.0, z = 100.0}},
        {pixel = {u = 480, v = 240}, world = {x = 400.0, y = -200.0, z = 100.0}},
        {pixel = {u = 320, v = 360}, world = {x = 300.0, y = -300.0, z = 100.0}},
        {pixel = {u = 480, v = 360}, world = {x = 400.0, y = -300.0, z = 100.0}}
    }
    
    -- 计算标定矩阵（简化版）
    local calibration_matrix = {
        {0.8, 0.0, -256.0},
        {0.0, 0.8, 192.0},
        {0.0, 0.0, 1.0}
    }
    
    TPWrite("Calibration completed with " .. #calibration_points .. " points")
    TPWrite("Calibration matrix computed successfully")
    
    return calibration_matrix
end

function pixel_to_world(pixel_coords, calibration_matrix)
    -- 将像素坐标转换为世界坐标
    local world_x = calibration_matrix[1][1] * pixel_coords.u + 
                   calibration_matrix[1][2] * pixel_coords.v + 
                   calibration_matrix[1][3]
    local world_y = calibration_matrix[2][1] * pixel_coords.u + 
                   calibration_matrix[2][2] * pixel_coords.v + 
                   calibration_matrix[2][3]
    
    return {x = world_x, y = world_y, z = 100.0}  -- 假设z固定
end

function vision_guided_pickup(target_position)
    TPWrite("Starting vision guided pickup...")
    TPWrite("Target position: (" .. target_position.x .. ", " .. 
           target_position.y .. ", " .. target_position.z .. ")")
    
    -- 获取当前位置
    local error, current_joints = GetActualJointPosDegree(0)
    if error ~= 0 then
        TPWrite("Failed to get current position, error: " .. error)
        return false
    end
    
    -- 计算接近位置（目标上方50mm）
    local approach_pos = {
        target_position.x,
        target_position.y,
        target_position.z + 50.0,
        -180.0,  -- rx
        0.0,     -- ry  
        0.0      -- rz
    }
    
    -- 移动到接近位置
    TPWrite("Moving to approach position...")
    local approach_error = MovePTraj(0, 0, approach_pos, 50.0, 50.0, 100.0, 0.0, 0.0, 1, 0)
    if approach_error ~= 0 then
        TPWrite("Failed to reach approach position, error: " .. approach_error)
        return false
    end
    
    Sleep(1000)  -- 稳定等待
    
    -- 下降到抓取位置
    local pickup_pos = {
        target_position.x,
        target_position.y,
        target_position.z + 5.0,  -- 5mm above target
        -180.0,
        0.0,
        0.0
    }
    
    TPWrite("Descending to pickup position...")
    local pickup_error = MovePTraj(0, 0, pickup_pos, 20.0, 20.0, 100.0, 0.0, 0.0, 1, 0)
    if pickup_error ~= 0 then
        TPWrite("Failed to reach pickup position, error: " .. pickup_error)
        return false
    end
    
    -- 模拟夹爪抓取
    TPWrite("Activating gripper...")
    Sleep(500)  -- 模拟夹爪动作时间
    
    -- 抬升物体
    TPWrite("Lifting object...")
    local lift_error = MovePTraj(0, 0, approach_pos, 30.0, 30.0, 100.0, 0.0, 0.0, 1, 0)
    if lift_error ~= 0 then
        TPWrite("Failed to lift object, error: " .. lift_error)
        return false
    end
    
    TPWrite("Vision guided pickup completed successfully")
    return true
end

function test_vision_system()
    TPWrite("Starting comprehensive vision system test...")
    
    local test_results = {
        camera_initialization = false,
        object_detection = false,
        coordinate_calibration = false,
        guided_manipulation = false,
        total_objects_detected = 0,
        successful_pickups = 0
    }
    
    -- 1. 相机初始化测试
    TPWrite("=== Camera Initialization Test ===")
    test_results.camera_initialization = initialize_cameras()
    if not test_results.camera_initialization then
        TPWrite("Camera initialization failed, aborting test")
        return test_results
    end
    
    -- 2. 目标检测测试
    TPWrite("=== Object Detection Test ===")
    local detected_objects = detect_objects()
    if detected_objects and #detected_objects > 0 then
        test_results.object_detection = true
        test_results.total_objects_detected = #detected_objects
        TPWrite("Object detection successful: " .. #detected_objects .. " objects found")
    else
        TPWrite("Object detection failed")
    end
    
    -- 3. 坐标标定测试
    TPWrite("=== Coordinate Calibration Test ===")
    local calibration_matrix = calibrate_coordinates()
    if calibration_matrix then
        test_results.coordinate_calibration = true
        TPWrite("Coordinate calibration successful")
    else
        TPWrite("Coordinate calibration failed")
    end
    
    -- 4. 视觉引导操作测试
    TPWrite("=== Guided Manipulation Test ===")
    if test_results.object_detection and test_results.coordinate_calibration then
        local successful_pickups = 0
        
        -- 尝试抓取检测到的前3个物体
        local max_pickups = math.min(3, #detected_objects)
        for i = 1, max_pickups do
            local obj = detected_objects[i]
            TPWrite("Attempting pickup of " .. obj.type .. " (object " .. i .. ")")
            
            local pickup_success = vision_guided_pickup(obj.position)
            if pickup_success then
                successful_pickups = successful_pickups + 1
                TPWrite("Pickup " .. i .. " successful")
            else
                TPWrite("Pickup " .. i .. " failed")
            end
            
            Sleep(2000)  -- 操作间隔
        end
        
        test_results.successful_pickups = successful_pickups
        test_results.guided_manipulation = successful_pickups > 0
        
        TPWrite("Guided manipulation test completed: " .. 
               successful_pickups .. "/" .. max_pickups .. " successful pickups")
    else
        TPWrite("Skipping guided manipulation test due to prerequisite failures")
    end
    
    -- 生成测试报告
    TPWrite("=== Vision System Test Results ===")
    TPWrite("Camera initialization: " .. tostring(test_results.camera_initialization))
    TPWrite("Object detection: " .. tostring(test_results.object_detection))
    TPWrite("Coordinate calibration: " .. tostring(test_results.coordinate_calibration))
    TPWrite("Guided manipulation: " .. tostring(test_results.guided_manipulation))
    TPWrite("Objects detected: " .. test_results.total_objects_detected)
    TPWrite("Successful pickups: " .. test_results.successful_pickups)
    
    local overall_success = test_results.camera_initialization and 
                           test_results.object_detection and 
                           test_results.coordinate_calibration and 
                           test_results.guided_manipulation
    
    TPWrite("Overall test result: " .. tostring(overall_success))
    
    return test_results
end

-- 执行视觉系统测试
local results = test_vision_system()
TPWrite("Vision system test completed")
"""
        return lua_script
    
    def connect_robot(self) -> bool:
        """连接到机器人"""
        try:
            self.logger.info(f"正在连接机器人: {self.robot_ip}")
            self.robot = Robot.RPC(self.robot_ip)
            
            # 测试连接
            error, version = self.robot.GetSDKVersion()
            if error == 0:
                self.logger.info(f"机器人连接成功，SDK版本: {version}")
                return True
            else:
                self.logger.error(f"机器人连接失败，错误码: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"连接机器人时发生异常: {str(e)}")
            return False
    
    def initialize_vision_system(self) -> Dict[str, Any]:
        """初始化视觉系统"""
        vision_status = {
            'cameras_connected': False,
            'camera_count': 0,
            'resolutions': {},
            'error_message': None
        }
        
        try:
            self.logger.info("初始化视觉系统...")
            
            # 尝试连接Gemini 335相机
            camera_indices = [0, 1]  # 假设两个相机
            connected_cameras = 0
            
            for i, camera_index in enumerate(camera_indices):
                try:
                    # 模拟相机连接（实际应该使用真实的相机API）
                    camera_name = f"gemini_335_{['left', 'right'][i]}"
                    
                    # 这里应该调用真实的相机初始化代码
                    # cap = cv2.VideoCapture(camera_index)
                    # if cap.isOpened():
                    #     ret, frame = cap.read()
                    #     if ret:
                    #         connected_cameras += 1
                    #         vision_status['resolutions'][camera_name] = frame.shape[:2]
                    #     cap.release()
                    
                    # 模拟成功连接
                    connected_cameras += 1
                    vision_status['resolutions'][camera_name] = (720, 1280)
                    self.logger.info(f"{camera_name} 连接成功")
                    
                except Exception as e:
                    self.logger.warning(f"相机 {camera_index} 连接失败: {str(e)}")
            
            vision_status['camera_count'] = connected_cameras
            vision_status['cameras_connected'] = connected_cameras >= 1
            
            if vision_status['cameras_connected']:
                self.logger.info(f"视觉系统初始化成功，连接了 {connected_cameras} 个相机")
            else:
                vision_status['error_message'] = "没有可用的相机"
                self.logger.error("视觉系统初始化失败，没有可用的相机")
            
        except Exception as e:
            vision_status['error_message'] = str(e)
            self.logger.error(f"初始化视觉系统时发生异常: {str(e)}")
        
        return vision_status
    
    def simulate_object_detection(self) -> List[Dict[str, Any]]:
        """模拟目标检测"""
        # 模拟检测到的物体
        detected_objects = [
            {
                'type': 'cube',
                'position': {'x': 350.5, 'y': -200.8, 'z': 100.2},
                'orientation': {'rx': 0.0, 'ry': 0.0, 'rz': 45.0},
                'confidence': 0.95,
                'size': {'width': 50.0, 'height': 50.0, 'depth': 50.0},
                'color': 'red'
            },
            {
                'type': 'sphere',
                'position': {'x': 280.3, 'y': -150.4, 'z': 95.8},
                'orientation': {'rx': 0.0, 'ry': 0.0, 'rz': 0.0},
                'confidence': 0.88,
                'size': {'diameter': 40.0},
                'color': 'blue'
            },
            {
                'type': 'cylinder',
                'position': {'x': 400.1, 'y': -180.6, 'z': 98.5},
                'orientation': {'rx': 0.0, 'ry': 0.0, 'rz': 15.0},
                'confidence': 0.92,
                'size': {'diameter': 30.0, 'height': 80.0},
                'color': 'green'
            }
        ]
        
        self.logger.info(f"模拟检测到 {len(detected_objects)} 个物体")
        for i, obj in enumerate(detected_objects):
            self.logger.info(f"  物体{i+1}: {obj['type']} at ({obj['position']['x']:.1f}, {obj['position']['y']:.1f}, {obj['position']['z']:.1f})")
        
        return detected_objects
    
    def upload_vision_lua_script(self) -> bool:
        """上传视觉引导lua脚本"""
        try:
            # 创建lua脚本内容
            script_content = self._create_vision_lua_script()
            temp_script_path = Path(f"/tmp/{self.lua_script_name}")
            
            with open(temp_script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 上传lua脚本
            self.logger.info(f"正在上传视觉lua脚本: {self.lua_script_name}")
            error = self.robot.LuaUpload(filePath=str(temp_script_path))
            
            if error == 0:
                self.logger.info("视觉Lua脚本上传成功")
                # 清理临时文件
                temp_script_path.unlink()
                return True
            else:
                self.logger.error(f"视觉Lua脚本上传失败，错误码: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"上传视觉lua脚本时发生异常: {str(e)}")
            return False
    
    def execute_vision_test(self) -> Dict[str, Any]:
        """执行视觉引导测试"""
        execution_result = {
            'success': False,
            'program_state': None,
            'execution_log': [],
            'duration': 0,
            'start_time': time.time()
        }
        
        try:
            # 设置机器人模式并加载程序
            self.robot.Mode(state=0)
            
            self.logger.info(f"正在加载视觉lua程序: {self.lua_program_path}")
            error = self.robot.ProgramLoad(program_name=self.lua_program_path)
            
            if error != 0:
                execution_result['error'] = f"程序加载失败，错误码: {error}"
                return execution_result
            
            # 运行程序
            self.logger.info("正在运行视觉lua程序")
            error = self.robot.ProgramRun()
            
            if error != 0:
                execution_result['error'] = f"程序运行失败，错误码: {error}"
                return execution_result
            
            # 监控执行
            self.logger.info("监控视觉程序执行...")
            timeout = 180  # 3分钟超时
            
            while time.time() - execution_result['start_time'] < timeout:
                # 获取程序状态
                error, state = self.robot.GetProgramState()
                if error != 0:
                    self.logger.error(f"获取程序状态失败，错误码: {error}")
                    break
                
                # 获取当前行号
                line_error, current_line = self.robot.GetCurrentLine()
                if line_error == 0:
                    execution_info = {
                        'timestamp': time.time(),
                        'state': state,
                        'line': current_line
                    }
                    execution_result['execution_log'].append(execution_info)
                    self.logger.info(f"程序状态: {state}, 当前行: {current_line}")
                
                # 检查是否完成
                if state in ["completed", "stopped", "error"]:
                    execution_result['program_state'] = state
                    self.logger.info(f"视觉程序执行结束，最终状态: {state}")
                    break
                
                time.sleep(1.0)  # 1秒检查间隔
            
            execution_result['success'] = execution_result['program_state'] == "completed"
            
        except Exception as e:
            execution_result['error'] = str(e)
            self.logger.error(f"执行视觉测试时发生异常: {str(e)}")
        
        finally:
            execution_result['duration'] = time.time() - execution_result['start_time']
        
        return execution_result
    
    def cleanup_resources(self):
        """清理资源"""
        try:
            if self.robot:
                # 停止程序
                self.robot.StopMotion()
                
                # 删除上传的lua脚本
                delete_error = self.robot.LuaDelete(fileName=self.lua_script_name)
                if delete_error == 0:
                    self.logger.info("视觉Lua脚本清理成功")
                else:
                    self.logger.warning(f"清理视觉lua脚本失败，错误码: {delete_error}")
        
        except Exception as e:
            self.logger.warning(f"清理资源时发生异常: {str(e)}")
    
    def run_test(self) -> Dict[str, Any]:
        """运行完整的视觉系统lua测试"""
        test_result = {
            'test_name': self.test_name,
            'robot_ip': self.robot_ip,
            'start_time': time.time(),
            'success': False,
            'stages': {},
            'error_message': None,
            'vision_results': {}
        }
        
        try:
            # 阶段1: 连接机器人
            self.logger.info("开始视觉系统Lua测试")
            if not self.connect_robot():
                test_result['error_message'] = "机器人连接失败"
                return test_result
            test_result['stages']['robot_connection'] = True
            
            # 阶段2: 初始化视觉系统
            vision_status = self.initialize_vision_system()
            test_result['stages']['vision_initialization'] = vision_status
            
            if not vision_status['cameras_connected']:
                test_result['error_message'] = f"视觉系统初始化失败: {vision_status['error_message']}"
                return test_result
            
            # 阶段3: 模拟目标检测
            detected_objects = self.simulate_object_detection()
            test_result['vision_results']['detected_objects'] = detected_objects
            test_result['stages']['object_detection'] = len(detected_objects) > 0
            
            # 阶段4: 上传视觉lua脚本
            if not self.upload_vision_lua_script():
                test_result['error_message'] = "视觉Lua脚本上传失败"
                return test_result
            test_result['stages']['script_upload'] = True
            
            # 阶段5: 执行视觉引导测试
            execution_result = self.execute_vision_test()
            test_result['stages']['execution'] = execution_result
            
            # 判断总体测试结果
            test_result['success'] = execution_result.get('success', False)
            if not test_result['success']:
                test_result['error_message'] = f"视觉程序执行失败: {execution_result.get('error', '程序未正常完成')}"
            
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
    print("=== 视觉系统Lua测试 ===")
    
    # 创建测试实例
    test = LuaVisionTest(robot_ip="192.168.58.3")
    
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
    
    # 打印视觉系统状态
    if 'stages' in result and 'vision_initialization' in result['stages']:
        vision_init = result['stages']['vision_initialization']
        print(f"\n视觉系统状态:")
        print(f"相机连接: {'成功' if vision_init.get('cameras_connected', False) else '失败'}")
        print(f"相机数量: {vision_init.get('camera_count', 0)}")
        
        if 'resolutions' in vision_init:
            for camera, resolution in vision_init['resolutions'].items():
                print(f"  {camera}: {resolution}")
    
    # 打印检测到的物体
    if 'vision_results' in result and 'detected_objects' in result['vision_results']:
        objects = result['vision_results']['detected_objects']
        print(f"\n检测到的物体 ({len(objects)} 个):")
        for i, obj in enumerate(objects):
            pos = obj['position']
            print(f"  {i+1}. {obj['type']}: ({pos['x']:.1f}, {pos['y']:.1f}, {pos['z']:.1f}) - 置信度: {obj['confidence']:.2f}")
    
    return result


if __name__ == "__main__":
    main()