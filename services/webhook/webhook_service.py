#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT Webhook 自动通知服务
支持文件监控、调试检测、Git提交等事件的自动webhook发送
"""

import json
import yaml
import requests
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import socket
import os


class WebhookNotifier:
    """Webhook通知服务"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        self.logger = self._setup_logger()
        self.session = requests.Session()
        
    def _find_config_file(self) -> str:
        """查找配置文件"""
        possible_paths = [
            Path(__file__).parent.parent.parent / "config" / "webhook_config.yaml",
            Path("config/webhook_config.yaml"),
            Path("webhook_config.yaml")
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError("未找到webhook配置文件")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"错误：无法加载webhook配置: {e}")
            return {}
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('webhook_notifier')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def send_notification(self, event_type: str, data: Dict[str, Any]) -> bool:
        """发送webhook通知"""
        if not self.config.get('webhook', {}).get('enabled', False):
            self.logger.info("Webhook未启用，跳过发送")
            return False
            
        webhook_url = self.config.get('webhook', {}).get('url')
        if not webhook_url or webhook_url == "YOUR_WEBHOOK_URL_HERE":
            self.logger.warning("Webhook URL未配置")
            return False
        
        try:
            # 获取消息模板和关键词
            template = self.config.get('templates', {}).get(event_type, {})
            if not template:
                self.logger.warning(f"未找到事件类型 {event_type} 的模板")
                return False
            
            # 使用统一关键词或模板中的关键词
            keyword = self.config.get('webhook', {}).get('keyword', template.get('keyword', 'infobot'))
            title = template.get('title', '')
            message_format = template.get('format', '')
            
            # 准备消息数据
            message_data = {
                'timestamp': datetime.now().strftime(
                    self.config.get('webhook', {}).get('message_format', {}).get('timestamp_format', '%Y-%m-%d %H:%M:%S')
                ),
                'hostname': socket.gethostname() if self.config.get('webhook', {}).get('message_format', {}).get('include_hostname', True) else '',
                'project': 'XC-ROBOT' if self.config.get('webhook', {}).get('message_format', {}).get('include_project_name', True) else '',
                **data
            }
            
            # 格式化消息内容
            formatted_message = message_format.format(**message_data)
            
            # 构建飞书webhook payload
            payload = {
                'msg_type': 'text',
                'content': {
                    'text': f"{title}\n\n{formatted_message}"
                }
            }
            
            # 发送webhook请求
            response = self.session.post(
                webhook_url,
                json=payload,
                timeout=self.config.get('webhook', {}).get('timeout', 30),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.logger.info(f"Webhook发送成功: {event_type} - {keyword}")
                return True
            else:
                self.logger.error(f"Webhook发送失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送webhook时发生错误: {e}")
            return False
    
    def send_file_event(self, filename: str, event_type: str, description: str = "", changes: str = ""):
        """发送文件操作事件"""
        data = {
            'filename': filename,
            'description': description or f"代码文件{event_type}",
            'changes': changes
        }
        
        template_key = f"file_{event_type}"
        self.send_notification(template_key, data)
    
    def send_debug_success(self, debug_info: str, result: str = "成功"):
        """发送调试成功事件"""
        data = {
            'debug_info': debug_info,
            'result': result
        }
        self.send_notification('debug_success', data)
    
    def send_commit_event(self, commit_message: str, file_count: int, author: str = ""):
        """发送Git提交事件"""
        data = {
            'commit_message': commit_message,
            'file_count': file_count,
            'author': author or os.getenv('USER', 'Unknown')
        }
        self.send_notification('commit_event', data)
    
    def send_test_complete(self, test_type: str, result: str):
        """发送测试完成事件"""
        data = {
            'test_type': test_type,
            'result': result
        }
        self.send_notification('test_complete', data)
    
    def send_error_alert(self, error_type: str, error_details: str):
        """发送错误警告事件"""
        data = {
            'error_type': error_type,
            'error_details': error_details
        }
        self.send_notification('error_alert', data)


# 全局通知器实例
_notifier = None

def get_webhook_notifier() -> WebhookNotifier:
    """获取webhook通知器实例（单例）"""
    global _notifier
    if _notifier is None:
        _notifier = WebhookNotifier()
    return _notifier


# 便捷函数
def notify_file_created(filename: str, description: str = ""):
    """通知文件创建"""
    get_webhook_notifier().send_file_event(filename, "created", description)

def notify_file_modified(filename: str, changes: str = ""):
    """通知文件修改"""
    get_webhook_notifier().send_file_event(filename, "modified", changes=changes)

def notify_debug_success(debug_info: str, result: str = "成功"):
    """通知调试成功"""
    get_webhook_notifier().send_debug_success(debug_info, result)

def notify_commit(commit_message: str, file_count: int, author: str = ""):
    """通知Git提交"""
    get_webhook_notifier().send_commit_event(commit_message, file_count, author)

def notify_test_complete(test_type: str, result: str):
    """通知测试完成"""
    get_webhook_notifier().send_test_complete(test_type, result)

def notify_error(error_type: str, error_details: str):
    """通知错误"""
    get_webhook_notifier().send_error_alert(error_type, error_details)


if __name__ == "__main__":
    # 测试示例
    notifier = WebhookNotifier()
    
    # 测试各种通知
    notify_file_created("test_webhook.py", "Webhook测试文件")
    notify_debug_success("系统测试", "所有测试通过")
    notify_commit("feat: 添加webhook自动通知系统", 5, "Claude")