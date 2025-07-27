#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT Webhook服务启动脚本
简化版后台启动脚本
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.webhook.webhook_daemon import WebhookDaemon


def start_webhook_service():
    """启动webhook服务"""
    print("🚀 启动XC-ROBOT Webhook后台监控服务...")
    
    try:
        # 创建日志目录
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 创建守护服务
        daemon = WebhookDaemon(work_dir=str(project_root))
        
        # 检查配置
        status = daemon.status()
        if not status['webhook_enabled']:
            print("❌ Webhook未启用，请检查配置文件")
            return False
            
        if not status['webhook_url_configured']:
            print("❌ Webhook URL未配置，请检查配置文件")
            return False
        
        print("✅ 配置检查通过")
        
        # 启动服务
        daemon.start()
        
        if daemon.running:
            print("✅ Webhook监控服务启动成功")
            print("📁 日志位置: logs/webhook_daemon.log")
            print("🔄 监控功能:")
            for service in daemon.services_started:
                print(f"   • {service}")
            
            print("\n💡 服务将在后台运行，监控以下事件:")
            print("   • 代码文件修改 (*.py, *.js, *.html, *.css)")
            print("   • 调试成功标识")
            print("   • Git提交操作")
            print("\n按Ctrl+C停止服务...")
            
            # 保持运行
            try:
                while daemon.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 收到停止信号，正在关闭服务...")
                daemon.stop()
                print("✅ 服务已停止")
                
            return True
        else:
            print("❌ 服务启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 启动服务时出错: {e}")
        return False


if __name__ == "__main__":
    start_webhook_service()