#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POI同步脚本 - 将core系统POI同步到multi-floor系统
解决MultiFloorMoveAction报"POI_NOT_FOUND"错误

根据项目文档分析，POI只存在于core系统中，
而MultiFloorMoveAction需要使用multi-floor系统中的POI
此脚本用于将POI从core系统同步到multi-floor系统
"""
import asyncio
import httpx
import json
import sys
import os
from datetime import datetime

class POISyncTool:
    """POI同步工具"""
    
    def __init__(self, ip="192.168.31.211", port=1448):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.client = None
        
        print(f"🔗 POI同步工具初始化")
        print(f"📡 底盘地址: {self.base_url}")
    
    async def connect(self):
        """连接底盘"""
        try:
            self.client = httpx.AsyncClient(timeout=15.0)
            
            print("🔍 正在连接底盘...")
            response = await self.client.get(f"{self.base_url}/api/core/system/v1/capabilities")
            
            if response.status_code == 200:
                capabilities = response.json()
                print(f"✅ 底盘连接成功!")
                
                # 检查系统能力
                has_multifloor = False
                for capability in capabilities:
                    if capability.get('name') == 'slamware.agent.multi_floor':
                        has_multifloor = True
                        print(f"✅ multi-floor插件已启用: v{capability.get('version')}")
                        break
                
                if not has_multifloor:
                    print("⚠️  警告: 未检测到multi-floor插件")
                
                return True
            else:
                print(f"❌ 底盘连接失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.aclose()
            print("✅ 已断开连接")
    
    async def get_core_pois(self):
        """获取core系统POI列表"""
        try:
            print("\n📍 正在获取core系统POI...")
            response = await self.client.get(f"{self.base_url}/api/core/artifact/v1/pois")
            
            if response.status_code == 200:
                poi_data = response.json()
                print(f"✅ core系统发现 {len(poi_data)} 个POI:")
                
                for i, poi in enumerate(poi_data, 1):
                    display_name = poi['metadata']['display_name']
                    pose = poi['pose']
                    print(f"  {i}. {display_name}: ({pose['x']:.3f}, {pose['y']:.3f}, {pose['yaw']:.3f})")
                
                return poi_data
            else:
                print(f"❌ 获取core系统POI失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 获取core系统POI异常: {e}")
            return []
    
    async def get_multifloor_pois(self):
        """获取multi-floor系统POI列表"""
        try:
            print("\n🏢 正在获取multi-floor系统POI...")
            response = await self.client.get(f"{self.base_url}/api/multi-floor/map/v1/pois")
            
            if response.status_code == 200:
                poi_data = response.json()
                print(f"✅ multi-floor系统发现 {len(poi_data)} 个POI:")
                
                for i, poi in enumerate(poi_data, 1):
                    display_name = poi.get('metadata', {}).get('display_name', '未知')
                    pose = poi.get('pose', {})
                    print(f"  {i}. {display_name}: ({pose.get('x', 0):.3f}, {pose.get('y', 0):.3f}, {pose.get('yaw', 0):.3f})")
                
                return poi_data
            else:
                print(f"⚠️  获取multi-floor系统POI失败: {response.status_code}")
                if response.status_code == 404:
                    print("💡 这通常表示multi-floor系统中还没有POI数据")
                return []
                
        except Exception as e:
            print(f"❌ 获取multi-floor系统POI异常: {e}")
            return []
    
    async def sync_pois_method1(self):
        """方法1: 使用官方同步API"""
        try:
            print("\n🔄 方法1: 使用官方同步API...")
            print("📡 调用: POST /api/multi-floor/map/v1/stcm/:sync")
            
            response = await self.client.post(f"{self.base_url}/api/multi-floor/map/v1/stcm/:sync")
            
            if response.status_code == 200:
                print("✅ 官方同步API调用成功!")
                return True
            else:
                print(f"❌ 官方同步API调用失败: {response.status_code}")
                if response.text:
                    print(f"   错误详情: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 官方同步API异常: {e}")
            return False
    
    async def sync_pois_method2(self):
        """方法2: 手动触发地图同步"""
        try:
            print("\n🔄 方法2: 手动触发地图同步...")
            
            # 尝试其他可能的同步端点
            sync_endpoints = [
                "/api/multi-floor/map/v1/sync",
                "/api/multi-floor/v1/sync",
                "/api/core/map/v1/sync"
            ]
            
            for endpoint in sync_endpoints:
                try:
                    print(f"📡 尝试: POST {endpoint}")
                    response = await self.client.post(f"{self.base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        print(f"✅ 同步成功: {endpoint}")
                        return True
                    else:
                        print(f"❌ {endpoint} 失败: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {endpoint} 异常: {e}")
            
            return False
                
        except Exception as e:
            print(f"❌ 手动同步异常: {e}")
            return False
    
    async def verify_sync(self, original_core_pois):
        """验证同步结果"""
        print("\n🔍 验证同步结果...")
        
        # 等待一下让同步完成
        await asyncio.sleep(2)
        
        # 重新获取multi-floor系统POI
        multifloor_pois = await self.get_multifloor_pois()
        
        if not multifloor_pois:
            print("❌ 同步后multi-floor系统仍无POI数据")
            return False
        
        # 对比POI数据
        core_poi_names = set()
        for poi in original_core_pois:
            name = poi['metadata']['display_name']
            core_poi_names.add(name)
        
        multifloor_poi_names = set()
        for poi in multifloor_pois:
            name = poi.get('metadata', {}).get('display_name', '')
            if name:
                multifloor_poi_names.add(name)
        
        print(f"\n📊 同步对比:")
        print(f"   Core系统POI: {len(core_poi_names)}个 - {sorted(core_poi_names)}")
        print(f"   Multi-floor系统POI: {len(multifloor_poi_names)}个 - {sorted(multifloor_poi_names)}")
        
        missing_pois = core_poi_names - multifloor_poi_names
        if missing_pois:
            print(f"   ⚠️  未同步的POI: {sorted(missing_pois)}")
            return False
        else:
            print(f"   ✅ 所有POI已成功同步!")
            return True
    
    async def test_multifloor_navigation(self, test_poi_name):
        """测试MultiFloorMoveAction是否可用"""
        try:
            print(f"\n🧪 测试MultiFloorMoveAction导航到POI '{test_poi_name}'...")
            
            payload = {
                "action_name": "slamtec.agent.actions.MultiFloorMoveAction",
                "options": {
                    "target": {
                        "poi_name": test_poi_name
                    },
                    "move_options": {
                        "mode": 0,
                        "flags": ["with_yaw"],
                        "acceptable_precision": 0.05,
                        "fail_retry_count": 2
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
                print(f"✅ MultiFloorMoveAction测试成功! Action ID: {action_id}")
                
                # 立即取消这个测试任务
                if action_id:
                    try:
                        cancel_response = await self.client.post(
                            f"{self.base_url}/api/core/motion/v1/actions/{action_id}/cancel"
                        )
                        print("✅ 测试任务已取消")
                    except:
                        pass
                
                return True
            else:
                print(f"❌ MultiFloorMoveAction测试失败: {response.status_code}")
                if response.text:
                    print(f"   错误详情: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ MultiFloorMoveAction测试异常: {e}")
            return False
    
    async def run_sync(self):
        """运行完整同步流程"""
        print("=" * 80)
        print("🔄 POI同步工具 - 解决MultiFloorMoveAction POI_NOT_FOUND问题")
        print("=" * 80)
        
        # 连接底盘
        if not await self.connect():
            print("❌ 无法连接底盘，同步失败")
            return False
        
        try:
            # 1. 获取当前POI状态
            core_pois = await self.get_core_pois()
            if not core_pois:
                print("❌ core系统中没有POI数据，无需同步")
                return False
            
            multifloor_pois_before = await self.get_multifloor_pois()
            
            # 2. 尝试同步方法
            sync_success = False
            
            # 方法1: 官方同步API
            if await self.sync_pois_method1():
                sync_success = True
            elif await self.sync_pois_method2():  # 方法2: 备选同步方法
                sync_success = True
            
            if not sync_success:
                print("\n❌ 所有同步方法都失败了")
                print("💡 建议手动操作:")
                print("   1. 在RoboStudio中重新加载地图")
                print("   2. 确认POI在当前地图中存在")
                print("   3. 检查multi-floor插件是否正常工作")
                return False
            
            # 3. 验证同步结果
            if await self.verify_sync(core_pois):
                print("\n🎉 POI同步成功!")
                
                # 4. 测试MultiFloorMoveAction
                if core_pois:
                    test_poi = core_pois[0]['metadata']['display_name']
                    if await self.test_multifloor_navigation(test_poi):
                        print(f"\n✅ MultiFloorMoveAction功能验证成功!")
                        print(f"💡 现在可以正常使用combined_shuaqiang.py了")
                    else:
                        print(f"\n⚠️  同步成功但MultiFloorMoveAction测试失败")
                        print(f"💡 可能需要等待一段时间或重启RoboStudio")
                
                return True
            else:
                print("\n❌ 同步验证失败")
                return False
                
        except Exception as e:
            print(f"❌ 同步流程异常: {e}")
            return False
        
        finally:
            await self.disconnect()

async def main():
    """主函数"""
    import sys
    
    # 解析命令行参数
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.31.211"
    
    print(f"🚀 启动POI同步工具")
    print(f"📡 目标底盘: {ip}:1448")
    
    sync_tool = POISyncTool(ip)
    success = await sync_tool.run_sync()
    
    if success:
        print("\n" + "=" * 80)
        print("🎉 POI同步完成! MultiFloorMoveAction现在应该可以正常工作了")
        print("💡 建议:")
        print("   1. 重新运行 combined_shuaqiang.py")
        print("   2. 如果仍有问题，请重启RoboStudio后再试")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ POI同步失败")
        print("💡 手动解决方案:")
        print("   1. 在RoboStudio中检查当前地图")
        print("   2. 确认POI '2' 确实存在")
        print("   3. 尝试重新创建POI点位")
        print("   4. 重启RoboStudio服务")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  用户中断同步操作")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()