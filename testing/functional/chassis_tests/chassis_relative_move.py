#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
底盘相对移动控制程序
"""

import requests
import math
import time

def get_current_pose(base_url="http://192.168.31.211:1448"):
    """获取当前位置"""
    endpoints = ["/api/core/slam/v1/localization/pose", "/api/core/robot/pose", "/api/robot/pose", "/api/core/pose"]
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'x' in data and 'y' in data:
                    return data
                elif 'pose' in data:
                    return data['pose']
        except:
            continue
    return None

def move_to_position(x, y, yaw, base_url="http://192.168.31.211:1448"):
    """移动到指定位置"""
    url = f"{base_url}/api/core/motion/v1/actions"
    payload = {
        "action_name": "slamtec.agent.actions.MoveToAction",
        "options": {
            "target": {"x": x, "y": y, "z": 0},
            "move_options": {
                "mode": 0,
                "flags": [],
                "yaw": yaw,
                "acceptable_precision": 0.1,
                "fail_retry_count": 3,
                "speed_ratio": 0.8
            }
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get('action_id')
    else:
        print(f"创建action失败: {response.status_code}, {response.text}")
    return None

def wait_for_completion(action_id, base_url="http://192.168.31.211:1448"):
    """等待动作完成"""
    url = f"{base_url}/api/core/motion/v1/actions/{action_id}"
    for i in range(60):
        response = requests.get(url)
        if response.status_code == 200:
            status = response.json()
            state = status.get('state', {})
            action_status = state.get('status')
            if action_status == 4:  # 完成
                result = state.get('result', -1)
                if result == 0:
                    return True
                else:
                    print(f"动作失败，结果码: {result}, 原因: {state.get('reason', '未知')}")
                    return False
            elif i % 5 == 0:  # 每5秒打印一次状态
                print(f"等待中... 状态: {action_status}")
        time.sleep(1)
    return False

def main():
    # 获取当前位置
    print("获取当前位置...")
    pose = get_current_pose()
    if not pose:
        print("无法获取当前位置")
        return
    
    current_x = pose.get('x', 0)
    current_y = pose.get('y', 0)
    current_yaw = pose.get('yaw', 0)
    
    print(f"\n当前位置: x={current_x:.3f}m, y={current_y:.3f}m, yaw={current_yaw:.3f}rad")
    
    # 选择方向
    print("\n选择移动方向:")
    print("1. 前进")
    print("2. 后退")
    print("3. 左移")
    print("4. 右移")
    print("5. 左转")
    print("6. 右转")
    
    choice = input("\n请输入选择(1-6): ")
    
    # 输入距离或角度
    if choice in ['1', '2', '3', '4']:
        distance = float(input("请输入移动距离(米，建议0.1-2.0): "))
        if distance > 5.0:
            print("警告：距离过大可能导致无法到达")
    elif choice in ['5', '6']:
        angle = float(input("请输入转向角度(度，建议15-90): "))
        distance = math.radians(angle)
    else:
        print("无效选择")
        return
    
    # 计算目标位置
    target_x = current_x
    target_y = current_y
    target_yaw = current_yaw
    
    if choice == '1':  # 前进
        target_x = current_x + distance * math.cos(current_yaw)
        target_y = current_y + distance * math.sin(current_yaw)
    elif choice == '2':  # 后退
        target_x = current_x - distance * math.cos(current_yaw)
        target_y = current_y - distance * math.sin(current_yaw)
    elif choice == '3':  # 左移
        target_x = current_x + distance * math.cos(current_yaw + math.pi/2)
        target_y = current_y + distance * math.sin(current_yaw + math.pi/2)
    elif choice == '4':  # 右移
        target_x = current_x + distance * math.cos(current_yaw - math.pi/2)
        target_y = current_y + distance * math.sin(current_yaw - math.pi/2)
    elif choice == '5':  # 左转
        target_yaw = current_yaw + distance
    elif choice == '6':  # 右转
        target_yaw = current_yaw - distance
    
    print(f"\n目标位置: x={target_x:.3f}m, y={target_y:.3f}m, yaw={target_yaw:.3f}rad")
    
    # 确认执行
    confirm = input("\n确认执行移动？(y/n): ")
    if confirm.lower() != 'y':
        print("取消移动")
        return
    
    # 执行移动
    print("\n开始移动...")
    action_id = move_to_position(target_x, target_y, target_yaw)
    if not action_id:
        print("创建移动指令失败")
        return
    
    print(f"移动指令已发送 (ID: {action_id})")
    
    # 等待完成
    if wait_for_completion(action_id):
        print("移动完成!")
    else:
        print("移动失败")

if __name__ == "__main__":
    main()