#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控程序动作分析器
用于分析主控程序中的机械臂和底盘动作，提取仿真数据
"""

import ast
import re
import json
from typing import List, Dict, Any, Tuple

class ProgramAnalyzer:
    """程序分析器"""
    
    def __init__(self):
        self.arm_actions = []  # 机械臂动作序列
        self.chassis_actions = []  # 底盘动作序列
        self.current_left_joints = [0, 0, 0, 0, 0, 0]
        self.current_right_joints = [0, 0, 0, 0, 0, 0]
        self.current_chassis_pos = [0, 0, 0]  # x, y, angle
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析程序文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分析Python代码
            result = self.analyze_python_code(content)
            
            return {
                'success': True,
                'arm_actions': self.arm_actions,
                'chassis_actions': self.chassis_actions,
                'total_actions': len(self.arm_actions) + len(self.chassis_actions),
                'analysis_result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'arm_actions': [],
                'chassis_actions': []
            }
    
    def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """分析Python代码"""
        try:
            # 解析AST
            tree = ast.parse(code)
            
            # 遍历AST节点
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    self.analyze_function_call(node)
            
            # 同时使用正则表达式分析
            self.analyze_with_regex(code)
            
            return {
                'parsed_successfully': True,
                'total_nodes': len(list(ast.walk(tree)))
            }
            
        except SyntaxError as e:
            # 如果AST解析失败，只使用正则表达式
            self.analyze_with_regex(code)
            return {
                'parsed_successfully': False,
                'syntax_error': str(e),
                'fallback_to_regex': True
            }
    
    def analyze_function_call(self, node: ast.Call):
        """分析函数调用"""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            
            # 机械臂动作
            if func_name in ['MoveJ', 'MoveL', 'MoveC', 'Circle']:
                self.extract_arm_movement(node, func_name)
            
            # 底盘动作  
            elif func_name in ['move_to_point', 'rotate_to_angle', 'move_forward', 'move_backward']:
                self.extract_chassis_movement(node, func_name)
    
    def extract_arm_movement(self, node: ast.Call, func_name: str):
        """提取机械臂动作"""
        try:
            # 提取参数
            args = []
            for arg in node.args:
                if isinstance(arg, ast.List):
                    # 解析列表参数（关节角度或坐标）
                    values = []
                    for elt in arg.elts:
                        if isinstance(elt, ast.Constant):
                            values.append(elt.value)
                        elif isinstance(elt, ast.Num):  # Python 3.7及以下
                            values.append(elt.n)
                    args.append(values)
                elif isinstance(elt, ast.Constant):
                    args.append(elt.value)
                elif isinstance(elt, ast.Num):
                    args.append(elt.n)
            
            # 创建动作记录
            action = {
                'type': 'arm_movement',
                'function': func_name,
                'timestamp': len(self.arm_actions) * 0.5,  # 假设每个动作0.5秒
                'parameters': args
            }
            
            # 根据动作类型更新关节状态
            if func_name == 'MoveJ' and len(args) > 0 and len(args[0]) == 6:
                # 假设是左臂（可以根据实际情况调整）
                self.current_left_joints = args[0][:]
                action['joints'] = args[0][:]
                action['arm'] = 'left'
            
            self.arm_actions.append(action)
            
        except Exception as e:
            # 如果解析失败，创建基本记录
            action = {
                'type': 'arm_movement',
                'function': func_name,
                'timestamp': len(self.arm_actions) * 0.5,
                'parameters': [],
                'parse_error': str(e)
            }
            self.arm_actions.append(action)
    
    def extract_chassis_movement(self, node: ast.Call, func_name: str):
        """提取底盘动作"""
        try:
            # 提取参数
            args = []
            for arg in node.args:
                if isinstance(arg, ast.Constant):
                    args.append(arg.value)
                elif isinstance(arg, ast.Num):
                    args.append(arg.n)
            
            # 创建动作记录
            action = {
                'type': 'chassis_movement',
                'function': func_name,
                'timestamp': len(self.chassis_actions) * 1.0,  # 假设每个动作1秒
                'parameters': args
            }
            
            # 根据动作类型更新底盘状态
            if func_name == 'move_to_point' and len(args) >= 2:
                self.current_chassis_pos[0] = args[0]
                self.current_chassis_pos[1] = args[1]
                action['position'] = [args[0], args[1]]
            elif func_name == 'rotate_to_angle' and len(args) >= 1:
                self.current_chassis_pos[2] = args[0]
                action['angle'] = args[0]
            
            self.chassis_actions.append(action)
            
        except Exception as e:
            action = {
                'type': 'chassis_movement',
                'function': func_name,
                'timestamp': len(self.chassis_actions) * 1.0,
                'parameters': [],
                'parse_error': str(e)
            }
            self.chassis_actions.append(action)
    
    def analyze_with_regex(self, code: str):
        """使用正则表达式分析代码"""
        # 机械臂动作模式
        arm_patterns = [
            r'robot\.MoveJ\s*\(\s*([^)]+)\)',
            r'robot\.MoveL\s*\(\s*([^)]+)\)',
            r'robot\.MoveC\s*\(\s*([^)]+)\)',
            r'left_arm\.MoveJ\s*\(\s*([^)]+)\)',
            r'right_arm\.MoveJ\s*\(\s*([^)]+)\)',
        ]
        
        for pattern in arm_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                self.parse_arm_action_from_string(match.group(0), match.group(1))
        
        # 底盘动作模式
        chassis_patterns = [
            r'chassis\.move_to_point\s*\(\s*([^)]+)\)',
            r'chassis\.rotate_to_angle\s*\(\s*([^)]+)\)',
            r'move_to_poi\s*\(\s*([^)]+)\)',
        ]
        
        for pattern in chassis_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                self.parse_chassis_action_from_string(match.group(0), match.group(1))
    
    def parse_arm_action_from_string(self, full_match: str, params_str: str):
        """从字符串解析机械臂动作"""
        try:
            # 提取函数名
            func_name = full_match.split('(')[0].split('.')[-1]
            
            # 简单参数解析
            # 查找列表模式 [x, y, z, ...]
            list_pattern = r'\[([^\]]+)\]'
            lists = re.findall(list_pattern, params_str)
            
            joint_values = []
            if lists:
                # 解析第一个列表作为关节角度
                values_str = lists[0]
                numbers = re.findall(r'-?\d+\.?\d*', values_str)
                joint_values = [float(n) for n in numbers]
            
            action = {
                'type': 'arm_movement',
                'function': func_name,
                'timestamp': len(self.arm_actions) * 0.5,
                'parameters': [joint_values] if joint_values else [],
                'source': 'regex'
            }
            
            if len(joint_values) == 6:
                action['joints'] = joint_values
                # 判断是左臂还是右臂（简单判断）
                if 'left' in full_match.lower():
                    action['arm'] = 'left'
                    self.current_left_joints = joint_values[:]
                elif 'right' in full_match.lower():
                    action['arm'] = 'right'
                    self.current_right_joints = joint_values[:]
                else:
                    action['arm'] = 'left'  # 默认左臂
                    self.current_left_joints = joint_values[:]
            
            self.arm_actions.append(action)
            
        except Exception as e:
            action = {
                'type': 'arm_movement',
                'function': 'unknown',
                'timestamp': len(self.arm_actions) * 0.5,
                'parameters': [],
                'parse_error': str(e),
                'source': 'regex'
            }
            self.arm_actions.append(action)
    
    def parse_chassis_action_from_string(self, full_match: str, params_str: str):
        """从字符串解析底盘动作"""
        try:
            # 提取函数名
            func_name = full_match.split('(')[0].split('.')[-1]
            
            # 解析数字参数
            numbers = re.findall(r'-?\d+\.?\d*', params_str)
            params = [float(n) for n in numbers]
            
            action = {
                'type': 'chassis_movement',
                'function': func_name,
                'timestamp': len(self.chassis_actions) * 1.0,
                'parameters': params,
                'source': 'regex'
            }
            
            # 更新底盘状态
            if func_name == 'move_to_point' and len(params) >= 2:
                self.current_chassis_pos[0] = params[0]
                self.current_chassis_pos[1] = params[1]
                action['position'] = [params[0], params[1]]
            elif func_name == 'rotate_to_angle' and len(params) >= 1:
                self.current_chassis_pos[2] = params[0]
                action['angle'] = params[0]
            
            self.chassis_actions.append(action)
            
        except Exception as e:
            action = {
                'type': 'chassis_movement',
                'function': 'unknown',
                'timestamp': len(self.chassis_actions) * 1.0,
                'parameters': [],
                'parse_error': str(e),
                'source': 'regex'
            }
            self.chassis_actions.append(action)
    
    def get_animation_sequence(self) -> List[Dict[str, Any]]:
        """获取动画序列"""
        # 合并机械臂和底盘动作，按时间排序
        all_actions = self.arm_actions + self.chassis_actions
        all_actions.sort(key=lambda x: x.get('timestamp', 0))
        
        return all_actions
    
    def get_chassis_path(self) -> List[Tuple[float, float, float]]:
        """获取底盘路径"""
        path = []
        current_pos = [0, 0, 0]
        
        for action in self.chassis_actions:
            if action['type'] == 'chassis_movement':
                if 'position' in action:
                    current_pos[0] = action['position'][0]
                    current_pos[1] = action['position'][1]
                if 'angle' in action:
                    current_pos[2] = action['angle']
                
                path.append((current_pos[0], current_pos[1], current_pos[2]))
        
        return path
    
    def get_arm_joint_sequence(self, arm: str = 'left') -> List[List[float]]:
        """获取机械臂关节序列"""
        sequence = []
        current_joints = [0, 0, 0, 0, 0, 0]
        
        for action in self.arm_actions:
            if action['type'] == 'arm_movement' and action.get('arm') == arm:
                if 'joints' in action:
                    current_joints = action['joints'][:]
                sequence.append(current_joints[:])
        
        return sequence

def test_analyzer():
    """测试分析器"""
    # 测试代码
    test_code = """
