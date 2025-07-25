#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
底盘刹车复位程序
"""

import requests
import json

def get_robot_status(base_url="http://192.168.31.211:1448"):
    """获取机器人状态"""
    endpoints = [
        "/api/core/status",
        "/api/core/robot/status",
        "/api/robot/status"
    ]
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            continue
    return None

def reset_brake(base_url="http://192.168.31.211:1448"):
    """尝试复位刹车"""
    # 尝试不同的复位API
    reset_endpoints = [
        ("/api/core/motion/v1/brake/release", {"release": False}),
        ("/api/core/motion/v1/brake/reset", {}),
        ("/api/core/robot/brake/engage", {}),
        ("/api/core/system/reset-errors", {})
    ]
    
    for endpoint, payload in reset_endpoints:
        try:
            print(f"尝试: {endpoint}")
            response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=5)
            print(f"结果: {response.status_code}")
            if response.status_code == 200:
                print("✅ 成功")
                return True
        except Exception as e:
            print(f"❌ 失败: {e}")
    return False

def main():
    print("底盘刹车状态检查与复位")
    print("="*40)
    
    # 获取状态
    print("\n1. 检查机器人状态...")
    status = get_robot_status()
    if status:
        print(f"状态信息: {json.dumps(status, indent=2, ensure_ascii=False)}")
    else:
        print("无法获取状态信息")
    
    # 尝试复位
    print("\n2. 尝试复位刹车...")
    if reset_brake():
        print("\n✅ 刹车复位成功，请尝试重新运行移动程序")
    else:
        print("\n❌ 自动复位失败")
        print("\n请尝试以下操作:")
        print("1. 检查底盘急停按钮是否被按下")
        print("2. 在RoboStudio中手动复位")
        print("3. 重启底盘控制器")
        print("4. 检查底盘是否处于手动模式")

if __name__ == "__main__":
    main()