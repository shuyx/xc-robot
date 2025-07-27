#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT Web测试API
为Web GUI提供REST API接口，调用Lua测试脚本
"""

import os
import sys
import json
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from typing import Dict, Any

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'testing/lua_scripts'))

from lua_bridge import LuaBridge, TestProgramManager

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化组件
lua_bridge = LuaBridge()
test_manager = TestProgramManager()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/test/connection', methods=['POST'])
def test_connection():
    """测试设备连接API"""
    try:
        data = request.get_json()
        device_type = data.get('device_type')
        device_ip = data.get('device_ip')
        
        if not device_type:
            return jsonify({
                'status': 'error',
                'message': '缺少设备类型参数'
            }), 400
        
        result = lua_bridge.test_connection(device_type, device_ip)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"连接测试API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test/run', methods=['POST'])
def run_test():
    """运行测试程序API"""
    try:
        data = request.get_json()
        test_type = data.get('test_type')
        test_file = data.get('test_file')
        
        if not test_type:
            return jsonify({
                'status': 'error',
                'message': '缺少测试类型参数'
            }), 400
        
        # 先进行安全校验
        safety_result = lua_bridge.validate_test_safety(test_type, data)
        
        if not safety_result.get('data', {}).get('approved', False):
            return jsonify({
                'status': 'safety_check_failed',
                'message': '安全校验未通过',
                'safety_result': safety_result
            }), 400
        
        # 执行测试
        result = lua_bridge.run_test_program(test_type, test_file)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"测试运行API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test/validate', methods=['POST'])
def validate_test():
    """验证测试安全性API"""
    try:
        data = request.get_json()
        test_type = data.get('test_type')
        test_params = data.get('test_params', {})
        
        if not test_type:
            return jsonify({
                'status': 'error',
                'message': '缺少测试类型参数'
            }), 400
        
        result = lua_bridge.validate_test_safety(test_type, test_params)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"安全验证API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test/file/validate', methods=['POST'])
def validate_test_file():
    """验证测试文件API"""
    try:
        data = request.get_json()
        test_file = data.get('test_file')
        
        if not test_file:
            return jsonify({
                'status': 'error',
                'message': '缺少测试文件参数'
            }), 400
        
        result = test_manager.validate_test_file(test_file)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"文件验证API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test/categories', methods=['GET'])
def get_test_categories():
    """获取测试分类API"""
    try:
        categories = test_manager.get_test_categories()
        return jsonify({
            'status': 'success',
            'data': categories
        })
        
    except Exception as e:
        logger.error(f"获取测试分类API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test/programs/<category>', methods=['GET'])
def get_test_programs(category):
    """获取指定分类的测试程序API"""
    try:
        programs = test_manager.get_test_programs(category)
        return jsonify({
            'status': 'success',
            'data': programs
        })
        
    except Exception as e:
        logger.error(f"获取测试程序API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test/results', methods=['GET'])
def get_test_results():
    """获取测试结果API"""
    try:
        result = lua_bridge.get_test_results()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取测试结果API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_system_logs():
    """获取系统日志API"""
    try:
        filter_level = request.args.get('level', 'all')
        max_lines = int(request.args.get('max_lines', 100))
        
        result = lua_bridge.get_system_logs(filter_level, max_lines)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取日志API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_api_status():
    """API状态检查"""
    return jsonify({
        'status': 'success',
        'message': 'XC-ROBOT Web测试API运行正常',
        'version': '1.0',
        'lua_bridge_available': lua_bridge is not None,
        'test_manager_available': test_manager is not None
    })

@app.route('/api/arm/move_joints', methods=['POST'])
def move_arm_joints():
    """机械臂关节运动API"""
    try:
        data = request.get_json()
        arm_side = data.get('arm_side')  # 'left' or 'right'
        joint_angles = data.get('joint_angles')  # [j1, j2, j3, j4, j5, j6]
        speed = data.get('speed', 20)
        
        if not arm_side or not joint_angles:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: arm_side 和 joint_angles'
            }), 400
        
        # 调用Lua控制脚本
        result = call_arm_control_lua('move_joints', {
            'arm_side': arm_side,
            'joint_angles': joint_angles,
            'speed': speed
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"机械臂关节运动API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/arm/move_cartesian', methods=['POST'])
def move_arm_cartesian():
    """机械臂笛卡尔运动API"""
    try:
        data = request.get_json()
        arm_side = data.get('arm_side')
        position = data.get('position')  # [x, y, z]
        orientation = data.get('orientation')  # [rx, ry, rz]
        speed = data.get('speed', 100)
        motion_type = data.get('motion_type', 'joint')  # 'joint' or 'linear'
        
        if not arm_side or not position or not orientation:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: arm_side, position, orientation'
            }), 400
        
        # 调用Lua控制脚本
        result = call_arm_control_lua('move_cartesian', {
            'arm_side': arm_side,
            'position': position,
            'orientation': orientation,
            'speed': speed,
            'motion_type': motion_type
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"机械臂笛卡尔运动API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/arm/status/<arm_side>', methods=['GET'])
def get_arm_status(arm_side):
    """获取机械臂状态API"""
    try:
        if arm_side not in ['left', 'right']:
            return jsonify({
                'status': 'error',
                'message': 'arm_side 必须是 left 或 right'
            }), 400
        
        # 调用Lua控制脚本
        result = call_arm_control_lua('get_status', {
            'arm_side': arm_side
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取机械臂状态API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/arm/enable', methods=['POST'])
def set_arm_enable():
    """机械臂使能/失能API"""
    try:
        data = request.get_json()
        arm_side = data.get('arm_side')
        enable = data.get('enable', True)
        
        if not arm_side:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: arm_side'
            }), 400
        
        # 调用Lua控制脚本
        result = call_arm_control_lua('set_enable', {
            'arm_side': arm_side,
            'enable': enable
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"机械臂使能API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/emergency_stop', methods=['POST'])
def emergency_stop():
    """紧急停止API"""
    try:
        data = request.get_json() or {}
        arm_side = data.get('arm_side')  # 可选，不指定则停止所有
        
        logger.warning("收到紧急停止请求")
        
        # 调用Lua紧急停止脚本
        result = call_arm_control_lua('emergency_stop', {
            'arm_side': arm_side
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"紧急停止API错误: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def call_arm_control_lua(action, params):
    """调用机械臂控制Lua脚本"""
    try:
        import subprocess
        import json
        
        # Lua脚本路径
        arm_control_script = os.path.join(project_root, 'testing/lua_scripts/arm_control.lua')
        
        # 参数JSON化
        params_json = json.dumps(params)
        
        # 执行Lua脚本
        cmd = ['lua', arm_control_script, action, params_json]
        logger.info(f"执行机械臂控制命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 机械臂运动可能需要较长时间
            cwd=project_root
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
            logger.error(f"Lua机械臂控制脚本执行失败: {result.stderr}")
            return {
                'status': 'error',
                'message': result.stderr,
                'stdout': result.stdout
            }
            
    except subprocess.TimeoutExpired:
        logger.error("Lua机械臂控制脚本执行超时")
        return {
            'status': 'error',
            'message': '机械臂控制执行超时'
        }
    except Exception as e:
        logger.error(f"调用Lua机械臂控制脚本异常: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def emergency_stop_fr3(ip):
    """FR3机械臂紧急停止"""
    try:
        # 这里应该调用FR3的紧急停止API
        # 简化实现
        import subprocess
        cmd = f"python -c \"from fairino import Robot; robot = Robot.RPC('{ip}'); robot.StopMotion()\""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            return {'status': 'success', 'message': 'FR3紧急停止成功'}
        else:
            return {'status': 'error', 'message': f'FR3停止失败: {result.stderr}'}
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def emergency_stop_chassis(ip):
    """底盘紧急停止"""
    try:
        import requests
        
        # 尝试停止当前动作
        stop_url = f"http://{ip}/api/core/motion/v1/stop"
        response = requests.post(stop_url, timeout=5)
        
        if response.status_code == 200:
            return {'status': 'success', 'message': '底盘紧急停止成功'}
        else:
            return {'status': 'error', 'message': f'底盘停止失败: {response.text}'}
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': '接口不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误'
    }), 500

def create_app():
    """创建Flask应用"""
    return app

if __name__ == '__main__':
    print("启动XC-ROBOT Web测试API服务器...")
    print("API端点:")
    print("  POST /api/test/connection - 测试设备连接")
    print("  POST /api/test/run - 运行测试程序")
    print("  POST /api/test/validate - 验证测试安全性")
    print("  POST /api/test/file/validate - 验证测试文件")
    print("  GET  /api/test/categories - 获取测试分类")
    print("  GET  /api/test/programs/<category> - 获取测试程序")
    print("  GET  /api/test/results - 获取测试结果")
    print("  GET  /api/logs - 获取系统日志")
    print("  GET  /api/status - API状态检查")
    print("  POST /api/emergency_stop - 紧急停止")
    print("\n服务器启动在 http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)