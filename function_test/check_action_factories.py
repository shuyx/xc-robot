#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查底盘支持的action类型
"""

import requests

def check_action_factories(base_url="http://192.168.31.211:1448"):
    """检查支持的action类型"""
    url = f"{base_url}/api/core/motion/v1/action-factories"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            factories = response.json()
            print("支持的action类型:")
            for i, factory in enumerate(factories, 1):
                print(f"{i}. {factory.get('action_name', 'Unknown')}")
            return factories
        else:
            print(f"获取失败: {response.status_code}")
    except Exception as e:
        print(f"错误: {e}")
    return None

if __name__ == "__main__":
    check_action_factories()