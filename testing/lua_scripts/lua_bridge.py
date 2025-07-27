#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lua测试桥接器
用于Web GUI和Lua测试脚本之间的通信
"""

import os
import sys
import json
import subprocess
import logging
from typing import Dict, Any, Optional

class LuaBridge:
    """Lua测试脚本桥接器"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.lua_script_path = os.path.join(self.project_root, 'testing/lua_scripts/test_bridge.lua')
        self.setup_logging()
        
    def setup_logging(self):
        """配置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def call_lua_script(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用Lua测试脚本"""
        try:
            if params is None:
                params = {}
                
            # 准备参数
            params_json = json.dumps(params)
            
            # 执行Lua脚本
            cmd = ['lua', self.lua_script_path, action, params_json]
            self.logger.info(f"执行Lua命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                try:
                    output_data = json.loads(result.stdout)
                    return {
                        'status': 'success',
                        'data': output_data
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'success',
                        'data': {'output': result.stdout}
                    }
            else:
                self.logger.error(f"Lua脚本执行失败: {result.stderr}")
                return {
                    'status': 'error',
                    'message': result.stderr,
                    'stdout': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("Lua脚本执行超时")
            return {
                'status': 'error',
                'message': '脚本执行超时'
            }
        except Exception as e:
            self.logger.error(f"调用Lua脚本异常: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def test_connection(self, device_type: str, device_ip: str = None) -> Dict[str, Any]:
        """测试设备连接"""
        params = {
            'device_type': device_type,
            'device_ip': device_ip
        }
        return self.call_lua_script('test_connection', params)
    
    def run_test_program(self, test_type: str, test_file: str = None) -> Dict[str, Any]:
        """运行测试程序"""
        params = {
            'test_type': test_type,
            'test_file': test_file or 'default.py'
        }
        return self.call_lua_script('run_test_program', params)
    
    def validate_test_safety(self, test_type: str, test_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """验证测试安全性"""
        params = {
            'test_type': test_type,
            'test_params': test_params or {}
        }
        return self.call_lua_script('validate_safety', params)
    
    def get_test_results(self) -> Dict[str, Any]:
        """获取测试结果"""
        return self.call_lua_script('get_test_results')
    
    def get_system_logs(self, filter_level: str = 'all', max_lines: int = 100) -> Dict[str, Any]:
        """获取系统日志"""
        params = {
            'filter_level': filter_level,
            'max_lines': max_lines
        }
        return self.call_lua_script('get_system_logs', params)

class TestProgramManager:
    """测试程序管理器"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.lua_bridge = LuaBridge()
        self.test_categories = {
            'chassis_test': {
                'name': '底盘测试',
                'programs': [
                    'chassis_connection_test.py',
                    'chassis_movement_test.py',
                    'chassis_navigation_test.py'
                ]
            },
            'left_arm_test': {
                'name': '左臂测试',
                'programs': [
                    'SAT001.py',  # 连接测试
                    'SAT002.py',  # 基础运动
                    'SAT003.py',  # 笛卡尔运动
                    'SAT004.py'   # 工作空间
                ]
            },
            'right_arm_test': {
                'name': '右臂测试',
                'programs': [
                    'SAT001.py',
                    'SAT002.py',
                    'SAT003.py',
                    'SAT004.py'
                ]
            },
            'dual_arm_test': {
                'name': '双臂协作测试',
                'programs': [
                    'DAT001.py',  # 同步连接
                    'DAT002.py',  # 安全距离
                    'dual_arm_cooperation.py'
                ]
            },
            'function_validation': {
                'name': '功能验证测试',
                'programs': [
                    'arm_function_test.py',
                    'chassis_function_test.py',
                    'vision_function_test.py'
                ]
            },
            'integration_test': {
                'name': '集成测试',
                'programs': [
                    'dual_arm_realtime_monitor.py',
                    'chassis_relative_move.py',
                    'system_integration_test.py'
                ]
            },
            'scenario_test': {
                'name': '场景测试',
                'programs': [
                    'pickup_scenario.py',
                    'assembly_scenario.py',
                    'inspection_scenario.py'
                ]
            }
        }
    
    def get_test_categories(self) -> Dict[str, Any]:
        """获取测试分类"""
        return self.test_categories
    
    def get_test_programs(self, category: str) -> List[str]:
        """获取指定分类的测试程序"""
        return self.test_categories.get(category, {}).get('programs', [])
    
    def validate_test_file(self, test_file: str) -> Dict[str, Any]:
        """验证测试文件"""
        result = {
            'valid': False,
            'message': '',
            'safety_warnings': [],
            'function_description': ''
        }
        
        # 检查文件是否存在
        possible_paths = [
            os.path.join(self.project_root, 'testing/hardware', test_file),
            os.path.join(self.project_root, 'testing/integration', test_file),
            os.path.join(self.project_root, 'testing/functional', test_file),
            os.path.join(self.project_root, 'testing/scenarios', test_file)
        ]
        
        file_found = False
        file_path = None
        
        for path in possible_paths:
            if os.path.exists(path):
                file_found = True
                file_path = path
                break
        
        if not file_found:
            result['message'] = f'测试文件不存在: {test_file}'
            return result
        
        try:
            # 读取文件内容进行分析
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基本安全检查
            safety_warnings = []
            
            if 'MoveJ' in content or 'MoveL' in content:
                safety_warnings.append('此程序包含机械臂运动指令，请确保周围安全')
            
            if 'move_to_position' in content:
                safety_warnings.append('此程序包含底盘移动指令，请确保移动路径畅通')
            
            if 'RobotEnable' in content:
                safety_warnings.append('此程序会使能机器人，请确保急停按钮可用')
            
            # 提取函数描述
            function_description = "标准测试程序"
            
            if '测试目的:' in content:
                lines = content.split('\n')
                for line in lines:
                    if '测试目的:' in line:
                        function_description = line.split('测试目的:')[-1].strip()
                        break
            
            result.update({
                'valid': True,
                'message': '测试文件验证通过',
                'safety_warnings': safety_warnings,
                'function_description': function_description,
                'file_path': file_path
            })
            
        except Exception as e:
            result['message'] = f'文件读取错误: {str(e)}'
        
        return result

def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法: python lua_bridge.py <action> [params...]")
        print("支持的操作:")
        print("  test_connection <device_type> [device_ip]")
        print("  run_test <test_type> [test_file]")
        print("  validate_safety <test_type>")
        print("  get_results")
        print("  get_logs [filter_level] [max_lines]")
        return
    
    bridge = LuaBridge()
    action = sys.argv[1]
    
    if action == 'test_connection':
        if len(sys.argv) >= 3:
            device_type = sys.argv[2]
            device_ip = sys.argv[3] if len(sys.argv) >= 4 else None
            result = bridge.test_connection(device_type, device_ip)
        else:
            result = {'status': 'error', 'message': '缺少设备类型参数'}
    
    elif action == 'run_test':
        if len(sys.argv) >= 3:
            test_type = sys.argv[2]
            test_file = sys.argv[3] if len(sys.argv) >= 4 else None
            result = bridge.run_test_program(test_type, test_file)
        else:
            result = {'status': 'error', 'message': '缺少测试类型参数'}
    
    elif action == 'validate_safety':
        if len(sys.argv) >= 3:
            test_type = sys.argv[2]
            result = bridge.validate_test_safety(test_type)
        else:
            result = {'status': 'error', 'message': '缺少测试类型参数'}
    
    elif action == 'get_results':
        result = bridge.get_test_results()
    
    elif action == 'get_logs':
        filter_level = sys.argv[2] if len(sys.argv) >= 3 else 'all'
        max_lines = int(sys.argv[3]) if len(sys.argv) >= 4 else 100
        result = bridge.get_system_logs(filter_level, max_lines)
    
    else:
        result = {'status': 'error', 'message': f'未知操作: {action}'}
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()