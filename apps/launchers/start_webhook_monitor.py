#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT Webhook监控启动器
启动自动化webhook通知服务
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.webhook.webhook_daemon import WebhookDaemon
from services.webhook import (
    notify_file_created, 
    notify_debug_success, 
    notify_commit,
    get_webhook_notifier
)


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    XC-ROBOT Webhook Monitor                  ║
║                      自动化通知服务                           ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_keywords():
    """打印关键词配置信息"""
    print("\n📋 Webhook关键词配置清单:")
    print("=" * 50)
    
    keywords = {
        "code_file": "代码文件操作通知（创建/修改）",
        "debug_success": "调试成功状态通知", 
        "commit": "Git提交事件通知",
        "test_complete": "测试完成结果通知",
        "error_alert": "错误警告通知"
    }
    
    for keyword, description in keywords.items():
        print(f"🔑 {keyword:<15} - {description}")
    
    print("\n💡 配置说明:")
    print("1. 在您的webhook机器人中设置上述任一关键词")
    print("2. 系统会根据事件类型自动选择对应关键词发送消息")
    print("3. 配置文件位置: config/webhook_config.yaml")
    print("4. 请将YOUR_WEBHOOK_URL_HERE替换为实际的webhook URL")


def test_webhook():
    """测试webhook发送"""
    print("\n🧪 测试Webhook发送功能...")
    
    try:
        # 测试各种通知类型
        notify_file_created("webhook_test.py", "Webhook测试文件")
        print("✅ 文件创建通知测试完成")
        
        notify_debug_success("Webhook系统测试", "所有组件正常运行")
        print("✅ 调试成功通知测试完成")
        
        notify_commit("feat: 添加webhook自动通知系统", 3, "XC-ROBOT")
        print("✅ Git提交通知测试完成")
        
        print("\n🎉 Webhook测试发送完成！请检查您的消息接收端。")
        
    except Exception as e:
        print(f"❌ Webhook测试失败: {e}")


def check_config():
    """检查配置状态"""
    print("\n🔍 检查配置状态...")
    
    try:
        notifier = get_webhook_notifier()
        config = notifier.config
        
        webhook_config = config.get('webhook', {})
        
        print(f"📄 配置文件: {notifier.config_path}")
        print(f"🔧 Webhook启用: {'✅' if webhook_config.get('enabled', False) else '❌'}")
        
        url = webhook_config.get('url', '')
        if url and url != "YOUR_WEBHOOK_URL_HERE":
            print(f"🌐 Webhook URL: ✅ 已配置")
        else:
            print(f"🌐 Webhook URL: ❌ 未配置或使用默认值")
            print("   请在config/webhook_config.yaml中设置正确的URL")
        
        # 检查各监控模块状态
        monitoring = config.get('monitoring', {})
        file_watch = monitoring.get('file_watch', {}).get('enabled', False)
        debug_watch = monitoring.get('debug_watch', {}).get('enabled', False)
        git_watch = monitoring.get('git_watch', {}).get('enabled', False)
        
        print(f"📁 文件监控: {'✅' if file_watch else '❌'}")
        print(f"🐛 调试监控: {'✅' if debug_watch else '❌'}")
        print(f"📦 Git监控: {'✅' if git_watch else '❌'}")
        
    except Exception as e:
        print(f"❌ 检查配置时出错: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XC-ROBOT Webhook监控启动器')
    parser.add_argument('--test', action='store_true', help='测试webhook发送')
    parser.add_argument('--config-check', action='store_true', help='检查配置状态')
    parser.add_argument('--keywords', action='store_true', help='显示关键词配置')
    parser.add_argument('--daemon', action='store_true', help='启动守护服务')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.keywords:
        print_keywords()
        return
    
    if args.config_check:
        check_config()
        return
    
    if args.test:
        test_webhook()
        return
    
    if args.daemon:
        print("🚀 启动Webhook监控守护服务...")
        daemon = WebhookDaemon(work_dir=str(project_root))
        daemon.run_forever()
        return
    
    # 默认显示帮助和关键词信息
    print_keywords()
    print("\n🚀 启动选项:")
    print("  --daemon        启动后台监控服务")
    print("  --test          测试webhook发送")
    print("  --config-check  检查配置状态")
    print("  --keywords      显示关键词配置")
    print("\n💡 使用示例:")
    print("  python start_webhook_monitor.py --daemon")
    print("  python start_webhook_monitor.py --test")


if __name__ == "__main__":
    main()