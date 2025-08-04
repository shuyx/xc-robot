#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级导航API调用脚本
基于Slamware RESTful API的精确导航和POI目标点导航
调用RoboStudio内置的导航规划功能
"""
import asyncio
import httpx
import json
import math
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 用户自定义运动序列
# 格式说明：
# - 字符串: POI名称 (如 "1", "home1", "22")
# - 字典: 等待命令 (如 {"wait": 5000} 表示等待5000毫秒即5秒)
USER_MOTION_SEQUENCE = [
    "1",               # 导航到POI "1"
    {"wait": 5000},    # 等待5秒
    "3",              # 导航到POI "22"
    {"wait": 5000},   # 等待14秒
    "home1"            # 最后返回home1
]

class AdvancedNavigationController:
    """高级导航控制器 - 调用RoboStudio内置导航功能"""
    
    def __init__(self, ip="192.168.31.211", port=1448):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.client = None
        self.connected = False
        self.pois = {}
        
        print(f"[初始化] 高级导航控制器: {self.base_url}")
        print("[INFO] 基于Slamware RESTful API v5.6，支持精确导航和POI目标点")
    
    async def connect(self):
        """连接底盘"""
        try:
            self.client = httpx.AsyncClient(timeout=10.0)
            
            # 测试连接 - 获取系统能力
            print("正在连接底盘...")
            response = await self.client.get(f"{self.base_url}/api/core/system/v1/capabilities")
            
            if response.status_code == 200:
                capabilities = response.json()
                print(f"[SUCCESS] 连接成功!")
                print(f"[INFO] 系统能力: {json.dumps(capabilities, indent=2, ensure_ascii=False)}")
                self.connected = True
                return True
            else:
                print(f"[ERROR] 连接失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 连接异常: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.aclose()
            self.connected = False
            print("[SUCCESS] 已断开连接")
    
    async def get_current_pose(self):
        """获取当前位姿"""
        if not self.connected:
            return None
        
        try:
            response = await self.client.get(f"{self.base_url}/api/core/slam/v1/localization/pose")
            if response.status_code == 200:
                pose = response.json()
                return {
                    'x': pose['x'],
                    'y': pose['y'],
                    'yaw': pose['yaw'],  # 弧度
                    'timestamp': datetime.now()
                }
        except Exception as e:
            print(f"[ERROR] 获取位姿失败: {e}")
        return None
    
    async def load_pois(self):
        """加载所有POI点位"""
        if not self.connected:
            return {}
        
        try:
            response = await self.client.get(f"{self.base_url}/api/core/artifact/v1/pois")
            if response.status_code == 200:
                poi_data = response.json()
                pois = {}
                
                print(f"[SUCCESS] 发现 {len(poi_data)} 个POI点位:")
                for i, poi in enumerate(poi_data, 1):
                    display_name = poi['metadata']['display_name']
                    poi_id = poi['id']
                    pose = poi['pose']
                    pois[display_name] = {
                        'id': poi_id,
                        'x': pose['x'],
                        'y': pose['y'],
                        'yaw': pose['yaw'],
                        'name': display_name
                    }
                    print(f"  {i}. {display_name} (ID: {poi_id}): ({pose['x']:.3f}, {pose['y']:.3f}, {math.degrees(pose['yaw']):.1f}°)")
                
                # 打印详细调试信息
                print(f"\n[DEBUG] POI详细信息:")
                for name, poi_info in pois.items():
                    print(f"  名称: '{name}' -> ID: '{poi_info['id']}'")
                
                self.pois = pois
                return pois
            else:
                print(f"[ERROR] 加载POI失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"[ERROR] POI加载异常: {e}")
            return {}
    
    async def move_to_action(self, target_x, target_y, target_yaw=None, with_yaw=True):
        """
        MoveToAction - 基础导航移动
        先使用简单的MoveToAction，如果成功再尝试更高级的功能
        """
        if not self.connected:
            return False
        
        try:
            # 构建MoveToAction请求（基于成功的脚本格式）
            payload = {
                "action_name": "slamtec.agent.actions.MoveToAction",
                "options": {
                    "target": {
                        "x": float(target_x),
                        "y": float(target_y),
                        "z": 0.0
                    }
                }
            }
            
            print(f"[MoveToAction] 目标: ({target_x:.3f}, {target_y:.3f})")
            if with_yaw and target_yaw is not None:
                print(f"[INFO] 目标角度: {math.degrees(target_yaw):.1f}°")
            print(f"[API] 调用: {payload['action_name']}")
            
            response = await self.client.post(
                f"{self.base_url}/api/core/motion/v1/actions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                action_id = result.get('action_id')
                print(f"[SUCCESS] 导航任务创建成功 - Action ID: {action_id}")
                
                if action_id:
                    # 监控导航进度
                    success = await self._monitor_navigation_action(action_id)
                    
                    # 如果需要精确角度控制，完成移动后再调整角度
                    if success and with_yaw and target_yaw is not None:
                        await asyncio.sleep(0.5)  # 等待移动稳定
                        return await self._adjust_final_angle(target_yaw)
                    
                    return success
                else:
                    print("[ERROR] 未获取到Action ID")
                    return False
            else:
                print(f"[ERROR] 导航任务创建失败: {response.status_code}")
                print(f"[ERROR] 响应内容: {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERROR] MoveToAction异常: {e}")
            return False
    
    async def multi_floor_move_action_poi(self, poi_name, pois_dict=None):
        """
        MultiFloorMoveAction - POI导航（使用测试验证通过的精确格式）
        自动处理角度，无需手动指定角度参数
        """
        if not self.connected:
            return False
        
        try:
            print(f"\n[MultiFloorMoveAction] 开始高精度POI导航到: {poi_name}")
            print(f"[INFO] 启用精确到角模式: with_yaw + 自由导航 (5cm精度)")
            
            # 先尝试POI名称，再尝试POI ID
            identifiers_to_try = [poi_name]
            if pois_dict and poi_name in pois_dict:
                poi_id = pois_dict[poi_name]['id']
                identifiers_to_try.append(poi_id)
                print(f"[DEBUG] POI '{poi_name}' 对应ID: '{poi_id}'")
            
            for i, identifier in enumerate(identifiers_to_try):
                identifier_type = "POI名称" if i == 0 else "POI ID" 
                print(f"\n[尝试] 使用{identifier_type}: '{identifier}'")
                
                # 使用完整的精确格式（包含move_options）
                payload = {
                    "action_name": "slamtec.agent.actions.MultiFloorMoveAction",
                    "options": {
                        "target": {
                            "poi_name": identifier
                        },
                        "move_options": {
                            "mode": 0,  # 自由导航模式(可靠性最高)
                            "flags": [
                                "with_yaw"     # 精确到角模式
                            ],
                            "acceptable_precision": 0.05,  # 5cm精度
                            "fail_retry_count": 2           # 失败重试2次
                        }
                    }
                }
                
                print(f"[格式] 使用精确到角格式（with_yaw + 自由导航）")
                print(f"[JSON] {json.dumps(payload, indent=2, ensure_ascii=False)}")
                
                response = await self.client.post(
                    f"{self.base_url}/api/core/motion/v1/actions",
                    json=payload
                )
                
                print(f"[结果] HTTP状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    action_id = result.get('action_id')
                    print(f"[SUCCESS] ✅ Action创建成功 - ID: {action_id}")
                    
                    if action_id:
                        # 监控导航执行
                        success = await self._monitor_navigation_action(action_id, timeout=90)
                        if success:
                            print(f"[SUCCESS] 🎯 MultiFloorMoveAction导航完成!")
                            return True
                        else:
                            print(f"[FAILED] 导航执行失败，尝试下一个标识符...")
                    else:
                        print("[ERROR] 未获取到Action ID")
                else:
                    print(f"[FAILED] Action创建失败: {response.status_code}")
                    if response.text:
                        print(f"[错误详情] {response.text}")
                    print(f"[INFO] 尝试下一个标识符...")
            
            print(f"[FAILED] 所有标识符都失败: {identifiers_to_try}")
            return False
                
        except Exception as e:
            print(f"[ERROR] MultiFloorMoveAction异常: {e}")
            return False
    
    async def multi_floor_move_action_coord(self, target_x, target_y, target_yaw=None, with_yaw=True):
        """
        MultiFloorMoveAction坐标导航 - 已证实不支持坐标参数
        自动降级使用MoveToAction进行坐标导航
        """
        print(f"[INFO] ⚠️  MultiFloorMoveAction不支持坐标导航（已通过测试验证）")
        print(f"[INFO] 🔄 自动降级使用MoveToAction进行坐标导航")
        
        # 直接使用MoveToAction，因为MultiFloorMoveAction不支持坐标
        return await self.move_to_action(target_x, target_y, target_yaw, with_yaw)
    
    async def _adjust_final_angle(self, target_yaw):
        """调整最终角度"""
        try:
            current_pose = await self.get_current_pose()
            if not current_pose:
                return True  # 无法获取当前角度，认为成功
            
            angle_error = abs(target_yaw - current_pose['yaw'])
            if angle_error > math.pi:
                angle_error = 2 * math.pi - angle_error
            
            if angle_error < 0.087:  # 小于5度，认为足够精确
                print(f"[角度] 当前角度已足够精确: {math.degrees(angle_error):.1f}°")
                return True
            
            print(f"[角度] 需要调整角度: {math.degrees(angle_error):.1f}°")
            
            # 使用RotateAction调整角度
            angle_diff = target_yaw - current_pose['yaw']
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            payload = {
                "action_name": "slamtec.agent.actions.RotateAction",
                "options": {
                    "angle": angle_diff
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/core/motion/v1/actions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                action_id = result.get('action_id')
                print(f"[角度] 角度调整任务创建成功 - ID: {action_id}")
                return await self._monitor_navigation_action(action_id, timeout=10)
            else:
                print(f"[角度] 角度调整失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[角度] 角度调整异常: {e}")
            return False
    
    async def navigate_to_poi(self, poi_name, pois, with_yaw=True):
        """
        导航到指定POI点位
        使用RoboStudio内置的导航规划
        """
        if poi_name not in pois:
            print(f"[ERROR] POI '{poi_name}' 不存在")
            available_pois = list(pois.keys())
            print(f"[INFO] 可用POI: {available_pois}")
            return False
        
        poi = pois[poi_name]
        print(f"\n[开始导航] 目标POI: {poi_name}")
        print(f"[目标位置] ({poi['x']:.6f}, {poi['y']:.6f}, {math.degrees(poi['yaw']):.3f}°)")
        
        # 获取当前位置
        current_pose = await self.get_current_pose()
        if current_pose:
            print(f"[当前位置] ({current_pose['x']:.6f}, {current_pose['y']:.6f}, {math.degrees(current_pose['yaw']):.3f}°)")
            
            # 计算距离
            dx = poi['x'] - current_pose['x']
            dy = poi['y'] - current_pose['y']
            distance = math.sqrt(dx*dx + dy*dy)
            print(f"[距离] {distance:.3f}米")
        
        # 分层导航策略
        target_yaw = poi['yaw'] if with_yaw else None
        success = False
        
        # 第一层：使用经过验证的MoveToAction（简单可靠）
        print("[第一层] 尝试基础MoveToAction导航...")
        success = await self.move_to_action(poi['x'], poi['y'], target_yaw, with_yaw)
        
        # 第二层：如果需要更高级功能，尝试POI名称导航
        if not success:
            print("[第二层] 尝试POI名称MultiFloorMoveAction导航...")
            success = await self.multi_floor_move_action_poi(poi_name, pois)
        
        # 第三层：坐标版本的MultiFloorMoveAction
        if not success:
            print("[第三层] 尝试坐标MultiFloorMoveAction导航...")
            success = await self.multi_floor_move_action_coord(
                poi['x'], poi['y'], target_yaw, with_yaw
            )
        
        if success:
            print(f"[SUCCESS] 成功导航到POI '{poi_name}'")
            
            # 验证最终位置
            await asyncio.sleep(1)
            final_pose = await self.get_current_pose()
            if final_pose:
                dx = poi['x'] - final_pose['x']
                dy = poi['y'] - final_pose['y']
                position_error = math.sqrt(dx*dx + dy*dy)
                angle_error = abs(poi['yaw'] - final_pose['yaw'])
                
                print(f"[最终位置] ({final_pose['x']:.6f}, {final_pose['y']:.6f}, {math.degrees(final_pose['yaw']):.3f}°)")
                print(f"[定位精度] 位置误差: {position_error*100:.1f}cm, 角度误差: {math.degrees(angle_error):.1f}°")
        else:
            print(f"[FAILED] 导航到POI '{poi_name}' 失败")
        
        return success
    
    async def navigate_to_coordinate(self, x, y, yaw=None, with_yaw=True):
        """
        导航到指定坐标
        使用RoboStudio内置的导航规划
        """
        print(f"\n[开始导航] 目标坐标: ({x:.3f}, {y:.3f})")
        if with_yaw and yaw is not None:
            print(f"[目标角度] {math.degrees(yaw):.1f}°")
        
        # 获取当前位置
        current_pose = await self.get_current_pose()
        if current_pose:
            print(f"[当前位置] ({current_pose['x']:.6f}, {current_pose['y']:.6f}, {math.degrees(current_pose['yaw']):.3f}°)")
            
            # 计算距离
            dx = x - current_pose['x']
            dy = y - current_pose['y']
            distance = math.sqrt(dx*dx + dy*dy)
            print(f"[距离] {distance:.3f}米")
        
        # 分层导航策略（坐标导航）
        success = False
        
        # 第一层：使用经过验证的MoveToAction（简单可靠）
        print("[第一层] 尝试基础MoveToAction导航...")
        success = await self.move_to_action(x, y, yaw, with_yaw)
        
        # 第二层：坐标版本的MultiFloorMoveAction
        if not success:
            print("[第二层] 尝试坐标MultiFloorMoveAction导航...")
            success = await self.multi_floor_move_action_coord(x, y, yaw, with_yaw)
        
        if success:
            print(f"[SUCCESS] 成功导航到目标坐标")
            
            # 验证最终位置
            await asyncio.sleep(1)
            final_pose = await self.get_current_pose()
            if final_pose:
                dx = x - final_pose['x']
                dy = y - final_pose['y']
                position_error = math.sqrt(dx*dx + dy*dy)
                
                print(f"[最终位置] ({final_pose['x']:.6f}, {final_pose['y']:.6f}, {math.degrees(final_pose['yaw']):.3f}°)")
                print(f"[定位精度] 位置误差: {position_error*100:.1f}cm")
                
                if with_yaw and yaw is not None:
                    angle_error = abs(yaw - final_pose['yaw'])
                    print(f"[角度精度] 角度误差: {math.degrees(angle_error):.1f}°")
        else:
            print(f"[FAILED] 导航到目标坐标失败")
        
        return success
    
    async def _monitor_navigation_action(self, action_id, timeout=60):
        """监控导航任务执行状态（参考成功脚本的监控逻辑）"""
        print(f"[监控] 开始监控导航任务 {action_id}")
        
        for i in range(timeout):  # 监控指定时长
            try:
                response = await self.client.get(
                    f"{self.base_url}/api/core/motion/v1/actions/{action_id}"
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    state = status_data.get('state', {})
                    status_code = state.get('status', 0)
                    reason = state.get('reason', '')
                    
                    # 使用和成功脚本相同的状态映射
                    status_names = {
                        0: "初始化",
                        1: "执行中", 
                        2: "暂停",
                        3: "取消",
                        4: "完成"
                    }
                    
                    current_status = status_names.get(status_code, f"未知状态({status_code})")
                    
                    # 显示策略：每5秒或状态变化时显示
                    if i % 5 == 0 or status_code in [3, 4]:
                        print(f"[监控] [{i+1}/{timeout}] 导航状态: {current_status}")
                        if reason:
                            print(f"        原因: {reason}")
                    
                    if status_code == 4:  # 完成
                        result_info = state.get('result', 0)
                        if result_info == 0:
                            print(f"[SUCCESS] 导航任务完成")
                            return True
                        else:
                            print(f"[FAILED] 导航任务失败，结果码: {result_info}")
                            return False
                    elif status_code == 3:  # 取消
                        print(f"[CANCELLED] 导航任务被取消")
                        return False
                        
            except Exception as e:
                print(f"[ERROR] 监控异常: {e}")
            
            await asyncio.sleep(1)
        
        print(f"[TIMEOUT] 导航监控超时")
        return False
    
    async def stop_all_actions(self):
        """停止所有运动"""
        if not self.connected:
            return False
        
        try:
            response = await self.client.post(f"{self.base_url}/api/core/motion/v1/stop")
            if response.status_code == 200:
                print("[SUCCESS] 已停止所有运动")
                return True
            else:
                print(f"[ERROR] 停止失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] 停止异常: {e}")
            return False
    
    def show_help(self):
        """显示帮助"""
        print("\n" + "="*80)
        print("                    分层导航API控制器")
        print("          MoveToAction优先 + MultiFloorMoveAction备选")
        print("="*80)
        print("  【POI导航模式】")
        print("  P - 显示所有POI点位")
        print("  G - 导航到指定POI (自动分层)")
        print("  1 - MoveToAction导航到POI")
        print("  2 - MultiFloorMoveAction POI导航")
        print("  3 - MultiFloorMoveAction坐标导航")
        print("")
        print("  【坐标导航模式】")
        print("  C - 导航到指定坐标 (自动分层)")
        print("  4 - MoveToAction导航到坐标")
        print("  5 - MultiFloorMoveAction导航到坐标")
        print("")
        print("  【状态查询】")
        print("  S - 显示当前状态")
        print("  L - 重新加载POI数据")
        print("")
        print("  【序列导航模式】")
        print("  Q - 执行用户自定义序列")
        print("  V - 预览用户序列")
        print("")
        print("  【控制功能】")
        print("  空格 - 停止所有运动")
        print("  H - 显示帮助")
        print("  X - 退出程序")
        print("-"*80)
        print("  🚀 导航方式比较:")
        print("     • MoveToAction: 基础API，支持坐标+角度控制，精度一般")
        print("     • MultiFloorMoveAction: 高级API，支持POI导航，with_yaw+precise精确模式")
        print("     • 已通过测试验证实际支持的参数格式")
        print("     • 可单独测试各种方式的精度差异")
        print("="*80)
    
    async def show_status(self):
        """显示当前状态"""
        print("\n[状态] 获取底盘当前状态...")
        
        pose = await self.get_current_pose()
        if pose:
            print(f"[位姿] 坐标: ({pose['x']:.6f}, {pose['y']:.6f})")
            print(f"[位姿] 角度: {math.degrees(pose['yaw']):.3f}°")
            print(f"[位姿] 时间: {pose['timestamp'].strftime('%H:%M:%S')}")
        else:
            print("[位姿] 无法获取位姿信息")
    
    async def interactive_poi_navigation(self, pois):
        """交互式POI导航"""
        if not pois:
            print("[ERROR] 无可用POI点位")
            return
        
        print("\n可用POI点位:")
        poi_list = list(pois.keys())
        for i, poi_name in enumerate(poi_list, 1):
            poi = pois[poi_name]
            print(f"  {i}. {poi_name}: ({poi['x']:.3f}, {poi['y']:.3f}, {math.degrees(poi['yaw']):.1f}°)")
        
        try:
            choice = input("\n请输入POI编号或名称: ").strip()
            
            # 修复POI名称判断逻辑
            poi_name = None
            
            # 首先尝试按编号选择（只有纯数字且在范围内才认为是编号）
            if choice.isdigit() and 1 <= int(choice) <= len(poi_list):
                index = int(choice) - 1
                poi_name = poi_list[index]
                print(f"[选择] 按编号选择POI: {poi_name}")
            else:
                # 按名称选择（直接匹配名称，包括数字名称如"1"、"3"）
                if choice in pois:
                    poi_name = choice
                    print(f"[选择] 按名称选择POI: {poi_name}")
                else:
                    print(f"[ERROR] POI '{choice}' 不存在")
                    print(f"[INFO] 可用POI名称: {list(pois.keys())}")
                    return
            
            # 选择是否启用精确角度
            yaw_choice = input("是否启用精确角度控制? (y/n, 默认y): ").strip().lower()
            with_yaw = yaw_choice != 'n'
            
            await self.navigate_to_poi(poi_name, pois, with_yaw)
            
        except KeyboardInterrupt:
            print("\n[INFO] 取消导航")
        except Exception as e:
            print(f"[ERROR] 导航失败: {e}")
    
    async def interactive_poi_navigation_method(self, pois, method):
        """交互式POI导航（指定方法）"""
        if not pois:
            print("[ERROR] 无可用POI点位")
            return
        
        print(f"\n=== 使用 {method.upper()} 导航到POI ===")
        print("可用POI点位:")
        for poi_name, poi in pois.items():
            print(f"  • {poi_name}: ({poi['x']:.3f}, {poi['y']:.3f}, {math.degrees(poi['yaw']):.1f}°)")
        
        try:
            poi_name = input("\n请输入POI名称: ").strip()
            
            if poi_name not in pois:
                print(f"[ERROR] POI '{poi_name}' 不存在")
                print(f"[INFO] 可用POI: {list(pois.keys())}")
                return
            
            poi = pois[poi_name]
            print(f"[选择] POI: {poi_name}")
            print(f"[坐标] ({poi['x']:.6f}, {poi['y']:.6f}, {math.degrees(poi['yaw']):.3f}°)")
            
            # 根据方法选择是否需要角度控制选项
            if method == "movetoaction":
                yaw_choice = input("是否启用精确角度控制? (y/n, 默认y): ").strip().lower()
                with_yaw = yaw_choice != 'n'
                target_yaw = poi['yaw'] if with_yaw else None
                
                print(f"\n[方法] MoveToAction + {'角度控制' if with_yaw else '仅位置'}")
                success = await self.move_to_action(poi['x'], poi['y'], target_yaw, with_yaw)
            
            elif method == "multifloor_poi":
                print(f"\n[方法] MultiFloorMoveAction (自动处理位置和角度)")
                success = await self.multi_floor_move_action_poi(poi_name, pois)
            
            elif method == "multifloor_coord":
                print(f"\n[方法] MultiFloorMoveAction坐标模式 (降级为MoveToAction)")
                yaw_choice = input("是否启用精确角度控制? (y/n, 默认y): ").strip().lower()
                with_yaw = yaw_choice != 'n'
                target_yaw = poi['yaw'] if with_yaw else None
                success = await self.multi_floor_move_action_coord(poi['x'], poi['y'], target_yaw, with_yaw)
            
            # 显示结果
            if success:
                print(f"\n[SUCCESS] ✅ 使用{method.upper()}成功导航到POI '{poi_name}'")
                
                # 验证最终位置
                await asyncio.sleep(1)
                final_pose = await self.get_current_pose()
                if final_pose:
                    dx = poi['x'] - final_pose['x']
                    dy = poi['y'] - final_pose['y']
                    position_error = math.sqrt(dx*dx + dy*dy)
                    angle_error = abs(poi['yaw'] - final_pose['yaw'])
                    
                    print(f"[最终位置] ({final_pose['x']:.6f}, {final_pose['y']:.6f}, {math.degrees(final_pose['yaw']):.3f}°)")
                    print(f"[定位精度] 位置误差: {position_error*100:.1f}cm, 角度误差: {math.degrees(angle_error):.1f}°")
            else:
                print(f"\n[FAILED] ❌ 使用{method.upper()}导航到POI '{poi_name}' 失败")
            
        except KeyboardInterrupt:
            print("\n[INFO] 取消导航")
        except Exception as e:
            print(f"[ERROR] 导航失败: {e}")
    
    async def interactive_coordinate_navigation_method(self, method):
        """交互式坐标导航（指定方法）"""
        try:
            print(f"\n=== 使用 {method.upper()} 导航到坐标 ===")
            print("请输入目标坐标:")
            x_str = input("X坐标(米): ").strip()
            y_str = input("Y坐标(米): ").strip()
            
            x = float(x_str)
            y = float(y_str)
            
            # 选择是否启用精确角度
            yaw_choice = input("是否指定目标角度? (y/n, 默认n): ").strip().lower() 
            yaw = None
            with_yaw = False
            
            if yaw_choice == 'y':
                yaw_str = input("目标角度(度): ").strip()
                yaw = math.radians(float(yaw_str))
                with_yaw = True
            
            print(f"\n[方法] 使用 {method.upper()}")
            print(f"[目标坐标] ({x:.3f}, {y:.3f})")
            if with_yaw and yaw is not None:
                print(f"[目标角度] {math.degrees(yaw):.1f}°")
            
            # 根据选择的方法进行导航
            success = False
            if method == "movetoaction":
                success = await self.move_to_action(x, y, yaw, with_yaw)
            elif method == "multifloor_coord":
                success = await self.multi_floor_move_action_coord(x, y, yaw, with_yaw)
            
            if success:
                print(f"[SUCCESS] 使用{method.upper()}成功导航到目标坐标")
                
                # 验证最终位置
                await asyncio.sleep(1)
                final_pose = await self.get_current_pose()
                if final_pose:
                    dx = x - final_pose['x']
                    dy = y - final_pose['y']
                    position_error = math.sqrt(dx*dx + dy*dy)
                    
                    print(f"[最终位置] ({final_pose['x']:.6f}, {final_pose['y']:.6f}, {math.degrees(final_pose['yaw']):.3f}°)")
                    print(f"[定位精度] 位置误差: {position_error*100:.1f}cm")
                    
                    if with_yaw and yaw is not None:
                        angle_error = abs(yaw - final_pose['yaw'])
                        print(f"[角度精度] 角度误差: {math.degrees(angle_error):.1f}°")
            else:
                print(f"[FAILED] 使用{method.upper()}导航到目标坐标失败")
            
        except ValueError:
            print("[ERROR] 输入格式错误，请输入数字")
        except KeyboardInterrupt:
            print("\n[INFO] 取消导航")
        except Exception as e:
            print(f"[ERROR] 导航失败: {e}")
    
    async def interactive_coordinate_navigation(self):
        """交互式坐标导航"""
        try:
            print("\n请输入目标坐标:")
            x_str = input("X坐标(米): ").strip()
            y_str = input("Y坐标(米): ").strip()
            
            x = float(x_str)
            y = float(y_str)
            
            # 选择是否启用精确角度
            yaw_choice = input("是否指定目标角度? (y/n, 默认n): ").strip().lower() 
            yaw = None
            with_yaw = False
            
            if yaw_choice == 'y':
                yaw_str = input("目标角度(度): ").strip()
                yaw = math.radians(float(yaw_str))
                with_yaw = True
            
            await self.navigate_to_coordinate(x, y, yaw, with_yaw)
            
        except ValueError:
            print("[ERROR] 输入格式错误，请输入数字")
        except KeyboardInterrupt:
            print("\n[INFO] 取消导航")
        except Exception as e:
            print(f"[ERROR] 导航失败: {e}")
    
    def show_sequence_preview(self):
        """显示用户序列预览"""
        if not USER_MOTION_SEQUENCE:
            print("[ERROR] 用户序列未定义或为空")
            return
        
        print(f"\n📋 用户自定义序列预览:")
        print(f"-" * 60)
        poi_count = 0
        wait_count = 0
        
        for i, step in enumerate(USER_MOTION_SEQUENCE, 1):
            if isinstance(step, str):
                poi_count += 1
                if step in self.pois:
                    poi = self.pois[step]
                    print(f"  {i:2d}. 🎯 导航到POI '{step}': ({poi['x']:.2f}, {poi['y']:.2f}, {math.degrees(poi['yaw']):.0f}°)")
                else:
                    print(f"  {i:2d}. ❌ 无效POI '{step}' (不存在)")
            elif isinstance(step, dict) and 'wait' in step:
                wait_count += 1
                wait_time = step['wait']
                print(f"  {i:2d}. ⏳ 等待 {wait_time}ms ({wait_time/1000:.1f}s)")
            else:
                print(f"  {i:2d}. ❓ 未知命令: {step}")
        
        print(f"-" * 60)
        print(f"📊 序列统计: {len(USER_MOTION_SEQUENCE)}步 ({poi_count}个POI + {wait_count}个等待)")
    
    async def wait_with_countdown(self, wait_time_ms: int):
        """等待指定时间并显示倒计时"""
        wait_seconds = wait_time_ms / 1000.0
        print(f"\n⏳ 等待 {wait_seconds:.1f} 秒...")
        
        remaining = wait_seconds
        while remaining > 0:
            if remaining >= 10 or remaining <= 5 or int(remaining) % 5 == 0:
                print(f"   ⏱️  剩余: {remaining:.1f}s")
            
            sleep_time = min(1.0, remaining)
            await asyncio.sleep(sleep_time)
            remaining -= sleep_time
        
        print(f"✅ 等待完成")
    
    async def execute_user_sequence(self):
        """执行用户自定义序列"""
        if not USER_MOTION_SEQUENCE:
            print("[ERROR] 用户序列未定义或为空")
            print("💡 请检查 motion_sequences.py 文件中的 USER_MOTION_SEQUENCE")
            return False
        
        # 验证序列
        print(f"\n🔍 验证用户序列...")
        invalid_pois = []
        for item in USER_MOTION_SEQUENCE:
            if isinstance(item, str) and item not in self.pois:
                invalid_pois.append(item)
        
        if invalid_pois:
            print(f"❌ 序列包含无效POI: {invalid_pois}")
            print(f"💡 可用POI: {list(self.pois.keys())}")
            return False
        
        # 显示序列预览
        self.show_sequence_preview()
        
        # 确认执行
        try:
            confirm = input(f"\n🤔 确认执行此序列? (y/n): ").strip().lower()
            if confirm != 'y':
                print("[INFO] 用户取消执行")
                return False
        except KeyboardInterrupt:
            print("\n[INFO] 用户取消执行")
            return False
        
        # 执行序列
        print(f"\n" + "="*80)
        print(f"🚀 开始执行用户自定义序列")
        print(f"📋 总步骤: {len(USER_MOTION_SEQUENCE)}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"="*80)
        
        success_count = 0
        failed_steps = []
        start_time = datetime.now()
        total_distance = 0.0
        
        for i, step in enumerate(USER_MOTION_SEQUENCE):
            step_start_time = datetime.now()
            print(f"\n📌 步骤 {i+1}/{len(USER_MOTION_SEQUENCE)}")
            print(f"⏰ 时间: {step_start_time.strftime('%H:%M:%S')}")
            
            try:
                if isinstance(step, str):
                    # POI导航
                    print(f"🎯 执行: 导航到POI '{step}'")
                    current_pose = await self.get_current_pose()
                    
                    success = await self.multi_floor_move_action_poi(step, self.pois)
                    
                    if success:
                        success_count += 1
                        print(f"✅ 步骤 {i+1} 完成")
                        
                        # 计算移动距离
                        if current_pose:
                            final_pose = await self.get_current_pose()
                            if final_pose:
                                dx = final_pose['x'] - current_pose['x']
                                dy = final_pose['y'] - current_pose['y']
                                distance = math.sqrt(dx*dx + dy*dy)
                                total_distance += distance
                                print(f"📏 本步移动: {distance:.3f}m")
                    else:
                        failed_steps.append(f"步骤{i+1}: 导航到'{step}'失败")
                        print(f"❌ 步骤 {i+1} 失败")
                        
                elif isinstance(step, dict) and 'wait' in step:
                    # 等待命令
                    wait_time = step['wait']
                    print(f"⏳ 执行: 等待 {wait_time}ms ({wait_time/1000:.1f}s)")
                    await self.wait_with_countdown(wait_time)
                    success_count += 1
                    print(f"✅ 步骤 {i+1} 完成")
                
            except KeyboardInterrupt:
                print(f"\n⚠️  用户中断序列执行")
                print(f"📊 已完成 {success_count}/{i+1} 步")
                return False
            except Exception as e:
                print(f"❌ 步骤 {i+1} 异常: {e}")
                failed_steps.append(f"步骤{i+1}: 异常 - {e}")
        
        # 显示执行结果
        end_time = datetime.now()
        total_elapsed = (end_time - start_time).total_seconds()
        
        print(f"\n" + "="*80)
        print(f"🏁 用户序列执行完成!")
        print(f"="*80)
        print(f"📊 执行统计:")
        print(f"   ✅ 成功步骤: {success_count}/{len(USER_MOTION_SEQUENCE)}")
        print(f"   ❌ 失败步骤: {len(failed_steps)}")
        print(f"   📏 总移动距离: {total_distance:.3f}m")
        print(f"   🕐 总执行时间: {total_elapsed:.1f}s")
        print(f"   ⏰ 结束时间: {end_time.strftime('%H:%M:%S')}")
        
        if failed_steps:
            print(f"\n❌ 失败步骤详情:")
            for failure in failed_steps:
                print(f"   • {failure}")
        
        success_rate = success_count / len(USER_MOTION_SEQUENCE) * 100
        print(f"\n🎯 成功率: {success_rate:.1f}%")
        
        return success_count == len(USER_MOTION_SEQUENCE)
    
    async def execute_user_sequence_auto(self):
        """自动执行用户序列（无需确认）"""
        if not USER_MOTION_SEQUENCE:
            print("[ERROR] 用户序列未定义或为空")
            return False
        
        # 验证序列
        invalid_pois = []
        for item in USER_MOTION_SEQUENCE:
            if isinstance(item, str) and item not in self.pois:
                invalid_pois.append(item)
        
        if invalid_pois:
            print(f"❌ 序列包含无效POI: {invalid_pois}")
            print(f"💡 可用POI: {list(self.pois.keys())}")
            return False
        
        # 执行序列
        print(f"🚀 开始执行用户自定义序列")
        print(f"📋 总步骤: {len(USER_MOTION_SEQUENCE)}")
        
        success_count = 0
        failed_steps = []
        start_time = datetime.now()
        total_distance = 0.0
        
        for i, step in enumerate(USER_MOTION_SEQUENCE):
            print(f"\n📌 步骤 {i+1}/{len(USER_MOTION_SEQUENCE)}")
            
            try:
                if isinstance(step, str):
                    # POI导航
                    print(f"🎯 导航到POI '{step}'")
                    current_pose = await self.get_current_pose()
                    
                    success = await self.multi_floor_move_action_poi(step, self.pois)
                    
                    if success:
                        success_count += 1
                        print(f"✅ 步骤 {i+1} 完成")
                        
                        # 计算移动距离
                        if current_pose:
                            final_pose = await self.get_current_pose()
                            if final_pose:
                                dx = final_pose['x'] - current_pose['x']
                                dy = final_pose['y'] - current_pose['y']
                                distance = math.sqrt(dx*dx + dy*dy)
                                total_distance += distance
                                print(f"📏 本步移动: {distance:.3f}m")
                    else:
                        failed_steps.append(f"步骤{i+1}: 导航到'{step}'失败")
                        print(f"❌ 步骤 {i+1} 失败")
                        
                elif isinstance(step, dict) and 'wait' in step:
                    # 等待命令
                    wait_time = step['wait']
                    print(f"⏳ 等待 {wait_time}ms ({wait_time/1000:.1f}s)")
                    await self.wait_with_countdown(wait_time)
                    success_count += 1
                    print(f"✅ 步骤 {i+1} 完成")
                
            except KeyboardInterrupt:
                print(f"\n⚠️  用户中断序列执行")
                print(f"📊 已完成 {success_count}/{i+1} 步")
                return False
            except Exception as e:
                print(f"❌ 步骤 {i+1} 异常: {e}")
                failed_steps.append(f"步骤{i+1}: 异常 - {e}")
        
        # 显示执行结果
        end_time = datetime.now()
        total_elapsed = (end_time - start_time).total_seconds()
        
        print(f"\n" + "="*80)
        print(f"🏁 用户序列执行完成!")
        print(f"📊 执行统计:")
        print(f"   ✅ 成功步骤: {success_count}/{len(USER_MOTION_SEQUENCE)}")
        print(f"   ❌ 失败步骤: {len(failed_steps)}")
        print(f"   📏 总移动距离: {total_distance:.3f}m")
        print(f"   🕐 总执行时间: {total_elapsed:.1f}s")
        print(f"🎯 成功率: {success_count / len(USER_MOTION_SEQUENCE) * 100:.1f}%")
        print(f"="*80)
        
        return success_count == len(USER_MOTION_SEQUENCE)
    
    async def run(self):
        """运行控制器"""
        print("=== 分层导航API控制器 ===")
        print("MoveToAction优先，自动降级确保可用性")
        
        # 连接底盘
        if not await self.connect():
            print("[ERROR] 无法连接底盘，请检查:")
            print(f"1. 底盘IP地址: {self.ip}")
            print("2. 底盘网络连接状态")
            print("3. RoboStudio是否正常运行")
            return
        
        # 加载POI数据
        print("\n正在加载POI数据...")
        pois = await self.load_pois()
        
        # 显示帮助和状态
        self.show_help()
        await self.show_status()
        
        print(f"\n请输入控制指令:")
        
        try:
            while True:
                try:
                    command = input(">>> ").strip().lower()
                    
                    if not command:
                        continue
                    
                    if command == 'p':
                        # 显示POI
                        if pois:
                            print(f"\n可用POI点位 ({len(pois)}个):")
                            for i, (name, poi) in enumerate(pois.items(), 1):
                                print(f"  {i}. {name}: ({poi['x']:.3f}, {poi['y']:.3f}, {math.degrees(poi['yaw']):.1f}°)")
                        else:
                            print("[INFO] 暂无POI点位")
                    
                    elif command == 'g':
                        # 导航到POI (自动分层)
                        await self.interactive_poi_navigation(pois)
                    
                    elif command == '1':
                        # MoveToAction导航到POI
                        await self.interactive_poi_navigation_method(pois, "movetoaction")
                    
                    elif command == '2':
                        # MultiFloorMoveAction POI导航
                        await self.interactive_poi_navigation_method(pois, "multifloor_poi")
                    
                    elif command == '3':
                        # MultiFloorMoveAction坐标导航
                        await self.interactive_poi_navigation_method(pois, "multifloor_coord")
                    
                    elif command == 'y':
                        # 导航到POI(启用精确角度)
                        if pois:
                            poi_name = input("请输入POI名称: ").strip()
                            await self.navigate_to_poi(poi_name, pois, with_yaw=True)
                    
                    elif command == 'n':
                        # 导航到POI(不要求角度)
                        if pois:
                            poi_name = input("请输入POI名称: ").strip()
                            await self.navigate_to_poi(poi_name, pois, with_yaw=False)
                    
                    elif command == 'c':
                        # 导航到坐标 (自动分层)
                        await self.interactive_coordinate_navigation()
                    
                    elif command == '4':
                        # MoveToAction导航到坐标
                        await self.interactive_coordinate_navigation_method("movetoaction")
                    
                    elif command == '5':
                        # MultiFloorMoveAction导航到坐标
                        await self.interactive_coordinate_navigation_method("multifloor_coord")
                    
                    elif command == 'q':
                        # 执行用户自定义序列
                        await self.execute_user_sequence()
                    
                    elif command == 'v':
                        # 预览用户序列
                        self.show_sequence_preview()
                    
                    elif command == 'a':
                        # 导航到坐标(启用精确角度)
                        try:
                            x = float(input("X坐标(米): "))
                            y = float(input("Y坐标(米): "))
                            yaw_deg = float(input("角度(度): "))
                            yaw = math.radians(yaw_deg)
                            await self.navigate_to_coordinate(x, y, yaw, with_yaw=True)
                        except ValueError:
                            print("[ERROR] 输入格式错误")
                    
                    elif command == 's':
                        # 显示状态
                        await self.show_status()
                    
                    elif command == 'l':
                        # 重新加载POI
                        print("正在重新加载POI数据...")
                        pois = await self.load_pois()
                    
                    elif command == ' ' or command == 'stop':
                        # 停止运动
                        await self.stop_all_actions()
                    
                    elif command == 'h' or command == 'help':
                        # 显示帮助
                        self.show_help()
                    
                    elif command == 'x' or command == 'exit':
                        print("[INFO] 正在退出...")
                        break
                    
                    else:
                        print(f"[WARNING] 未知命令: {command}")
                        print("输入 H 查看帮助")
                
                except KeyboardInterrupt:
                    print("\n[INFO] 检测到中断信号")
                    break
                except Exception as e:
                    print(f"[ERROR] 命令执行错误: {e}")
        
        finally:
            await self.stop_all_actions()  # 安全停止
            await self.disconnect()
            print("[INFO] 程序已退出")

async def main():
    """主函数"""
    import sys
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.31.211"
    
    controller = AdvancedNavigationController(ip)
    await controller.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] 程序被用户中断")
    except Exception as e:
        print(f"[ERROR] 程序运行错误: {e}")
        import traceback
        traceback.print_exc()