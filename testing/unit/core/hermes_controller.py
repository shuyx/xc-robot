import requests
import json
import time
from typing import List, Dict, Optional

class HermesRobotAPI:
    def __init__(self, base_url: str = "http://192.168.31.211:1448"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_all_pois(self) -> List[Dict]:
        """
        获取当前地图中的所有POI信息
        返回POI列表，每个POI包含id、pose和metadata
        """
        try:
            url = f"{self.base_url}/api/core/artifact/v1/pois"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取POI信息失败: {e}")
            return []
    
    def get_action_factories(self) -> List[Dict]:
        """
        获取所有支持的Action类型
        返回支持的action_name列表
        """
        try:
            url = f"{self.base_url}/api/core/motion/v1/action-factories"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取Action工厂信息失败: {e}")
            return []
    
    def create_move_to_action(self, x: float, y: float, z: float = 0, 
                            yaw: float = 0, mode: int = 0, 
                            acceptable_precision: float = 0.1,
                            fail_retry_count: int = 3,
                            speed_ratio: float = 1.0) -> Optional[int]:
        """
        创建移动到指定位置的Action
        
        Args:
            x, y, z: 目标位置坐标
            yaw: 目标朝向角度
            mode: 移动模式
            acceptable_precision: 可接受的精度
            fail_retry_count: 失败重试次数
            speed_ratio: 速度比率
            
        Returns:
            action_id: 创建成功返回action ID，失败返回None
        """
        try:
            url = f"{self.base_url}/api/core/motion/v1/actions"
            payload = {
                "action_name": "slamtec.agent.actions.MoveToAction",
                "options": {
                    "target": {
                        "x": x,
                        "y": y,
                        "z": z
                    },
                    "move_options": {
                        "mode": mode,
                        "flags": [],
                        "yaw": yaw,
                        "acceptable_precision": acceptable_precision,
                        "fail_retry_count": fail_retry_count,
                        "speed_ratio": speed_ratio
                    }
                }
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get('action_id')
        except requests.exceptions.RequestException as e:
            print(f"创建移动Action失败: {e}")
            return None
    
    def get_action_status(self, action_id: int) -> Optional[Dict]:
        """
        查询Action状态
        
        Args:
            action_id: Action ID
            
        Returns:
            包含action状态信息的字典，失败返回None
        """
        try:
            url = f"{self.base_url}/api/core/motion/v1/actions/{action_id}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"查询Action状态失败: {e}")
            return None
    
    def wait_for_action_completion(self, action_id: int, timeout: int = 60) -> bool:
        """
        等待Action完成
        
        Args:
            action_id: Action ID
            timeout: 超时时间（秒）
            
        Returns:
            True表示成功完成，False表示失败或超时
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_action_status(action_id)
            if not status:
                return False
            
            # status为4表示action已结束
            if status.get('state', {}).get('status') == 4:
                result = status.get('state', {}).get('result', -1)
                if result == 0:  # 假设0表示成功
                    print(f"Action {action_id} 执行成功")
                    return True
                else:
                    reason = status.get('state', {}).get('reason', '未知错误')
                    print(f"Action {action_id} 执行失败: {reason}")
                    return False
            
            # 打印当前状态
            stage = status.get('stage', 'UNKNOWN')
            print(f"Action {action_id} 当前状态: {stage}")
            
            time.sleep(1)  # 每秒检查一次
        
        print(f"Action {action_id} 执行超时")
        return False
    
    # 🔄 MODIFIED: 修改为通过display_name查找POI
    def find_poi_by_display_name(self, display_name: str) -> Optional[Dict]:
        """
        通过display_name查找POI
        
        Args:
            display_name: POI的显示名称（如'p1', 'p2'）
            
        Returns:
            找到的POI字典，未找到返回None
        """
        pois = self.get_all_pois()
        
        for poi in pois:
            metadata = poi.get('metadata', {})
            if metadata.get('display_name') == display_name:
                return poi
        
        return None
    
    # 🔄 MODIFIED: 修改为支持通过display_name移动
    def move_to_poi(self, poi_identifier: str) -> bool:
        """
        移动到指定POI位置
        
        Args:
            poi_identifier: POI的display_name（如'p1', 'p2'）或POI的ID
            
        Returns:
            True表示成功，False表示失败
        """
        # 首先尝试通过display_name查找
        target_poi = self.find_poi_by_display_name(poi_identifier)
        
        # 如果通过display_name没找到，再尝试通过ID查找
        if not target_poi:
            pois = self.get_all_pois()
            for poi in pois:
                if poi.get('id') == poi_identifier:
                    target_poi = poi
                    break
        
        if not target_poi:
            print(f"未找到POI: {poi_identifier}")
            return False
        
        # 获取目标位置
        pose = target_poi.get('pose', {})
        x = pose.get('x', 0)
        y = pose.get('y', 0)
        yaw = pose.get('yaw', 0)
        
        # 获取显示名称用于日志
        display_name = target_poi.get('metadata', {}).get('display_name', poi_identifier)
        poi_id = target_poi.get('id', 'N/A')
        
        print(f"移动到POI '{display_name}' (ID: {poi_id})")
        print(f"目标位置: x={x}, y={y}, yaw={yaw}")
        
        # 创建移动Action
        action_id = self.create_move_to_action(x, y, yaw=yaw)
        if not action_id:
            return False
        
        # 等待完成
        return self.wait_for_action_completion(action_id)
    
    def execute_movement_sequence(self, poi_sequence: List[str]) -> bool:
        """
        执行连续的POI移动序列
        
        Args:
            poi_sequence: POI display_name的列表，按顺序移动
            
        Returns:
            True表示整个序列都成功完成，False表示任何一步失败
        """
        print(f"开始执行移动序列: {' → '.join(poi_sequence)}")
        print("="*60)
        
        for i, poi_name in enumerate(poi_sequence, 1):
            print(f"\n步骤 {i}/{len(poi_sequence)}: 移动到 {poi_name}")
            print("-"*40)
            
            success = self.move_to_poi(poi_name)
            if not success:
                print(f"❌ 移动到 {poi_name} 失败，序列终止")
                return False
            
            print(f"✅ 成功到达 {poi_name}")
            
            # 如果不是最后一个位置，等待一下再继续
            if i < len(poi_sequence):
                print("等待2秒后继续下一步...")
                time.sleep(2)
        
        print("\n🎉 所有移动序列执行完成！")
        return True
    
    # 🆕 NEW: 添加自动执行两个POI往返的方法
    def execute_auto_round_trip(self) -> bool:
        """
        自动执行两个POI之间的往返移动
        自动识别地图中的所有POI，按顺序执行：POI1 → POI2 → POI1
        
        Returns:
            True表示往返成功，False表示失败
        """
        # 获取所有POI
        pois = self.get_all_pois()
        if len(pois) < 2:
            print(f"❌ 地图中只有 {len(pois)} 个POI，至少需要2个POI才能执行往返移动")
            return False
        
        # 提取POI的display_name，按字母顺序排序
        poi_names = []
        for poi in pois:
            display_name = poi.get('metadata', {}).get('display_name')
            if display_name:
                poi_names.append(display_name)
        
        poi_names.sort()  # 按字母顺序排序，确保p1在p2前面
        
        if len(poi_names) < 2:
            print("❌ 没有找到足够的有效POI（需要有display_name）")
            return False
        
        poi1 = poi_names[0]  # 第一个POI
        poi2 = poi_names[1]  # 第二个POI
        
        print(f"📍 自动识别到POI: {poi1}, {poi2}")
        print(f"执行路径：当前位置 → {poi1} → {poi2} → {poi1}")
        
        # 执行往返移动
        sequence = [poi1, poi2, poi1]
        return self.execute_movement_sequence(sequence)
    
    def execute_round_trip(self, poi1: str, poi2: str) -> bool:
        """
        执行往返移动：当前位置 → poi1 → poi2 → poi1
        
        Args:
            poi1: 第一个POI的display_name
            poi2: 第二个POI的display_name
            
        Returns:
            True表示往返成功，False表示失败
        """
        sequence = [poi1, poi2, poi1]
        return self.execute_movement_sequence(sequence)
    
    def print_all_pois(self):
        """打印所有POI信息"""
        pois = self.get_all_pois()
        if not pois:
            print("没有找到POI信息")
            return
        
        print("当前地图中的POI信息:")
        print("-" * 50)
        for poi in pois:
            poi_id = poi.get('id', 'N/A')
            pose = poi.get('pose', {})
            x = pose.get('x', 0)
            y = pose.get('y', 0)
            yaw = pose.get('yaw', 0)
            display_name = poi.get('metadata', {}).get('display_name', '无名称')
            print(f"显示名称: {display_name}")
            print(f"ID: {poi_id}")
            print(f"位置: x={x}, y={y}, yaw={yaw}")
            print(f"完整元数据: {poi.get('metadata', {})}")
            print("-" * 30)
    
    def print_action_factories(self):
        """打印所有支持的Action类型"""
        factories = self.get_action_factories()
        if not factories:
            print("没有找到支持的Action类型")
            return
        
        print("支持的Action类型:")
        print("-" * 30)
        for factory in factories:
            action_name = factory.get('action_name', 'N/A')
            print(f"- {action_name}")

# 🔄 MODIFIED: 简化main函数，使用自动识别
def main():
    """
    主函数：自动执行两个POI之间的往返移动
    """
    # 创建API客户端
    robot = HermesRobotAPI()
    print(f"连接到Hermes机器人: {robot.base_url}")
    
    # 查看所有POI
    print("\n=== 当前地图中的POI信息 ===")
    robot.print_all_pois()
    
    # 自动执行往返移动
    print("\n=== 开始执行自动往返移动任务 ===")
    
    success = robot.execute_auto_round_trip()
    
    if success:
        print("\n🎉 往返移动任务完成！")
        print("机器人已完成所有移动序列")
    else:
        print("\n❌ 往返移动任务失败")

# 测试连接的简单函数
def test_connection():
    """测试与Hermes机器人的连接"""
    robot = HermesRobotAPI()
    print(f"测试连接: {robot.base_url}")
    
    # 尝试获取POI信息来测试连接
    pois = robot.get_all_pois()
    if pois is not None:
        print("✅ 连接成功！")
        print(f"找到 {len(pois)} 个POI")
        return True
    else:
        print("❌ 连接失败，请检查网络和IP地址")
        return False

if __name__ == "__main__":
    # 首先测试连接
    if test_connection():
        print("\n" + "="*60)
        main()
    else:
        print("无法连接到机器人，程序终止")