import sys
from Robot import Robot

# 创建机器人实例
robot = Robot.RPC('192.168.58.2')

# 机械臂动作
robot.MoveJ([0, -30, -60, -90, 0, 0], tool=0, user=0, vel=30)
robot.MoveL([327.359, -420.973, 518.377, -177.199, 3.209, 114.449], tool=0, user=0, vel=30)
robot.MoveJ([28.166, -108.269, -59.859, -87, 94.532, -0.7], tool=0, user=0, vel=30)

# 底盘动作
chassis.move_to_point(100, 200)
chassis.rotate_to_angle(90)
chassis.move_to_point(300, 400)
"""
    
    analyzer = ProgramAnalyzer()
    result = analyzer.analyze_python_code(test_code)
    
    print("分析结果:")
    print(f"解析成功: {result['parsed_successfully']}")
    print(f"机械臂动作数: {len(analyzer.arm_actions)}")
    print(f"底盘动作数: {len(analyzer.chassis_actions)}")
    
    print("\n机械臂动作:")
    for action in analyzer.arm_actions:
        print(f"  {action['function']}: {action.get('joints', action['parameters'])}")
    
    print("\n底盘动作:")
    for action in analyzer.chassis_actions:
        print(f"  {action['function']}: {action['parameters']}")
    
    print(f"\n底盘路径: {analyzer.get_chassis_path()}")

if __name__ == "__main__":
    test_analyzer()