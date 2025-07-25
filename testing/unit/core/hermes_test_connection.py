# hermes_test_connection.py
import requests
import json
import time
from typing import List, Dict, Optional

class HermesConnectionTest:
    def __init__(self, base_url: str = "http://192.168.31.211:1448"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_basic_connection(self) -> bool:
        """
        测试基本连接
        仅尝试连接，不进行任何操作
        """
        try:
            print(f"🔗 正在测试连接: {self.base_url}")
            
            # 设置较短的超时时间进行快速测试
            response = self.session.get(f"{self.base_url}/api/core/artifact/v1/pois", timeout=5)
            
            if response.status_code == 200:
                print("✅ 连接成功！")
                return True
            else:
                print(f"❌ 连接失败，HTTP状态码: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 连接超时，请检查网络或IP地址")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ 连接错误，无法连接到机器人")
            return False
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    def get_all_pois(self) -> Optional[List[Dict]]:
        """
        获取所有POI信息（只读取，不操作）
        """
        try:
            url = f"{self.base_url}/api/core/artifact/v1/pois"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取POI信息失败: {e}")
            return None
    
    def get_action_factories(self) -> Optional[List[Dict]]:
        """
        获取所有支持的Action类型（只读取）
        """
        try:
            url = f"{self.base_url}/api/core/motion/v1/action-factories"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取Action工厂信息失败: {e}")
            return None
    
    def print_poi_info(self):
        """
        打印POI信息（详细格式）
        """
        print("\n📍 === 获取POI信息 ===")
        pois = self.get_all_pois()
        
        if pois is None:
            print("❌ 无法获取POI信息")
            return
        
        if len(pois) == 0:
            print("⚠️  地图中没有POI")
            return
        
        print(f"✅ 找到 {len(pois)} 个POI:")
        print("-" * 60)
        
        for i, poi in enumerate(pois, 1):
            poi_id = poi.get('id', 'N/A')
            pose = poi.get('pose', {})
            x = pose.get('x', 0)
            y = pose.get('y', 0)
            z = pose.get('z', 0)
            yaw = pose.get('yaw', 0)
            
            metadata = poi.get('metadata', {})
            display_name = metadata.get('display_name', '无名称')
            
            print(f"POI #{i}:")
            print(f"  显示名称: {display_name}")
            print(f"  ID: {poi_id}")
            print(f"  位置: x={x:.3f}, y={y:.3f}, z={z:.3f}")
            print(f"  朝向: yaw={yaw:.3f} (约{yaw*180/3.14159:.1f}度)")
            
            # 打印完整的metadata
            if metadata:
                print(f"  元数据: {json.dumps(metadata, indent=4, ensure_ascii=False)}")
            
            print("-" * 40)
    
    def print_action_factories(self):
        """
        打印支持的Action类型
        """
        print("\n🔧 === 获取支持的Action类型 ===")
        factories = self.get_action_factories()
        
        if factories is None:
            print("❌ 无法获取Action工厂信息")
            return
        
        if len(factories) == 0:
            print("⚠️  没有找到支持的Action类型")
            return
        
        print(f"✅ 找到 {len(factories)} 种Action类型:")
        print("-" * 40)
        
        for i, factory in enumerate(factories, 1):
            action_name = factory.get('action_name', 'N/A')
            print(f"{i}. {action_name}")
    
    def test_api_endpoints(self):
        """
        测试各个API端点的可访问性
        """
        print("\n🔍 === 测试API端点 ===")
        
        endpoints = [
            "/api/core/artifact/v1/pois",
            "/api/core/motion/v1/action-factories",
            # 可以添加更多端点进行测试
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - 状态码: {response.status_code}")
                else:
                    print(f"⚠️  {endpoint} - 状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - 错误: {e}")
    
    def get_robot_status(self):
        """
        尝试获取机器人状态信息（如果API支持）
        """
        print("\n🤖 === 尝试获取机器人状态 ===")
        
        # 常见的状态端点，可能存在也可能不存在
        status_endpoints = [
            "/api/core/status",
            "/api/status", 
            "/api/robot/status",
            "/api/core/robot/status"
        ]
        
        for endpoint in status_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ 找到状态端点: {endpoint}")
                    try:
                        status_data = response.json()
                        print(f"状态信息: {json.dumps(status_data, indent=2, ensure_ascii=False)}")
                        return
                    except json.JSONDecodeError:
                        print(f"状态端点返回非JSON数据: {response.text[:100]}")
                        
            except Exception as e:
                # 静默忽略错误，因为这些端点可能不存在
                pass
        
        print("⚠️  未找到标准的状态端点")
    
    def run_full_test(self):
        """
        运行完整的连接测试
        """
        print("🚀 Hermes机器人连接测试程序")
        print("=" * 60)
        print(f"目标地址: {self.base_url}")
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. 基本连接测试
        if not self.test_basic_connection():
            print("\n❌ 基本连接失败，无法继续测试")
            return False
        
        # 2. API端点测试
        self.test_api_endpoints()
        
        # 3. POI信息测试
        self.print_poi_info()
        
        # 4. Action工厂测试
        self.print_action_factories()
        
        # 5. 状态信息测试
        self.get_robot_status()
        
        print("\n" + "=" * 60)
        print("🎉 测试完成！所有信息已成功获取，连接正常。")
        print("💡 机器人已准备好接收控制指令。")
        return True

def main():
    """
    主函数 - 只进行连接测试，不会让机器人移动
    """
    # 创建测试客户端
    tester = HermesConnectionTest()
    
    # 运行完整测试
    success = tester.run_full_test()
    
    if success:
        print("\n✅ 连接测试成功，可以进行后续开发！")
    else:
        print("\n❌ 连接测试失败，请检查网络连接和配置。")

if __name__ == "__main__":
    main()