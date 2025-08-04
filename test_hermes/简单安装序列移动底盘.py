#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化序列导航脚本
专门使用MultiFloorMoveAction进行POI序列导航
自动执行用户自定义序列
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
    "3",               # 导航到POI "3"
    {"wait": 5000},    # 等待5秒
    "home1"            # 最后返回home1
]

class SimpleSequenceNavigator:
    """简化序列导航器 - 专用MultiFloorMoveAction"""
    
    def __init__(self, ip="192.168.31.211", port=1448):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.client = None
        self.connected = False
        self.pois = {}
        
        print(f"🚀 简化序列导航器")
        print(f"📡 底盘地址: {self.base_url}")
        print(f"🎯 使用MultiFloorMoveAction精确导航")
    
    async def connect(self):
        """连接底盘"""
        try:
            self.client = httpx.AsyncClient(timeout=10.0)
            
            print("🔗 正在连接底盘...")
            response = await self.client.get(f"{self.base_url}/api/core/system/v1/capabilities")
            
            if response.status_code == 200:
                print(f"✅ 连接成功!")
                self.connected = True
                return True
            else:
                print(f"❌ 连接失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.aclose()
            self.connected = False
            print("✅ 已断开连接")
    
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
                    'yaw': pose['yaw'],
                    'timestamp': datetime.now()
                }
        except Exception as e:
            print(f"❌ 获取位姿失败: {e}")
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
                
                print(f"📍 发现 {len(poi_data)} 个POI点位:")
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
                    print(f"  {i}. {display_name}: ({pose['x']:.3f}, {pose['y']:.3f}, {math.degrees(pose['yaw']):.1f}°)")
                
                self.pois = pois
                return pois
            else:
                print(f"❌ 加载POI失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ POI加载异常: {e}")
            return {}
    
    async def navigate_to_poi(self, poi_name):
        """
        使用MultiFloorMoveAction导航到POI
        精确到角模式，自动处理位置和角度
        """
        if not self.connected:
            return False
        
        try:
            print(f"🎯 导航到POI '{poi_name}'")
            
            # 获取目标POI信息
            if poi_name not in self.pois:
                print(f"❌ POI '{poi_name}' 不存在")
                return False
            
            target_poi = self.pois[poi_name]
            target_x = target_poi['x']
            target_y = target_poi['y']
            target_yaw = target_poi['yaw']
            
            print(f"  目标位置: ({target_x:.3f}, {target_y:.3f}, {math.degrees(target_yaw):.1f}°)")
            
            # 先尝试POI名称，再尝试POI ID
            identifiers_to_try = [poi_name]
            poi_id = target_poi['id']
            identifiers_to_try.append(poi_id)
            
            for i, identifier in enumerate(identifiers_to_try):
                identifier_type = "POI名称" if i == 0 else "POI ID" 
                print(f"  尝试使用{identifier_type}: '{identifier}'")
                
                # 使用精确到角格式
                payload = {
                    "action_name": "slamtec.agent.actions.MultiFloorMoveAction",
                    "options": {
                        "target": {
                            "poi_name": identifier
                        },
                        "move_options": {
                            "mode": 0,  # 自由导航模式
                            "flags": ["with_yaw"],  # 精确到角模式
                            "acceptable_precision": 0.05,  # 5cm精度
                            "fail_retry_count": 2  # 失败重试2次
                        }
                    }
                }
                
                response = await self.client.post(
                    f"{self.base_url}/api/core/motion/v1/actions",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    action_id = result.get('action_id')
                    print(f"  ✅ 任务创建成功 - ID: {action_id}")
                    
                    if action_id:
                        success = await self._monitor_navigation(action_id)
                        if success:
                            print(f"  🎯 成功到达POI '{poi_name}'")
                            
                            # 计算和显示误差
                            await self._show_navigation_accuracy(target_x, target_y, target_yaw, poi_name)
                            return True
                        else:
                            print(f"  ❌ 导航执行失败")
                    else:
                        print("  ❌ 未获取到Action ID")
                else:
                    print(f"  ❌ 任务创建失败: {response.status_code}")
                    if response.text:
                        print(f"  错误详情: {response.text}")
            
            print(f"❌ 所有尝试都失败")
            return False
                
        except Exception as e:
            print(f"❌ 导航异常: {e}")
            return False
    
    async def _monitor_navigation(self, action_id, timeout=60):
        """监控导航任务执行状态"""
        print(f"  🔍 监控导航任务...")
        
        for i in range(timeout):
            try:
                response = await self.client.get(
                    f"{self.base_url}/api/core/motion/v1/actions/{action_id}"
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    state = status_data.get('state', {})
                    status_code = state.get('status', 0)
                    reason = state.get('reason', '')
                    
                    status_names = {
                        0: "初始化",
                        1: "执行中", 
                        2: "暂停",
                        3: "取消",
                        4: "完成"
                    }
                    
                    current_status = status_names.get(status_code, f"未知状态({status_code})")
                    
                    # 每5秒或状态变化时显示
                    if i % 5 == 0 or status_code in [3, 4]:
                        print(f"    [{i+1}s] {current_status}")
                        if reason:
                            print(f"    原因: {reason}")
                    
                    if status_code == 4:  # 完成
                        result_info = state.get('result', 0)
                        if result_info == 0:
                            print(f"    ✅ 导航完成")
                            return True
                        else:
                            print(f"    ❌ 导航失败，结果码: {result_info}")
                            return False
                    elif status_code == 3:  # 取消
                        print(f"    ❌ 导航被取消")
                        return False
                        
            except Exception as e:
                print(f"    ❌ 监控异常: {e}")
            
            await asyncio.sleep(1)
        
        print(f"    ⏰ 监控超时")
        return False
    
    async def _show_navigation_accuracy(self, target_x, target_y, target_yaw, poi_name):
        """显示导航精度和误差"""
        try:
            # 等待一下让底盘稳定
            await asyncio.sleep(0.5)
            
            # 获取当前实际位置
            current_pose = await self.get_current_pose()
            if not current_pose:
                print(f"  ❌ 无法获取当前位置，跳过精度计算")
                return
            
            actual_x = current_pose['x']
            actual_y = current_pose['y'] 
            actual_yaw = current_pose['yaw']
            
            # 计算位置误差
            dx = target_x - actual_x
            dy = target_y - actual_y
            position_error = math.sqrt(dx*dx + dy*dy)
            
            # 计算角度误差（处理角度跳跃）
            angle_diff = target_yaw - actual_yaw
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            angle_error = abs(angle_diff)
            
            # 显示精度信息
            print(f"  📍 精度报告:")
            print(f"    目标位置: ({target_x:.6f}, {target_y:.6f}, {math.degrees(target_yaw):.3f}°)")
            print(f"    实际位置: ({actual_x:.6f}, {actual_y:.6f}, {math.degrees(actual_yaw):.3f}°)")
            print(f"    位置误差: {position_error*100:.1f}cm")
            print(f"    角度误差: {math.degrees(angle_error):.1f}°")
            
            # 精度评估
            if position_error <= 0.05:  # 5cm以内
                position_grade = "🟢 优秀"
            elif position_error <= 0.10:  # 10cm以内
                position_grade = "🟡 良好"
            else:
                position_grade = "🔴 一般"
            
            if math.degrees(angle_error) <= 3:  # 3度以内
                angle_grade = "🟢 优秀"
            elif math.degrees(angle_error) <= 10:  # 10度以内
                angle_grade = "🟡 良好" 
            else:
                angle_grade = "🔴 一般"
            
            print(f"    精度评级: {position_grade} (位置) | {angle_grade} (角度)")
            
        except Exception as e:
            print(f"  ❌ 精度计算异常: {e}")
    
    async def wait_with_countdown(self, wait_time_ms: int):
        """等待指定时间并显示倒计时"""
        wait_seconds = wait_time_ms / 1000.0
        print(f"⏳ 等待 {wait_seconds:.1f} 秒...")
        
        remaining = wait_seconds
        while remaining > 0:
            if remaining >= 10 or remaining <= 5 or int(remaining) % 5 == 0:
                print(f"   ⏱️  剩余: {remaining:.1f}s")
            
            sleep_time = min(1.0, remaining)
            await asyncio.sleep(sleep_time)
            remaining -= sleep_time
        
        print(f"✅ 等待完成")
    
    def show_sequence_preview(self):
        """显示序列预览"""
        if not USER_MOTION_SEQUENCE:
            print("❌ 序列为空")
            return
        
        print(f"\n📋 序列预览:")
        print(f"-" * 50)
        poi_count = 0
        wait_count = 0
        
        for i, step in enumerate(USER_MOTION_SEQUENCE, 1):
            if isinstance(step, str):
                poi_count += 1
                if step in self.pois:
                    poi = self.pois[step]
                    print(f"  {i:2d}. 🎯 导航到 '{step}': ({poi['x']:.2f}, {poi['y']:.2f}, {math.degrees(poi['yaw']):.0f}°)")
                else:
                    print(f"  {i:2d}. ❌ 无效POI '{step}'")
            elif isinstance(step, dict) and 'wait' in step:
                wait_count += 1
                wait_time = step['wait']
                print(f"  {i:2d}. ⏳ 等待 {wait_time}ms ({wait_time/1000:.1f}s)")
            else:
                print(f"  {i:2d}. ❓ 未知命令: {step}")
        
        print(f"-" * 50)
        print(f"📊 总计: {len(USER_MOTION_SEQUENCE)}步 ({poi_count}个POI + {wait_count}个等待)")
    
    async def execute_sequence(self):
        """执行用户序列"""
        if not USER_MOTION_SEQUENCE:
            print("❌ 序列为空")
            return False
        
        # 验证序列中的POI
        print(f"🔍 验证序列...")
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
        
        # 执行序列
        print(f"\n" + "="*60)
        print(f"🚀 开始执行序列")
        print(f"📋 总步骤: {len(USER_MOTION_SEQUENCE)}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"="*60)
        
        success_count = 0
        failed_steps = []
        start_time = datetime.now()
        total_distance = 0.0
        
        for i, step in enumerate(USER_MOTION_SEQUENCE):
            step_start_time = datetime.now()
            print(f"\n📌 步骤 {i+1}/{len(USER_MOTION_SEQUENCE)}")
            print(f"⏰ {step_start_time.strftime('%H:%M:%S')}")
            
            try:
                if isinstance(step, str):
                    # POI导航
                    print(f"🎯 执行: 导航到POI '{step}'")
                    current_pose = await self.get_current_pose()
                    
                    success = await self.navigate_to_poi(step)
                    
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
                                print(f"📏 移动距离: {distance:.3f}m")
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
        
        print(f"\n" + "="*60)
        print(f"🏁 序列执行完成!")
        print(f"="*60)
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
        print(f"="*60)
        
        return success_count == len(USER_MOTION_SEQUENCE)
    
    async def stop_all_actions(self):
        """停止所有运动"""
        if not self.connected:
            return False
        
        try:
            response = await self.client.post(f"{self.base_url}/api/core/motion/v1/stop")
            if response.status_code == 200:
                print("⛔ 已停止所有运动")
                return True
            else:
                print(f"❌ 停止失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 停止异常: {e}")
            return False
    
    async def run(self):
        """运行导航器"""
        print("=" * 60)
        print("🤖 简化序列导航器")  
        print("🎯 专用MultiFloorMoveAction精确导航")
        print("📋 自动执行用户自定义序列")
        print("=" * 60)
        
        # 连接底盘
        if not await self.connect():
            print("❌ 无法连接底盘，请检查:")
            print(f"   1. 底盘IP地址: {self.ip}")
            print("   2. 底盘网络连接状态")
            print("   3. RoboStudio是否正常运行")
            return
        
        # 加载POI数据
        print("\n📍 正在加载POI数据...")
        pois = await self.load_pois()
        
        if not pois:
            print("❌ 无可用POI点位，程序退出")
            return
        
        try:
            # 直接执行序列
            await self.execute_sequence()
            
        except KeyboardInterrupt:
            print("\n⚠️  程序被用户中断")
        except Exception as e:
            print(f"❌ 程序运行错误: {e}")
        finally:
            await self.stop_all_actions()
            await self.disconnect()
            print("👋 程序已退出")

async def main():
    """主函数"""
    import sys
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.31.211"
    
    navigator = SimpleSequenceNavigator(ip)
    await navigator.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()